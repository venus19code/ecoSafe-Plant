-- ==========================================================
-- ECOSAFE PLANT - SCHEMA INICIAL (SPEC 001)
-- ==========================================================

CREATE DATABASE IF NOT EXISTS ecoSafe_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecoSafe_db;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'SUPERVISOR', 'OPERARIO') NOT NULL DEFAULT 'OPERARIO',
    area VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Registro de Auditoría
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity VARCHAR(50) NOT NULL,
    details TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================
-- GESTIÓN DE RESIDUOS (SPEC 002)
-- ==========================================================

-- Categorías de Residuos
CREATE TABLE IF NOT EXISTS waste_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    color_code VARCHAR(7) NOT NULL DEFAULT '#2d6a4f',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tipos específicos de Residuos
CREATE TABLE IF NOT EXISTS waste_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    default_unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    is_hazardous BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (category_id) REFERENCES waste_categories(id) ON DELETE CASCADE,
    INDEX idx_waste_type_cat (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registros periódicos de generación de residuos
CREATE TABLE IF NOT EXISTS waste_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    waste_type_id INT NOT NULL,
    recorded_by_user_id INT NOT NULL,
    record_date DATE NOT NULL,
    quantity DECIMAL(12, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    area VARCHAR(100) NOT NULL,
    disposal_method VARCHAR(100) NOT NULL,
    disposal_certificate_url VARCHAR(255) NULL,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (waste_type_id) REFERENCES waste_types(id),
    FOREIGN KEY (recorded_by_user_id) REFERENCES users(id),
    INDEX idx_waste_rec_date (record_date),
    INDEX idx_waste_rec_type (waste_type_id),
    INDEX idx_waste_rec_user (recorded_by_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================
-- CONSUMO DE RECURSOS: AGUA Y ENERGÍA (SPEC 003)
-- ==========================================================

-- Puntos de medición / Medidores
CREATE TABLE IF NOT EXISTS utility_meters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_type ENUM('AGUA', 'ENERGIA') NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    location_area VARCHAR(100) NOT NULL,
    multiplier DECIMAL(6, 2) NOT NULL DEFAULT 1.00,
    unit VARCHAR(20) NOT NULL DEFAULT 'm3',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_meter_type (resource_type),
    INDEX idx_meter_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Lecturas periódicas de medidores
CREATE TABLE IF NOT EXISTS utility_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meter_id INT NOT NULL,
    recorded_by_user_id INT NOT NULL,
    reading_date DATE NOT NULL,
    reading_value DECIMAL(12, 2) NOT NULL,
    consumption DECIMAL(12, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    cost_amount DECIMAL(12, 2) NULL,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meter_id) REFERENCES utility_meters(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by_user_id) REFERENCES users(id),
    INDEX idx_reading_meter (meter_id),
    INDEX idx_reading_date (reading_date),
    INDEX idx_reading_user (recorded_by_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Metas ambientales de consumo por mes y año
CREATE TABLE IF NOT EXISTS utility_targets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_type ENUM('AGUA', 'ENERGIA') NOT NULL,
    target_year INT NOT NULL,
    target_month INT NOT NULL,
    target_consumption DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_target (resource_type, target_year, target_month),
    INDEX idx_target_period (target_year, target_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================
-- SEGURIDAD LABORAL Y GESTIÓN DE RIESGOS - SST (SPEC 004)
-- ==========================================================

-- Matriz de Identificación de Peligros y Valoración de Riesgos (IPVR)
CREATE TABLE IF NOT EXISTS sst_hazards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(100) NOT NULL,
    activity VARCHAR(150) NOT NULL,
    hazard_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    potential_consequences TEXT NULL,
    risk_level ENUM('BAJO', 'MEDIO', 'ALTO', 'CRITICO') NOT NULL DEFAULT 'MEDIO',
    controls_in_place TEXT NULL,
    recommended_actions TEXT NULL,
    status ENUM('ACTIVO', 'CONTROLADO', 'EN_REVISION') NOT NULL DEFAULT 'ACTIVO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hazard_area (area),
    INDEX idx_hazard_risk (risk_level),
    INDEX idx_hazard_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reportes de incidentes, actos y condiciones inseguras
CREATE TABLE IF NOT EXISTS sst_incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reported_by_user_id INT NOT NULL,
    incident_type ENUM('CONDICION_INSEGURA', 'ACTO_INSEGURO', 'CASI_ACCIDENTE', 'ACCIDENTE_LEVE', 'ACCIDENTE_GRAVE') NOT NULL,
    incident_date DATETIME NOT NULL,
    location_detail VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    evidence_photo_url VARCHAR(255) NULL,
    severity ENUM('BAJA', 'MEDIA', 'ALTA') NOT NULL DEFAULT 'MEDIA',
    status ENUM('PENDIENTE', 'EN_ATENCION', 'RESUELTO', 'DESESTIMADO') NOT NULL DEFAULT 'PENDIENTE',
    assigned_to_user_id INT NULL,
    resolution_notes TEXT NULL,
    resolved_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(id),
    INDEX idx_incident_status (status),
    INDEX idx_incident_severity (severity),
    INDEX idx_incident_date (incident_date),
    INDEX idx_incident_user (reported_by_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================
-- CONTROL DE EPP Y DOTACIONES (SPEC 005)
-- ==========================================================

-- Catálogo de Elementos de Protección Personal
CREATE TABLE IF NOT EXISTS epp_catalog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    category ENUM('CABEZA', 'VISUAL', 'AUDITIVA', 'RESPIRATORIA', 'MANOS', 'PIES', 'CUERPO') NOT NULL,
    standard_code VARCHAR(50) NULL,
    lifespan_days INT NOT NULL DEFAULT 90,
    description TEXT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_epp_category (category),
    INDEX idx_epp_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registro de entregas y asignaciones de dotación a operarios
CREATE TABLE IF NOT EXISTS epp_deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    epp_id INT NOT NULL,
    worker_id INT NOT NULL,
    delivered_by_user_id INT NOT NULL,
    delivery_date DATE NOT NULL,
    next_renewal_date DATE NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    reason ENUM('DOTACION_PERIODICA', 'INGRESO_NUEVO', 'DETERIORO', 'PERDIDA') NOT NULL DEFAULT 'DOTACION_PERIODICA',
    worker_signature_confirmed BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (epp_id) REFERENCES epp_catalog(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES users(id),
    FOREIGN KEY (delivered_by_user_id) REFERENCES users(id),
    INDEX idx_delivery_worker (worker_id),
    INDEX idx_delivery_epp (epp_id),
    INDEX idx_delivery_renewal (next_renewal_date),
    INDEX idx_delivery_date (delivery_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inspecciones periódicas de uso y estado de EPP en planta
CREATE TABLE IF NOT EXISTS epp_inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspector_user_id INT NOT NULL,
    worker_id INT NOT NULL,
    inspection_date DATE NOT NULL,
    area VARCHAR(100) NOT NULL,
    is_compliant BOOLEAN NOT NULL DEFAULT TRUE,
    deficiencies_found TEXT NULL,
    corrective_actions TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspector_user_id) REFERENCES users(id),
    FOREIGN KEY (worker_id) REFERENCES users(id),
    INDEX idx_inspection_worker (worker_id),
    INDEX idx_inspection_date (inspection_date),
    INDEX idx_inspection_compliant (is_compliant)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;




