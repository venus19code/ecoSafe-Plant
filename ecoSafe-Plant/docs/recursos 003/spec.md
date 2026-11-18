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

---

## ✅ Seguimiento de Tareas

> Marca cada tarea cuando esté completada. Actualiza la fecha entre paréntesis al finalizar.

### Base de Datos MySQL
- [x] Incluir DDL de `utility_meters`, `utility_readings` y `utility_targets` en `schema.sql` (18/11/2026)
- [x] Agregar medidores predeterminados en `seed.sql` (Medidor General Agua, Medidor General Energía) (18/11/2026)

### Backend en Python
- [x] Crear `backend/routes/utility_routes.py` (18/11/2026)
- [x] Endpoint `GET /api/utilities/meters` para listar medidores activos (18/11/2026)
- [x] Endpoint `POST /api/utilities/readings` con cálculo automático de diferencia respecto a la lectura anterior (18/11/2026)
- [x] Endpoint `GET /api/utilities/readings` con filtros de medidor y periodo (18/11/2026)
- [x] Endpoint `GET /api/utilities/summary` con totales mensuales y comparación contra metas (18/11/2026)

### Frontend en HTML / CSS / JavaScript
- [x] Maquetar la página `frontend/pages/recursos.html` con pestañas (Agua / Energía) (18/11/2026)
- [x] Crear tarjetas de resumen (Consumo total m³/kWh, Costo estimado, Porcentaje de meta) (18/11/2026)
- [x] Crear modal para registrar nueva lectura con pre-llenado de la lectura anterior (18/11/2026)
- [x] Desarrollar `frontend/js/recursos.js` para consumir la API y actualizar las vistas (18/11/2026)
- [x] Añadir modal de configuración de metas mensuales (solo ADMIN/SUPERVISOR) (18/11/2026)


---

## 🧪 Tests de Funcionalidad

> Ejecuta estas pruebas una vez que el módulo esté implementado para verificar que todo funciona según la especificación. Marca cada test cuando lo hayas validado.

### Backend (API Python)

- [x] **TEST-003-B1**: `GET /api/utilities/meters` → retorna `200` con los medidores sembrados (Medidor General Agua, Medidor General Energía).
- [x] **TEST-003-B2**: `POST /api/utilities/readings` con la primera lectura de un medidor (sin lectura previa) → retorna `201` con `consumption` igual a `reading_value`.
- [x] **TEST-003-B3**: `POST /api/utilities/readings` con una segunda lectura → retorna `201` con `consumption = lectura_nueva - lectura_anterior` calculado automáticamente.
- [x] **TEST-003-B4**: `POST /api/utilities/readings` con `reading_value` menor que la lectura anterior → retorna `400 Bad Request` (el medidor no puede retroceder).
- [x] **TEST-003-B5**: `GET /api/utilities/readings?resource_type=AGUA&month=11&year=2026` → retorna solo lecturas de agua del mes indicado.
- [x] **TEST-003-B6**: `GET /api/utilities/summary?month=11&year=2026` → retorna consumo total de agua y energía del mes, costo acumulado y porcentaje de meta consumida.
- [x] **TEST-003-B7**: `POST /api/utilities/targets` con `resource_type=AGUA, target_month=11, target_year=2026, target_consumption=500` → retorna `201`.
- [x] **TEST-003-B8**: `POST /api/utilities/targets` con la misma combinación (mes/año/recurso ya existente) → actualiza el valor en lugar de duplicar (upsert o `409` descriptivo).

### Base de Datos MySQL

- [x] **TEST-003-D1**: Verificar que la restricción `UNIQUE KEY uq_target` en `utility_targets` impide duplicados de meta para el mismo mes, año y tipo de recurso.
- [x] **TEST-003-D2**: Confirmar que insertar una lectura con un `meter_id` inexistente falla por clave foránea.

### Frontend (HTML + CSS + JS)

- [x] **TEST-003-F1**: La página `recursos.html` carga con las dos pestañas (Agua / Energía) visibles y funcionales.
- [x] **TEST-003-F2**: Al abrir el modal de nueva lectura, el campo "Última lectura registrada" se pre-llena con el valor de la lectura anterior del medidor seleccionado.
- [x] **TEST-003-F3**: Al escribir la lectura actual, el campo "Consumo calculado" se actualiza en tiempo real mostrando la diferencia.
- [x] **TEST-003-F4**: La barra de progreso de meta muestra el porcentaje correcto (ej. si la meta es 500 m³ y se consumieron 300, debe mostrar 60%).
- [x] **TEST-003-F5**: Cuando el consumo supera el 100% de la meta, la barra y la tarjeta KPI cambian a color rojo de alerta.
- [x] **TEST-003-F6**: La página es usable en celular (375px): las tarjetas KPI y la tabla se apilan verticalmente sin desbordamiento.
