-- ==========================================================
-- ECOSAFE PLANT - DATOS INICIALES (SEED 001)
-- ==========================================================

USE ecoSafe_db;

-- Contraseña para todos los usuarios semilla de prueba: EcoSafe2026*
-- Hash generado con bcrypt (costo 10): $2b$10$wT8m9G6h3dK4Qx7pY0uPwe8i4cM5Z1oA9Vb2cE3dF4g5h6j7k8l9m
-- (init_db.py también se encarga de verificar y actualizar los hashes con bcrypt nativo)

INSERT INTO users (id, name, email, password_hash, role, area, is_active)
VALUES 
(1, 'Administrador EcoSafe', 'admin@ecosafe.com', '$2b$10$7Zrqc1511t9V/KGyQh474erG8Q/634qjXWvX4M3K3L7L7qO/Q8qCe', 'ADMIN', 'Dirección General', TRUE),
(2, 'Supervisor de Planta', 'supervisor@ecosafe.com', '$2b$10$7Zrqc1511t9V/KGyQh474erG8Q/634qjXWvX4M3K3L7L7qO/Q8qCe', 'SUPERVISOR', 'Beneficio y Fermentación', TRUE),
(3, 'Operario de Producción', 'operario@ecosafe.com', '$2b$10$7Zrqc1511t9V/KGyQh474erG8Q/634qjXWvX4M3K3L7L7qO/Q8qCe', 'OPERARIO', 'Secado y Empaque', TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name), role=VALUES(role), area=VALUES(area);

INSERT INTO audit_logs (user_id, action, entity, details)
VALUES (1, 'INITIALIZE', 'SYSTEM', '{"event": "Base de datos inicializada con usuarios semilla de Spec 001"}');

-- ==========================================================
-- DATOS SEMILLA - GESTIÓN DE RESIDUOS (SPEC 002)
-- ==========================================================

-- Categorías de Residuos
INSERT INTO waste_categories (id, name, description, color_code)
VALUES
(1, 'Orgánicos de proceso', 'Residuos biodegradables derivados del beneficio de café y cacao', '#2d6a4f'),
(2, 'Aprovechables / Reciclables', 'Materiales con potencial de reciclaje y valorización industrial', '#3b82f6'),
(3, 'No aprovechables / Ordinarios', 'Residuos sólidos comunes sin posibilidad de reaprovechamiento', '#6b7280'),
(4, 'Peligrosos (RESPEL)', 'Residuos con características corrosivas, reactivas, tóxicas o inflamables', '#ef4444')
ON DUPLICATE KEY UPDATE name=VALUES(name), description=VALUES(description), color_code=VALUES(color_code);

-- Tipos de Residuos
INSERT INTO waste_types (id, category_id, name, default_unit, is_hazardous)
VALUES
-- Orgánicos (ID 1)
(1, 1, 'Cáscara de cacao', 'kg', FALSE),
(2, 1, 'Mucílago de cacao', 'litros', FALSE),
(3, 1, 'Pulpa de café', 'kg', FALSE),
(4, 1, 'Cascarilla de café', 'kg', FALSE),

-- Reciclables (ID 2)
(5, 2, 'Cartón y papel de embalaje', 'kg', FALSE),
(6, 2, 'Plástico de empaque (film/polipropileno)', 'kg', FALSE),
(7, 2, 'Chatarra metálica y latas', 'kg', FALSE),
(8, 2, 'Vidrio', 'kg', FALSE),

-- Ordinarios (ID 3)
(9, 3, 'Basura común de planta', 'kg', FALSE),
(10, 3, 'Residuos de barrido y aseo', 'kg', FALSE),

-- Peligrosos (ID 4)
(11, 4, 'Envases vacíos de agroquímicos / sanitizantes', 'kg', TRUE),
(12, 4, 'Aceites usados de maquinaria', 'galones', TRUE),
(13, 4, 'Baterías y acumuladores', 'kg', TRUE),
(14, 4, 'Luminarias fluorescentes en desuso', 'unidades', TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name), default_unit=VALUES(default_unit), is_hazardous=VALUES(is_hazardous);

-- Registros de prueba (Mes actual: Noviembre 2026 y Mes anterior: Octubre 2026)
INSERT INTO waste_records (id, waste_type_id, recorded_by_user_id, record_date, quantity, unit, area, disposal_method, notes)
VALUES
-- Octubre 2026 (Mes anterior)
(1, 1, 2, '2026-10-15', 1250.00, 'kg', 'Despulpado y Fermentación', 'Compostaje', 'Cáscara fresca trasladada a fosa de compost 1'),
(2, 3, 3, '2026-10-20', 980.00, 'kg', 'Beneficio húmedo', 'Lombricultura', 'Pulpa de café mezclada con lecho'),
(3, 5, 3, '2026-10-25', 140.00, 'kg', 'Empaque y Almacén', 'Reciclaje / Gestor autorizado', 'Lote de cartón compactado'),
(4, 9, 3, '2026-10-28', 210.00, 'kg', 'Casino y Oficinas', 'Relleno sanitario', 'Recolección municipal de ordinarios'),
(5, 12, 2, '2026-10-30', 25.00, 'galones', 'Mantenimiento Mecánico', 'Gestor RESPEL autorizado', 'Cambio de aceite de motor despulpadora'),

-- Noviembre 2026 (Mes actual)
(6, 1, 2, '2026-11-05', 1420.50, 'kg', 'Despulpado y Fermentación', 'Compostaje', 'Cáscara de cacao enriquecida con cal'),
(7, 2, 2, '2026-11-08', 350.00, 'litros', 'Fermentación', 'Alimentación animal', 'Mucílago suministrado a cerdos de finca vecina'),
(8, 3, 3, '2026-11-12', 1100.00, 'kg', 'Beneficio húmedo', 'Lombricultura', 'Pulpa de café madura'),
(9, 5, 3, '2026-11-14', 185.00, 'kg', 'Empaque y Almacén', 'Reciclaje / Gestor autorizado', 'Venta a cooperativa de recicladores'),
(10, 6, 3, '2026-11-16', 75.20, 'kg', 'Línea de Empaque', 'Reciclaje / Gestor autorizado', 'Rollos plásticos sobrantes de prueba'),
(11, 9, 3, '2026-11-17', 160.00, 'kg', 'Planta General', 'Relleno sanitario', 'Desechos no reciclables'),
(12, 11, 1, '2026-11-17', 18.00, 'kg', 'Bodega de Insumos', 'Gestor RESPEL autorizado', 'Triple lavado realizado según norma ICA')
ON DUPLICATE KEY UPDATE quantity=VALUES(quantity), area=VALUES(area), disposal_method=VALUES(disposal_method);

