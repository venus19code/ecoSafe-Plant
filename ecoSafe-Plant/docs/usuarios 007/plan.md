# Plan de Implementación - 007: Gestión de Usuarios y Roles

## 1. Objetivo
Centralizar la administración de las cuentas de acceso a EcoSafe Plant: crear usuarios, asignar rol y área, editarlos, activarlos/desactivarlos y restablecer contraseñas. Todo bajo control exclusivo del rol **ADMIN**, con registro de auditoría de cada cambio.

## 2. Enfoque
- **Gestión de identidad sin borrado físico**: los usuarios nunca se eliminan; se desactivan (`is_active = FALSE`) para conservar la trazabilidad de sus registros históricos en los demás módulos.
- **Control de acceso por rol**: el backend protege los endpoints con `@role_required(...)` y el frontend oculta el módulo a quien no sea ADMIN.
- **Seguridad de contraseñas**: hash bcrypt (reutilizando `utils/auth.hash_password`), nunca se almacenan ni devuelven contraseñas en texto plano.
- **Auditoría**: cada alta, edición, cambio de estado o reseteo de contraseña se registra en `audit_logs`.

## 3. Fases de Ejecución

### Fase 1: Backend en Python
- Crear `backend/routes/user_routes.py` con el CRUD de usuarios (listar, ver, crear, editar, cambiar estado, restablecer contraseña) y un endpoint de resumen.
- Registrar el blueprint en `app.py`.
- Retirar el `GET /users` duplicado de `auth_routes.py` (pasa a `user_routes.py` con más funcionalidad).

### Fase 2: Frontend en HTML / CSS / JS
- Maquetar `frontend/pages/usuarios.html` con tarjetas de resumen, filtros y tabla de usuarios.
- Desarrollar `frontend/js/usuarios.js` con los modales de alta/edición y de reseteo de contraseña.
- Agregar el enlace "👤 Usuarios (007)" al menú lateral, visible solo para ADMIN.

### Fase 3: Seguridad y Trazabilidad
- Impedir que un administrador se desactive a sí mismo o deje el sistema sin administradores activos.
- Registrar auditoría en cada operación de escritura.
- Restringir la vista de gestión a usuarios con rol ADMIN.
