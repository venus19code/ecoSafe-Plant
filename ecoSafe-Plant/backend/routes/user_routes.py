from flask import Blueprint, request, jsonify, g
from database import fetch_one, fetch_all, execute_query
from utils.auth import role_required, log_audit, hash_password
import json

user_bp = Blueprint("users", __name__)

VALID_ROLES = ("ADMIN", "SUPERVISOR", "OPERARIO")
MIN_PASSWORD_LENGTH = 8


# ==========================================================
# HELPERS
# ==========================================================

def _serialize_user(user):
    """Convierte un registro de users en un diccionario seguro (sin password_hash)."""
    if not user:
        return None
    created = user.get("created_at")
    if hasattr(created, "strftime"):
        created = created.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "area": user["area"],
        "is_active": bool(user["is_active"]),
        "created_at": created,
    }


def _count_other_active_admins(exclude_id):
    """Cuenta los ADMIN activos distintos del usuario indicado."""
    row = fetch_one(
        "SELECT COUNT(*) AS total FROM users WHERE role = 'ADMIN' AND is_active = TRUE AND id <> %s",
        (exclude_id,),
    )
    return int(row["total"]) if row else 0


# ==========================================================
# RESUMEN Y LISTADO
# ==========================================================

@user_bp.route("/users/stats", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR")
def user_stats():
    """
    Retorna el resumen de usuarios: total, activos, inactivos y conteo por rol.
    TEST-007-B14
    """
    try:
        rows = fetch_all(
            "SELECT role, is_active, COUNT(*) AS total FROM users GROUP BY role, is_active"
        ) or []

        total = 0
        active = 0
        by_role = {"ADMIN": 0, "SUPERVISOR": 0, "OPERARIO": 0}
        for row in rows:
            count = int(row["total"])
            total += count
            if bool(row["is_active"]):
                active += count
            role = row["role"]
            if role in by_role:
                by_role[role] += count

        return jsonify({
            "total": total,
            "active": active,
            "inactive": total - active,
            "by_role": by_role,
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar el resumen de usuarios: {str(e)}"}), 500


@user_bp.route("/users", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR")
def list_users():
    """
    Lista los usuarios del sistema.
    Filtros opcionales: q (nombre/correo/área), role, active.
    TEST-007-B1, TEST-007-B2, TEST-007-B3
    """
    try:
        q = request.args.get("q", type=str)
        role = request.args.get("role", type=str)
        active = request.args.get("active", type=str)

        conditions = []
        params = []

        if q:
            like = f"%{q.strip().lower()}%"
            conditions.append("(LOWER(name) LIKE %s OR LOWER(email) LIKE %s OR LOWER(area) LIKE %s)")
            params.extend([like, like, like])

        if role:
            role_clean = role.strip().upper()
            if role_clean in VALID_ROLES:
                conditions.append("role = %s")
                params.append(role_clean)

        if active is not None and active.strip().lower() in ("true", "false"):
            conditions.append("is_active = %s")
            params.append(active.strip().lower() == "true")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        users = fetch_all(
            f"""
            SELECT id, name, email, role, area, is_active, created_at
            FROM users
            {where_clause}
            ORDER BY role ASC, name ASC
            """,
            tuple(params),
        ) or []

        serialized = [_serialize_user(u) for u in users]

        return jsonify({
            "count": len(serialized),
            "users": serialized,
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar usuarios: {str(e)}"}), 500


@user_bp.route("/users/<int:user_id>", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR")
def get_user(user_id):
    """Retorna el detalle de un usuario. TEST-007-B1."""
    try:
        user = fetch_one(
            "SELECT id, name, email, role, area, is_active, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        if not user:
            return jsonify({"error": f"El usuario con ID {user_id} no existe"}), 404

        return jsonify({"user": _serialize_user(user)}), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar el usuario: {str(e)}"}), 500


# ==========================================================
# CREACIÓN
# ==========================================================

@user_bp.route("/users", methods=["POST"])
@role_required("ADMIN")
def create_user():
    """
    Crea un nuevo usuario. Solo ADMIN.
    TEST-007-B4, TEST-007-B5, TEST-007-B6
    """
    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        role = (data.get("role") or "OPERARIO").strip().upper()
        area = (data.get("area") or "").strip()

        if not name or not email or not password or not area:
            return jsonify({
                "error": "Los campos nombre, correo, contraseña y área son obligatorios"
            }), 400

        if role not in VALID_ROLES:
            return jsonify({"error": "Rol inválido. Debe ser ADMIN, SUPERVISOR u OPERARIO"}), 400

        if len(password) < MIN_PASSWORD_LENGTH:
            return jsonify({
                "error": f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
            }), 400

        if fetch_one("SELECT id FROM users WHERE email = %s", (email,)):
            return jsonify({"error": "El correo electrónico ya se encuentra registrado"}), 409

        hashed = hash_password(password)
        result = execute_query(
            """
            INSERT INTO users (name, email, password_hash, role, area, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            """,
            (name, email, hashed, role, area),
        )
        new_id = result["last_id"]

        log_audit(
            g.current_user["sub"],
            "USER_CREATE",
            "USER",
            json.dumps({"user_id": new_id, "email": email, "role": role, "area": area}),
        )

        created = fetch_one(
            "SELECT id, name, email, role, area, is_active, created_at FROM users WHERE id = %s",
            (new_id,),
        )
        return jsonify({
            "message": "Usuario creado exitosamente",
            "user": _serialize_user(created),
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al crear el usuario: {str(e)}"}), 500


# ==========================================================
# EDICIÓN
# ==========================================================

@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@role_required("ADMIN")
def update_user(user_id):
    """Actualiza nombre, correo, rol y área de un usuario. TEST-007-B7."""
    try:
        existing = fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        if not existing:
            return jsonify({"error": f"El usuario con ID {user_id} no existe"}), 404

        data = request.get_json() or {}

        name = (data.get("name", existing["name"]) or "").strip()
        email = (data.get("email", existing["email"]) or "").strip().lower()
        role = (data.get("role", existing["role"]) or "").strip().upper()
        area = (data.get("area", existing["area"]) or "").strip()

        if not name or not email or not area:
            return jsonify({"error": "Nombre, correo y área no pueden quedar vacíos"}), 400

        if role not in VALID_ROLES:
            return jsonify({"error": "Rol inválido. Debe ser ADMIN, SUPERVISOR u OPERARIO"}), 400

        duplicate = fetch_one(
            "SELECT id FROM users WHERE email = %s AND id <> %s", (email, user_id)
        )
        if duplicate:
            return jsonify({"error": "El correo electrónico ya está en uso por otro usuario"}), 409

        # No degradar al último ADMIN activo
        if existing["role"] == "ADMIN" and role != "ADMIN" and bool(existing["is_active"]):
            if _count_other_active_admins(user_id) == 0:
                return jsonify({
                    "error": "No se puede cambiar el rol del último administrador activo"
                }), 400

        execute_query(
            "UPDATE users SET name = %s, email = %s, role = %s, area = %s WHERE id = %s",
            (name, email, role, area, user_id),
        )

        log_audit(
            g.current_user["sub"],
            "USER_UPDATE",
            "USER",
            json.dumps({"user_id": user_id, "email": email, "role": role, "area": area}),
        )

        updated = fetch_one(
            "SELECT id, name, email, role, area, is_active, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        return jsonify({
            "message": "Usuario actualizado correctamente",
            "user": _serialize_user(updated),
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar el usuario: {str(e)}"}), 500


# ==========================================================
# ESTADO (ACTIVAR / DESACTIVAR)
# ==========================================================

@user_bp.route("/users/<int:user_id>/status", methods=["PATCH"])
@role_required("ADMIN")
def set_user_status(user_id):
    """
    Activa o desactiva un usuario (borrado lógico).
    TEST-007-B8, TEST-007-B9, TEST-007-B10
    """
    try:
        existing = fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        if not existing:
            return jsonify({"error": f"El usuario con ID {user_id} no existe"}), 404

        data = request.get_json() or {}
        if "is_active" not in data:
            return jsonify({"error": "Debe indicar el campo 'is_active'"}), 400

        new_status = bool(data.get("is_active"))
        current_id = int(g.current_user["sub"])

        if user_id == current_id and not new_status:
            return jsonify({"error": "No puedes desactivar tu propia cuenta"}), 400

        if (
            not new_status
            and existing["role"] == "ADMIN"
            and bool(existing["is_active"])
            and _count_other_active_admins(user_id) == 0
        ):
            return jsonify({
                "error": "Debe existir al menos un administrador activo en el sistema"
            }), 400

        execute_query("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id))

        log_audit(
            current_id,
            "USER_STATUS",
            "USER",
            json.dumps({"user_id": user_id, "is_active": new_status}),
        )

        updated = fetch_one(
            "SELECT id, name, email, role, area, is_active, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        return jsonify({
            "message": "Usuario activado correctamente" if new_status else "Usuario desactivado correctamente",
            "user": _serialize_user(updated),
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al cambiar el estado del usuario: {str(e)}"}), 500


# ==========================================================
# RESTABLECER CONTRASEÑA
# ==========================================================

@user_bp.route("/users/<int:user_id>/password", methods=["PATCH"])
@role_required("ADMIN")
def reset_user_password(user_id):
    """Restablece la contraseña de un usuario. TEST-007-B11."""
    try:
        existing = fetch_one("SELECT id, email FROM users WHERE id = %s", (user_id,))
        if not existing:
            return jsonify({"error": f"El usuario con ID {user_id} no existe"}), 404

        data = request.get_json() or {}
        new_password = data.get("new_password") or data.get("password") or ""

        if len(new_password) < MIN_PASSWORD_LENGTH:
            return jsonify({
                "error": f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
            }), 400

        hashed = hash_password(new_password)
        execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))

        log_audit(
            g.current_user["sub"],
            "USER_PASSWORD_RESET",
            "USER",
            json.dumps({"user_id": user_id, "email": existing["email"]}),
        )

        return jsonify({"message": "Contraseña actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al restablecer la contraseña: {str(e)}"}), 500
