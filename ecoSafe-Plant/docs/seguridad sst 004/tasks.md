# Lista de Tareas - 004: Seguridad Laboral y Gestión de Riesgos (SST)

- [ ] **1. Base de Datos MySQL**
  - [ ] 1.1 Incluir sentencias DDL de `sst_hazards` y `sst_incidents` en `schema.sql`.
  - [ ] 1.2 Agregar datos semilla en `seed.sql` con matriz de peligros típica de plantas de producción.

- [ ] **2. Backend en Python**
  - [ ] 2.1 Crear `backend/routes/sst_routes.py`.
  - [ ] 2.2 Endpoints CRUD para la matriz de peligros (`/api/sst/hazards`).
  - [ ] 2.3 Endpoint para reportar incidentes `POST /api/sst/incidents`.
  - [ ] 2.4 Endpoint `GET /api/sst/incidents` con filtros por severidad y estado.
  - [ ] 2.5 Endpoint `PATCH /api/sst/incidents/<id>/status` para cierre de acciones correctivas.
  - [ ] 2.6 Endpoint `GET /api/sst/summary` con métricas de seguridad para el dashboard.

- [ ] **3. Frontend en HTML / CSS / JavaScript**
  - [ ] 3.1 Maquetar la página `frontend/pages/seguridad.html`.
  - [ ] 3.2 Crear visualizador de matriz de peligros con filtros y códigos de color según severidad.
  - [ ] 3.3 Crear modal de registro de nuevo peligro en la matriz.
  - [ ] 3.4 Crear formulario táctil para reporte de incidentes y condiciones inseguras.
  - [ ] 3.5 Desarrollar `frontend/js/seguridad.js` para la lógica interactiva.
