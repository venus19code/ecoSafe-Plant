# Lista de Tareas - 002: Gestión de Residuos

- [x] **1. Base de Datos MySQL** (18/11/2026)
  - [x] 1.1 Agregar sentencias DDL para `waste_categories`, `waste_types` y `waste_records` al script de schema.
  - [x] 1.2 Agregar datos semilla en `seed.sql` con categorías y tipos de residuos típicos de planta (cacao, café, reciclables, RESPEL).

- [x] **2. Backend en Python** (18/11/2026)
  - [x] 2.1 Crear `backend/routes/waste_routes.py`.
  - [x] 2.2 Endpoint `GET /api/waste/types` para obtener categorías y tipos.
  - [x] 2.3 Endpoint `POST /api/waste/records` con validación de datos numéricos y fechas.
  - [x] 2.4 Endpoints `GET`, `PUT`, `DELETE` para `/api/waste/records/<id>`.
  - [x] 2.5 Endpoint `GET /api/waste/summary` para agregaciones mensuales y % de aprovechamiento.

- [x] **3. Frontend en HTML / CSS / JavaScript** (18/11/2026)
  - [x] 3.1 Maquetar la página `frontend/pages/residuos.html`.
  - [x] 3.2 Añadir tarjetas de KPIs superiores (Total generado, % valorizado, total peligroso).
  - [x] 3.3 Diseñar formulario modal en HTML/CSS para registrar un residuo.
  - [x] 3.4 Implementar `frontend/js/residuos.js` con consumo de API mediante `fetch()`.
  - [x] 3.5 Añadir buscador en tiempo real y filtros por fecha en la tabla.
