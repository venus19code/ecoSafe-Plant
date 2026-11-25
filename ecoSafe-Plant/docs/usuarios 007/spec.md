# Especificación Técnica - 007: Gestión de Usuarios y Roles

## 1. Visión General
El módulo de Gestión de Usuarios permite al administrador controlar quién puede ingresar a EcoSafe Plant y con qué permisos. Administra las cuentas de la tabla `users`: crear, editar rol y área, activar/desactivar y restablecer contraseñas. Los usuarios desactivados conservan todo su historial, pero no pueden iniciar sesión.

## 2. Requerimientos Funcionales
1. **Listado de usuarios**:
   - Ver todos los usuarios con nombre, correo, rol, área, estado y fecha de registro.
   - Buscar por nombre, correo o área.
   - Filtrar por rol (ADMIN, SUPERVISOR, OPERARIO) y por estado (Activo / Inactivo).
2. **Crear usuario** (solo ADMIN):
   - Campos: nombre, correo, contraseña inicial, rol y área.
   - Validar correo único, rol válido y contraseña de mínimo 8 caracteres.
3. **Editar usuario** (solo ADMIN):
   - Actualizar nombre, correo, rol y área.
   - Impedir correos duplicados.
   - Impedir que el último ADMIN activo cambie de rol.
4. **Activar / Desactivar** (solo ADMIN):
   - Desactivación lógica (nunca borrado físico).
   - Un ADMIN no puede desactivarse a sí mismo.
   - El sistema debe conservar al menos un ADMIN activo.
5. **Restablecer contraseña** (solo ADMIN):
   - Asignar una nueva contraseña (mínimo 8 caracteres), almacenada con hash bcrypt.
6. **Resumen / KPIs**:
   - Total de usuarios, activos, inactivos y cantidad de administradores.
7. **Auditoría**:
   - Registrar en `audit_logs`: alta, edición, cambio de estado y reseteo de contraseña.
8. **Exportación**:
   - Descargar el listado filtrado a CSV.

## 3. Modelo de Datos (MySQL)

La información se almacena en la tabla `users` (Spec 001):

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'SUPERVISOR', 'OPERARIO') NOT NULL DEFAULT 'OPERARIO',
    area VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

Los cambios se registran en `audit_logs` (Spec 001):

```sql
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity VARCHAR(50) NOT NULL,
    details TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. Endpoints de la API en Python (Flask)

| Método | Ruta | Roles permitidos | Descripción |
|--------|------|------------------|-------------|
| GET | `/api/users` | ADMIN, SUPERVISOR | Lista de usuarios con filtros `q`, `role`, `active`. |
| GET | `/api/users/stats` | ADMIN, SUPERVISOR | Resumen: total, activos, inactivos y conteo por rol. |
| GET | `/api/users/<id>` | ADMIN, SUPERVISOR | Detalle de un usuario. |
| POST | `/api/users` | ADMIN | Crea un usuario. |
| PUT | `/api/users/<id>` | ADMIN | Actualiza nombre, correo, rol y área. |
| PATCH | `/api/users/<id>/status` | ADMIN | Activa o desactiva un usuario. |
| PATCH | `/api/users/<id>/password` | ADMIN | Restablece la contraseña. |

### Respuestas
- `GET /api/users` → `200` `{ "count": N, "users": [ ... ] }`
- `GET /api/users/stats` → `200` `{ "total": N, "active": N, "inactive": N, "by_role": { "ADMIN": n, "SUPERVISOR": n, "OPERARIO": n } }`
- `POST /api/users` → `201` `{ "message": "...", "user": { ... } }`
- Errores: `400` datos inválidos, `401` sin token, `403` rol no autorizado, `404` usuario no encontrado, `409` correo duplicado.

## 5. Frontend (HTML + CSS + JavaScript)
- **Vista**: `frontend/pages/usuarios.html`.
- **Lógica JS**: `frontend/js/usuarios.js` con:
  - Tarjetas de resumen (Total, Activos, Inactivos, Administradores).
  - Barra de búsqueda y filtros por rol y estado.
  - Tabla de usuarios con acciones: Editar, Activar/Desactivar, Restablecer contraseña.
  - Modal de alta/edición y modal de reseteo de contraseña.
  - Botón de exportación CSV.
- **Control de acceso**: el enlace del menú y la página solo son accesibles para rol ADMIN; cualquier otro rol es redirigido al Dashboard.

---

## ✅ Seguimiento de Tareas

> Marca cada tarea cuando esté completada. Actualiza la fecha entre paréntesis al finalizar.

### Backend en Python
- [x] Crear `backend/routes/user_routes.py` (18/11/2026)
- [x] Endpoint `GET /api/users` con filtros `q`, `role`, `active` (18/11/2026)
- [x] Endpoint `GET /api/users/stats` de resumen por rol y estado (18/11/2026)
- [x] Endpoint `GET /api/users/<id>` de detalle (18/11/2026)
- [x] Endpoint `POST /api/users` de alta con hash bcrypt (18/11/2026)
- [x] Endpoint `PUT /api/users/<id>` de edición (18/11/2026)
- [x] Endpoint `PATCH /api/users/<id>/status` con validaciones de auto-bloqueo (18/11/2026)
- [x] Endpoint `PATCH /api/users/<id>/password` de reseteo (18/11/2026)
- [x] Registrar el blueprint en `app.py` y retirar el `/users` duplicado de `auth_routes.py` (18/11/2026)

### Frontend en HTML / CSS / JavaScript
- [x] Maquetar `frontend/pages/usuarios.html` (18/11/2026)
- [x] Cuadrícula de tarjetas de resumen (18/11/2026)
- [x] Tabla de usuarios con badges de rol y estado (18/11/2026)
- [x] Modales de alta/edición y de reseteo de contraseña (18/11/2026)
- [x] Programar `frontend/js/usuarios.js` con peticiones a la API (18/11/2026)
- [x] Enlace "Usuarios (007)" en el menú lateral visible solo para ADMIN (18/11/2026)
- [x] Exportación del listado a CSV (18/11/2026)

---

## 🧪 Tests de Funcionalidad

> Ejecuta estas pruebas una vez que el módulo esté implementado. Marca cada test cuando lo hayas validado.

### Backend (API Python)

- [ ] **TEST-007-B1**: `GET /api/users` con token ADMIN → `200` y `{ count, users }` con al menos los usuarios semilla.
- [ ] **TEST-007-B2**: `GET /api/users?role=ADMIN` → solo devuelve usuarios con rol ADMIN.
- [ ] **TEST-007-B3**: `GET /api/users?q=<texto>` → filtra por nombre, correo o área.
- [ ] **TEST-007-B4**: `POST /api/users` con datos válidos → `201` y el usuario se crea con contraseña hasheada.
- [ ] **TEST-007-B5**: `POST /api/users` con correo ya existente → `409 Conflict`.
- [ ] **TEST-007-B6**: `POST /api/users` con contraseña de menos de 8 caracteres → `400 Bad Request`.
- [ ] **TEST-007-B7**: `PUT /api/users/<id>` actualiza nombre, correo, rol y área → `200`.
- [ ] **TEST-007-B8**: `PATCH /api/users/<id>/status` con `is_active=false` desactiva el usuario → `200`.
- [ ] **TEST-007-B9**: Un ADMIN no puede desactivar su propia cuenta → `400 Bad Request`.
- [ ] **TEST-007-B10**: No se puede desactivar al último ADMIN activo → `400 Bad Request`.
- [ ] **TEST-007-B11**: `PATCH /api/users/<id>/password` actualiza el hash y permite iniciar sesión con la nueva contraseña.
- [ ] **TEST-007-B12**: Cualquier endpoint de usuarios sin token → `401 Unauthorized`.
- [ ] **TEST-007-B13**: Un usuario OPERARIO o SUPERVISOR que intente `POST`, `PUT` o `PATCH` → `403 Forbidden`.
- [ ] **TEST-007-B14**: `GET /api/users/stats` → `200` con `total`, `active`, `inactive` y `by_role` coherentes.

### Integración

- [ ] **TEST-007-I1**: Un usuario desactivado no puede iniciar sesión (`POST /api/auth/login` → `403`).
- [ ] **TEST-007-I2**: Un usuario recién creado puede iniciar sesión con su contraseña inicial.
- [ ] **TEST-007-I3**: Los cambios de rol se reflejan en el siguiente inicio de sesión del usuario.

### Frontend (HTML + CSS + JS)

- [ ] **TEST-007-F1**: La página `usuarios.html` muestra las 4 tarjetas de resumen con valores numéricos.
- [ ] **TEST-007-F2**: La tabla lista a todos los usuarios con badge de rol y estado.
- [ ] **TEST-007-F3**: El buscador y los filtros de rol/estado reducen la tabla en tiempo real.
- [ ] **TEST-007-F4**: El botón "Nuevo Usuario" abre el modal y al guardar aparece el nuevo usuario sin recargar.
- [ ] **TEST-007-F5**: El botón "Editar" abre el modal precargado y guarda los cambios.
- [ ] **TEST-007-F6**: El botón "Desactivar" cambia el estado del usuario y actualiza las tarjetas de resumen.
- [ ] **TEST-007-F7**: El botón "Restablecer contraseña" permite asignar una nueva contraseña.
- [ ] **TEST-007-F8**: Un usuario sin rol ADMIN no ve el enlace "Usuarios" y es redirigido si intenta abrir la página.
- [ ] **TEST-007-F9**: "Exportar CSV" descarga un archivo `.csv` con los usuarios filtrados.
- [ ] **TEST-007-F10**: En pantalla de celular (375px) la tabla es desplazable y los modales son usables.
