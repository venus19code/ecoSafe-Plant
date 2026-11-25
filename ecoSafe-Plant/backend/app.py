import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from routes.auth_routes import auth_bp
from routes.waste_routes import waste_bp
from routes.utility_routes import utility_bp
from routes.sst_routes import sst_bp
from routes.epp_routes import epp_bp
from routes.dashboard_routes import dashboard_bp
from routes.user_routes import user_bp

# Rutas base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR)
app.config.from_object(Config)

# Habilitar CORS para permitir llamadas desde el frontend independiente (Live Server / navegador)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Registrar Blueprints de API
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(waste_bp, url_prefix="/api")
app.register_blueprint(utility_bp, url_prefix="/api")
app.register_blueprint(sst_bp, url_prefix="/api")
app.register_blueprint(epp_bp, url_prefix="/api")
app.register_blueprint(dashboard_bp, url_prefix="/api")
app.register_blueprint(user_bp, url_prefix="/api")

# ==========================================================
# ENDPOINT DE SALUD (para plataformas de despliegue)
# ==========================================================

@app.route("/api/health")
def health():
    """Verificación rápida de que el servicio está en línea."""
    return jsonify({"status": "ok", "service": "ecosafe-plant"})

# ==========================================================
# INICIALIZACIÓN AUTOMÁTICA DE BASE DE DATOS (NUBE)
# ==========================================================

def _needs_db_init():
    """Indica si la base de datos aún no tiene usuarios (primera puesta en marcha)."""
    from database import fetch_one
    try:
        row = fetch_one("SELECT COUNT(*) AS total FROM users")
        return not row or row.get("total", 0) == 0
    except Exception:
        return True

if Config.AUTO_INIT_DB and _needs_db_init():
    try:
        from init_db import run_init_db
        run_init_db()
    except Exception as e:
        print(f"[Aviso] No se pudo inicializar la base de datos automáticamente: {e}")

# ==========================================================
# RUTAS PARA SERVIR EL FRONTEND (ARQUITECTURA MONOLITO)
# ==========================================================

@app.route("/")
def index():
    """Sirve la página principal de inicio de sesión."""
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    """Sirve archivos estáticos (CSS, JS, imágenes, páginas)."""
    full_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, path)
    elif os.path.exists(os.path.join(FRONTEND_DIR, f"{path}.html")):
        return send_from_directory(FRONTEND_DIR, f"{path}.html")
    else:
        # Si no se encuentra, retornar el index
        return send_from_directory(FRONTEND_DIR, "index.html")

# Manejo de errores globales
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    print(f"Iniciando servidor EcoSafe Plant en http://localhost:{Config.PORT}")
    print(f"Sirviendo Frontend desde: {FRONTEND_DIR}")
    print(f"API endpoints disponibles en: http://localhost:{Config.PORT}/api")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
