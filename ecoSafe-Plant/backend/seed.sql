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

-- ==========================================================
-- DATOS SEMILLA - CONSUMO DE RECURSOS (SPEC 003)
-- ==========================================================

-- Medidores de Agua y Energía
INSERT INTO utility_meters (id, resource_type, code, name, location_area, multiplier, unit, is_active)
VALUES
(1, 'AGUA', 'MED-AGUA-01', 'Medidor General de Agua (Red Principal)', 'Entrada Principal Planta', 1.00, 'm3', TRUE),
(2, 'AGUA', 'MED-AGUA-02', 'Sub-medidor Lavado y Beneficio Húmedo', 'Área de Beneficio y Fermentación', 1.00, 'm3', TRUE),
(3, 'ENERGIA', 'MED-ELEC-01', 'Transformador General Energía Eléctrica', 'Subestación Eléctrica', 1.00, 'kWh', TRUE),
(4, 'ENERGIA', 'MED-ELEC-02', 'Sub-medidor Línea de Secado y Tostado', 'Nave de Maquinaria y Secado', 1.00, 'kWh', TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name), location_area=VALUES(location_area), unit=VALUES(unit), is_active=VALUES(is_active);

-- Metas Ambientales Mensuales (Octubre y Noviembre 2026)
INSERT INTO utility_targets (resource_type, target_year, target_month, target_consumption)
VALUES
('AGUA', 2026, 10, 480.00),
('ENERGIA', 2026, 10, 3500.00),
('AGUA', 2026, 11, 450.00),
('ENERGIA', 2026, 11, 3200.00)
ON DUPLICATE KEY UPDATE target_consumption=VALUES(target_consumption);

-- Lecturas históricas de Medidores (Octubre y Noviembre 2026)
INSERT INTO utility_readings (id, meter_id, recorded_by_user_id, reading_date, reading_value, consumption, unit, cost_amount, notes)
VALUES
-- Octubre 2026
-- Medidor General Agua: Lectura inicial 1200 m3 -> Lectura 1580 m3 (Consumo 380 m3)
(1, 1, 2, '2026-10-01', 1200.00, 1200.00, 'm3', 0.00, 'Lectura inicial de calibración del medidor'),
(2, 1, 2, '2026-10-31', 1580.00, 380.00, 'm3', 1444000.00, 'Consumo mensual de agua facturado a $3.800/m3'),

-- Transformador General Energía: Lectura inicial 45000 kWh -> Lectura 48150 kWh (Consumo 3150 kWh)
(3, 3, 2, '2026-10-01', 45000.00, 45000.00, 'kWh', 0.00, 'Lectura base periodo octubre'),
(4, 3, 2, '2026-10-31', 48150.00, 3150.00, 'kWh', 2520000.00, 'Consumo energía octubre facturado a $800/kWh'),

-- Noviembre 2026 (Mes Actual)
-- Medidor General Agua: Lectura intermedia semana 1 (1660 m3 -> consumo 80 m3)
(5, 1, 2, '2026-11-07', 1660.00, 80.00, 'm3', 304000.00, 'Corte semanal semana 1'),
-- Medidor General Agua: Lectura intermedia semana 2 (1755 m3 -> consumo 95 m3)
(6, 1, 3, '2026-11-14', 1755.00, 95.00, 'm3', 361000.00, 'Corte semanal semana 2'),
-- Medidor General Agua: Lectura actual semana 3 (1840 m3 -> consumo 85 m3)
(7, 1, 3, '2026-11-17', 1840.00, 85.00, 'm3', 323000.00, 'Corte semanal semana 3 - dentro de meta proyectada'),

-- Sub-medidor Lavado: Lectura inicial 300 m3 -> 390 m3
(8, 2, 3, '2026-11-01', 300.00, 300.00, 'm3', 0.00, 'Puesta en marcha de sub-medidor lavado'),
(9, 2, 3, '2026-11-16', 368.00, 68.00, 'm3', 258400.00, 'Consumo intensivo en lavado de tanques'),

-- Transformador Energía: Lectura semana 1 (48900 kWh -> consumo 750 kWh)
(10, 3, 2, '2026-11-07', 48900.00, 750.00, 'kWh', 600000.00, 'Semana 1 de noviembre'),
-- Transformador Energía: Lectura semana 2 (49720 kWh -> consumo 820 kWh)
(11, 3, 3, '2026-11-14', 49720.00, 820.00, 'kWh', 656000.00, 'Semana 2 de noviembre'),
-- Transformador Energía: Lectura actual (50550 kWh -> consumo 830 kWh)
(12, 3, 3, '2026-11-17', 50550.00, 830.00, 'kWh', 664000.00, 'Semana 3 de noviembre')
ON DUPLICATE KEY UPDATE reading_value=VALUES(reading_value), consumption=VALUES(consumption), cost_amount=VALUES(cost_amount);

-- ==========================================================
-- DATOS SEMILLA - SEGURIDAD Y SALUD EN EL TRABAJO (SPEC 004)
-- ==========================================================

-- Matriz de Peligros y Valoración de Riesgos (IPVR)
INSERT INTO sst_hazards (id, area, activity, hazard_type, description, potential_consequences, risk_level, controls_in_place, recommended_actions, status)
VALUES
(1, 'Despulpado y Fermentación', 'Despulpado continuo de café y cacao', 'Mecánico / Atrapamiento',
 'Riesgo de atrapamiento de extremidades superiores en rodillos y engranajes de la máquina despulpadora',
 'Laceraciones graves, fracturas o amputación de falanges', 'CRITICO',
 'Pulsador de parada de emergencia cercano, señalización visual de peligro mecánico',
 'Instalar guarda perimetral de policarbonato con sensor de apertura de seguridad', 'ACTIVO'),

(2, 'Beneficio húmedo', 'Lavado de tanques de fermentación y canales de corrimiento', 'Locativo / Superficies resbaladizas',
 'Piso húmedo constante con restos mucilaginosos que generan alto riesgo de resbalón y caída al mismo nivel',
 'Traumatismos osteomusculares, esguinces de tobillo, contusiones lumbares', 'ALTO',
 'Uso obligatorio de botas de caucho con suela de grabado antideslizante',
 'Aplicar tratamiento epóxico antideslizante en pasillos principales e instalar pasamanos', 'ACTIVO'),

(3, 'Nave de Maquinaria y Secado', 'Operación de molinos y ventiladores de secado artificial', 'Físico / Ruido industrial',
 'Exposición continua a presiones sonoras superiores a 85 dBA generadas por motores y extractores',
 'Hipoacusia neurosensorial bilateral progresiva, fatiga auditiva', 'MEDIO',
 'Uso obligatorio de protectores auditivos tipo copa o inserción de silicona',
 'Realizar sonometría de banda octava anual y aislamiento acústico de la caseta de turbinas', 'CONTROLADO'),

(4, 'Línea de Selección y Empaque', 'Zarandeo, selección y tamizado de cascarilla y grano', 'Químico / Polvos orgánicos',
 'Inhalación de material particulado fino vegetal y polvo orgánico suspendido en el ambiente de empaque',
 'Irritación de vías aéreas superiores, rinitis alérgica ocupacional, bronquitis', 'MEDIO',
 'Mascarillas N95 para operarios de turno, cortinas de polietileno',
 'Instalar campana de extracción localizada en boca de descarga de la tolva', 'ACTIVO'),

(5, 'Bodega y Almacén General', 'Inspección y estiba de sacos de café y cacao', 'Biológico / Mohos y Hongos',
 'Proliferación potencial de hongos y esporas fúngicas por humedad en esquinas de almacenamiento',
 'Alergias dérmicas, micosis, dificultades respiratorias leves', 'BAJO',
 'Control semanal de humedad y ventilación natural cruzada',
 'Mantener estibas plásticas a mínimo 15 cm del piso y 50 cm de paredes perimetrales', 'CONTROLADO'),

(6, 'Bodega y Almacén General', 'Cargue y descargue manual de sacos de 50 kg', 'Biomecánico / Manipulación manual de cargas',
 'Levantamiento y traslado repetitivo de peso superior al límite recomendado (25 kg) por una sola persona',
 'Lumbalgias agudas, hernias discales, sobreesfuerzo dorsal', 'ALTO',
 'Capacitación en higiene postural y técnica de levantamiento con rodillas flectadas',
 'Dotar de carretillas hidráulicas zorras y exigir levantamiento en parejas para bultos > 25 kg', 'ACTIVO')
ON DUPLICATE KEY UPDATE description=VALUES(description), risk_level=VALUES(risk_level), controls_in_place=VALUES(controls_in_place);

-- Reportes de Incidentes y Condiciones Inseguras
INSERT INTO sst_incidents (id, reported_by_user_id, incident_type, incident_date, location_detail, description, severity, status, assigned_to_user_id, resolution_notes, resolved_at)
VALUES
(1, 3, 'CONDICION_INSEGURA', '2026-11-10 09:30:00', 'Pasillo 2 junto al canal de beneficio húmedo',
 'Rejilla de drenaje rota y desnivel en el piso con empozamiento de mucílago sin cinta de señalización', 'ALTA', 'PENDIENTE', NULL, NULL, NULL),

(2, 3, 'CASI_ACCIDENTE', '2026-11-14 14:15:00', 'Línea de Empaque, tolva clasificadora 3',
 'Cable de alimentación eléctrica del vibrador con cubierta desgastada, casi rozó estructura metálica húmeda', 'MEDIA', 'EN_ATENCION', 2, 'Supervisor inspeccionó el cable. Se programó al electricista para reemplazo inmediato.', NULL),

(3, 2, 'CONDICION_INSEGURA', '2026-11-12 11:00:00', 'Taller de Mantenimiento Mecánico',
 'Ausencia de extintor de polvo químico seco ABC en la zona de banco de esmeril y soldadura eléctrica', 'MEDIA', 'RESUELTO', 1, 'Se ubicó extintor de 20 lbs tipo ABC recargado y debidamente demarcado según norma NTC.', '2026-11-15 16:00:00')
ON DUPLICATE KEY UPDATE status=VALUES(status), resolution_notes=VALUES(resolution_notes), resolved_at=VALUES(resolved_at);

-- ==========================================================
-- DATOS SEMILLA - ELEMENTOS DE PROTECCIÓN PERSONAL (SPEC 005)
-- ==========================================================

-- Catálogo de EPP (Al menos 1 por cada categoría estándar)
INSERT INTO epp_catalog (id, name, category, standard_code, lifespan_days, description, stock_quantity, is_active)
VALUES
(1, 'Casco de Seguridad Tipo I Clase E', 'CABEZA', 'ANSI Z89.1', 730, 'Casco dieléctrico de polietileno de alta densidad con suspensión de 4 puntos y barbuquejo', 25, TRUE),
(2, 'Gafas de Seguridad Antiempañantes', 'VISUAL', 'ANSI Z87.1', 180, 'Lentes de policarbonato transparentes con protección UV y recubrimiento antivaho para planta', 42, TRUE),
(3, 'Protector Auditivo Tipo Copa 27 dB', 'AUDITIVA', 'ANSI S3.19', 365, 'Orejeras acolchadas dieléctricas de alta atenuación para operarios en áreas de molienda y secado', 18, TRUE),
(4, 'Mascarilla Desechable N95 con Válvula', 'RESPIRATORIA', 'NIOSH N95', 30, 'Protección contra partículas y polvillo orgánico de cascarilla durante zarandeo y empaque', 150, TRUE),
(5, 'Guantes de Nitrilo Verde Calibre 15', 'MANOS', 'EN 388 / EN 374', 60, 'Guantes resistentes a químicos, desinfectantes y acidez del mucílago durante lavado', 60, TRUE),
(6, 'Guantes de Carnaza Reforzada', 'MANOS', 'NTC 2190', 90, 'Guantes de cuero vacuno para estibado, cargue de bultos y mantenimiento mecánico', 35, TRUE),
(7, 'Botas de Seguridad en Caucho con Puntera', 'PIES', 'ASTM F2413', 180, 'Botas impermeables caña alta con puntera de acero y suela autolimpiante antideslizante', 22, TRUE),
(8, 'Delantal Industrial Impermeable de PVC', 'CUERPO', 'NTC 3610', 180, 'Peto impermeable de alta resistencia química para operarios de fermentación y lavado', 20, TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name), category=VALUES(category), lifespan_days=VALUES(lifespan_days), stock_quantity=VALUES(stock_quantity);

-- Entregas y Asignaciones de Dotación (Incluye vigentes, vencidas y próximas a vencer)
INSERT INTO epp_deliveries (id, epp_id, worker_id, delivered_by_user_id, delivery_date, next_renewal_date, quantity, reason, worker_signature_confirmed, notes)
VALUES
-- Entrega 1: Casco (Vigente hasta 2028)
(1, 1, 3, 2, '2026-06-01', '2028-05-31', 1, 'INGRESO_NUEVO', TRUE, 'Dotación inicial al ingresar a la planta'),

-- Entrega 2: Botas de seguridad (Vencidas el 2026-11-06 - ALERTA VENCIDA!)
(2, 7, 3, 2, '2026-05-10', '2026-11-06', 1, 'DOTACION_PERIODICA', TRUE, 'Desgaste severo en suela reportado por el trabajador, requiere recambio urgente'),

-- Entrega 3: Mascarilla N95 (Próxima a vencer en diciembre 2026 - ALERTA PRÓXIMA!)
(3, 4, 3, 2, '2026-11-01', '2026-12-01', 5, 'DOTACION_PERIODICA', TRUE, 'Lote de mascarillas para el mes de empaque de cosecha'),

-- Entrega 4: Guantes de nitrilo para Supervisor (Vigente)
(4, 5, 2, 1, '2026-10-15', '2026-12-14', 2, 'DOTACION_PERIODICA', TRUE, 'Dotación bimestral para inspecciones de lavado'),

-- Entrega 5: Gafas de seguridad para Operario (Vigente)
(5, 2, 3, 2, '2026-09-01', '2027-02-28', 1, 'DETERIORO', TRUE, 'Reemplazo de gafas rayadas por partículas de cascarilla')
ON DUPLICATE KEY UPDATE delivery_date=VALUES(delivery_date), next_renewal_date=VALUES(next_renewal_date), notes=VALUES(notes);

-- Rondas de Inspección de Uso de EPP
INSERT INTO epp_inspections (id, inspector_user_id, worker_id, inspection_date, area, is_compliant, deficiencies_found, corrective_actions)
VALUES
(1, 2, 3, '2026-11-05', 'Despulpado y Fermentación', FALSE,
 'El operario no portaba protector auditivo mientras operaba la despulpadora en marcha.',
 'Se le hizo entrega de protectores tipo copa de repuesto y se reiteró el riesgo de hipoacusia.'),

(2, 2, 3, '2026-11-12', 'Beneficio húmedo', TRUE,
 NULL,
 'Operario porta botas de caucho antideslizantes, gafas y guantes de nitrilo en óptimo estado de conservación.')
ON DUPLICATE KEY UPDATE is_compliant=VALUES(is_compliant), deficiencies_found=VALUES(deficiencies_found), corrective_actions=VALUES(corrective_actions);




