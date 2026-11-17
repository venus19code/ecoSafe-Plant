# Especificación Técnica - 001: Arquitectura Base y Autenticación

## 1. Visión General
EcoSafe Plant es una plataforma web orientada al control ambiental y la seguridad y salud en el trabajo (SST) en plantas de producción.
Esta fase establece los cimientos del sistema: arquitectura monorepo con backend en **Python**, frontend en **HTML5, CSS3 y JavaScript (Vanilla)**, y base de datos relacional en **MySQL**.

## 2. Arquitectura del Monolito
El proyecto se organizará en la raíz con la siguiente estructura:
```
pagina_web/
├── backend/               # API y lógica en Python (Flask / FastAPI)
│   ├── config.py          # Configuración de base de datos MySQL y variables de entorno
│   ├── database.py        # Conexión MySQL y pool de conexiones
│   ├── models/            # Modelos / Consultas SQL
│   ├── routes/            # Rutas de la API (auth, residuos, recursos, sst, epp, dashboard)
│   ├── schema.sql         # Script DDL de creación de tablas en MySQL
│   ├── seed.sql           # Datos iniciales (usuario admin y catálogos)
│   ├── requirements.txt   # Dependencias de Python (Flask/FastAPI, PyMySQL/SQLAlchemy, PyJWT, bcrypt)
│   └── app.py             # Punto de entrada del servidor
├── frontend/              # Interfaz de usuario (HTML, CSS, JavaScript)
│   ├── index.html         # Login / Entrada principal
│   ├── pages/             # Vistas (dashboard, residuos, recursos, sst, epp)
│   ├── css/               # Hojas de estilo personalizadas (responsive, tema ecológico)
│   ├── js/                # Lógica del cliente, llamadas a la API (fetch), manejo de sesión
│   └── assets/            # Iconos, imágenes, manifest.json para PWA
├── docs/                  # Documentación del proyecto (001, 002, ...)
└── ecoSafe-Plant/         # Documento de requerimientos iniciales
```

## 3. Modelo de Datos Base (MySQL)

### Tabla `users`
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

### Tabla `audit_logs`
```sql
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity VARCHAR(50) NOT NULL,
    details TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 4. API Endpoints (Base y Autenticación en Python)
- `POST /api/auth/register`: Registro de usuario (hash con `bcrypt`).
- `POST /api/auth/login`: Validación de credenciales y retorno de token JWT.
- `GET /api/auth/me`: Verificación de sesión y datos del usuario actual.
- `GET /api/users`: Lista de usuarios (acceso solo ADMIN / SUPERVISOR).

## 5. Diseño y Frontend (HTML + CSS + JS)
- **HTML5 Semántico**: Estructura limpia y accesible.
- **CSS3 Responsive**: Flexbox/Grid con variables CSS para la paleta ecológica (`#1b4332`, `#2d6a4f`, `#40916c`, `#d8f3dc`).
- **JavaScript Modular**: Módulos ES6 o funciones nativas con `fetch` para consumir los endpoints en Python.
- **PWA Ready**: `manifest.json` y service worker básico para la funcionalidad "Agregar a pantalla de inicio" desde celular o tablet.

---

## ✅ Seguimiento de Tareas

> Marca cada tarea cuando esté completada. Actualiza la fecha entre paréntesis al finalizar.

### Preparación y Estructura
- [x] Crear estructura de carpetas `backend/` y `frontend/` (17/11/2026)
- [x] Crear `requirements.txt` con dependencias de Python (17/11/2026)
- [x] Crear `.env.example` y `.gitignore` (17/11/2026)

### Base de Datos MySQL
- [x] Crear script `backend/schema.sql` con tablas `users` y `audit_logs` (17/11/2026)
- [x] Crear script `backend/seed.sql` con usuario administrador por defecto (17/11/2026)
- [x] Crear `backend/init_db.py` para inicializar y verificar conexión a MySQL (17/11/2026)

### Backend Python — API y Auth
- [x] Crear `backend/database.py` para gestionar conexiones con PyMySQL (17/11/2026)
- [x] Crear `backend/utils/auth.py` con funciones de hash (bcrypt) y validación JWT (17/11/2026)
- [x] Crear decoradores `@login_required` y `@role_required` (17/11/2026)
- [x] Implementar `backend/routes/auth_routes.py` (login, register, me) (17/11/2026)
- [x] Configurar `backend/app.py` con CORS y prefijo `/api` (17/11/2026)

### Frontend — HTML, CSS y JavaScript
- [x] Crear `frontend/index.html` con pantalla de login responsiva (17/11/2026)
- [x] Crear `frontend/css/styles.css` con tema ecológico y diseño mobile-first (17/11/2026)
- [x] Crear `frontend/js/api.js` para peticiones fetch con JWT automático (17/11/2026)
- [x] Crear `frontend/js/auth.js` para manejo de sesión y redirección por rol (17/11/2026)
- [x] Crear `frontend/manifest.json` para soporte PWA (17/11/2026)
- [x] Crear `frontend/pages/dashboard.html` como página base protegida (17/11/2026)


---

## 🧪 Tests de Funcionalidad

> Ejecuta estas pruebas una vez que el módulo esté implementado para verificar que todo funciona según la especificación. Marca cada test cuando lo hayas validado.

### Backend (API Python)

- [ ] **TEST-001-B1**: `POST /api/auth/register` con datos válidos → retorna `201` y datos del usuario creado (sin `password_hash`).
- [ ] **TEST-001-B2**: `POST /api/auth/register` con email duplicado → retorna `409 Conflict`.
- [ ] **TEST-001-B3**: `POST /api/auth/login` con credenciales correctas → retorna `200` con un token JWT válido.
- [ ] **TEST-001-B4**: `POST /api/auth/login` con contraseña incorrecta → retorna `401 Unauthorized`.
- [ ] **TEST-001-B5**: `GET /api/auth/me` con token válido en el header `Authorization: Bearer <token>` → retorna `200` con datos del usuario.
- [ ] **TEST-001-B6**: `GET /api/auth/me` sin token → retorna `401 Unauthorized`.
- [ ] **TEST-001-B7**: `GET /api/users` con rol `OPERARIO` → retorna `403 Forbidden`.
- [ ] **TEST-001-B8**: `GET /api/users` con rol `ADMIN` → retorna `200` con lista de usuarios.

### Base de Datos MySQL

- [ ] **TEST-001-D1**: Ejecutar `schema.sql` desde cero en MySQL sin errores.
- [ ] **TEST-001-D2**: Ejecutar `seed.sql` y verificar que el usuario administrador por defecto existe en la tabla `users`.
- [ ] **TEST-001-D3**: Verificar que las claves foráneas de `audit_logs` → `users` funcionan (insertar log válido y verificar que rechaza un `user_id` inexistente).

### Frontend (HTML + CSS + JS)

- [ ] **TEST-001-F1**: Abrir `frontend/index.html` en el navegador → la pantalla de login se muestra correctamente en escritorio, tablet (768px) y móvil (375px).
- [ ] **TEST-001-F2**: Ingresar credenciales válidas → se redirige al dashboard y el token queda guardado en `localStorage`.
- [ ] **TEST-001-F3**: Ingresar credenciales incorrectas → se muestra un mensaje de error visible sin recargar la página.
- [ ] **TEST-001-F4**: Cerrar sesión (logout) → el token se elimina de `localStorage` y se redirige al login.
- [ ] **TEST-001-F5**: Acceder a una página protegida sin token (manualmente borrando `localStorage`) → redirige automáticamente al login.
- [ ] **TEST-001-F6**: Verificar que `manifest.json` es válido (abrir DevTools → Application → Manifest) y el botón "Agregar a pantalla de inicio" aparece en Chrome móvil.
