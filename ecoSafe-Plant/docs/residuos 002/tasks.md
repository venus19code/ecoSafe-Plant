# Lista de Tareas - 002: Gestión de Residuos

- [ ] **1. Base de Datos MySQL**
  - [ ] 1.1 Agregar sentencias DDL para `waste_categories`, `waste_types` y `waste_records` al script de schema.
  - [ ] 1.2 Agregar datos semilla en `seed.sql` con categorías y tipos de residuos típicos de planta (cacao, café, reciclables, RESPEL).

- [ ] **2. Backend en Python**
  - [ ] 2.1 Crear `backend/routes/waste_routes.py`.
  - [ ] 2.2 Endpoint `GET /api/waste/types` para obtener categorías y tipos.
  - [ ] 2.3 Endpoint `POST /api/waste/records` con validación de datos numéricos y fechas.
  - [ ] 2.4 Endpoints `GET`, `PUT`, `DELETE` para `/api/waste/records/<id>`.
  - [ ] 2.5 Endpoint `GET /api/waste/summary` para agregaciones mensuales y % de aprovechamiento.

- [ ] **3. Frontend en HTML / CSS / JavaScript**
  - [ ] 3.1 Maquetar la página `frontend/pages/residuos.html`.
  - [ ] 3.2 Añadir tarjetas de KPIs superiores (Total generado, % valorizado, total peligroso).
  - [ ] 3.3 Diseñar formulario modal en HTML/CSS para registrar un residuo.
  - [ ] 3.4 Implementar `frontend/js/residuos.js` con consumo de API mediante `fetch()`.
  - [ ] 3.5 Añadir buscador en tiempo real y filtros por fecha en la tabla.
