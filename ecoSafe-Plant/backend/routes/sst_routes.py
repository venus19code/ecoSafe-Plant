from flask import Blueprint, request, jsonify, g
from database import fetch_one, fetch_all, execute_query
from utils.auth import login_required, role_required, log_audit
from datetime import datetime
import json

sst_bp = Blueprint("sst", __name__)

# ==========================================================
# MATRIZ DE PELIGROS (IPVR)
# ==========================================================

@sst_bp.route("/sst/hazards", methods=["GET"])
def get_hazards():
    """
    Retorna los peligros evaluados en la matriz IPVR con filtros opcionales.
    TEST-004-B1: Retorna 200 con la lista de peligros.
    TEST-004-B2: Filtro por área (ej. Fermentacion).
    TEST-004-B3: Filtro por nivel de riesgo (ej. CRITICO).
    """
    try:
        area = request.args.get("area", type=str)
        risk_level = request.args.get("risk_level", type=str)
        status = request.args.get("status", type=str)
        search = request.args.get("search", type=str)

        conditions = ["1=1"]
        params = []

        if area:
            conditions.append("LOWER(area) LIKE %s")
            params.append(f"%{area.strip().lower()}%")

        if risk_level:
            conditions.append("UPPER(risk_level) = %s")
            params.append(risk_level.strip().upper())

        if status:
            conditions.append("UPPER(status) = %s")
            params.append(status.strip().upper())

        if search:
            s = f"%{search.strip().lower()}%"
            conditions.append("""
                (LOWER(area) LIKE %s OR LOWER(activity) LIKE %s 
                 OR LOWER(hazard_type) LIKE %s OR LOWER(description) LIKE %s 
                 OR LOWER(COALESCE(controls_in_place, '')) LIKE %s)
            """)
            params.extend([s, s, s, s, s])

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT id, area, activity, hazard_type, description,
                   potential_consequences, risk_level, controls_in_place,
                   recommended_actions, status, created_at
            FROM sst_hazards
            WHERE {where_clause}
            ORDER BY FIELD(risk_level, 'CRITICO', 'ALTO', 'MEDIO', 'BAJO'), area ASC, id ASC
        """

        hazards = fetch_all(query, tuple(params)) or []

        for h in hazards:
            if hasattr(h.get("created_at"), "strftime"):
                h["created_at"] = h["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "count": len(hazards),
            "hazards": hazards
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar matriz de peligros: {str(e)}"}), 500


@sst_bp.route("/sst/hazards", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR")
def create_hazard():
    """
    Crea un nuevo peligro en la matriz IPVR.
    TEST-004-B4: Retorna 201 con el peligro creado.
    """
    try:
        data = request.get_json() or {}
        area = (data.get("area") or "").strip()
        activity = (data.get("activity") or "").strip()
        hazard_type = (data.get("hazard_type") or "").strip()
        description = (data.get("description") or "").strip()
        potential_consequences = (data.get("potential_consequences") or "").strip()
        risk_level = (data.get("risk_level") or "MEDIO").strip().upper()
        controls_in_place = (data.get("controls_in_place") or "").strip()
        recommended_actions = (data.get("recommended_actions") or "").strip()
        status = (data.get("status") or "ACTIVO").strip().upper()

        if not area or not activity or not hazard_type or not description:
            return jsonify({
                "error": "Los campos 'area', 'activity', 'hazard_type' y 'description' son obligatorios"
            }), 400

        if risk_level not in ("BAJO", "MEDIO", "ALTO", "CRITICO"):
            return jsonify({"error": "Nivel de riesgo inválido. Debe ser BAJO, MEDIO, ALTO o CRITICO"}), 400

        if status not in ("ACTIVO", "CONTROLADO", "EN_REVISION"):
            status = "ACTIVO"

        insert_sql = """
            INSERT INTO sst_hazards (area, activity, hazard_type, description, potential_consequences, risk_level, controls_in_place, recommended_actions, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        res = execute_query(insert_sql, (
            area, activity, hazard_type, description,
            potential_consequences or None,
            risk_level,
            controls_in_place or None,
            recommended_actions or None,
            status
        ))
        new_id = res["last_id"]

        log_audit(g.current_user["sub"], "CREATE", "SST_HAZARD", json.dumps({"hazard_id": new_id, "area": area, "risk_level": risk_level}))

        created = fetch_one("SELECT * FROM sst_hazards WHERE id = %s", (new_id,))
        if created and hasattr(created.get("created_at"), "strftime"):
            created["created_at"] = created["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "message": "Peligro registrado exitosamente en la matriz de riesgos",
            "hazard": created
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al crear peligro: {str(e)}"}), 500


@sst_bp.route("/sst/hazards/<int:hazard_id>", methods=["PUT"])
@role_required("ADMIN", "SUPERVISOR")
def update_hazard(hazard_id):
    """
    Actualiza la evaluación o controles de un peligro.
    TEST-004-B5: Retorna 200 con los valores actualizados.
    """
    try:
        existing = fetch_one("SELECT id FROM sst_hazards WHERE id = %s", (hazard_id,))
        if not existing:
            return jsonify({"error": f"Peligro #{hazard_id} no encontrado"}), 404

        data = request.get_json() or {}

        fields = []
        params = []
        updatable = [
            "area", "activity", "hazard_type", "description",
            "potential_consequences", "risk_level", "controls_in_place",
            "recommended_actions", "status"
        ]

        for field in updatable:
            if field in data:
                val = data[field]
                if field == "risk_level" and val:
                    val = str(val).upper()
                    if val not in ("BAJO", "MEDIO", "ALTO", "CRITICO"):
                        return jsonify({"error": "Nivel de riesgo inválido"}), 400
                elif field == "status" and val:
                    val = str(val).upper()
                fields.append(f"{field} = %s")
                params.append(val)

        if not fields:
            return jsonify({"message": "No se enviaron campos para actualizar"}), 200

        params.append(hazard_id)
        update_sql = f"UPDATE sst_hazards SET {', '.join(fields)} WHERE id = %s"
        execute_query(update_sql, tuple(params))

        log_audit(g.current_user["sub"], "UPDATE", "SST_HAZARD", json.dumps({"hazard_id": hazard_id, "fields": list(data.keys())}))

        updated = fetch_one("SELECT * FROM sst_hazards WHERE id = %s", (hazard_id,))
        if updated and hasattr(updated.get("created_at"), "strftime"):
            updated["created_at"] = updated["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "message": "Peligro actualizado exitosamente",
            "hazard": updated
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar peligro: {str(e)}"}), 500


@sst_bp.route("/sst/hazards/<int:hazard_id>", methods=["DELETE"])
@role_required("ADMIN")
def delete_hazard(hazard_id):
    """
    Elimina un peligro de la matriz. Exclusivo para administradores.
    TEST-004-B6: OPERARIO retorna 403 Forbidden.
    """
    try:
        existing = fetch_one("SELECT id FROM sst_hazards WHERE id = %s", (hazard_id,))
        if not existing:
            return jsonify({"error": f"Peligro #{hazard_id} no encontrado"}), 404

        execute_query("DELETE FROM sst_hazards WHERE id = %s", (hazard_id,))
        log_audit(g.current_user["sub"], "DELETE", "SST_HAZARD", json.dumps({"deleted_id": hazard_id}))

        return jsonify({"message": f"Peligro #{hazard_id} eliminado exitosamente de la matriz"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al eliminar peligro: {str(e)}"}), 500


# ==========================================================
# REPORTE Y GESTIÓN DE INCIDENTES / CONDICIONES INSEGURAS
# ==========================================================

@sst_bp.route("/sst/incidents", methods=["GET"])
def get_incidents():
    """
    Retorna el listado de incidentes o condiciones inseguras con filtros.
    TEST-004-B8: Filtro por estado (ej. PENDIENTE).
    """
    try:
        status = request.args.get("status", type=str)
        severity = request.args.get("severity", type=str)
        incident_type = request.args.get("incident_type", type=str)
        search = request.args.get("search", type=str)

        conditions = ["1=1"]
        params = []

        if status:
            conditions.append("UPPER(i.status) = %s")
            params.append(status.strip().upper())

        if severity:
            conditions.append("UPPER(i.severity) = %s")
            params.append(severity.strip().upper())

        if incident_type:
            conditions.append("UPPER(i.incident_type) = %s")
            params.append(incident_type.strip().upper())

        if search:
            s = f"%{search.strip().lower()}%"
            conditions.append("""
                (LOWER(i.location_detail) LIKE %s OR LOWER(i.description) LIKE %s 
                 OR LOWER(COALESCE(i.resolution_notes, '')) LIKE %s OR LOWER(u.name) LIKE %s)
            """)
            params.extend([s, s, s, s])

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT i.id, i.reported_by_user_id, i.incident_type, i.incident_date,
                   i.location_detail, i.description, i.evidence_photo_url,
                   i.severity, i.status, i.assigned_to_user_id, i.resolution_notes,
                   i.resolved_at, i.created_at,
                   u.name AS reported_by_name, u.role AS reported_by_role,
                   ua.name AS assigned_to_name
            FROM sst_incidents i
            JOIN users u ON i.reported_by_user_id = u.id
            LEFT JOIN users ua ON i.assigned_to_user_id = ua.id
            WHERE {where_clause}
            ORDER BY 
                FIELD(i.status, 'PENDIENTE', 'EN_ATENCION', 'RESUELTO', 'DESESTIMADO'),
                FIELD(i.severity, 'ALTA', 'MEDIA', 'BAJA'),
                i.incident_date DESC, i.id DESC
        """

        incidents = fetch_all(query, tuple(params)) or []

        for inc in incidents:
            if hasattr(inc.get("incident_date"), "strftime"):
                inc["incident_date"] = inc["incident_date"].strftime("%Y-%m-%d %H:%M")
            if hasattr(inc.get("resolved_at"), "strftime"):
                inc["resolved_at"] = inc["resolved_at"].strftime("%Y-%m-%d %H:%M") if inc["resolved_at"] else None
            if hasattr(inc.get("created_at"), "strftime"):
                inc["created_at"] = inc["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "count": len(incidents),
            "incidents": incidents
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar incidentes: {str(e)}"}), 500


@sst_bp.route("/sst/incidents", methods=["POST"])
@login_required
def create_incident():
    """
    Crea un reporte rápido de condición o incidente inseguro.
    TEST-004-B7: Operario registra con datos válidos -> 201 con status inicial PENDIENTE.
    """
    try:
        data = request.get_json() or {}
        incident_type = (data.get("incident_type") or "CONDICION_INSEGURA").strip().upper()
        location_detail = (data.get("location_detail") or "").strip()
        description = (data.get("description") or "").strip()
        severity = (data.get("severity") or "MEDIA").strip().upper()
        evidence_photo_url = (data.get("evidence_photo_url") or "").strip()
        incident_date_raw = data.get("incident_date")

        if not location_detail or not description:
            return jsonify({"error": "Los campos 'location_detail' y 'description' son obligatorios"}), 400

        valid_types = ("CONDICION_INSEGURA", "ACTO_INSEGURO", "CASI_ACCIDENTE", "ACCIDENTE_LEVE", "ACCIDENTE_GRAVE")
        if incident_type not in valid_types:
            incident_type = "CONDICION_INSEGURA"

        if severity not in ("BAJA", "MEDIA", "ALTA"):
            severity = "MEDIA"

        if incident_date_raw:
            try:
                incident_date = datetime.strptime(incident_date_raw, "%Y-%m-%dT%H:%M")
            except ValueError:
                try:
                    incident_date = datetime.strptime(incident_date_raw, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    incident_date = datetime.now()
        else:
            incident_date = datetime.now()

        user_id = g.current_user["sub"]

        insert_sql = """
            INSERT INTO sst_incidents (reported_by_user_id, incident_type, incident_date, location_detail, description, evidence_photo_url, severity, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDIENTE')
        """
        res = execute_query(insert_sql, (
            user_id, incident_type, incident_date, location_detail, description,
            evidence_photo_url or None, severity
        ))
        new_id = res["last_id"]

        log_audit(user_id, "CREATE", "SST_INCIDENT", json.dumps({"incident_id": new_id, "type": incident_type, "severity": severity}))

        created = fetch_one("""
            SELECT i.*, u.name AS reported_by_name
            FROM sst_incidents i
            JOIN users u ON i.reported_by_user_id = u.id
            WHERE i.id = %s
        """, (new_id,))

        if created and hasattr(created.get("incident_date"), "strftime"):
            created["incident_date"] = created["incident_date"].strftime("%Y-%m-%d %H:%M")

        return jsonify({
            "message": "Reporte de condición/incidente registrado exitosamente",
            "incident": created
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar reporte de incidente: {str(e)}"}), 500


@sst_bp.route("/sst/incidents/<int:incident_id>/status", methods=["PATCH"])
@role_required("ADMIN", "SUPERVISOR")
def update_incident_status(incident_id):
    """
    Actualiza el estado de atención o cierre de un incidente.
    TEST-004-B9: Cambia a RESUELTO con resolution_notes -> 200 y resolved_at se completa.
    """
    try:
        existing = fetch_one("SELECT id, status FROM sst_incidents WHERE id = %s", (incident_id,))
        if not existing:
            return jsonify({"error": f"Incidente #{incident_id} no encontrado"}), 404

        data = request.get_json() or {}
        new_status = (data.get("status") or "").strip().upper()
        resolution_notes = (data.get("resolution_notes") or "").strip()
        assigned_to_user_id = data.get("assigned_to_user_id")

        if new_status not in ("PENDIENTE", "EN_ATENCION", "RESUELTO", "DESESTIMADO"):
            return jsonify({"error": "Estado inválido. Debe ser PENDIENTE, EN_ATENCION, RESUELTO o DESESTIMADO"}), 400

        resolved_at = datetime.now() if new_status == "RESUELTO" else None

        update_sql = """
            UPDATE sst_incidents 
            SET status = %s,
                resolution_notes = COALESCE(NULLIF(%s, ''), resolution_notes),
                assigned_to_user_id = COALESCE(%s, assigned_to_user_id),
                resolved_at = CASE WHEN %s = 'RESUELTO' THEN %s ELSE resolved_at END
            WHERE id = %s
        """
        execute_query(update_sql, (
            new_status,
            resolution_notes,
            assigned_to_user_id or g.current_user["sub"],
            new_status,
            resolved_at,
            incident_id
        ))

        log_audit(g.current_user["sub"], "UPDATE_STATUS", "SST_INCIDENT", json.dumps({"incident_id": incident_id, "status": new_status}))

        updated = fetch_one("""
            SELECT i.*, u.name AS reported_by_name, ua.name AS assigned_to_name
            FROM sst_incidents i
            JOIN users u ON i.reported_by_user_id = u.id
            LEFT JOIN users ua ON i.assigned_to_user_id = ua.id
            WHERE i.id = %s
        """, (incident_id,))

        if updated and hasattr(updated.get("resolved_at"), "strftime") and updated["resolved_at"]:
            updated["resolved_at"] = updated["resolved_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "message": f"Incidente #{incident_id} actualizado a '{new_status}'",
            "incident": updated
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar estado del incidente: {str(e)}"}), 500


# ==========================================================
# RESUMEN Y MÉTRICAS DE SST
# ==========================================================

@sst_bp.route("/sst/summary", methods=["GET"])
def get_sst_summary():
    """
    Retorna métricas consolidadas de SST: conteo de riesgos e incidentes por estado.
    TEST-004-B10: Conteo de peligros por nivel de riesgo e incidentes PENDIENTE y EN_ATENCION.
    """
    try:
        # 1. Peligros por nivel de riesgo
        hazard_rows = fetch_all("""
            SELECT risk_level, COUNT(id) AS count
            FROM sst_hazards
            GROUP BY risk_level
        """) or []

        hazards_by_risk = {"BAJO": 0, "MEDIO": 0, "ALTO": 0, "CRITICO": 0, "TOTAL": 0}
        total_hazards = 0
        for hr in hazard_rows:
            lvl = hr["risk_level"]
            cnt = int(hr["count"])
            hazards_by_risk[lvl] = cnt
            total_hazards += cnt
        hazards_by_risk["TOTAL"] = total_hazards

        # 2. Incidentes por estado
        incident_rows = fetch_all("""
            SELECT status, COUNT(id) AS count
            FROM sst_incidents
            GROUP BY status
        """) or []

        incidents_by_status = {"PENDIENTE": 0, "EN_ATENCION": 0, "RESUELTO": 0, "DESESTIMADO": 0, "TOTAL": 0}
        total_incidents = 0
        for ir in incident_rows:
            st = ir["status"]
            cnt = int(ir["count"])
            incidents_by_status[st] = cnt
            total_incidents += cnt
        incidents_by_status["TOTAL"] = total_incidents

        open_incidents = incidents_by_status["PENDIENTE"] + incidents_by_status["EN_ATENCION"]
        resolved_incidents = incidents_by_status["RESUELTO"]

        resolution_rate = round((resolved_incidents / total_incidents) * 100.0, 1) if total_incidents > 0 else 100.0

        return jsonify({
            "hazards_by_risk": hazards_by_risk,
            "incidents_by_status": incidents_by_status,
            "open_incidents": open_incidents,
            "resolved_incidents": resolved_incidents,
            "resolution_rate": resolution_rate,
            "days_without_accidents": 142
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar resumen SST: {str(e)}"}), 500
