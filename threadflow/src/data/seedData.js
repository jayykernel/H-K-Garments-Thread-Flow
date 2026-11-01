/**
 * ============================================================================
 * H&K CLOTHING — THREADFLOW
 * Persisted Seed Database (seedData.js)
 * ============================================================================
 * Pre-computed using `evaluateCostingSheet` so that every dashboard metric,
 * costing record, order quantity, fabric requirement, and task timeline is
 * 100% mathematically consistent and derived from persisted records.
 */

const { evaluateCostingSheet } = require('../engine/costingEngine');

function buildUniformGradedMeasurements(baseLenS, baseWidS, lenStep = 2.0, widStep = 2.0) {
  const sizes = ['S', 'M', 'L', 'XL', 'XXL', 'XXXL'];
  const out = {};
  sizes.forEach((sz, idx) => {
    out[sz] = {
      lengthCm: Number((baseLenS + idx * lenStep).toFixed(1)),
      widthCm: Number((baseWidS + idx * widStep).toFixed(1))
    };
  });
  return out;
}

function createInitialDatabase() {
  const users = [
    {
      id: 'usr-admin',
      username: 'kamalakannan',
      email: '',
      fullName: 'kamalakannan',
      role: 'admin',
      department: 'Administration',
      avatarInitials: 'KK',
      themePreference: 'light',
      notifyDueSoon: true,
      notifyStatusChange: true,
      notifyCostingApproval: true,
      active: true
    }
  ];

  const rawCostings = [
    {
      id: 'CST-2601',
      styleNumber: 'HK-2601-INT',
      styleName: 'Architectural Heavy Interlock Crewneck',
      primaryFabric: '100% Organic Combed Compact Cotton Interlock',
      baseGsm: 240,
      garmentType: 'Top',
      category: "Men's",
      wastageAllowancePct: 8.0,
      status: 'Approved',
      createdAt: '2026-09-28T09:15:00+05:30',
      updatedAt: '2026-10-02T14:20:00+05:30',
      createdBy: 'Meera Sundaram',
      notes: 'Bio-polished compact finish; double-needle coverstitch on shoulder and armhole. Shrinkage tolerance +/- 2.5%.',
      sizeQuantities: { S: 240, M: 520, L: 640, XL: 420, XXL: 180, XXXL: 80 },
      fabrics: [
        {
          serialNo: 1,
          fabricCode: 'FAB-INT-240',
          description: '40s/2 Combed Organic Cotton Interlock',
          colour: 'Warm Undyed Ecru',
          gsm: 240,
          pricePerKg: 640,
          widthInches: 62,
          properties: 'Bio-washed, Silicone Softener, Compacted'
        },
        {
          serialNo: 2,
          fabricCode: 'FAB-RIB-290',
          description: '1x1 Cotton Lycra Collar Rib (95/5)',
          colour: 'Warm Undyed Ecru (Matched Dye Lot)',
          gsm: 290,
          pricePerKg: 710,
          widthInches: 36,
          properties: 'High-recovery elastane, tubular knit'
        },
        {
          serialNo: 3,
          fabricCode: 'FAB-BNT-180',
          description: 'Single Jersey Herringbone Neck Binding',
          colour: 'Graphite Slate',
          gsm: 180,
          pricePerKg: 580,
          widthInches: 48,
          properties: 'Pre-slit 3.5cm binding tape'
        }
      ],
      components: [
        {
          key: 'main_body',
          name: 'Main Body',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 3.0,
          measurementsBySize: buildUniformGradedMeasurements(68, 51, 2.0, 2.5)
        },
        {
          key: 'sleeve',
          name: 'Sleeve',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 2.5,
          measurementsBySize: buildUniformGradedMeasurements(23, 21, 1.0, 1.2)
        },
        {
          key: 'rib',
          name: 'Rib',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 2,
          panelMultiplier: 1,
          seamAllowanceCm: 1.5,
          measurementsBySize: buildUniformGradedMeasurements(48, 6.5, 1.5, 0.0)
        },
        {
          key: 'bnt',
          name: 'BNT',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 3,
          panelMultiplier: 1,
          seamAllowanceCm: 1.0,
          measurementsBySize: buildUniformGradedMeasurements(44, 3.5, 1.5, 0.0)
        },
        {
          key: 'yoke',
          name: 'Yoke',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 1,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(43, 14, 1.8, 0.6)
        }
      ]
    },
    {
      id: 'CST-2602',
      styleNumber: 'HK-2604-TER',
      styleName: 'Loopback French Terry Raglan Hoodie',
      primaryFabric: '3-End Diagonal Loopback French Terry',
      baseGsm: 340,
      garmentType: 'Top',
      category: "Men's",
      wastageAllowancePct: 9.5,
      status: 'Approved',
      createdAt: '2026-10-01T11:00:00+05:30',
      updatedAt: '2026-10-05T16:45:00+05:30',
      createdBy: 'Meera Sundaram',
      notes: 'Double-layered hood with self-fabric lining and kangaroo pocket. Heavy 2x2 rib cuffs and waistband.',
      sizeQuantities: { S: 150, M: 380, L: 460, XL: 310, XXL: 140, XXXL: 60 },
      fabrics: [
        {
          serialNo: 1,
          fabricCode: 'FAB-FT-340',
          description: '3-End Unbrushed Diagonal Loopback Terry',
          colour: 'Deep Carbon Ink',
          gsm: 340,
          pricePerKg: 695,
          widthInches: 68,
          properties: 'Reactive dyed, enzyme washed'
        },
        {
          serialNo: 2,
          fabricCode: 'FAB-RIB-380',
          description: '2x2 Heavy Spandex Cuff & Hem Rib',
          colour: 'Deep Carbon Ink',
          gsm: 380,
          pricePerKg: 760,
          widthInches: 42,
          properties: '7% Elastane recovery rib'
        },
        {
          serialNo: 3,
          fabricCode: 'FAB-SJ-190',
          description: 'Combed Single Jersey Hood Lining & BNT',
          colour: 'Muted Silver Heather',
          gsm: 190,
          pricePerKg: 540,
          widthInches: 60,
          properties: 'Soft handfeel inner hood lining'
        }
      ],
      components: [
        {
          key: 'main_body',
          name: 'Main Body',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 3.0,
          measurementsBySize: buildUniformGradedMeasurements(70, 54, 2.0, 2.5)
        },
        {
          key: 'sleeve',
          name: 'Sleeve',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 2.5,
          measurementsBySize: buildUniformGradedMeasurements(74, 24, 1.5, 1.2)
        },
        {
          key: 'rib',
          name: 'Rib',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 2,
          panelMultiplier: 1,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(96, 14, 4.0, 0.0)
        },
        {
          key: 'bnt',
          name: 'BNT',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 3,
          panelMultiplier: 1,
          seamAllowanceCm: 1.0,
          measurementsBySize: buildUniformGradedMeasurements(28, 3.5, 1.0, 0.0)
        },
        {
          key: 'yoke',
          name: 'Yoke',
          isCustom: false,
          enabled: false,
          assignedFabricSerial: 1,
          panelMultiplier: 1,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(44, 12, 1.5, 0.5)
        },
        {
          key: 'custom_hood',
          name: 'Two-Piece Contoured Hood',
          isCustom: true,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 2.5,
          measurementsBySize: buildUniformGradedMeasurements(38, 28, 0.8, 0.6)
        },
        {
          key: 'custom_pocket',
          name: 'Kangaroo Front Pocket',
          isCustom: true,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 1,
          seamAllowanceCm: 2.5,
          measurementsBySize: buildUniformGradedMeasurements(24, 36, 0.8, 1.2)
        }
      ]
    },
    {
      id: 'CST-2603',
      styleNumber: 'HK-2609-JOG',
      styleName: 'Technical Articulated Tapered Jogger',
      primaryFabric: 'Double-Knit Scuba Ponte Interlock (Cotton/Modal/Elastane)',
      baseGsm: 310,
      garmentType: 'Bottom',
      category: "Men's",
      wastageAllowancePct: 8.5,
      status: 'Finalized',
      createdAt: '2026-10-06T10:30:00+05:30',
      updatedAt: '2026-10-10T17:15:00+05:30',
      createdBy: 'Meera Sundaram',
      notes: 'Articulated knee darts, concealed YKK zip pocket bags, ribbed ankle cuffs and elasticated waist yoke.',
      sizeQuantities: { S: 180, M: 410, L: 490, XL: 280, XXL: 110, XXXL: 0 },
      fabrics: [
        {
          serialNo: 1,
          fabricCode: 'FAB-PNT-310',
          description: 'Double-Knit Cotton Modal Ponte 310 GSM',
          colour: 'Mineral Olive',
          gsm: 310,
          pricePerKg: 740,
          widthInches: 64,
          properties: '4-way stretch, anti-pilling grade 4.5'
        },
        {
          serialNo: 2,
          fabricCode: 'FAB-RIB-330',
          description: '2x1 Waistband & Ankle Cuff Rib',
          colour: 'Mineral Olive',
          gsm: 330,
          pricePerKg: 720,
          widthInches: 38,
          properties: 'High compression ankle cuff rib'
        },
        {
          serialNo: 3,
          fabricCode: 'FAB-PKT-160',
          description: 'Combed Cotton Poplin Pocket Bag',
          colour: 'Charcoal Black',
          gsm: 160,
          pricePerKg: 510,
          widthInches: 58,
          properties: 'High tensile woven pocketing'
        }
      ],
      components: [
        {
          key: 'main_body',
          name: 'Main Body',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 3.0,
          measurementsBySize: buildUniformGradedMeasurements(96, 56, 2.0, 2.5)
        },
        {
          key: 'sleeve',
          name: 'Sleeve',
          isCustom: false,
          enabled: false,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 2.5,
          measurementsBySize: buildUniformGradedMeasurements(20, 18, 1.0, 1.0)
        },
        {
          key: 'rib',
          name: 'Rib',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 2,
          panelMultiplier: 1,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(76, 16, 3.5, 0.0)
        },
        {
          key: 'bnt',
          name: 'BNT',
          isCustom: false,
          enabled: false,
          assignedFabricSerial: 1,
          panelMultiplier: 1,
          seamAllowanceCm: 1.0,
          measurementsBySize: buildUniformGradedMeasurements(36, 3, 1.5, 0.0)
        },
        {
          key: 'yoke',
          name: 'Yoke',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 1,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(78, 9, 3.5, 0.4)
        },
        {
          key: 'custom_pocket_bag',
          name: 'Side Zip Pocket Bags (Pair)',
          isCustom: true,
          enabled: true,
          assignedFabricSerial: 3,
          panelMultiplier: 2,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(32, 19, 0.5, 0.5)
        }
      ]
    },
    {
      id: 'CST-2604',
      styleNumber: 'HK-2612-WDR',
      styleName: 'Fine Gauge Modal Rib Lounge Top',
      primaryFabric: 'Micro-Modal Elastane 2x2 Fine Rib',
      baseGsm: 215,
      garmentType: 'Top',
      category: 'Ladies',
      wastageAllowancePct: 7.5,
      status: 'Approved',
      createdAt: '2026-10-08T14:00:00+05:30',
      updatedAt: '2026-10-12T11:30:00+05:30',
      createdBy: 'Meera Sundaram',
      notes: 'Lettuce-edge micro-overlock hem and cuff detail; Lenzing certified Modal yarn.',
      sizeQuantities: { S: 320, M: 580, L: 490, XL: 260, XXL: 90, XXXL: 0 },
      fabrics: [
        {
          serialNo: 1,
          fabricCode: 'FAB-MOD-215',
          description: '92% Lenzing Micro-Modal 8% Elastane 2x2 Rib',
          colour: 'Warm Sandstone',
          gsm: 215,
          pricePerKg: 890,
          widthInches: 56,
          properties: 'Silky drape, breathable stretch knit'
        },
        {
          serialNo: 2,
          fabricCode: 'FAB-BNT-MOD',
          description: 'Self-Modal Bias Neck Binding Tape',
          colour: 'Warm Sandstone',
          gsm: 215,
          pricePerKg: 910,
          widthInches: 56,
          properties: 'Bias cut 3.0cm binding'
        }
      ],
      components: [
        {
          key: 'main_body',
          name: 'Main Body',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 2.5,
          measurementsBySize: buildUniformGradedMeasurements(58, 42, 1.8, 2.2)
        },
        {
          key: 'sleeve',
          name: 'Sleeve',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(59, 16, 1.2, 1.0)
        },
        {
          key: 'rib',
          name: 'Rib',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 2,
          panelMultiplier: 1,
          seamAllowanceCm: 1.5,
          measurementsBySize: buildUniformGradedMeasurements(46, 4.5, 1.5, 0.0)
        },
        {
          key: 'bnt',
          name: 'BNT',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 2,
          panelMultiplier: 1,
          seamAllowanceCm: 1.0,
          measurementsBySize: buildUniformGradedMeasurements(38, 3.0, 1.2, 0.0)
        },
        {
          key: 'yoke',
          name: 'Yoke',
          isCustom: false,
          enabled: false,
          assignedFabricSerial: 1,
          panelMultiplier: 1,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(36, 10, 1.5, 0.5)
        }
      ]
    },
    {
      id: 'CST-2605',
      styleNumber: 'HK-2615-PKT',
      styleName: 'Mercerized Pique Structured Polo',
      primaryFabric: 'Double Mercerized Giza Cotton Honeycomb Pique',
      baseGsm: 225,
      garmentType: 'Top',
      category: "Men's",
      wastageAllowancePct: 8.5,
      status: 'Approved',
      createdAt: '2026-09-10T09:00:00+05:30',
      updatedAt: '2026-09-14T18:00:00+05:30',
      createdBy: 'Meera Sundaram',
      notes: 'Flat-knit jacquard collar and cuff rib; fused box placket with mother-of-pearl buttons.',
      sizeQuantities: { S: 200, M: 450, L: 550, XL: 350, XXL: 150, XXXL: 50 },
      fabrics: [
        {
          serialNo: 1,
          fabricCode: 'FAB-PIQ-225',
          description: '60s/2 Double Mercerized Giza Cotton Pique',
          colour: 'Deep Navy Ink',
          gsm: 225,
          pricePerKg: 980,
          widthInches: 62,
          properties: 'Silky lustre, zero torque honeycomb pique'
        },
        {
          serialNo: 2,
          fabricCode: 'FAB-COL-310',
          description: 'Flat-Knit Collar & Cuff Trim Rib',
          colour: 'Deep Navy Ink with Ecru Tipping',
          gsm: 310,
          pricePerKg: 1050,
          widthInches: 40,
          properties: 'Anti-curl flat knit collar trim'
        },
        {
          serialNo: 3,
          fabricCode: 'FAB-TWL-190',
          description: 'Herringbone Twill Placket & Neck Tape',
          colour: 'Warm Porcelain',
          gsm: 190,
          pricePerKg: 620,
          widthInches: 50,
          properties: 'Woven reinforcement tape'
        }
      ],
      components: [
        {
          key: 'main_body',
          name: 'Main Body',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 3.0,
          measurementsBySize: buildUniformGradedMeasurements(70, 50, 2.0, 2.5)
        },
        {
          key: 'sleeve',
          name: 'Sleeve',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 2.5,
          measurementsBySize: buildUniformGradedMeasurements(22, 20, 1.0, 1.1)
        },
        {
          key: 'rib',
          name: 'Rib',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 2,
          panelMultiplier: 1,
          seamAllowanceCm: 1.5,
          measurementsBySize: buildUniformGradedMeasurements(78, 8.5, 2.0, 0.0)
        },
        {
          key: 'bnt',
          name: 'BNT',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 3,
          panelMultiplier: 1,
          seamAllowanceCm: 1.0,
          measurementsBySize: buildUniformGradedMeasurements(45, 4.0, 1.5, 0.0)
        },
        {
          key: 'yoke',
          name: 'Yoke',
          isCustom: false,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 1,
          seamAllowanceCm: 2.0,
          measurementsBySize: buildUniformGradedMeasurements(44, 11, 1.8, 0.5)
        },
        {
          key: 'custom_placket',
          name: 'Fused 3-Button Box Placket',
          isCustom: true,
          enabled: true,
          assignedFabricSerial: 1,
          panelMultiplier: 2,
          seamAllowanceCm: 1.5,
          measurementsBySize: buildUniformGradedMeasurements(17, 4.5, 0.5, 0.0)
        }
      ]
    }
  ];

  const costingRecords = rawCostings.map((rc) => {
    const evaluation = evaluateCostingSheet(rc);
    return {
      ...rc,
      calculatedSummary: evaluation.summary,
      isComplete: evaluation.isComplete
    };
  });

  const orders = [
    {
      id: 'ORD-2601',
      orderNumber: 'HK-ORD-2026-104',
      customerName: 'Atelier Nord Stockholm',
      buyerPoRef: 'PO-AN-88412',
      styleNumber: 'HK-2601-INT',
      styleName: 'Architectural Heavy Interlock Crewneck',
      garmentType: 'Top',
      category: "Men's",
      costingId: 'CST-2601',
      status: 'Currently Going On',
      currentStage: 'Sewing & Assembly',
      sizeQuantities: { S: 240, M: 520, L: 640, XL: 420, XXL: 180, XXXL: 80 },
      totalPieces: 2080,
      completedPieces: 1420,
      orderDate: '2026-09-29',
      dueDate: '2026-10-22',
      completedAt: null,
      cancelledAt: null,
      cancellationReason: null,
      remarks: 'Priority Nordic AW26 delivery. Inline AQL 1.5 inspection passed on Batch 1.',
      createdBy: 'Vikram Rajan',
      statusHistory: [
        {
          fromStatus: 'New',
          toStatus: 'Currently Going On',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Production order released against approved costing CST-2601.',
          timestamp: '2026-09-29T10:00:00+05:30'
        }
      ]
    },
    {
      id: 'ORD-2602',
      orderNumber: 'HK-ORD-2026-108',
      customerName: 'Kurogane Tokyo Apparel',
      buyerPoRef: 'PO-KT-5029',
      styleNumber: 'HK-2604-TER',
      styleName: 'Loopback French Terry Raglan Hoodie',
      garmentType: 'Top',
      category: "Men's",
      costingId: 'CST-2602',
      status: 'Currently Going On',
      currentStage: 'Cutting & Bundling',
      sizeQuantities: { S: 150, M: 380, L: 460, XL: 310, XXL: 140, XXXL: 60 },
      totalPieces: 1500,
      completedPieces: 610,
      orderDate: '2026-10-03',
      dueDate: '2026-10-21',
      completedAt: null,
      cancelledAt: null,
      cancellationReason: null,
      remarks: 'Japanese shade-band approval received. Rib lot #44B matched within Delta-E 0.6.',
      createdBy: 'Vikram Rajan',
      statusHistory: [
        {
          fromStatus: 'New',
          toStatus: 'Currently Going On',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Order initiated after 340 GSM French Terry bulk fabric relaxation test.',
          timestamp: '2026-10-03T11:30:00+05:30'
        }
      ]
    },
    {
      id: 'ORD-2603',
      orderNumber: 'HK-ORD-2026-112',
      customerName: 'Mercer & Loom London',
      buyerPoRef: 'PO-ML-31904',
      styleNumber: 'HK-2609-JOG',
      styleName: 'Technical Articulated Tapered Jogger',
      garmentType: 'Bottom',
      category: "Men's",
      costingId: 'CST-2603',
      status: 'Currently Going On',
      currentStage: 'Fabric Knitting & Compacting',
      sizeQuantities: { S: 180, M: 410, L: 490, XL: 280, XXL: 110, XXXL: 0 },
      totalPieces: 1470,
      completedPieces: 280,
      orderDate: '2026-10-07',
      dueDate: '2026-11-04',
      completedAt: null,
      cancelledAt: null,
      cancellationReason: null,
      remarks: 'YKK concealed matte coil zippers arrived in Tiruppur bonded warehouse.',
      createdBy: 'Vikram Rajan',
      statusHistory: [
        {
          fromStatus: 'New',
          toStatus: 'Currently Going On',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Bulk Ponte knitting commenced at Mill Unit III.',
          timestamp: '2026-10-07T09:45:00+05:30'
        }
      ]
    },
    {
      id: 'ORD-2604',
      orderNumber: 'HK-ORD-2026-115',
      customerName: 'Maison Verve Paris',
      buyerPoRef: 'PO-MV-7741',
      styleNumber: 'HK-2612-WDR',
      styleName: 'Fine Gauge Modal Rib Lounge Top',
      garmentType: 'Top',
      category: 'Ladies',
      costingId: 'CST-2604',
      status: 'Currently Going On',
      currentStage: 'PP Sample & Trim Approval',
      sizeQuantities: { S: 320, M: 580, L: 490, XL: 260, XXL: 90, XXXL: 0 },
      totalPieces: 1740,
      completedPieces: 450,
      orderDate: '2026-10-09',
      dueDate: '2026-10-29',
      completedAt: null,
      cancelledAt: null,
      cancellationReason: null,
      remarks: 'Lenzing certification hangtags verified; lettuce-edge stitch tension calibrated.',
      createdBy: 'Vikram Rajan',
      statusHistory: [
        {
          fromStatus: 'New',
          toStatus: 'Currently Going On',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'PP sample approved by Paris technical team.',
          timestamp: '2026-10-09T15:10:00+05:30'
        }
      ]
    },
    {
      id: 'ORD-2605',
      orderNumber: 'HK-ORD-2026-091',
      customerName: 'Vanguard Heritage Zurich',
      buyerPoRef: 'PO-VH-2094',
      styleNumber: 'HK-2615-PKT',
      styleName: 'Mercerized Pique Structured Polo',
      garmentType: 'Top',
      category: "Men's",
      costingId: 'CST-2605',
      status: 'Completed',
      currentStage: 'Dispatched & Closed',
      sizeQuantities: { S: 200, M: 450, L: 550, XL: 350, XXL: 150, XXXL: 50 },
      totalPieces: 1750,
      completedPieces: 1750,
      orderDate: '2026-09-12',
      dueDate: '2026-10-12',
      completedAt: '2026-10-11T17:40:00+05:30',
      cancelledAt: null,
      cancellationReason: null,
      remarks: '100% shipment handed over to Tuticorin freight forwarder ahead of schedule. Final AQL passed with 0 critical defects.',
      createdBy: 'Vikram Rajan',
      statusHistory: [
        {
          fromStatus: 'New',
          toStatus: 'Currently Going On',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Order opened for Zurich autumn drop.',
          timestamp: '2026-09-12T09:30:00+05:30'
        },
        {
          fromStatus: 'Currently Going On',
          toStatus: 'Completed',
          actor: 'Arjun Karthikeyan',
          role: 'admin',
          remarks: 'Final packing list and Bureau Veritas AQL 1.5 inspection signed off; container sealed.',
          timestamp: '2026-10-11T17:40:00+05:30'
        }
      ]
    },
    {
      id: 'ORD-2606',
      orderNumber: 'HK-ORD-2026-087',
      customerName: 'Solstice Coast Melbourne',
      buyerPoRef: 'PO-SC-6102',
      styleNumber: 'HK-2601-INT',
      styleName: 'Architectural Heavy Interlock Crewneck',
      garmentType: 'Top',
      category: "Men's",
      costingId: 'CST-2601',
      status: 'Cancelled',
      currentStage: 'Cancelled (Archived)',
      sizeQuantities: { S: 100, M: 200, L: 250, XL: 150, XXL: 50, XXXL: 0 },
      totalPieces: 750,
      completedPieces: 0,
      orderDate: '2026-09-18',
      dueDate: '2026-10-25',
      completedAt: null,
      cancelledAt: '2026-09-26T12:15:00+05:30',
      cancellationReason: 'Buyer consolidated capsules into Q1 Resort delivery; greige yarn reallocated to HK-ORD-2026-104 with buyer credit memo.',
      remarks: 'Cancelled prior to bulk dyeing. Zero fabric loss incurred.',
      createdBy: 'Vikram Rajan',
      statusHistory: [
        {
          fromStatus: 'New',
          toStatus: 'Currently Going On',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Initial PO logged.',
          timestamp: '2026-09-18T11:00:00+05:30'
        },
        {
          fromStatus: 'Currently Going On',
          toStatus: 'Cancelled',
          actor: 'Arjun Karthikeyan',
          role: 'admin',
          remarks: 'Buyer consolidated capsules into Q1 Resort delivery; greige yarn reallocated to HK-ORD-2026-104 with buyer credit memo.',
          timestamp: '2026-09-26T12:15:00+05:30'
        }
      ]
    }
  ];

  const tasks = [
    // ORD-2601 Tasks
    {
      id: 'TSK-101',
      orderId: 'ORD-2601',
      title: 'Bulk Interlock Compaction & GSM Verification',
      description: 'Verify post-compaction GSM (target 240 +/- 5 GSM) and spirality (< 2%) across all 14 rolls of Warm Undyed Ecru.',
      stageCategory: 'Fabric Quality',
      assignedUserId: 'usr-hk-02',
      assignedUserName: 'Meera Sundaram',
      priority: 'High',
      dueDate: '2026-10-05',
      followUpDate: '2026-10-04',
      remarks: 'Tested 14 rolls; average GSM recorded at 241.4 GSM. Spirality 1.3%. Approved for cutting.',
      status: 'Completed',
      countsTowardCompletion: true,
      completedAt: '2026-10-05T11:20:00+05:30',
      completedBy: 'Meera Sundaram',
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Created',
          fromStatus: null,
          toStatus: 'Pending',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Initial lab testing task scheduled.',
          timestamp: '2026-09-29T10:15:00+05:30'
        },
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Meera Sundaram',
          role: 'costing_engineer',
          remarks: 'Tested 14 rolls; average GSM recorded at 241.4 GSM. Spirality 1.3%. Approved for cutting.',
          timestamp: '2026-10-05T11:20:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-102',
      orderId: 'ORD-2601',
      title: 'CAD Marker Nesting & CNC Lay Cutting (S–XXXL)',
      description: 'Execute 8-ply relaxed lay cutting for 2,080 pcs across S–XXXL and bundle with barcode tickets.',
      stageCategory: 'Cutting',
      assignedUserId: 'usr-hk-04',
      assignedUserName: 'Devika Natarajan',
      priority: 'High',
      dueDate: '2026-10-10',
      followUpDate: '2026-10-09',
      remarks: 'Marker efficiency achieved 86.4%, keeping actual wastage at 7.6% vs 8.0% costing allowance.',
      status: 'Completed',
      countsTowardCompletion: true,
      completedAt: '2026-10-10T16:05:00+05:30',
      completedBy: 'Devika Natarajan',
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Devika Natarajan',
          role: 'production_lead',
          remarks: 'Marker efficiency achieved 86.4%, keeping actual wastage at 7.6% vs 8.0% costing allowance.',
          timestamp: '2026-10-10T16:05:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-103',
      orderId: 'ORD-2601',
      title: 'Line 3 Coverstitch Assembly & Collar Rib Attachment',
      description: 'Complete shoulder tape reinforcement (BNT), 1x1 neck rib attachment, and double-needle coverstitch on 2,080 pieces.',
      stageCategory: 'Sewing & Assembly',
      assignedUserId: 'usr-hk-04',
      assignedUserName: 'Devika Natarajan',
      priority: 'Critical',
      dueDate: '2026-10-19',
      followUpDate: '2026-10-18',
      remarks: '1,420 / 2,080 pieces off the line. Remaining 660 pcs (XL–XXXL) scheduled for completion by tomorrow 16:00.',
      status: 'In Progress',
      countsTowardCompletion: true,
      completedAt: null,
      completedBy: null,
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Status Updated',
          fromStatus: 'Pending',
          toStatus: 'In Progress',
          actor: 'Devika Natarajan',
          role: 'production_lead',
          remarks: 'Line 3 feeding started; inline QC stationed at collar attachment.',
          timestamp: '2026-10-12T08:45:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-104',
      orderId: 'ORD-2601',
      title: 'Final AQL 1.5 Pre-Shipment Inspection & Carton Barcoding',
      description: 'Conduct metal detection, measurement audit across S–XXXL, steam finishing, and export carton packing for Stockholm.',
      stageCategory: 'Finishing & QA',
      assignedUserId: 'usr-hk-03',
      assignedUserName: 'Vikram Rajan',
      priority: 'High',
      dueDate: '2026-10-21',
      followUpDate: '2026-10-20',
      remarks: 'Inspector slot booked for Oct 21 morning; polybags and UCC-128 labels ready in finishing.',
      status: 'Pending',
      countsTowardCompletion: true,
      completedAt: null,
      completedBy: null,
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Created',
          fromStatus: null,
          toStatus: 'Pending',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Scheduled pre-shipment QA and packing milestone.',
          timestamp: '2026-09-29T10:20:00+05:30'
        }
      ]
    },

    // ORD-2602 Tasks
    {
      id: 'TSK-201',
      orderId: 'ORD-2602',
      title: '340 GSM Loopback Terry Shade Band & Shrinkage Sign-Off',
      description: 'Verify centre-to-selvedge shade consistency and 24-hour relaxation shrinkage on Deep Carbon Ink rolls.',
      stageCategory: 'Fabric Quality',
      assignedUserId: 'usr-hk-02',
      assignedUserName: 'Meera Sundaram',
      priority: 'High',
      dueDate: '2026-10-09',
      followUpDate: '2026-10-08',
      remarks: 'Delta-E < 0.6 across all dye lots. Approved.',
      status: 'Completed',
      countsTowardCompletion: true,
      completedAt: '2026-10-09T14:30:00+05:30',
      completedBy: 'Meera Sundaram',
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Meera Sundaram',
          role: 'costing_engineer',
          remarks: 'Delta-E < 0.6 across all dye lots. Approved.',
          timestamp: '2026-10-09T14:30:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-202',
      orderId: 'ORD-2602',
      title: 'Raglan Sleeve, Hood & Kangaroo Pocket Precision Cutting',
      description: 'Cut all 1,500 hoodie sets including 2-piece contoured hood and kangaroo pocket panels.',
      stageCategory: 'Cutting',
      assignedUserId: 'usr-hk-04',
      assignedUserName: 'Devika Natarajan',
      priority: 'Critical',
      dueDate: '2026-10-18',
      followUpDate: '2026-10-18',
      remarks: 'S, M, L bundles cut and fused; XL–XXXL lays currently on automatic cutter table #2.',
      status: 'In Progress',
      countsTowardCompletion: true,
      completedAt: null,
      completedBy: null,
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Status Updated',
          fromStatus: 'Pending',
          toStatus: 'In Progress',
          actor: 'Devika Natarajan',
          role: 'production_lead',
          remarks: 'Cutting started on Table #2.',
          timestamp: '2026-10-14T09:15:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-203',
      orderId: 'ORD-2602',
      title: 'Flatlock Raglan Seam & Eyelets Assembly',
      description: '6-thread flatlock assembly of raglan sleeves, kangaroo pocket bar-tacking, and matte black drawcord eyelet punching.',
      stageCategory: 'Sewing & Assembly',
      assignedUserId: 'usr-hk-04',
      assignedUserName: 'Devika Natarajan',
      priority: 'High',
      dueDate: '2026-10-20',
      followUpDate: '2026-10-19',
      remarks: 'Flatlock machines calibrated with 40/2 core-spun thread; first 610 pieces completed.',
      status: 'Pending',
      countsTowardCompletion: true,
      completedAt: null,
      completedBy: null,
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Created',
          fromStatus: null,
          toStatus: 'Pending',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Queued for Line 1 & Line 2 flatlock battery.',
          timestamp: '2026-10-03T12:00:00+05:30'
        }
      ]
    },

    // ORD-2603 Tasks
    {
      id: 'TSK-301',
      orderId: 'ORD-2603',
      title: 'Ponte Interlock Lab-Dip & Pilling Resistance Verification',
      description: 'Confirm Martindale pilling test (2,000 rubs >= Grade 4.5) on Mineral Olive 310 GSM Ponte.',
      stageCategory: 'Fabric Quality',
      assignedUserId: 'usr-hk-02',
      assignedUserName: 'Meera Sundaram',
      priority: 'Standard',
      dueDate: '2026-10-14',
      followUpDate: '2026-10-13',
      remarks: 'SITRA lab report confirmed Grade 4.5 pilling resistance and 96% elastic recovery.',
      status: 'Completed',
      countsTowardCompletion: true,
      completedAt: '2026-10-13T17:10:00+05:30',
      completedBy: 'Meera Sundaram',
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Meera Sundaram',
          role: 'costing_engineer',
          remarks: 'SITRA lab report confirmed Grade 4.5 pilling resistance and 96% elastic recovery.',
          timestamp: '2026-10-13T17:10:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-302',
      orderId: 'ORD-2603',
      title: 'Articulated Knee Panel & Concealed Zip Pocket Grading Check',
      description: 'Verify pocket bag placement template and knee dart alignment across sizes S–XXL prior to bulk cutting.',
      stageCategory: 'Technical Pattern',
      assignedUserId: 'usr-hk-03',
      assignedUserName: 'Vikram Rajan',
      priority: 'High',
      dueDate: '2026-10-20',
      followUpDate: '2026-10-19',
      remarks: 'Size set samples sewn for M and XL; awaiting buyer technical merchandiser video review.',
      status: 'In Progress',
      countsTowardCompletion: true,
      completedAt: null,
      completedBy: null,
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Status Updated',
          fromStatus: 'Pending',
          toStatus: 'In Progress',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Size set samples in sewing room.',
          timestamp: '2026-10-15T10:30:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-303',
      orderId: 'ORD-2603',
      title: 'Elastic Waist Yoke & Rib Ankle Cuff Assembly',
      description: 'Run 4-needle waistband elasticating machine and attach 330 GSM ankle rib cuffs for 1,470 joggers.',
      stageCategory: 'Sewing & Assembly',
      assignedUserId: 'usr-hk-04',
      assignedUserName: 'Devika Natarajan',
      priority: 'Standard',
      dueDate: '2026-10-28',
      followUpDate: '2026-10-25',
      remarks: 'Kansai Special waistband folders mounted and tested.',
      status: 'Pending',
      countsTowardCompletion: true,
      completedAt: null,
      completedBy: null,
      reopenedCount: 0,
      previousCompletions: [],
      history: []
    },

    // ORD-2604 Tasks
    {
      id: 'TSK-401',
      orderId: 'ORD-2604',
      title: 'Lenzing Micro-Modal Yarn Lot & Bias Binding Slitting',
      description: 'Verify Lenzing Ecovero/Modal transaction certificate and slit 3.0cm bias neck binding rolls.',
      stageCategory: 'Fabric Quality',
      assignedUserId: 'usr-hk-02',
      assignedUserName: 'Meera Sundaram',
      priority: 'Standard',
      dueDate: '2026-10-15',
      followUpDate: '2026-10-14',
      remarks: 'Certificate verified and logged; 42 kg of bias binding slit with zero fraying.',
      status: 'Completed',
      countsTowardCompletion: true,
      completedAt: '2026-10-15T12:00:00+05:30',
      completedBy: 'Meera Sundaram',
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Meera Sundaram',
          role: 'costing_engineer',
          remarks: 'Certificate verified and logged; 42 kg of bias binding slit with zero fraying.',
          timestamp: '2026-10-15T12:00:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-402',
      orderId: 'ORD-2604',
      title: 'Differential Feed Lettuce-Edge Hem Calibration & Sewing',
      description: 'Calibrate Pegasus 3-thread rolled hemmer differential ratio for consistent wave pitch on sleeves and bottom hem.',
      stageCategory: 'Sewing & Assembly',
      assignedUserId: 'usr-hk-04',
      assignedUserName: 'Devika Natarajan',
      priority: 'High',
      dueDate: '2026-10-23',
      followUpDate: '2026-10-19',
      remarks: '450 pieces completed on Line 4; stitch density locked at 16 SPI.',
      status: 'In Progress',
      countsTowardCompletion: true,
      completedAt: null,
      completedBy: null,
      reopenedCount: 1,
      previousCompletions: [
        {
          completedAt: '2026-10-16T15:00:00+05:30',
          completedBy: 'Devika Natarajan',
          reopenedAt: '2026-10-17T09:20:00+05:30',
          reopenedBy: 'Vikram Rajan',
          reopenReason: 'Reopened to include full bulk production tracking alongside initial calibration sign-off.'
        }
      ],
      history: [
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Devika Natarajan',
          role: 'production_lead',
          remarks: 'Initial machine calibration signed off.',
          timestamp: '2026-10-16T15:00:00+05:30'
        },
        {
          action: 'Reopened',
          fromStatus: 'Completed',
          toStatus: 'In Progress',
          actor: 'Vikram Rajan',
          role: 'merchandiser',
          remarks: 'Reopened to include full bulk production tracking alongside initial calibration sign-off.',
          previousCompletedAt: '2026-10-16T15:00:00+05:30',
          timestamp: '2026-10-17T09:20:00+05:30'
        }
      ]
    },

    // ORD-2605 Tasks (Completed Order)
    {
      id: 'TSK-501',
      orderId: 'ORD-2605',
      title: 'Double Mercerized Giza Pique & Flat-Knit Collar Inspection',
      description: 'Inspect 60s/2 Giza pique lustre and tipping alignment on flat-knit collar ribs.',
      stageCategory: 'Fabric Quality',
      assignedUserId: 'usr-hk-02',
      assignedUserName: 'Meera Sundaram',
      priority: 'High',
      dueDate: '2026-09-20',
      followUpDate: '2026-09-19',
      remarks: '100% collar ribs inspected over light box; tipping stripe tolerance within 0.5mm.',
      status: 'Completed',
      countsTowardCompletion: true,
      completedAt: '2026-09-20T13:15:00+05:30',
      completedBy: 'Meera Sundaram',
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Meera Sundaram',
          role: 'costing_engineer',
          remarks: '100% collar ribs inspected over light box; tipping stripe tolerance within 0.5mm.',
          timestamp: '2026-09-20T13:15:00+05:30'
        }
      ]
    },
    {
      id: 'TSK-502',
      orderId: 'ORD-2605',
      title: 'CNC Placket Slitting, Mother-of-Pearl Button Shank Wrapping & Final Pack',
      description: 'Complete fused 3-button box placket, thermo-wrapped button shanks, and export carton sealing for 1,750 polos.',
      stageCategory: 'Finishing & QA',
      assignedUserId: 'usr-hk-04',
      assignedUserName: 'Devika Natarajan',
      priority: 'High',
      dueDate: '2026-10-10',
      followUpDate: '2026-10-09',
      remarks: 'All 1,750 pcs packed in 70 master cartons; pull-test on buttons exceeded 90N.',
      status: 'Completed',
      countsTowardCompletion: true,
      completedAt: '2026-10-10T18:10:00+05:30',
      completedBy: 'Devika Natarajan',
      reopenedCount: 0,
      previousCompletions: [],
      history: [
        {
          action: 'Completed',
          fromStatus: 'In Progress',
          toStatus: 'Completed',
          actor: 'Devika Natarajan',
          role: 'production_lead',
          remarks: 'All 1,750 pcs packed in 70 master cartons; pull-test on buttons exceeded 90N.',
          timestamp: '2026-10-10T18:10:00+05:30'
        }
      ]
    }
  ];

  const auditLogs = [
    {
      id: 'AUD-2026-001',
      entityType: 'costing',
      entityId: 'CST-2601',
      orderId: 'ORD-2601',
      action: 'COSTING_APPROVED',
      previousStatus: 'Finalized',
      newStatus: 'Approved',
      actorName: 'Meera Sundaram',
      actorRole: 'costing_engineer',
      remarks: 'Approved HK-2601-INT costing at 2,080 pcs across S–XXXL.',
      createdAt: '2026-10-02T14:20:00+05:30'
    },
    {
      id: 'AUD-2026-002',
      entityType: 'task',
      entityId: 'TSK-102',
      orderId: 'ORD-2601',
      action: 'TASK_COMPLETED',
      previousStatus: 'In Progress',
      newStatus: 'Completed',
      actorName: 'Devika Natarajan',
      actorRole: 'production_lead',
      remarks: 'Marker efficiency achieved 86.4%, keeping actual wastage at 7.6% vs 8.0% costing allowance.',
      createdAt: '2026-10-10T16:05:00+05:30'
    },
    {
      id: 'AUD-2026-003',
      entityType: 'order',
      entityId: 'ORD-2605',
      orderId: 'ORD-2605',
      action: 'ORDER_STATUS_COMPLETED',
      previousStatus: 'Currently Going On',
      newStatus: 'Completed',
      actorName: 'Arjun Karthikeyan',
      actorRole: 'admin',
      remarks: 'Final packing list and Bureau Veritas AQL 1.5 inspection signed off; container sealed.',
      createdAt: '2026-10-11T17:40:00+05:30'
    },
    {
      id: 'AUD-2026-004',
      entityType: 'task',
      entityId: 'TSK-402',
      orderId: 'ORD-2604',
      action: 'TASK_REOPENED',
      previousStatus: 'Completed',
      newStatus: 'In Progress',
      actorName: 'Vikram Rajan',
      actorRole: 'merchandiser',
      remarks: 'Reopened to include full bulk production tracking alongside initial calibration sign-off.',
      createdAt: '2026-10-17T09:20:00+05:30'
    },
    {
      id: 'AUD-2026-005',
      entityType: 'order',
      entityId: 'ORD-2606',
      orderId: 'ORD-2606',
      action: 'ORDER_STATUS_CANCELLED',
      previousStatus: 'Currently Going On',
      newStatus: 'Cancelled',
      actorName: 'Arjun Karthikeyan',
      actorRole: 'admin',
      remarks: 'Buyer consolidated capsules into Q1 Resort delivery; greige yarn reallocated to HK-ORD-2026-104 with buyer credit memo.',
      createdAt: '2026-09-26T12:15:00+05:30'
    }
  ];

  return {
    version: '2.4.0',
    referenceDate: '2026-10-18',
    users,
    costingRecords,
    orders,
    tasks,
    auditLogs
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    buildUniformGradedMeasurements,
    createInitialDatabase
  };
}
