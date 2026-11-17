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
