# Lista de Tareas - 005: Elementos de Protección Personal (EPP)

- [x] **1. Base de Datos MySQL** (18/11/2026)
  - [x] 1.1 Incluir DDL de `epp_catalog`, `epp_deliveries` y `epp_inspections` en `schema.sql`.
  - [x] 1.2 Agregar catálogo base de EPP en `seed.sql`.

- [x] **2. Backend en Python** (18/11/2026)
  - [x] 2.1 Crear `backend/routes/epp_routes.py`.
  - [x] 2.2 Endpoints para catálogo de EPP (`/api/epp/catalog`).
  - [x] 2.3 Endpoint `POST /api/epp/deliveries` con cálculo automático de fecha de renovación.
  - [x] 2.4 Endpoint `GET /api/epp/deliveries` filtrado por colaborador y fechas.
  - [x] 2.5 Endpoint `POST /api/epp/inspections` y `GET /api/epp/inspections`.
  - [x] 2.6 Endpoint `GET /api/epp/renewals-due` para alertar vencimientos.

- [x] **3. Frontend en HTML / CSS / JavaScript** (18/11/2026)
  - [x] 3.1 Maquetar la página `frontend/pages/epp.html` con pestañas.
  - [x] 3.2 Modal para registrar entrega de dotación a un operario.
  - [x] 3.3 Modal para registrar inspección rápida de EPP durante recorridos.
  - [x] 3.4 Desarrollar `frontend/js/epp.js` con lógica de renderizado y peticiones a la API.
  - [x] 3.5 Banner de alerta para dotaciones vencidas.
