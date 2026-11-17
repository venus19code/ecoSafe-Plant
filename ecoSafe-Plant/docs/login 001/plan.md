# Plan de Implementación - 001: Arquitectura Base y Autenticación

## 1. Objetivo de la Fase
Establecer la estructura monorepo del proyecto con `backend/` en **Python**, `frontend/` en **HTML/CSS/JS** y base de datos relacional en **MySQL**.

## 2. Definición del Stack Tecnológico
- **Lenguaje Backend**: Python 3.
  - Framework recomendado: **Flask** (o FastAPI). Flask es ligero, directo y se integra naturalmente con frontend estático de HTML/CSS/JS mediante templates o API REST pura.
  - Conector MySQL: `PyMySQL` o `mysql-connector-python` con `SQLAlchemy` (opcional) para consultas limpias y seguras contra inyección SQL.
  - Autenticación: `PyJWT` para tokens de sesión y `bcrypt` para hash seguro de contraseñas.
- **Frontend**: HTML5, CSS3 y JavaScript nativo (Vanilla JS).
  - Sin dependencias de compiladores externos pesados como Node/Webpack; carga directa y rápida en navegadores de PC, tablets y móviles.
  - Componentes visuales reutilizables (Sidebar, Topbar, Modales, Tablas y Formularios).
- **Base de Datos**: MySQL 8.x / MariaDB.
  - Scripts `schema.sql` reproducibles para crear la base de datos `ecosafe_db`.
  - Script `seed.sql` para poblar el usuario administrador inicial.

## 3. Fases de Ejecución

### Fase 1: Entorno y Repositorio Base
- Crear las carpetas `backend/` y `frontend/`.
- Preparar entorno virtual de Python (`venv`) y archivo `requirements.txt`.
- Configurar archivo de variables de entorno `.env` para credenciales de MySQL (host, port, user, password, database).

### Fase 2: Esquema de Base de Datos MySQL
- Diseñar y redactar `schema.sql` con la definición de tablas iniciales (`users`, `audit_logs`).
- Redactar `seed.sql` con el usuario administrador por defecto (`admin@ecosafe.com`).
- Crear script en Python `init_db.py` para inicializar y verificar la conexión a MySQL de forma automatizada.

### Fase 3: Backend - API de Autenticación
- Crear módulo `database.py` con pool de conexiones a MySQL.
- Implementar decorador `@login_required` y `@role_required(['ADMIN', 'SUPERVISOR'])`.
- Implementar endpoints `/api/auth/login`, `/api/auth/register`, `/api/auth/me`.

### Fase 4: Frontend - Shell de la Aplicación
- Crear estructura en `frontend/` con `index.html` (pantalla de inicio de sesión).
- Crear `frontend/css/styles.css` con sistema de variables, diseño responsive y paleta ecológica de EcoSafe.
- Crear `frontend/js/api.js` (cliente HTTP con `fetch` y almacenamiento de token en `localStorage`).
- Crear `frontend/pages/layout.html` o plantilla base para el menú lateral (Sidebar) y barra superior de navegación.
- Añadir `manifest.json` para soporte de instalación como PWA en celulares.
