# Lista de Tareas - 003: Consumo de Recursos (Agua y Energía)

- [ ] **1. Base de Datos MySQL**
  - [ ] 1.1 Incluir DDL de `utility_meters`, `utility_readings` y `utility_targets` en `schema.sql`.
  - [ ] 1.2 Agregar medidores predeterminados en `seed.sql`.

- [ ] **2. Backend en Python**
  - [ ] 2.1 Crear `backend/routes/utility_routes.py`.
  - [ ] 2.2 Endpoint `GET /api/utilities/meters` para listar medidores activos.
  - [ ] 2.3 Endpoint `POST /api/utilities/readings` con cálculo automático de diferencia respecto a la lectura anterior.
  - [ ] 2.4 Endpoint `GET /api/utilities/readings` con filtros de medidor y periodo.
  - [ ] 2.5 Endpoint `GET /api/utilities/summary` con totales mensuales y comparación contra metas.

- [ ] **3. Frontend en HTML / CSS / JavaScript**
  - [ ] 3.1 Maquetar la página `frontend/pages/recursos.html` con pestañas (Agua / Energía).
  - [ ] 3.2 Crear tarjetas de resumen (Consumo total m³/kWh, Costo estimado, Porcentaje de meta).
  - [ ] 3.3 Crear modal para registrar nueva lectura con pre-llenado de la lectura anterior.
  - [ ] 3.4 Desarrollar `frontend/js/recursos.js` para consumir la API y actualizar las vistas.
  - [ ] 3.5 Añadir modal de configuración de metas mensuales.
