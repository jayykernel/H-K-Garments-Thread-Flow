/**
 * ============================================================================
 * H&K CLOTHING — THREADFLOW
 * Workflow, Order Lifecycle, Audit Trail & Authorization Engine (workflowEngine.js)
 * ============================================================================
 *
 * DOMAIN RULES:
 * 1. Task Workflow States: 'Pending' -> 'In Progress' -> 'Completed'
 *    - Completing a task validates permissions, sets `completedAt` ISO timestamp,
 *      records `completedBy`, updates status to 'Completed', and appends an
 *      immutable entry to `auditLogs` and the task's `history` array.
 *    - Reopening a completed task is explicitly supported: it requires a reason/remark,
 *      preserves previous completion timestamps in `history` and `previousCompletions`,
 *      increments `reopenedCount`, transitions status to 'In Progress' or 'Pending',
 *      and appends an audit trail entry.
 * 2. Order Workflow Progress Calculation:
 *    - Every task has `countsTowardCompletion: boolean` (default true for production
 *      milestones; optional advisory notes can be false).
 *    - Order workflow progress (%) = round((completedMilestoneTasks / totalMilestoneTasks) * 100).
 * 3. Order Lifecycle Transitions:
 *    - 'Currently Going On' <-> 'Completed' <-> 'Cancelled'
 *    - Completing or cancelling an order NEVER deletes tasks, costing links, or audit logs.
 *    - Cancelling an order requires a cancellation reason and preserves all history.
 * 4. Role-Based Access Control (RBAC):
 *    - 'admin': all permissions (costing, orders, tasks, users, settings, reset)
 *    - 'costing_engineer': create/edit/finalize costing, view orders & tasks, update tasks
 *    - 'merchandiser': create/edit costing, create/update orders, create/complete/reopen tasks
 *    - 'production_lead': update/complete/reopen tasks, update order stage & progress, view costing
 *    - 'viewer': read-only access across all modules; mutations are rejected server/engine-side
 */

const ROLE_PERMISSIONS = {
  admin: [
    'costing:write',
    'costing:approve',
    'task:write',
    'task:complete',
    'task:reopen',
    'order:write',
    'order:transition',
    'user:manage',
    'settings:write'
  ],
  merchandiser: [
    'costing:write',
    'task:write',
    'task:complete',
    'task:reopen',
    'order:write',
    'order:transition',
    'settings:write'
  ],
  costing_engineer: [
    'costing:write',
    'costing:approve',
    'task:write',
    'task:complete',
    'settings:write'
  ],
  production_lead: [
    'task:write',
    'task:complete',
    'task:reopen',
    'order:write',
    'order:transition',
    'settings:write'
  ],
  viewer: ['settings:write']
};

function hasPermission(user, permission) {
  if (!user || !user.role) return false;
  const perms = ROLE_PERMISSIONS[user.role] || [];
  return perms.includes(permission);
}

function assertPermission(user, permission) {
  if (!user) {
    return { allowed: false, error: 'Authentication required. Please sign in.' };
  }
  if (!hasPermission(user, permission)) {
    return {
      allowed: false,
      error: `Access denied: Role "${user.role}" does not have "${permission}" permission.`
    };
  }
  return { allowed: true, error: null };
}

/**
 * Calculates order workflow completion percentage from actual persisted tasks.
 * Explicitly defines which tasks count toward completion (`countsTowardCompletion !== false`).
 */
function calculateOrderWorkflowProgress(orderId, tasks) {
  const orderTasks = (tasks || []).filter((t) => t.orderId === orderId);
  const milestoneTasks = orderTasks.filter((t) => t.countsTowardCompletion !== false);
  const totalCount = milestoneTasks.length;
  if (totalCount === 0) {
    return {
      orderId,
      totalTasks: orderTasks.length,
      milestoneTasks: 0,
      completedTasks: 0,
      inProgressTasks: 0,
      pendingTasks: 0,
      progressPct: 0
    };
  }
  const completedTasks = milestoneTasks.filter((t) => t.status === 'Completed').length;
  const inProgressTasks = milestoneTasks.filter((t) => t.status === 'In Progress').length;
  const pendingTasks = milestoneTasks.filter((t) => t.status === 'Pending').length;
  const progressPct = Math.round((completedTasks / totalCount) * 100);

  return {
    orderId,
    totalTasks: orderTasks.length,
    milestoneTasks: totalCount,
    completedTasks,
    inProgressTasks,
    pendingTasks,
    progressPct
  };
}

/**
 * Marks a task as Completed with validation, timestamp, and audit history.
 */
function completeWorkflowTask({ task, actor, remarks = '', timestamp = new Date().toISOString() }) {
  const auth = assertPermission(actor, 'task:complete');
  if (!auth.allowed) {
    return { ok: false, error: auth.error };
  }
  if (!task || !task.id) {
    return { ok: false, error: 'Valid task record is required.' };
  }
  if (task.status === 'Completed') {
    return { ok: false, error: `Task "${task.title}" is already marked Completed.` };
  }

  const prevStatus = task.status;
  const cleanRemarks = String(remarks || task.remarks || '').trim();
  const auditEntry = {
    id: `AUD-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    entityType: 'task',
    entityId: task.id,
    orderId: task.orderId,
    action: 'TASK_COMPLETED',
    previousStatus: prevStatus,
    newStatus: 'Completed',
    actorName: actor.fullName || actor.name || actor.email,
    actorRole: actor.role,
    remarks: cleanRemarks || 'Task verified and marked completed.',
    createdAt: timestamp
  };

  const updatedTask = {
    ...task,
    status: 'Completed',
    remarks: cleanRemarks || task.remarks,
    completedAt: timestamp,
    completedBy: actor.fullName || actor.name || actor.email,
    updatedAt: timestamp,
    history: [
      ...(Array.isArray(task.history) ? task.history : []),
      {
        action: 'Completed',
        fromStatus: prevStatus,
        toStatus: 'Completed',
        actor: actor.fullName || actor.name || actor.email,
        role: actor.role,
        remarks: auditEntry.remarks,
        timestamp
      }
    ]
  };

  return {
    ok: true,
    task: updatedTask,
    auditEntry
  };
}

/**
 * Reopens a Completed task without erasing its previous completion history.
 */
function reopenWorkflowTask({
  task,
  actor,
  targetStatus = 'In Progress',
  reason = '',
  timestamp = new Date().toISOString()
}) {
  const auth = assertPermission(actor, 'task:reopen');
  if (!auth.allowed) {
    return { ok: false, error: auth.error };
  }
  if (!task || !task.id) {
    return { ok: false, error: 'Valid task record is required.' };
  }
  if (task.status !== 'Completed') {
    return { ok: false, error: 'Only a Completed task can be reopened.' };
  }
  if (!['Pending', 'In Progress'].includes(targetStatus)) {
    return { ok: false, error: 'Target status on reopen must be Pending or In Progress.' };
  }
  const cleanReason = String(reason || '').trim();
  if (!cleanReason) {
    return { ok: false, error: 'A remark or reason is required when reopening a completed task.' };
  }

  const previousCompletionRecord = {
    completedAt: task.completedAt,
    completedBy: task.completedBy,
    reopenedAt: timestamp,
    reopenedBy: actor.fullName || actor.name || actor.email,
    reopenReason: cleanReason
  };

  const auditEntry = {
    id: `AUD-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    entityType: 'task',
    entityId: task.id,
    orderId: task.orderId,
    action: 'TASK_REOPENED',
    previousStatus: 'Completed',
    newStatus: targetStatus,
    actorName: actor.fullName || actor.name || actor.email,
    actorRole: actor.role,
    remarks: cleanReason,
    createdAt: timestamp
  };

  const updatedTask = {
    ...task,
    status: targetStatus,
    remarks: cleanReason,
    completedAt: null,
    completedBy: null,
    reopenedCount: (Number(task.reopenedCount) || 0) + 1,
    previousCompletions: [
      ...(Array.isArray(task.previousCompletions) ? task.previousCompletions : []),
      previousCompletionRecord
    ],
    updatedAt: timestamp,
    history: [
      ...(Array.isArray(task.history) ? task.history : []),
      {
        action: 'Reopened',
        fromStatus: 'Completed',
        toStatus: targetStatus,
        actor: actor.fullName || actor.name || actor.email,
        role: actor.role,
        remarks: cleanReason,
        previousCompletedAt: task.completedAt,
        timestamp
      }
    ]
  };

  return {
    ok: true,
    task: updatedTask,
    auditEntry
  };
}

/**
 * Transitions an Order status ('Currently Going On', 'Completed', 'Cancelled')
 * while preserving all historical data, linked costing, and audit trail.
 */
function transitionOrderStatus({
  order,
  actor,
  newStatus,
  remarks = '',
  timestamp = new Date().toISOString()
}) {
  const auth = assertPermission(actor, 'order:transition');
  if (!auth.allowed) {
    return { ok: false, error: auth.error };
  }
  if (!order || !order.id) {
    return { ok: false, error: 'Valid order record is required.' };
  }
  const validStatuses = ['Currently Going On', 'Completed', 'Cancelled'];
  if (!validStatuses.includes(newStatus)) {
    return { ok: false, error: `Invalid order status "${newStatus}".` };
  }
  if (order.status === newStatus) {
    return { ok: false, error: `Order ${order.orderNumber} is already in "${newStatus}" status.` };
  }

  const cleanRemarks = String(remarks || '').trim();
  if (newStatus === 'Cancelled' && !cleanRemarks) {
    return { ok: false, error: 'A cancellation reason/remark is required to cancel an order.' };
  }

  const prevStatus = order.status;
  const auditEntry = {
    id: `AUD-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    entityType: 'order',
    entityId: order.id,
    orderId: order.id,
    action: `ORDER_STATUS_${newStatus.toUpperCase().replace(/\s+/g, '_')}`,
    previousStatus: prevStatus,
    newStatus,
    actorName: actor.fullName || actor.name || actor.email,
    actorRole: actor.role,
    remarks: cleanRemarks || `Order transitioned from ${prevStatus} to ${newStatus}.`,
    createdAt: timestamp
  };

  const updatedOrder = {
    ...order,
    status: newStatus,
    completedAt: newStatus === 'Completed' ? timestamp : order.completedAt,
    cancelledAt: newStatus === 'Cancelled' ? timestamp : order.cancelledAt,
    cancellationReason: newStatus === 'Cancelled' ? cleanRemarks : order.cancellationReason,
    completedPieces: newStatus === 'Completed' ? order.totalPieces : order.completedPieces,
    currentStage:
      newStatus === 'Completed'
        ? 'Dispatched & Closed'
        : newStatus === 'Cancelled'
        ? 'Cancelled (Archived)'
        : order.currentStage === 'Dispatched & Closed' || order.currentStage === 'Cancelled (Archived)'
        ? 'Sewing & Assembly'
        : order.currentStage,
    remarks: cleanRemarks || order.remarks,
    updatedAt: timestamp,
    statusHistory: [
      ...(Array.isArray(order.statusHistory) ? order.statusHistory : []),
      {
        fromStatus: prevStatus,
        toStatus: newStatus,
        actor: actor.fullName || actor.name || actor.email,
        role: actor.role,
        remarks: auditEntry.remarks,
        timestamp
      }
    ]
  };

  return {
    ok: true,
    order: updatedOrder,
    auditEntry
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ROLE_PERMISSIONS,
    hasPermission,
    assertPermission,
    calculateOrderWorkflowProgress,
    completeWorkflowTask,
    reopenWorkflowTask,
    transitionOrderStatus
  };
}
