# Lista de Tareas - 007: Gestión de Usuarios y Roles

- [x] **1. Backend en Python** (18/11/2026)
  - [x] 1.1 Crear `backend/routes/user_routes.py`.
  - [x] 1.2 Endpoint `GET /api/users` con filtros `q`, `role`, `active`.
  - [x] 1.3 Endpoint `GET /api/users/stats` de resumen por rol y estado.
  - [x] 1.4 Endpoint `GET /api/users/<id>` de detalle.
  - [x] 1.5 Endpoint `POST /api/users` de alta con hash bcrypt.
  - [x] 1.6 Endpoint `PUT /api/users/<id>` de edición.
  - [x] 1.7 Endpoint `PATCH /api/users/<id>/status` con validaciones de auto-bloqueo y último admin.
  - [x] 1.8 Endpoint `PATCH /api/users/<id>/password` de reseteo.
  - [x] 1.9 Registrar el blueprint en `app.py` y retirar el `/users` duplicado de `auth_routes.py`.

- [x] **2. Frontend en HTML / CSS / JavaScript** (18/11/2026)
  - [x] 2.1 Maquetar `frontend/pages/usuarios.html`.
  - [x] 2.2 Cuadrícula de tarjetas de resumen (Total, Activos, Inactivos, Administradores).
  - [x] 2.3 Tabla de usuarios con badges de rol y estado.
  - [x] 2.4 Modales de alta/edición y de reseteo de contraseña.
  - [x] 2.5 Desarrollar `frontend/js/usuarios.js` con peticiones a la API.
  - [x] 2.6 Enlace "Usuarios (007)" en el menú lateral visible solo para ADMIN.
  - [x] 2.7 Exportación del listado filtrado a CSV.

- [x] **3. Seguridad y Trazabilidad** (18/11/2026)
  - [x] 3.1 Validar correo único y contraseña de mínimo 8 caracteres.
  - [x] 3.2 Impedir auto-desactivación y preservar al menos un ADMIN activo.
  - [x] 3.3 Registrar en `audit_logs` cada alta, edición, cambio de estado y reseteo.
  - [x] 3.4 Restringir la vista al rol ADMIN en frontend y backend.
