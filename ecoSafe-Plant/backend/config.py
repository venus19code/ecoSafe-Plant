import os
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()


def _db_from_url():
    """
    Permite configurar la base de datos con una sola variable (DATABASE_URL o MYSQL_URL),
    formato: mysql://usuario:clave@host:3306/nombre_bd
    Útil en plataformas como Railway, Heroku o Clever Cloud que entregan esa URL.
    """
    url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or ""
    if not url:
        return {}
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "",
        "port": parsed.port or 3306,
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "name": (parsed.path or "").lstrip("/") or "ecosafe_db",
    }


_DB_URL = _db_from_url()


class Config:
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "ecosafe_secret_jwt_key_super_segura_2026")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

    # Configuración de MySQL
    DB_HOST = os.getenv("DB_HOST") or _DB_URL.get("host") or "localhost"
    DB_PORT = int(os.getenv("DB_PORT") or _DB_URL.get("port") or 3306)
    DB_USER = os.getenv("DB_USER") or _DB_URL.get("user") or "root"
    DB_PASSWORD = os.getenv("DB_PASSWORD") or _DB_URL.get("password") or ""
    DB_NAME = os.getenv("DB_NAME") or _DB_URL.get("name") or "ecosafe_db"

    # SSL para MySQL en la nube (obligatorio en Aiven, TiDB Cloud, PlanetScale, etc.)
    DB_SSL = os.getenv("DB_SSL", "false").lower() in ("true", "1", "yes")
    DB_SSL_CA = os.getenv("DB_SSL_CA", "")

    # Crear tablas y cargar datos de demostración automáticamente al arrancar
    AUTO_INIT_DB = os.getenv("AUTO_INIT_DB", "false").lower() in ("true", "1", "yes")
