import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from config import Config
from database import execute_query

def hash_password(password: str) -> str:
    """Genera un hash bcrypt seguro para la contraseña."""
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def create_token(user: dict) -> str:
    """Genera un token JWT con los datos básicos del usuario y tiempo de expiración."""
    payload = {
        "sub": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "area": user.get("area", ""),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    """Decodifica y valida un token JWT."""
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "El token ha expirado. Por favor inicia sesión nuevamente."}
    except jwt.InvalidTokenError:
        return {"error": "Token inválido o corrupto."}

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "No se proporcionó el token de autorización"}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Formato de token inválido. Use 'Bearer <token>'"}), 401

        token = parts[1]
        decoded = decode_token(token)
        if "error" in decoded:
            return jsonify({"error": decoded["error"]}), 401

        # Guardar datos del usuario autenticado en el contexto de Flask (g)
        g.current_user = decoded
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorador para verificar que el usuario tenga alguno de los roles permitidos."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_role = g.current_user.get("role")
            if user_role not in allowed_roles:
                return jsonify({
                    "error": f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}"
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_audit(user_id: int, action: str, entity: str, details: str = None):
    """Registra una acción en la tabla de auditoría."""
    try:
        query = """
            INSERT INTO audit_logs (user_id, action, entity, details)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(query, (user_id, action, entity, details))
    except Exception as e:
        print(f"[Advertencia Auditoría] No se pudo registrar el log: {e}")
