# Despliegue del prototipo (Netlify + Render + Railway)

Arquitectura elegida para la demostración:

```
Navegador
   │
   ├── Frontend estático  →  Netlify        (ecoSafe-Plant/frontend)
   │        └── llamadas /api/*  →  Render  (ecoSafe-Plant/backend)
   │                                     └── MySQL  →  Railway
```

- **Netlify**: solo sirve los archivos HTML, CSS y JS. No ejecuta Python.
- **Render**: ejecuta Flask con gunicorn y atiende `/api/*` (plan gratuito).
- **Railway**: tu MySQL actual (se mantiene intacto).

> Es una demo: no hay datos sensibles ni configuración de alta disponibilidad.

---

## 0. Requisito previo: repositorio en GitHub

El repositorio debe estar subido a GitHub porque Netlify y Render despliegan desde ahí.

```powershell
cd C:\Users\joenu\OneDrive\Documentos\Trabajo_Dani\pagina_web
git add .
git commit -m "Configuracion de despliegue"
git push
```

---

## 1. Railway: obtener los datos públicos de MySQL

Railway entrega dos tipos de conexión:

| Tipo | Host | Cuándo usarla |
|---|---|---|
| Privada (interna) | `*.railway.internal` | Solo desde servicios **dentro** de Railway |
| Pública (TCP Proxy) | `*.proxy.rlwy.net` o similar | Desde Render, tu PC o cualquier servidor externo |

Como el backend va en Render, necesitas la **pública**:

1. Entra al proyecto en Railway → servicio **MySQL**.
2. Pestaña **Settings → Networking → Public Networking** → **Generate Domain** (TCP Proxy).
3. Copia estos datos (están en la pestaña **Variables** del servicio MySQL):
   - `MYSQL_HOST` / `MYSQLPORT` / `MYSQLUSER` / `MYSQLPASSWORD` / `MYSQLDATABASE`
   - O la variable `MYSQL_PUBLIC_URL` completa (`mysql://usuario:clave@host:puerto/basededatos`).

> Si el host empieza por `mysql.railway.internal`, **no** funcionará desde Render.
> Si ya tienes las tablas y los datos cargados, no tienes que hacer nada más con la base.

---

## 2. Render: desplegar el backend Flask

1. Crea una cuenta en <https://render.com> y conecta tu GitHub.
2. **New → Web Service** → selecciona el repositorio.
3. Configura:

   | Campo | Valor |
   |---|---|
   | Name | `ecosafe-plant-api` |
   | Root Directory | `ecoSafe-Plant/backend` |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120` |
   | Instance Type | `Free` |

   > También puedes usar **New → Blueprint** y Render leerá el archivo `render.yaml`
   > que ya está en la raíz del repositorio.

4. En **Environment Variables** agrega:

   | Variable | Valor |
   |---|---|
   | `PYTHON_VERSION` | `3.12.6` |
   | `DEBUG` | `false` |
   | `SECRET_KEY` | una cadena larga y aleatoria |
   | `DB_HOST` | host público de Railway |
   | `DB_PORT` | puerto público de Railway |
   | `DB_USER` | usuario de Railway |
   | `DB_PASSWORD` | contraseña de Railway |
   | `DB_NAME` | base de datos de Railway |
   | `AUTO_INIT_DB` | `true` |
   | `DB_SSL` | `false` (cámbialo a `true` si la conexión falla por SSL) |

   Alternativa: en vez de las 5 variables `DB_*`, usa una sola:
   `DATABASE_URL = mysql://usuario:clave@host:puerto/basededatos`

5. Deploy. Cuando termine, comprueba:

   ```
   https://TU-BACKEND.onrender.com/api/health
   → {"status": "ok", "service": "ecosafe-plant"}
   ```

6. Prueba el login real:

   ```powershell
   curl.exe -X POST https://TU-BACKEND.onrender.com/api/auth/login `
     -H "Content-Type: application/json" `
     -d '{\"email\":\"admin@ecosafe.com\",\"password\":\"Admin123*\"}'
   ```

   Debe devolver un `token` JWT.

---

## 3. Netlify: desplegar el frontend

1. Crea una cuenta en <https://app.netlify.com> y conecta el mismo repositorio.
2. **Add new site → Import an existing project → GitHub** → elige el repositorio.
3. Configura:

   | Campo | Valor |
   |---|---|
   | Base directory | *(vacío)* |
   | Build command | *(vacío)* |
   | Publish directory | `ecoSafe-Plant/frontend` |

   El archivo `netlify.toml` de la raíz ya contiene estos valores, así que Netlify
   los detecta solo.

4. **Site configuration → Environment variables** → agrega:

   | Variable | Valor |
   |---|---|
   | `ECOSAFE_API_URL` | `https://TU-BACKEND.onrender.com/api` |

   El `build command` del `netlify.toml` escribe esa URL en `frontend/js/config.js`.

   > Si prefieres no usar variables, edita `ecoSafe-Plant/frontend/js/config.js`:
   > ```js
   > window.ECOSAFE_API_URL = "https://TU-BACKEND.onrender.com/api";
   > ```
   > y haz commit + push. No pongas `/` al final.

5. Deploy. La URL queda como `https://algo.netlify.app`.

6. Abre la URL y prueba con las cuentas de demostración:

   | Rol | Correo | Contraseña |
   |---|---|---|
   | Admin | `admin@ecosafe.com` | `Admin123*` |
   | Supervisor | `supervisor@ecosafe.com` | `Supervisor123*` |
   | Operario | `operario@ecosafe.com` | `Operario123*` |

---

## 4. Cómo funciona internamente

- `frontend/js/config.js` define `window.ECOSAFE_API_URL`.
- `frontend/js/api.js` usa ese valor; si está vacío usa `/api` del mismo origen
  (modo monolito con Flask).
- El backend permite CORS desde cualquier origen en `/api/*`, por eso Netlify puede
  llamar a Render.
- `backend/app.py` expone `/api/health` y, con `AUTO_INIT_DB=true`, crea las tablas y
  los datos de demostración **solo si la base está vacía**.
- `backend/Procfile` y `backend/.python-version` definen el arranque con gunicorn.

---

## 5. Alternativas de hosting para el backend

| Plataforma | Ventaja | Nota |
|---|---|---|
| **Render** (recomendado) | Gratis, despliegue automático desde GitHub | Se suspende tras ~15 min sin uso; el primer acceso tarda ~50 s |
| **Railway** | Todo en el mismo proyecto que MySQL | Requiere plan de pago (~5 USD/mes) tras el crédito inicial |
| **PythonAnywhere** | Gratis e incluye MySQL | Despliegue manual (subir archivos y recargar la web app) |
| **Koyeb / Fly.io** | Contenedores gratuitos | Necesitan Dockerfile o buildpack; más pasos |

Si prefieres **una sola plataforma**, mueve el backend a Railway: mismo repositorio,
Root Directory `ecoSafe-Plant/backend`, y usa las variables internas de MySQL
(`MYSQLHOST`, `MYSQLPORT`, ...). En ese caso `DB_SSL=false`.

---

## 6. Problemas frecuentes

| Síntoma | Causa / solución |
|---|---|
| La página de Netlify carga pero el login dice "No se pudo conectar" | `ECOSAFE_API_URL` mal configurada o sin `/api` al final. Revisa `js/config.js` en el sitio publicado. |
| Error CORS en la consola | El backend no está respondiendo; verifica `/api/health` en la URL de Render. Flask-CORS ya permite cualquier origen. |
| `Can't connect to MySQL server` | Usaste el host interno de Railway (`*.railway.internal`). Usa el host público (TCP Proxy). |
| `SSL connection is required` | Agrega `DB_SSL=true` y vuelve a desplegar. |
| `Access denied for user` | Usuario/contraseña incorrectos, o `DB_NAME` no coincide. |
| `bcrypt` o `cryptography` fallan al instalar | Confirma `PYTHON_VERSION=3.12.6`. |
| Primera carga muy lenta | El plan gratuito de Render "duerme" el servicio. Es normal en una demo. |
| Se ven los estilos pero no los datos | El token expiró: cierra sesión y vuelve a entrar. |
| `404` en `assets/icon-192.png` | El manifest PWA referencia iconos que no existen; no afecta la demo. |
