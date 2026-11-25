from flask import Blueprint, request, jsonify, g
from database import fetch_one, fetch_all, execute_query
from utils.auth import hash_password, check_password, create_token, login_required, role_required, log_audit
import json

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    """
    Registra un nuevo usuario en el sistema.
    Espera JSON: { name, email, password, role, area }
    """
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "OPERARIO").upper()
    area = (data.get("area") or "").strip()

    # Validaciones básicas
    if not name or not email or not password or not area:
        return jsonify({"error": "Todos los campos (nombre, correo, contraseña y área) son obligatorios"}), 400

    if role not in ("ADMIN", "SUPERVISOR", "OPERARIO"):
        return jsonify({"error": "Rol inválido. Debe ser ADMIN, SUPERVISOR u OPERARIO"}), 400

    # Verificar si el correo ya existe
    existing_user = fetch_one("SELECT id FROM users WHERE email = %s", (email,))
    if existing_user:
        return jsonify({"error": "El correo electrónico ya se encuentra registrado"}), 409

    # Generar hash seguro de la contraseña
    hashed = hash_password(password)

    # Insertar en base de datos
    insert_query = """
        INSERT INTO users (name, email, password_hash, role, area, is_active)
        VALUES (%s, %s, %s, %s, %s, TRUE)
    """
    result = execute_query(insert_query, (name, email, hashed, role, area))
    new_user_id = result["last_id"]

    # Registrar en auditoría
    log_audit(new_user_id, "REGISTER", "USER", json.dumps({"email": email, "role": role, "area": area}))

    return jsonify({
        "message": "Usuario registrado exitosamente",
        "user": {
            "id": new_user_id,
            "name": name,
            "email": email,
            "role": role,
            "area": area,
            "is_active": True
        }
    }), 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    Inicia sesión validando credenciales y retorna un token JWT.
    Espera JSON: { email, password }
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Debe proporcionar correo y contraseña"}), 400

    user = fetch_one("SELECT * FROM users WHERE email = %s", (email,))
    if not user:
        return jsonify({"error": "Credenciales inválidas"}), 401

    if not user["is_active"]:
        return jsonify({"error": "Este usuario ha sido desactivado. Contacte al administrador"}), 403

    if not check_password(password, user["password_hash"]):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Generar token JWT
    token = create_token(user)

    # Registrar login en auditoría
    log_audit(user["id"], "LOGIN", "AUTH", json.dumps({"email": email, "ip": request.remote_addr}))

    return jsonify({
        "message": "Inicio de sesión exitoso",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "area": user["area"]
        }
    }), 200

@auth_bp.route("/auth/me", methods=["GET"])
@login_required
def get_current_user_profile():
    """Retorna la información del usuario autenticado actual."""
    user_id = g.current_user["sub"]
    user = fetch_one("SELECT id, name, email, role, area, is_active, created_at FROM users WHERE id = %s", (user_id,))
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"user": user}), 200

@auth_bp.route("/health", methods=["GET"])
def health_check():
    """Verifica el estado del servicio y la conexión a MySQL."""
    db_status = "ok"
    try:
        test = fetch_one("SELECT 1 as test")
        if not test or test["test"] != 1:
            db_status = "error_query"
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    return jsonify({
        "status": "online",
        "service": "EcoSafe Plant API",
        "version": "1.0.0 (Spec 001)",
        "database": db_status
    }), 200
