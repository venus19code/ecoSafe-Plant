# Ejecutar EcoSafe Plant con Docker

Stack local completo (sin instalar Python ni MySQL en el equipo):

| Servicio  | Imagen                | URL / puerto                                    |
|-----------|-----------------------|-------------------------------------------------|
| `backend` | Python 3.12 + Flask   | <http://localhost:5000> (API + frontend)         |
| `db`      | MySQL 8.0             | `localhost:3307` (solo para clientes externos)   |
| `adminer` | Adminer 4             | <http://localhost:8080> (visor de la BD)         |

La base de datos se guarda en el volumen `ecosafe_mysql_data`.

---

## 1. Requisitos

- Docker Desktop con el motor Linux activo (`docker info` debe responder).
- Puertos libres: `5000`, `8080` y `3307` (o cámbialos en `.env`).

---

## 2. Primer arranque

Desde la carpeta `pagina_web/ecoSafe-Plant` (donde está `docker-compose.yml`):

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

La primera vez, el backend crea las tablas y carga los datos de demostración
(`AUTO_INIT_DB=true`) cuando detecta la base vacía. Puedes seguirlo con:

```powershell
docker compose logs -f backend
```

Cuando termine verás `¡INICIALIZACIÓN COMPLETADA CON ÉXITO!`.

### URLs

- Aplicación: <http://localhost:5000>
- Health check: <http://localhost:5000/api/health>
- Adminer: <http://localhost:8080>

### Usuarios de prueba

| Correo                      | Contraseña        | Rol        |
|-----------------------------|-------------------|------------|
| `admin@ecosafe.com`         | `Admin123*`       | ADMIN      |
| `supervisor@ecosafe.com`    | `Supervisor123*`  | SUPERVISOR |
| `operario@ecosafe.com`      | `Operario123*`    | OPERARIO   |

---

## 3. Revisar la base de datos

### Opción A: Adminer (navegador)

1. Abre <http://localhost:8080>.
2. Inicia sesión con:
   - **Sistema**: MySQL / MariaDB
   - **Servidor**: `db`
   - **Usuario**: `ecosafe`
   - **Contraseña**: `ecosafe123`
   - **Base de datos**: `ecosafe_db`
3. Ahí puedes ver tablas, filas y ejecutar SQL.

> El usuario `root` / `rootpass` también existe dentro del contenedor, pero
> la aplicación usa el usuario limitado `ecosafe`.

### Opción B: línea de comandos (dentro del contenedor)

```powershell
docker compose exec db mysql -uecosafe -pecosafe123 -D ecosafe_db -e "SHOW TABLES; SELECT id,email,role FROM users;"
```

### Opción C: cliente MySQL desde tu PC

- Host: `127.0.0.1`
- Puerto: `3307`
- Usuario: `ecosafe`
- Contraseña: `ecosafe123`
- Base de datos: `ecosafe_db`

(Si el 3307 choca con otro servicio, cambia `MYSQL_PORT` en `.env`.)

---

## 4. Comandos útiles

```powershell
# Estado de los contenedores
docker compose ps

# Logs en vivo
docker compose logs -f
docker compose logs -f backend

# Detener sin borrar datos
docker compose down

# Reconstruir el backend tras cambiar código
docker compose up -d --build backend

# Reiniciar todo
docker compose restart

# Ejecutar la suite completa de tests dentro del contenedor
# (usa la BD real del stack)
docker compose exec backend python -m unittest discover -p "test_*.py" -v

# Volver a ejecutar la inicialización/semillas manualmente
docker compose exec backend python init_db.py
```

### Borrar todo y empezar de cero

```powershell
docker compose down -v
docker compose up -d --build
```

`-v` elimina el volumen `ecosafe_mysql_data`; sin `-v` los datos se conservan.

---

## 5. Variables de entorno

Se configuran en `.env` (copia de `.env.example`):

| Variable        | Por defecto    | Descripción                                        |
|-----------------|----------------|----------------------------------------------------|
| `MYSQL_ROOT_PASSWORD` | `rootpass` | Clave del root del contenedor MySQL                |
| `DB_USER`       | `ecosafe`      | Usuario que usa el backend                         |
| `DB_PASSWORD`   | `ecosafe123`   | Clave de ese usuario                               |
| `DB_NAME`       | `ecosafe_db`   | Nombre de la base                                  |
| `MYSQL_PORT`    | `3307`         | Puerto del host para MySQL                         |
| `BACKEND_PORT`  | `5000`         | Puerto del host para la aplicación                 |
| `ADMINER_PORT`  | `8080`         | Puerto del host para Adminer                       |
| `SECRET_KEY`    | valor demo     | Clave para firmar los JWT (cámbiala en producción) |
| `AUTO_INIT_DB`  | `true`         | Crear tablas y semillas si la BD está vacía        |

---

## 6. Notas

- `schema.sql` y `seed.sql` usan el nombre histórico `ecoSafe_db`; `init_db.py`
  ignora esas sentencias `CREATE DATABASE`/`USE` y trabaja contra `DB_NAME`
  (en Linux los nombres de base de datos distinguen mayúsculas).
- El backend sirve también el frontend, por eso la imagen copia `backend/` y
  `frontend/`.
- `docker compose down` conserva los datos; `docker compose down -v` los borra.
- La suite completa (35 tests) pasa dentro del contenedor; los endpoints del
  dashboard requieren JWT, igual que el resto de operaciones de escritura.
