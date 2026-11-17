# Lista de Tareas - 005: Elementos de Protección Personal (EPP)

- [ ] **1. Base de Datos MySQL**
  - [ ] 1.1 Incluir DDL de `epp_catalog`, `epp_deliveries` y `epp_inspections` en `schema.sql`.
  - [ ] 1.2 Agregar catálogo base de EPP en `seed.sql`.

- [ ] **2. Backend en Python**
  - [ ] 2.1 Crear `backend/routes/epp_routes.py`.
  - [ ] 2.2 Endpoints para catálogo de EPP (`/api/epp/catalog`).
  - [ ] 2.3 Endpoint `POST /api/epp/deliveries` con cálculo automático de fecha de renovación.
  - [ ] 2.4 Endpoint `GET /api/epp/deliveries` filtrado por colaborador y fechas.
  - [ ] 2.5 Endpoint `POST /api/epp/inspections` y `GET /api/epp/inspections`.
  - [ ] 2.6 Endpoint `GET /api/epp/renewals-due` para alertar vencimientos.

- [ ] **3. Frontend en HTML / CSS / JavaScript**
  - [ ] 3.1 Maquetar la página `frontend/pages/epp.html` con pestañas.
  - [ ] 3.2 Modal para registrar entrega de dotación a un operario.
  - [ ] 3.3 Modal para registrar inspección rápida de EPP durante recorridos.
  - [ ] 3.4 Desarrollar `frontend/js/epp.js` con lógica de renderizado y peticiones a la API.
  - [ ] 3.5 Banner de alerta para dotaciones vencidas.
