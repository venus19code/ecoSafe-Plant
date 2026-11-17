# Especificación Técnica - 003: Consumo de Recursos (Agua y Energía)

## 1. Visión General
El seguimiento al consumo de agua y energía es fundamental para la sostenibilidad y reducción de costos operativos en la planta. Este módulo permite registrar lecturas de medidores (diarias o mensuales), calcular consumos netos automáticamente, comparar con metas ambientales y detectar anomalías o sobrecostos.

## 2. Requerimientos Funcionales
1. **Puntos de Medición (Medidores/Áreas)**:
   - Registro de medidores principales y sub-medidores por área (ej. Medidor General de Agua, Planta de Lavado, Caldera, Oficinas, Transformador General de Energía, Línea de Tostado).
2. **Registro de Consumo**:
   - Tipo de recurso: **Agua** (m³ o Litros) o **Energía** (kWh).
   - Modalidad de registro:
     - *Por lectura acumulada del medidor* (Lectura inicial vs Lectura final = Consumo calculado automáticamente).
     - *Por factura / consumo directo del periodo* (Consumo total mensual en m³ o kWh, valor monetario facturado).
   - Fecha de lectura o periodo facturado (Mes / Año).
   - Observaciones (fugas identificadas, mantenimiento, paradas de planta).
3. **Metas y Alertas de Consumo**:
   - Definición de límites mensuales de consumo (m³ de agua y kWh de energía).
   - Indicador visual tipo semáforo cuando el consumo supera la meta presupuestada.
4. **Cálculo de Indicadores Clave**:
   - Consumo total del periodo (Agua y Energía).
   - Variación % respecto al mes anterior.
   - Costo total acumulado de servicios públicos.

## 3. Modelo de Datos (MySQL)

```sql
CREATE TABLE utility_meters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_type ENUM('AGUA', 'ENERGIA') NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    location_area VARCHAR(100) NOT NULL,
    multiplier DECIMAL(6, 2) NOT NULL DEFAULT 1.00,
    unit VARCHAR(20) NOT NULL DEFAULT 'm3',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE utility_readings (
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
    FOREIGN KEY (meter_id) REFERENCES utility_meters(id),
    FOREIGN KEY (recorded_by_user_id) REFERENCES users(id)
);

CREATE TABLE utility_targets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_type ENUM('AGUA', 'ENERGIA') NOT NULL,
    target_year INT NOT NULL,
    target_month INT NOT NULL,
    target_consumption DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_target (resource_type, target_year, target_month)
);
```

## 4. Endpoints de la API en Python (Flask / FastAPI)
- `GET /api/utilities/meters`: Listar medidores configurados.
- `POST /api/utilities/meters`: Crear o actualizar medidor.
- `GET /api/utilities/readings`: Listado con filtros por recurso, medidor y fechas.
- `POST /api/utilities/readings`: Registrar lectura (calcula el consumo automáticamente buscando la lectura anterior).
- `GET /api/utilities/summary`: Consumos consolidados por mes, comparativa con metas y variación intermensual.
- `GET /api/utilities/targets`: Metas de consumo ambiental configuradas.
- `POST /api/utilities/targets`: Establecer o editar meta para un mes/año.

## 5. Frontend (HTML + CSS + JavaScript)
- **Vista**: `frontend/pages/recursos.html`.
- **Estilos**: `frontend/css/recursos.css`.
- **Lógica JS**: `frontend/js/recursos.js` con:
  - Pestañas para conmutar entre Agua y Energía.
  - Cálculo automático en tiempo real en el formulario al escribir la lectura actual.
  - Barras de progreso visuales con CSS para mostrar el porcentaje de meta consumido.
