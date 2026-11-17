# Lista de Tareas - 001: Arquitectura Base y Autenticación

- [x] **1. Preparación y Estructura**
  - [x] 1.1 Validar instalación y versión de Python y MySQL con el usuario.
  - [x] 1.2 Crear estructura de carpetas `backend/` y `frontend/`.
  - [x] 1.3 Crear `requirements.txt` con librerías de Python (`Flask`, `flask-cors`, `PyMySQL`, `bcrypt`, `PyJWT`, `python-dotenv`).
  - [x] 1.4 Crear `.env.example` y `.gitignore`.

- [x] **2. Base de Datos MySQL**
  - [x] 2.1 Crear script `backend/schema.sql` con creación de base de datos `ecosafe_db` y tablas `users` y `audit_logs`.
  - [x] 2.2 Crear script `backend/seed.sql` con usuario administrador por defecto con contraseña hasheada.
  - [x] 2.3 Crear script `backend/init_db.py` para ejecutar el schema y verificar la conexión a MySQL.

- [x] **3. Backend Python - API y Auth**
  - [x] 3.1 Crear `backend/database.py` para gestionar conexiones con `PyMySQL`.
  - [x] 3.2 Crear `backend/utils/auth.py` con funciones de hash con `bcrypt` y generación/validación de tokens JWT.
  - [x] 3.3 Crear decoradores de autenticación y autorización por roles (`@login_required`, `@role_required`).
  - [x] 3.4 Implementar `backend/routes/auth_routes.py` (`login`, `register`, `me`, `users`).
  - [x] 3.5 Configurar `backend/app.py` integrando CORS y sirviendo estáticos en arquitectura de monolito.

- [x] **4. Frontend - HTML, CSS y JavaScript**
  - [x] 4.1 Crear `frontend/index.html` con pantalla de login estilizada y responsiva.
  - [x] 4.2 Crear `frontend/css/styles.css` con variables CSS para el tema ecológico de EcoSafe Plant y diseño mobile-first.
  - [x] 4.3 Crear `frontend/js/api.js` para peticiones `fetch` que adjunten automáticamente el token `Authorization: Bearer <token>`.
  - [x] 4.4 Crear `frontend/js/auth.js` para manejar el login, logout y redirección según rol.
  - [x] 4.5 Crear `frontend/manifest.json` para permitir "Agregar a pantalla de inicio" en celulares y tablets.
  - [x] 4.6 Crear `frontend/pages/dashboard.html` como página base protegida post-login.
