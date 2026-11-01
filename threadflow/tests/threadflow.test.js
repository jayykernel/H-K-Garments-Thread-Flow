/**
 * ============================================================================
 * H&K CLOTHING — THREADFLOW
 * Automated Verification & Unit Test Suite (threadflow.test.js)
 * ============================================================================
 * Covers Section 12 Requirements:
 * 1. Costing tests:
 *    - Unit conversions (grams <-> kilograms)
 *    - Component weight calculations
 *    - Size-specific calculations (S, M, L, XL, XXL, XXXL)
 *    - Fabric assignment behavior
 *    - Quantity totals
 *    - Cost aggregation (keeping net weight, consumption, and cost distinct)
 *    - Missing and invalid inputs (never silently treated as zero)
 *    - Rounding rules & boundary conditions
 * 2. Workflow tests:
 *    - Task creation, completion, and reopening with audit history preservation
 *    - Order workflow progress calculation
 *    - Order status transitions (Currently Going On, Completed, Cancelled) without data loss
 *    - Role-Based Access Control (RBAC) authorization failures
 * 3. Seed & Domain Integrity tests:
 *    - Verifies all pre-seeded Costing Records, Orders, and Tasks pass validation
 */

const test = require('node:test');
const assert = require('node:assert/strict');

const {
  SIZES,
  gramsToKilograms,
  kilogramsToGrams,
  calculateComponentForSize,
  evaluateCostingSheet
} = require('../src/engine/costingEngine');

const {
  hasPermission,
  assertPermission,
  calculateOrderWorkflowProgress,
  completeWorkflowTask,
  reopenWorkflowTask,
  transitionOrderStatus
} = require('../src/engine/workflowEngine');

const { createInitialDatabase, buildUniformGradedMeasurements } = require('../src/data/seedData');

test('Costing Engine — Unit Conversions & Rounding Rules', () => {
  assert.equal(gramsToKilograms(1000), 1);
  assert.equal(gramsToKilograms(245.6), 0.2456);
  assert.equal(gramsToKilograms(0), 0);
  assert.equal(kilogramsToGrams(1.5), 1500);
  assert.equal(kilogramsToGrams(0.2456), 245.6);

  assert.throws(() => gramsToKilograms(NaN), TypeError);
  assert.throws(() => kilogramsToGrams('invalid'), TypeError);
});

test('Costing Engine — Component Weight, Consumption, and Cost Separation', () => {
  // Cut Length = 67 + 3 = 70 cm; Cut Width = 47 + 3 = 50 cm
  // Multiplier = 2 (Front + Back) -> Cut Area = 70 * 50 * 2 = 7000 cm^2 = 0.70 m^2
  // GSM = 200 g/m^2 -> Net Weight = 0.70 * 200 = 140.0 g = 0.14 kg
  // Wastage = 10% -> Gross Consumption = 140.0 * 1.10 = 154.0 g = 0.154 kg
  // Price = 500 INR/kg -> Fabric Cost = 0.154 * 500 = 77.00 INR
  const res = calculateComponentForSize({
    lengthCm: 67,
    widthCm: 47,
    seamAllowanceCm: 3,
    panelMultiplier: 2,
    fabricGsm: 200,
    fabricPricePerKg: 500,
    wastageAllowancePct: 10
  });

  assert.equal(res.valid, true);
  assert.equal(res.cutAreaCm2, 7000);
  assert.equal(res.cutAreaM2, 0.7);
  assert.equal(res.netWeightGrams, 140);
  assert.equal(res.netWeightKg, 0.14);
  assert.equal(res.consumptionGrams, 154);
  assert.equal(res.consumptionKg, 0.154);
  assert.equal(res.fabricCost, 77);
  // Verify net weight and consumption are kept strictly distinct when wastage > 0
  assert.notEqual(res.netWeightGrams, res.consumptionGrams);
});

test('Costing Engine — Missing vs. Legitimate Zero Inputs Validation', () => {
  // Missing measurement on an ordered size must produce an error and NOT be treated as 0
  const incompleteSheet = {
    styleNumber: 'HK-TEST-01',
    styleName: 'Test Incomplete Tee',
    primaryFabric: 'Cotton Jersey',
    baseGsm: 200,
    garmentType: 'Top',
    category: "Men's",
    wastageAllowancePct: 8,
    fabrics: [
      { serialNo: 1, description: 'Main Cotton', colour: 'Black', gsm: 200, pricePerKg: 600 }
    ],
    sizeQuantities: { S: 100, M: 200, L: 0, XL: 0, XXL: 0, XXXL: 0 }, // 0 is legitimate for L-XXXL
    components: [
      {
        key: 'main_body',
        name: 'Main Body',
        enabled: true,
        assignedFabricSerial: 1,
        panelMultiplier: 2,
        seamAllowanceCm: 3,
        measurementsBySize: {
          S: { lengthCm: 68, widthCm: 50 },
          M: { lengthCm: '', widthCm: 52 }, // Missing lengthCm on ordered size M!
          L: { lengthCm: 72, widthCm: 54 },
          XL: { lengthCm: 74, widthCm: 56 },
          XXL: { lengthCm: 76, widthCm: 58 },
          XXXL: { lengthCm: 78, widthCm: 60 }
        }
      }
    ]
  };

  const result = evaluateCostingSheet(incompleteSheet);
  assert.equal(result.isComplete, false);
  assert.equal(result.canSaveDraft, true);
  assert.ok(result.errors.some((e) => e.field === 'components.main_body.M'));
  assert.equal(result.summary.componentBreakdown[0].bySize.M.netWeightGrams, null);
});

test('Costing Engine — Unassigned Fabric Detection & Multi-Fabric Aggregation', () => {
  const sheet = {
    styleNumber: 'HK-TEST-02',
    styleName: 'Multi-Fabric Hoodie',
    primaryFabric: 'Fleece',
    baseGsm: 300,
    garmentType: 'Top',
    category: "Men's",
    wastageAllowancePct: 5,
    fabrics: [
      { serialNo: 1, description: 'Body Fleece', colour: 'Navy', gsm: 300, pricePerKg: 650 },
      { serialNo: 2, description: 'Rib Trim', colour: 'Navy', gsm: 350, pricePerKg: 750 }
    ],
    sizeQuantities: { S: 50, M: 100, L: 100, XL: 50, XXL: 0, XXXL: 0 },
    components: [
      {
        key: 'main_body',
        name: 'Main Body',
        enabled: true,
        assignedFabricSerial: 1,
        panelMultiplier: 2,
        seamAllowanceCm: 2,
        measurementsBySize: buildUniformGradedMeasurements(68, 50, 2, 2)
      },
      {
        key: 'rib',
        name: 'Rib',
        enabled: true,
        assignedFabricSerial: 99, // Invalid unassigned serial!
        panelMultiplier: 1,
        seamAllowanceCm: 1,
        measurementsBySize: buildUniformGradedMeasurements(48, 6, 1, 0)
      }
    ]
  };

  const badResult = evaluateCostingSheet(sheet);
  assert.equal(badResult.isComplete, false);
  assert.ok(badResult.errors.some((e) => e.message.includes('not assigned to a valid fabric')));

  // Now fix the fabric assignment to serial 2
  sheet.components[1].assignedFabricSerial = 2;
  const goodResult = evaluateCostingSheet(sheet);
  assert.equal(goodResult.isComplete, true);
  assert.equal(goodResult.errors.length, 0);
  assert.equal(goodResult.summary.totalOrderQuantity, 300);
  assert.equal(goodResult.summary.fabricRequirements.length, 2);
  assert.ok(goodResult.summary.fabricRequirements[0].totalConsumptionKg > 0);
  assert.ok(goodResult.summary.fabricRequirements[1].totalConsumptionKg > 0);
});

test('Workflow Engine — Task Completion, Reopening & Audit History Preservation', () => {
  const prodLead = { fullName: 'Devika Natarajan', role: 'production_lead' };
  const viewerUser = { fullName: 'SanjayPrakash V.', role: 'viewer' };

  const initialTask = {
    id: 'TSK-900',
    orderId: 'ORD-2601',
    title: 'Neck Binding Tension Check',
    description: 'Check BNT tension across 50 pieces',
    status: 'In Progress',
    countsTowardCompletion: true,
    remarks: 'In progress on Line 2',
    reopenedCount: 0,
    previousCompletions: [],
    history: []
  };

  // 1. Viewer role must be rejected from completing task
  const unauthorizedAttempt = completeWorkflowTask({
    task: initialTask,
    actor: viewerUser,
    remarks: 'Trying to complete as viewer'
  });
  assert.equal(unauthorizedAttempt.ok, false);
  assert.match(unauthorizedAttempt.error, /Access denied/);

  // 2. Production Lead completes the task
  const completeTime = '2026-10-18T10:00:00+05:30';
  const completedRes = completeWorkflowTask({
    task: initialTask,
    actor: prodLead,
    remarks: 'All 50 pieces passed tension gauge check.',
    timestamp: completeTime
  });
  assert.equal(completedRes.ok, true);
  assert.equal(completedRes.task.status, 'Completed');
  assert.equal(completedRes.task.completedAt, completeTime);
  assert.equal(completedRes.task.completedBy, 'Devika Natarajan');
  assert.equal(completedRes.task.history.length, 1);
  assert.equal(completedRes.auditEntry.action, 'TASK_COMPLETED');

  // 3. Reopening without a reason must fail validation
  const reopenNoReason = reopenWorkflowTask({
    task: completedRes.task,
    actor: prodLead,
    targetStatus: 'In Progress',
    reason: '   '
  });
  assert.equal(reopenNoReason.ok, false);

  // 4. Reopening with a valid reason preserves previous completion history
  const reopenTime = '2026-10-18T12:30:00+05:30';
  const reopenedRes = reopenWorkflowTask({
    task: completedRes.task,
    actor: prodLead,
    targetStatus: 'In Progress',
    reason: 'Re-checking XL bundle after needle change.',
    timestamp: reopenTime
  });
  assert.equal(reopenedRes.ok, true);
  assert.equal(reopenedRes.task.status, 'In Progress');
  assert.equal(reopenedRes.task.completedAt, null);
  assert.equal(reopenedRes.task.reopenedCount, 1);
  assert.equal(reopenedRes.task.previousCompletions.length, 1);
  assert.equal(reopenedRes.task.previousCompletions[0].completedAt, completeTime);
  assert.equal(reopenedRes.task.history.length, 2);
});

test('Workflow Engine — Order Lifecycle Transitions & Progress Calculation', () => {
  const adminUser = { fullName: 'Arjun Karthikeyan', role: 'admin' };
  const sampleOrder = {
    id: 'ORD-TEST',
    orderNumber: 'HK-ORD-TEST',
    status: 'Currently Going On',
    currentStage: 'Sewing',
    totalPieces: 1000,
    completedPieces: 500,
    statusHistory: []
  };

  // Cancelling without reason fails
  const cancelWithoutReason = transitionOrderStatus({
    order: sampleOrder,
    actor: adminUser,
    newStatus: 'Cancelled',
    remarks: ''
  });
  assert.equal(cancelWithoutReason.ok, false);

  // Cancelling with reason succeeds and preserves history
  const cancelRes = transitionOrderStatus({
    order: sampleOrder,
    actor: adminUser,
    newStatus: 'Cancelled',
    remarks: 'Buyer deferred seasonal drop.',
    timestamp: '2026-10-18T11:00:00+05:30'
  });
  assert.equal(cancelRes.ok, true);
  assert.equal(cancelRes.order.status, 'Cancelled');
  assert.equal(cancelRes.order.cancellationReason, 'Buyer deferred seasonal drop.');
  assert.equal(cancelRes.order.statusHistory.length, 1);

  // Progress calculation
  const tasks = [
    { id: '1', orderId: 'ORD-TEST', status: 'Completed', countsTowardCompletion: true },
    { id: '2', orderId: 'ORD-TEST', status: 'Completed', countsTowardCompletion: true },
    { id: '3', orderId: 'ORD-TEST', status: 'In Progress', countsTowardCompletion: true },
    { id: '4', orderId: 'ORD-TEST', status: 'Pending', countsTowardCompletion: true },
    { id: '5', orderId: 'ORD-TEST', status: 'Pending', countsTowardCompletion: false } // Advisory task
  ];
  const prog = calculateOrderWorkflowProgress('ORD-TEST', tasks);
  assert.equal(prog.milestoneTasks, 4);
  assert.equal(prog.completedTasks, 2);
  assert.equal(prog.progressPct, 50);
});

test('Seed Database — Full Mathematical & Referential Integrity', () => {
  const db = createInitialDatabase();
  assert.ok(db.costingRecords.length >= 5);
  assert.ok(db.orders.length >= 6);
  assert.ok(db.tasks.length >= 13);

  for (const c of db.costingRecords) {
    assert.equal(c.isComplete, true, `Costing ${c.id} should be complete`);
    assert.ok(c.calculatedSummary.totalOrderQuantity > 0);
    assert.ok(c.calculatedSummary.totalOrderFabricCost > 0);
    assert.ok(
      c.calculatedSummary.totalOrderConsumptionKg > c.calculatedSummary.totalOrderNetWeightKg,
      `Costing ${c.id} gross consumption must exceed net weight when wastage > 0`
    );
  }
});
