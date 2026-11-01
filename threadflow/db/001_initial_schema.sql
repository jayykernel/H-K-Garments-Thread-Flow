-- ============================================================================
-- H&K CLOTHING — THREADFLOW
-- PostgreSQL Production Database Schema & Migrations (001_initial_schema.sql)
-- ============================================================================

BEGIN;

-- 1. Roles & Users (Authentication & RBAC)
CREATE TYPE user_role AS ENUM ('admin', 'merchandiser', 'costing_engineer', 'production_lead', 'viewer');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role user_role NOT NULL DEFAULT 'merchandiser',
    department VARCHAR(100) NOT NULL DEFAULT 'Merchandising & Costing',
    avatar_initials VARCHAR(4) NOT NULL,
    theme_preference VARCHAR(16) NOT NULL DEFAULT 'light',
    notify_due_soon BOOLEAN NOT NULL DEFAULT TRUE,
    notify_status_change BOOLEAN NOT NULL DEFAULT TRUE,
    notify_costing_approval BOOLEAN NOT NULL DEFAULT TRUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Costing Records (Master Garment Technical Costing)
CREATE TYPE garment_type AS ENUM ('Top', 'Bottom');
CREATE TYPE garment_category AS ENUM ('Men''s', 'Ladies', 'Other');
CREATE TYPE costing_status AS ENUM ('Draft', 'Finalized', 'Approved', 'Archived');

CREATE TABLE costing_records (
    id VARCHAR(32) PRIMARY KEY,
    style_number VARCHAR(64) NOT NULL,
    style_name VARCHAR(200) NOT NULL,
    primary_fabric VARCHAR(200) NOT NULL,
    base_gsm NUMERIC(8,2) NOT NULL CHECK (base_gsm > 0),
    garment_type garment_type NOT NULL,
    category garment_category NOT NULL,
    wastage_allowance_pct NUMERIC(5,2) NOT NULL DEFAULT 8.00 CHECK (wastage_allowance_pct >= 0 AND wastage_allowance_pct <= 50),
    status costing_status NOT NULL DEFAULT 'Draft',
    size_quantities JSONB NOT NULL, -- { S, M, L, XL, XXL, XXXL }
    calculated_summary JSONB NOT NULL, -- Persisted snapshot of calculation output
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_costing_style_number ON costing_records(style_number);
CREATE INDEX idx_costing_status ON costing_records(status);

-- 3. Costing Fabrics (Multi-Fabric Entries per Costing Sheet)
CREATE TABLE costing_fabrics (
    id VARCHAR(48) PRIMARY KEY,
    costing_id VARCHAR(32) NOT NULL REFERENCES costing_records(id) ON DELETE CASCADE,
    serial_no INTEGER NOT NULL,
    fabric_code VARCHAR(64) NOT NULL,
    description VARCHAR(255) NOT NULL,
    colour VARCHAR(100) NOT NULL,
    gsm NUMERIC(8,2) NOT NULL CHECK (gsm > 0),
    price_per_kg NUMERIC(10,2) NOT NULL CHECK (price_per_kg > 0),
    width_inches NUMERIC(6,2) DEFAULT 60.0,
    properties VARCHAR(255),
    UNIQUE (costing_id, serial_no)
);

-- 4. Costing Components & Size-Specific Measurements
CREATE TABLE costing_components (
    id VARCHAR(48) PRIMARY KEY,
    costing_id VARCHAR(32) NOT NULL REFERENCES costing_records(id) ON DELETE CASCADE,
    component_key VARCHAR(64) NOT NULL, -- main_body, sleeve, rib, bnt, yoke, or custom
    component_name VARCHAR(120) NOT NULL,
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_fabric_serial INTEGER NOT NULL,
    panel_multiplier NUMERIC(5,2) NOT NULL DEFAULT 2.0 CHECK (panel_multiplier > 0),
    seam_allowance_cm NUMERIC(5,2) NOT NULL DEFAULT 2.5 CHECK (seam_allowance_cm >= 0),
    measurements_by_size JSONB NOT NULL -- { S: { lengthCm, widthCm }, M: ... }
);

-- 5. Manufacturing Orders (Lifecycle & Traceability)
CREATE TYPE order_status AS ENUM ('Currently Going On', 'Completed', 'Cancelled');

CREATE TABLE orders (
    id VARCHAR(32) PRIMARY KEY,
    order_number VARCHAR(64) UNIQUE NOT NULL,
    customer_name VARCHAR(180) NOT NULL,
    buyer_po_ref VARCHAR(100) NOT NULL,
    style_number VARCHAR(64) NOT NULL,
    style_name VARCHAR(200) NOT NULL,
    garment_type garment_type NOT NULL,
    category garment_category NOT NULL,
    costing_id VARCHAR(32) REFERENCES costing_records(id) ON DELETE SET NULL,
    status order_status NOT NULL DEFAULT 'Currently Going On',
    current_stage VARCHAR(100) NOT NULL DEFAULT 'Fabric Sourcing',
    size_quantities JSONB NOT NULL,
    total_pieces INTEGER NOT NULL CHECK (total_pieces >= 0),
    completed_pieces INTEGER NOT NULL DEFAULT 0 CHECK (completed_pieces >= 0),
    order_date DATE NOT NULL,
    due_date DATE NOT NULL,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    remarks TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_due_date ON orders(due_date);
CREATE INDEX idx_orders_style_number ON orders(style_number);

-- 6. Workflow Tasks (Status Follow-Up System)
CREATE TYPE task_status AS ENUM ('Pending', 'In Progress', 'Completed');
CREATE TYPE task_priority AS ENUM ('Standard', 'High', 'Critical');

CREATE TABLE workflow_tasks (
    id VARCHAR(32) PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    stage_category VARCHAR(80) NOT NULL,
    assigned_user_id UUID REFERENCES users(id),
    assigned_user_name VARCHAR(150) NOT NULL,
    priority task_priority NOT NULL DEFAULT 'Standard',
    due_date DATE NOT NULL,
    follow_up_date DATE NOT NULL,
    remarks TEXT,
    status task_status NOT NULL DEFAULT 'Pending',
    counts_toward_completion BOOLEAN NOT NULL DEFAULT TRUE,
    completed_at TIMESTAMPTZ,
    completed_by VARCHAR(150),
    reopened_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_order_id ON workflow_tasks(order_id);
CREATE INDEX idx_tasks_status ON workflow_tasks(status);
CREATE INDEX idx_tasks_follow_up_date ON workflow_tasks(follow_up_date);

-- 7. Immutable Audit & Status-Change History Log
CREATE TABLE audit_logs (
    id VARCHAR(48) PRIMARY KEY,
    entity_type VARCHAR(32) NOT NULL, -- 'order', 'task', 'costing', 'auth'
    entity_id VARCHAR(48) NOT NULL,
    order_id VARCHAR(32),
    action VARCHAR(80) NOT NULL,
    previous_status VARCHAR(64),
    new_status VARCHAR(64),
    actor_name VARCHAR(150) NOT NULL,
    actor_role VARCHAR(64) NOT NULL,
    remarks TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_order_id ON audit_logs(order_id);

COMMIT;
