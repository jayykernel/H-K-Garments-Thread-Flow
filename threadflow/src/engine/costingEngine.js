/**
 * ============================================================================
 * H&K CLOTHING — THREADFLOW
 * Pure Garment Costing Calculation Engine (costingEngine.js)
 * ============================================================================
 *
 * MATHEMATICAL FORMULAS, UNITS & ASSUMPTIONS:
 * 1. Supported Sizes: S, M, L, XL, XXL, XXXL
 * 2. Supported Garment Types: 'Top', 'Bottom'
 * 3. Supported Categories: "Men's", 'Ladies', 'Other'
 * 4. Standard Components:
 *    - Main Body (Front + Back panels for Top; Left + Right leg panels for Bottom)
 *    - Sleeve (Left + Right sleeves for Top; optional for sleeveless/Bottom)
 *    - Rib (Neck band, cuff rib, hem rib, or waistband rib)
 *    - BNT (Back Neck Tape / binding trim)
 *    - Yoke (Back/Front shoulder yoke or waist yoke)
 *    - Other Parts (Dynamically added custom panels: Pockets, Hood, Placket, Gusset, etc.)
 *
 * 5. Component Cut Area & Net Weight (per size s, component c, assigned fabric f):
 *    - CutLength_cm = lengthCm + seamAllowanceCm
 *    - CutWidth_cm  = widthCm + seamAllowanceCm
 *    - CutArea_cm2  = CutLength_cm * CutWidth_cm * panelMultiplier
 *    - CutArea_m2   = CutArea_cm2 / 10,000  (1 m^2 = 10,000 cm^2)
 *    - ComponentNetWeight_g = CutArea_m2 * FabricGSM_g_per_m2
 *    - ComponentNetWeight_kg = ComponentNetWeight_g / 1,000
 *
 * 6. Distinction Between Garment Net Weight, Fabric Consumption, and Fabric Cost:
 *    - Garment Net Weight (g / kg): The physical finished + seam cut weight of the garment
 *      components before process wastage.
 *    - Gross Fabric Consumption (g / kg): Incorporates process wastage allowance
 *      (cutting marker loss, end-bit loss, knitting/compact shrinkage allowance):
 *        Consumption_g  = ComponentNetWeight_g * (1 + wastageAllowancePct / 100)
 *        Consumption_kg = Consumption_g / 1,000
 *    - Fabric Cost (INR):
 *        ComponentFabricCost = Consumption_kg * FabricPricePerKg
 *
 * 7. Missing Input vs. Legitimate Zero Handling:
 *    - A size quantity of 0 is a legitimate zero (that size is not ordered in this batch).
 *    - Missing measurements (null, undefined, '', NaN, or <= 0) on an ENABLED component,
 *      or an unassigned/non-existent fabric serial, or a missing/invalid fabric price/GSM,
 *      are NEVER silently coerced to zero. They generate explicit validation errors
 *      and mark `isComplete: false` so a costing record cannot be finalized with missing data.
 */

const SIZES = ['S', 'M', 'L', 'XL', 'XXL', 'XXXL'];
const GARMENT_TYPES = ['Top', 'Bottom'];
const GARMENT_CATEGORIES = ["Men's", 'Ladies', 'Other'];

const DEFAULT_STANDARD_COMPONENTS = [
  {
    key: 'main_body',
    name: 'Main Body',
    isCustom: false,
    enabled: true,
    panelMultiplier: 2,
    seamAllowanceCm: 3.0,
    description: 'Front & Back Torso Panels (Top) or Main Leg Panels (Bottom)'
  },
  {
    key: 'sleeve',
    name: 'Sleeve',
    isCustom: false,
    enabled: true,
    panelMultiplier: 2,
    seamAllowanceCm: 2.5,
    description: 'Left & Right Sleeve Panels'
  },
  {
    key: 'rib',
    name: 'Rib',
    isCustom: false,
    enabled: true,
    panelMultiplier: 1,
    seamAllowanceCm: 1.5,
    description: 'Neckband / Cuff / Waistband Rib Trim'
  },
  {
    key: 'bnt',
    name: 'BNT',
    isCustom: false,
    enabled: true,
    panelMultiplier: 1,
    seamAllowanceCm: 1.0,
    description: 'Back Neck Tape & Shoulder Reinforcement Binding'
  },
  {
    key: 'yoke',
    name: 'Yoke',
    isCustom: false,
    enabled: false,
    panelMultiplier: 1,
    seamAllowanceCm: 2.0,
    description: 'Upper Back Yoke or Waist Yoke Panel'
  }
];

function roundTo(value, decimals = 4) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return 0;
  const factor = Math.pow(10, decimals);
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

function gramsToKilograms(grams) {
  if (typeof grams !== 'number' || !Number.isFinite(grams)) {
    throw new TypeError('gramsToKilograms requires a finite number');
  }
  return roundTo(grams / 1000, 6);
}

function kilogramsToGrams(kilograms) {
  if (typeof kilograms !== 'number' || !Number.isFinite(kilograms)) {
    throw new TypeError('kilogramsToGrams requires a finite number');
  }
  return roundTo(kilograms * 1000, 3);
}

function isMissingNumber(val) {
  if (val === null || val === undefined || val === '') return true;
  const num = Number(val);
  return !Number.isFinite(num);
}

/**
 * Calculates single component weight, consumption, and cost for one size.
 */
function calculateComponentForSize({
  lengthCm,
  widthCm,
  seamAllowanceCm = 2.5,
  panelMultiplier = 2,
  fabricGsm,
  fabricPricePerKg,
  wastageAllowancePct = 8
}) {
  if (
    isMissingNumber(lengthCm) ||
    isMissingNumber(widthCm) ||
    isMissingNumber(fabricGsm) ||
    isMissingNumber(fabricPricePerKg)
  ) {
    return {
      valid: false,
      error: 'Missing required measurement, GSM, or fabric price input',
      cutAreaCm2: null,
      cutAreaM2: null,
      netWeightGrams: null,
      netWeightKg: null,
      consumptionGrams: null,
      consumptionKg: null,
      fabricCost: null
    };
  }

  const len = Number(lengthCm);
  const wid = Number(widthCm);
  const seam = isMissingNumber(seamAllowanceCm) ? 0 : Number(seamAllowanceCm);
  const mult = isMissingNumber(panelMultiplier) ? 1 : Number(panelMultiplier);
  const gsm = Number(fabricGsm);
  const price = Number(fabricPricePerKg);
  const wastage = isMissingNumber(wastageAllowancePct) ? 0 : Number(wastageAllowancePct);

  if (len <= 0 || wid <= 0) {
    return {
      valid: false,
      error: 'Component length and width must be strictly greater than 0 cm',
      cutAreaCm2: null,
      cutAreaM2: null,
      netWeightGrams: null,
      netWeightKg: null,
      consumptionGrams: null,
      consumptionKg: null,
      fabricCost: null
    };
  }

  if (gsm <= 0 || price <= 0 || mult <= 0 || seam < 0 || wastage < 0) {
    return {
      valid: false,
      error: 'GSM, fabric price, and panel multiplier must be > 0; seam and wastage must be >= 0',
      cutAreaCm2: null,
      cutAreaM2: null,
      netWeightGrams: null,
      netWeightKg: null,
      consumptionGrams: null,
      consumptionKg: null,
      fabricCost: null
    };
  }

  const cutLengthCm = len + seam;
  const cutWidthCm = wid + seam;
  const cutAreaCm2 = cutLengthCm * cutWidthCm * mult;
  const cutAreaM2 = cutAreaCm2 / 10000;

  const netWeightGrams = cutAreaM2 * gsm;
  const netWeightKg = netWeightGrams / 1000;

  const consumptionGrams = netWeightGrams * (1 + wastage / 100);
  const consumptionKg = consumptionGrams / 1000;
  const fabricCost = consumptionKg * price;

  return {
    valid: true,
    error: null,
    cutLengthCm: roundTo(cutLengthCm, 2),
    cutWidthCm: roundTo(cutWidthCm, 2),
    cutAreaCm2: roundTo(cutAreaCm2, 2),
    cutAreaM2: roundTo(cutAreaM2, 5),
    netWeightGrams: roundTo(netWeightGrams, 3),
    netWeightKg: roundTo(netWeightKg, 5),
    consumptionGrams: roundTo(consumptionGrams, 3),
    consumptionKg: roundTo(consumptionKg, 5),
    fabricCost: roundTo(fabricCost, 2)
  };
}

/**
 * Evaluates an entire Costing Sheet input and returns full size-wise, component-wise,
 * and fabric-wise breakdowns alongside strict validation errors & warnings.
 */
function evaluateCostingSheet(costingInput) {
  const errors = [];
  const warnings = [];

  if (!costingInput || typeof costingInput !== 'object') {
    return {
      isComplete: false,
      canSaveDraft: false,
      errors: [{ field: 'root', message: 'Costing input payload is required.' }],
      warnings: [],
      summary: null
    };
  }

  const {
    styleNumber = '',
    styleName = '',
    primaryFabric = '',
    baseGsm,
    garmentType = 'Top',
    category = "Men's",
    wastageAllowancePct = 8,
    fabrics = [],
    sizeQuantities = {},
    components = []
  } = costingInput;

  // 1. Validate Garment Header Metadata
  if (!String(styleNumber).trim()) {
    errors.push({ step: 1, field: 'styleNumber', message: 'Style Number is required to identify the costing record.' });
  }
  if (!String(styleName).trim()) {
    errors.push({ step: 1, field: 'styleName', message: 'Style Name is required.' });
  }
  if (!String(primaryFabric).trim()) {
    warnings.push({ step: 1, field: 'primaryFabric', message: 'Primary fabric summary description is recommended.' });
  }
  if (isMissingNumber(baseGsm) || Number(baseGsm) <= 0) {
    errors.push({ step: 1, field: 'baseGsm', message: 'Base GSM must be a valid positive number (e.g., 180).' });
  }
  if (!GARMENT_TYPES.includes(garmentType)) {
    errors.push({ step: 1, field: 'garmentType', message: 'Garment Type must be Top or Bottom.' });
  }
  if (!GARMENT_CATEGORIES.includes(category)) {
    errors.push({ step: 1, field: 'category', message: "Category must be Men's, Ladies, or Other." });
  }
  if (isMissingNumber(wastageAllowancePct) || Number(wastageAllowancePct) < 0 || Number(wastageAllowancePct) > 50) {
    errors.push({ step: 1, field: 'wastageAllowancePct', message: 'Process wastage allowance must be between 0% and 50%.' });
  }

  // 2. Validate Fabrics
  const fabricMap = new Map();
  if (!Array.isArray(fabrics) || fabrics.length === 0) {
    errors.push({ step: 2, field: 'fabrics', message: 'At least one fabric entry must be configured in Fabric Setup.' });
  } else {
    fabrics.forEach((fab, idx) => {
      const serial = Number(fab.serialNo);
      if (!Number.isInteger(serial) || serial <= 0) {
        errors.push({ step: 2, field: `fabrics[${idx}].serialNo`, message: `Fabric row ${idx + 1} has an invalid serial number.` });
      } else if (fabricMap.has(serial)) {
        errors.push({ step: 2, field: `fabrics[${idx}].serialNo`, message: `Duplicate fabric serial number #${serial}.` });
      }
      if (!String(fab.description || '').trim()) {
        errors.push({ step: 2, field: `fabrics[${idx}].description`, message: `Fabric #${serial || idx + 1} requires a description/identifier.` });
      }
      if (!String(fab.colour || '').trim()) {
        errors.push({ step: 2, field: `fabrics[${idx}].colour`, message: `Fabric #${serial || idx + 1} requires a colour specification.` });
      }
      const effGsm = !isMissingNumber(fab.gsm) ? Number(fab.gsm) : Number(baseGsm);
      if (!Number.isFinite(effGsm) || effGsm <= 0) {
        errors.push({ step: 2, field: `fabrics[${idx}].gsm`, message: `Fabric #${serial || idx + 1} requires a valid GSM > 0.` });
      }
      if (isMissingNumber(fab.pricePerKg) || Number(fab.pricePerKg) <= 0) {
        errors.push({ step: 2, field: `fabrics[${idx}].pricePerKg`, message: `Fabric #${serial || idx + 1} requires a valid Price per Kg > 0.` });
      }
      if (Number.isInteger(serial) && serial > 0) {
        fabricMap.set(serial, {
          ...fab,
          serialNo: serial,
          effectiveGsm: effGsm,
          pricePerKg: isMissingNumber(fab.pricePerKg) ? null : Number(fab.pricePerKg)
        });
      }
    });
  }

  // 3. Validate Size Quantities (distinguish missing vs legitimate 0)
  const normalizedQuantities = {};
  let totalOrderQuantity = 0;
  let hasAnyPositiveSizeQty = false;

  for (const size of SIZES) {
    const rawQty = sizeQuantities ? sizeQuantities[size] : undefined;
    if (rawQty === null || rawQty === undefined || rawQty === '') {
      errors.push({
        step: 4,
        field: `sizeQuantities.${size}`,
        message: `Quantity for size ${size} is missing. Enter 0 if size ${size} is not ordered.`
      });
      normalizedQuantities[size] = 0;
    } else {
      const q = Number(rawQty);
      if (!Number.isInteger(q) || q < 0) {
        errors.push({
          step: 4,
          field: `sizeQuantities.${size}`,
          message: `Quantity for size ${size} must be a non-negative integer.`
        });
        normalizedQuantities[size] = 0;
      } else {
        normalizedQuantities[size] = q;
        totalOrderQuantity += q;
        if (q > 0) hasAnyPositiveSizeQty = true;
      }
    }
  }

  if (!hasAnyPositiveSizeQty) {
    errors.push({
      step: 4,
      field: 'sizeQuantities',
      message: 'Total order quantity across S–XXXL must be greater than 0 pieces to finalize costing.'
    });
  }

  // 4. Validate & Calculate Components across Sizes
  const enabledComponents = Array.isArray(components)
    ? components.filter((c) => c && c.enabled !== false)
    : [];

  if (enabledComponents.length === 0) {
    errors.push({
      step: 3,
      field: 'components',
      message: 'At least one garment component (e.g., Main Body) must be enabled.'
    });
  }

  // Check garment type specific guidance
  const mainBodyComp = enabledComponents.find((c) => c.key === 'main_body');
  if (!mainBodyComp) {
    warnings.push({
      step: 3,
      field: 'components.main_body',
      message: 'Main Body component is not enabled; verify whether this is intentional.'
    });
  }
  if (garmentType === 'Bottom') {
    const sleeveComp = enabledComponents.find((c) => c.key === 'sleeve');
    if (sleeveComp) {
      warnings.push({
        step: 3,
        field: 'components.sleeve',
        message: 'Garment type is Bottom, but Sleeve component is enabled. Disable Sleeve unless needed as a trim/panel.'
      });
    }
  }

  const componentBreakdown = [];
  const sizeSummaries = {};
  for (const size of SIZES) {
    sizeSummaries[size] = {
      size,
      quantity: normalizedQuantities[size],
      garmentNetWeightGrams: 0,
      garmentNetWeightKg: 0,
      garmentConsumptionGrams: 0,
      garmentConsumptionKg: 0,
      garmentFabricCost: 0,
      extendedNetWeightKg: 0,
      extendedConsumptionKg: 0,
      extendedFabricCost: 0,
      incompleteComponents: []
    };
  }

  const fabricRequirementsMap = new Map();
  for (const [serial, fab] of fabricMap.entries()) {
    fabricRequirementsMap.set(serial, {
      serialNo: serial,
      fabricCode: fab.fabricCode || `FAB-0${serial}`,
      description: fab.description || '',
      colour: fab.colour || '',
      gsm: fab.effectiveGsm,
      pricePerKg: fab.pricePerKg || 0,
      assignedComponents: [],
      totalNetWeightKg: 0,
      totalConsumptionKg: 0,
      totalCost: 0
    });
  }

  enabledComponents.forEach((comp, cIdx) => {
    const compName = String(comp.name || `Component ${cIdx + 1}`).trim();
    const assignedSerial = Number(comp.assignedFabricSerial);
    const assignedFabric = fabricMap.get(assignedSerial);

    if (!assignedFabric) {
      errors.push({
        step: 3,
        field: `components.${comp.key || cIdx}.assignedFabricSerial`,
        message: `Component "${compName}" is not assigned to a valid fabric serial number.`
      });
    } else {
      const reqEntry = fabricRequirementsMap.get(assignedSerial);
      if (reqEntry && !reqEntry.assignedComponents.includes(compName)) {
        reqEntry.assignedComponents.push(compName);
      }
    }

    const compSizesResult = {};
    for (const size of SIZES) {
      const m = comp.measurementsBySize && comp.measurementsBySize[size]
        ? comp.measurementsBySize[size]
        : {};
      const sizeQty = normalizedQuantities[size];

      const lengthMissing = isMissingNumber(m.lengthCm);
      const widthMissing = isMissingNumber(m.widthCm);

      if (lengthMissing || widthMissing) {
        const msg = `Component "${compName}" is missing ${lengthMissing && widthMissing ? 'Length & Width' : lengthMissing ? 'Length' : 'Width'} measurement for size ${size}.`;
        if (sizeQty > 0) {
          errors.push({
            step: 3,
            field: `components.${comp.key || cIdx}.${size}`,
            message: msg
          });
        } else {
          warnings.push({
            step: 3,
            field: `components.${comp.key || cIdx}.${size}`,
            message: `${msg} (Size ${size} currently has 0 order quantity).`
          });
        }
        sizeSummaries[size].incompleteComponents.push(compName);
        compSizesResult[size] = {
          valid: false,
          lengthCm: m.lengthCm ?? null,
          widthCm: m.widthCm ?? null,
          netWeightGrams: null,
          consumptionGrams: null,
          consumptionKg: null,
          fabricCost: null
        };
        continue;
      }

      const lenNum = Number(m.lengthCm);
      const widNum = Number(m.widthCm);
      if (lenNum <= 0 || widNum <= 0) {
        errors.push({
          step: 3,
          field: `components.${comp.key || cIdx}.${size}`,
          message: `Component "${compName}" in size ${size} must have Length and Width > 0 cm (got ${lenNum} x ${widNum}).`
        });
        sizeSummaries[size].incompleteComponents.push(compName);
        compSizesResult[size] = {
          valid: false,
          lengthCm: lenNum,
          widthCm: widNum,
          netWeightGrams: null,
          consumptionGrams: null,
          consumptionKg: null,
          fabricCost: null
        };
        continue;
      }

      if (!assignedFabric || isMissingNumber(assignedFabric.effectiveGsm) || isMissingNumber(assignedFabric.pricePerKg)) {
        sizeSummaries[size].incompleteComponents.push(compName);
        compSizesResult[size] = {
          valid: false,
          lengthCm: lenNum,
          widthCm: widNum,
          netWeightGrams: null,
          consumptionGrams: null,
          consumptionKg: null,
          fabricCost: null
        };
        continue;
      }

      const calc = calculateComponentForSize({
        lengthCm: lenNum,
        widthCm: widNum,
        seamAllowanceCm: comp.seamAllowanceCm ?? 2.5,
        panelMultiplier: comp.panelMultiplier ?? 2,
        fabricGsm: assignedFabric.effectiveGsm,
        fabricPricePerKg: assignedFabric.pricePerKg,
        wastageAllowancePct: Number(wastageAllowancePct)
      });

      if (!calc.valid) {
        errors.push({
          step: 3,
          field: `components.${comp.key || cIdx}.${size}`,
          message: `Component "${compName}" (${size}): ${calc.error}`
        });
        sizeSummaries[size].incompleteComponents.push(compName);
      } else {
        sizeSummaries[size].garmentNetWeightGrams = roundTo(
          sizeSummaries[size].garmentNetWeightGrams + calc.netWeightGrams,
          3
        );
        sizeSummaries[size].garmentConsumptionGrams = roundTo(
          sizeSummaries[size].garmentConsumptionGrams + calc.consumptionGrams,
          3
        );
        sizeSummaries[size].garmentFabricCost = roundTo(
          sizeSummaries[size].garmentFabricCost + calc.fabricCost,
          2
        );

        // Accumulate fabric requirements for ordered quantity
        const reqEntry = fabricRequirementsMap.get(assignedSerial);
        if (reqEntry && sizeQty > 0) {
          const extNetKg = (calc.netWeightGrams * sizeQty) / 1000;
          const extConsKg = calc.consumptionKg * sizeQty;
          const extCost = extConsKg * assignedFabric.pricePerKg;
          reqEntry.totalNetWeightKg = roundTo(reqEntry.totalNetWeightKg + extNetKg, 3);
          reqEntry.totalConsumptionKg = roundTo(reqEntry.totalConsumptionKg + extConsKg, 3);
          reqEntry.totalCost = roundTo(reqEntry.totalCost + extCost, 2);
        }
      }

      compSizesResult[size] = {
        ...calc,
        lengthCm: lenNum,
        widthCm: widNum
      };
    }

    componentBreakdown.push({
      key: comp.key || `custom_${cIdx}`,
      name: compName,
      isCustom: Boolean(comp.isCustom),
      enabled: true,
      assignedFabricSerial: assignedSerial,
      assignedFabricDescription: assignedFabric ? assignedFabric.description : 'Unassigned',
      assignedFabricColour: assignedFabric ? assignedFabric.colour : '—',
      panelMultiplier: Number(comp.panelMultiplier ?? 2),
      seamAllowanceCm: Number(comp.seamAllowanceCm ?? 2.5),
      bySize: compSizesResult
    });
  });

  // 5. Finalize Size-Wise & Order-Level Totals
  let totalOrderNetWeightKg = 0;
  let totalOrderConsumptionKg = 0;
  let totalOrderFabricCost = 0;

  for (const size of SIZES) {
    const s = sizeSummaries[size];
    s.garmentNetWeightKg = gramsToKilograms(s.garmentNetWeightGrams);
    s.garmentConsumptionKg = gramsToKilograms(s.garmentConsumptionGrams);
    s.extendedNetWeightKg = roundTo(s.garmentNetWeightKg * s.quantity, 3);
    s.extendedConsumptionKg = roundTo(s.garmentConsumptionKg * s.quantity, 3);
    s.extendedFabricCost = roundTo(s.garmentFabricCost * s.quantity, 2);

    totalOrderNetWeightKg = roundTo(totalOrderNetWeightKg + s.extendedNetWeightKg, 3);
    totalOrderConsumptionKg = roundTo(totalOrderConsumptionKg + s.extendedConsumptionKg, 3);
    totalOrderFabricCost = roundTo(totalOrderFabricCost + s.extendedFabricCost, 2);
  }

  // Warn if any fabric in Fabric Setup is unused by any enabled component
  for (const [serial, req] of fabricRequirementsMap.entries()) {
    if (req.assignedComponents.length === 0) {
      warnings.push({
        step: 2,
        field: `fabrics.serial_${serial}`,
        message: `Fabric #${serial} (${req.description}) is not assigned to any enabled component.`
      });
    }
  }

  const avgGarmentNetWeightGrams =
    totalOrderQuantity > 0
      ? roundTo((totalOrderNetWeightKg * 1000) / totalOrderQuantity, 2)
      : roundTo(
          SIZES.reduce((acc, sz) => acc + sizeSummaries[sz].garmentNetWeightGrams, 0) / SIZES.length,
          2
        );

  const avgGarmentConsumptionGrams =
    totalOrderQuantity > 0
      ? roundTo((totalOrderConsumptionKg * 1000) / totalOrderQuantity, 2)
      : roundTo(
          SIZES.reduce((acc, sz) => acc + sizeSummaries[sz].garmentConsumptionGrams, 0) / SIZES.length,
          2
        );

  const weightedAvgPieceFabricCost =
    totalOrderQuantity > 0
      ? roundTo(totalOrderFabricCost / totalOrderQuantity, 2)
      : roundTo(
          SIZES.reduce((acc, sz) => acc + sizeSummaries[sz].garmentFabricCost, 0) / SIZES.length,
          2
        );

  return {
    isComplete: errors.length === 0,
    canSaveDraft: Boolean(String(styleNumber).trim() && String(styleName).trim()),
    errors,
    warnings,
    summary: {
      styleNumber: String(styleNumber).trim(),
      styleName: String(styleName).trim(),
      garmentType,
      category,
      baseGsm: Number(baseGsm) || 0,
      wastageAllowancePct: Number(wastageAllowancePct) || 0,
      totalOrderQuantity,
      totalOrderNetWeightKg,
      totalOrderConsumptionKg,
      totalOrderFabricCost,
      avgGarmentNetWeightGrams,
      avgGarmentConsumptionGrams,
      weightedAvgPieceFabricCost,
      sizeSummaries,
      componentBreakdown,
      fabricRequirements: Array.from(fabricRequirementsMap.values())
    }
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    SIZES,
    GARMENT_TYPES,
    GARMENT_CATEGORIES,
    DEFAULT_STANDARD_COMPONENTS,
    roundTo,
    gramsToKilograms,
    kilogramsToGrams,
    calculateComponentForSize,
    evaluateCostingSheet
  };
}
