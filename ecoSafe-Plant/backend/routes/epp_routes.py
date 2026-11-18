from flask import Blueprint, request, jsonify, g
from database import fetch_one, fetch_all, execute_query
from utils.auth import login_required, role_required, log_audit
from datetime import datetime, timedelta, date
import json

epp_bp = Blueprint("epp", __name__)

VALID_CATEGORIES = ("CABEZA", "VISUAL", "AUDITIVA", "RESPIRATORIA", "MANOS", "PIES", "CUERPO")

# ==========================================================
# CATÁLOGO DE EPP
# ==========================================================

@epp_bp.route("/epp/catalog", methods=["GET"])
def get_catalog():
    """
    Retorna el catálogo de elementos de protección personal con filtros opcionales.
    TEST-005-B1: Retorna 200 con el catálogo de EPP sembrado.
    TEST-005-B2: Filtro por categoría (ej. category=MANOS).
    """
    try:
        category = request.args.get("category", type=str)
        is_active = request.args.get("is_active", default="true", type=str).lower() == "true"
        search = request.args.get("search", type=str)

        conditions = ["is_active = %s"]
        params = [is_active]

        if category:
            cat_clean = category.strip().upper()
            if cat_clean in VALID_CATEGORIES:
                conditions.append("category = %s")
                params.append(cat_clean)

        if search:
            s = f"%{search.strip().lower()}%"
            conditions.append("""
                (LOWER(name) LIKE %s OR LOWER(COALESCE(standard_code, '')) LIKE %s 
                 OR LOWER(COALESCE(description, '')) LIKE %s)
            """)
            params.extend([s, s, s])

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT id, name, category, standard_code, lifespan_days,
                   description, stock_quantity, is_active, created_at
            FROM epp_catalog
            WHERE {where_clause}
            ORDER BY category ASC, name ASC
        """
        items = fetch_all(query, tuple(params)) or []

        for item in items:
            if hasattr(item.get("created_at"), "strftime"):
                item["created_at"] = item["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "count": len(items),
            "catalog": items
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar catálogo de EPP: {str(e)}"}), 500


@epp_bp.route("/epp/catalog", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR")
def create_catalog_item():
    """
    Añade un nuevo elemento al catálogo de EPP.
    TEST-005-B3: Retorna 201 con el nuevo elemento creado.
    """
    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        category = (data.get("category") or "").strip().upper()
        standard_code = (data.get("standard_code") or "").strip()
        lifespan_days = data.get("lifespan_days")
        description = (data.get("description") or "").strip()
        stock_quantity = data.get("stock_quantity", 0)

        if not name or category not in VALID_CATEGORIES:
            return jsonify({
                "error": f"El nombre es obligatorio y la categoría debe ser una de: {', '.join(VALID_CATEGORIES)}"
            }), 400

        try:
            days_val = int(lifespan_days)
            if days_val <= 0:
                return jsonify({"error": "La vida útil debe ser mayor a 0 días"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "El campo 'lifespan_days' debe ser un número entero válido"}), 400

        try:
            stock_val = max(0, int(stock_quantity))
        except (ValueError, TypeError):
            stock_val = 0

        insert_sql = """
            INSERT INTO epp_catalog (name, category, standard_code, lifespan_days, description, stock_quantity, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """
        res = execute_query(insert_sql, (
            name, category, standard_code or None, days_val,
            description or None, stock_val
        ))
        new_id = res["last_id"]

        log_audit(g.current_user["sub"], "CREATE", "EPP_CATALOG", json.dumps({"epp_id": new_id, "name": name, "category": category}))

        created = fetch_one("SELECT * FROM epp_catalog WHERE id = %s", (new_id,))
        return jsonify({
            "message": "Elemento de EPP agregado exitosamente al catálogo",
            "item": created
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al crear elemento de EPP: {str(e)}"}), 500


# ==========================================================
# ENTREGAS Y ASIGNACIÓN DE DOTACIÓN
# ==========================================================

@epp_bp.route("/epp/deliveries", methods=["GET"])
def get_deliveries():
    """
    Retorna el historial de entregas de dotación con filtros.
    TEST-005-B6: Filtro por trabajador (worker_id).
    """
    try:
        worker_id = request.args.get("worker_id", type=int)
        epp_id = request.args.get("epp_id", type=int)
        category = request.args.get("category", type=str)
        reason = request.args.get("reason", type=str)
        search = request.args.get("search", type=str)

        conditions = ["1=1"]
        params = []

        if worker_id:
            conditions.append("ed.worker_id = %s")
            params.append(worker_id)

        if epp_id:
            conditions.append("ed.epp_id = %s")
            params.append(epp_id)

        if category and category.upper() in VALID_CATEGORIES:
            conditions.append("ec.category = %s")
            params.append(category.upper())

        if reason:
            conditions.append("ed.reason = %s")
            params.append(reason.strip().upper())

        if search:
            s = f"%{search.strip().lower()}%"
            conditions.append("""
                (LOWER(ec.name) LIKE %s OR LOWER(uw.name) LIKE %s 
                 OR LOWER(uw.area) LIKE %s OR LOWER(COALESCE(ed.notes, '')) LIKE %s)
            """)
            params.extend([s, s, s, s])

        where_clause = " AND ".join(conditions)

        today_str = date.today().isoformat()

        query = f"""
            SELECT ed.id, ed.epp_id, ed.worker_id, ed.delivered_by_user_id,
                   ed.delivery_date, ed.next_renewal_date, ed.quantity,
                   ed.reason, ed.worker_signature_confirmed, ed.notes, ed.created_at,
                   ec.name AS epp_name, ec.category AS epp_category, ec.standard_code,
                   ec.lifespan_days,
                   uw.name AS worker_name, uw.email AS worker_email, uw.area AS worker_area,
                   ud.name AS delivered_by_name,
                   DATEDIFF(ed.next_renewal_date, '{today_str}') AS days_until_renewal,
                   (ed.next_renewal_date <= '{today_str}') AS is_expired
            FROM epp_deliveries ed
            JOIN epp_catalog ec ON ed.epp_id = ec.id
            JOIN users uw ON ed.worker_id = uw.id
            JOIN users ud ON ed.delivered_by_user_id = ud.id
            WHERE {where_clause}
            ORDER BY ed.delivery_date DESC, ed.id DESC
        """

        deliveries = fetch_all(query, tuple(params)) or []

        for d in deliveries:
            if hasattr(d.get("delivery_date"), "strftime"):
                d["delivery_date"] = d["delivery_date"].strftime("%Y-%m-%d")
            if hasattr(d.get("next_renewal_date"), "strftime"):
                d["next_renewal_date"] = d["next_renewal_date"].strftime("%Y-%m-%d")
            d["is_expired"] = bool(d.get("is_expired"))

        return jsonify({
            "count": len(deliveries),
            "deliveries": deliveries
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar entregas de EPP: {str(e)}"}), 500


@epp_bp.route("/epp/deliveries", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR")
def create_delivery():
    """
    Registra la entrega de dotación a un trabajador.
    Calcula automáticamente: next_renewal_date = delivery_date + lifespan_days.
    TEST-005-B4: Retorna 201 con next_renewal_date calculado.
    TEST-005-B5: Si delivery_date = 2026-11-17 y lifespan = 90 -> next_renewal_date = 2027-02-15.
    """
    try:
        data = request.get_json() or {}
        epp_id = data.get("epp_id")
        worker_id = data.get("worker_id")
        delivery_date_str = (data.get("delivery_date") or "").strip()
        quantity = data.get("quantity", 1)
        reason = (data.get("reason") or "DOTACION_PERIODICA").strip().upper()
        notes = (data.get("notes") or "").strip()

        if not epp_id or not worker_id or not delivery_date_str:
            return jsonify({"error": "Los campos 'epp_id', 'worker_id' y 'delivery_date' son obligatorios"}), 400

        try:
            delivery_date = datetime.strptime(delivery_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Utilice YYYY-MM-DD"}), 400

        try:
            qty_val = max(1, int(quantity))
        except (ValueError, TypeError):
            qty_val = 1

        valid_reasons = ("DOTACION_PERIODICA", "INGRESO_NUEVO", "DETERIORO", "PERDIDA")
        if reason not in valid_reasons:
            reason = "DOTACION_PERIODICA"

        # Verificar existencia de EPP y obtener su vida útil
        epp = fetch_one("SELECT id, name, lifespan_days, stock_quantity FROM epp_catalog WHERE id = %s", (epp_id,))
        if not epp:
            return jsonify({"error": f"El elemento de EPP con ID {epp_id} no existe"}), 404

        # Verificar existencia del trabajador
        worker = fetch_one("SELECT id, name, area FROM users WHERE id = %s", (worker_id,))
        if not worker:
            return jsonify({"error": f"El trabajador con ID {worker_id} no existe en el sistema"}), 404

        # TEST-005-B4 y B5: Cálculo exacto de próxima renovación
        lifespan_days = int(epp.get("lifespan_days", 90))
        next_renewal_date = delivery_date + timedelta(days=lifespan_days)

        delivered_by = g.current_user["sub"]

        insert_sql = """
            INSERT INTO epp_deliveries (epp_id, worker_id, delivered_by_user_id, delivery_date, next_renewal_date, quantity, reason, worker_signature_confirmed, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s)
        """
        res = execute_query(insert_sql, (
            epp_id, worker_id, delivered_by, delivery_date,
            next_renewal_date, qty_val, reason, notes or None
        ))
        new_id = res["last_id"]

        # Disminuir stock si aplica
        execute_query("UPDATE epp_catalog SET stock_quantity = GREATEST(0, stock_quantity - %s) WHERE id = %s", (qty_val, epp_id))

        log_audit(delivered_by, "DELIVER_EPP", "EPP_DELIVERY", json.dumps({
            "delivery_id": new_id,
            "epp_id": epp_id,
            "worker_id": worker_id,
            "next_renewal_date": next_renewal_date.isoformat()
        }))

        # Obtener registro completo recién creado
        created = fetch_one("""
            SELECT ed.id, ed.epp_id, ed.worker_id, ed.delivery_date, ed.next_renewal_date,
                   ed.quantity, ed.reason, ed.notes,
                   ec.name AS epp_name, ec.category AS epp_category, ec.lifespan_days,
                   u.name AS worker_name
            FROM epp_deliveries ed
            JOIN epp_catalog ec ON ed.epp_id = ec.id
            JOIN users u ON ed.worker_id = u.id
            WHERE ed.id = %s
        """, (new_id,))

        if created:
            if hasattr(created.get("delivery_date"), "strftime"):
                created["delivery_date"] = created["delivery_date"].strftime("%Y-%m-%d")
            if hasattr(created.get("next_renewal_date"), "strftime"):
                created["next_renewal_date"] = created["next_renewal_date"].strftime("%Y-%m-%d")

        return jsonify({
            "message": "Entrega de dotación registrada exitosamente",
            "delivery": created
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar entrega de dotación: {str(e)}"}), 500


# ==========================================================
# ALERTAS DE VENCIMIENTO Y RENOVACIÓN
# ==========================================================

@epp_bp.route("/epp/renewals-due", methods=["GET"])
def get_renewals_due():
    """
    Retorna la lista de EPPs vencidos o próximos a vencer en los siguientes 30 días.
    TEST-005-B9: Retorna dotaciones vencidas o con next_renewal_date <= hoy + 30 días.
    """
    try:
        today_str = date.today().isoformat()

        query = f"""
            SELECT ed.id, ed.epp_id, ed.worker_id, ed.delivery_date, ed.next_renewal_date,
                   ed.quantity, ed.reason, ed.notes,
                   ec.name AS epp_name, ec.category AS epp_category, ec.stock_quantity,
                   uw.name AS worker_name, uw.area AS worker_area,
                   DATEDIFF(ed.next_renewal_date, '{today_str}') AS days_left,
                   (ed.next_renewal_date <= '{today_str}') AS is_expired
            FROM epp_deliveries ed
            JOIN epp_catalog ec ON ed.epp_id = ec.id
            JOIN users uw ON ed.worker_id = uw.id
            WHERE ed.next_renewal_date <= DATE_ADD('{today_str}', INTERVAL 30 DAY)
            ORDER BY ed.next_renewal_date ASC
        """

        renewals = fetch_all(query) or []

        expired_count = 0
        due_soon_count = 0

        for r in renewals:
            if hasattr(r.get("delivery_date"), "strftime"):
                r["delivery_date"] = r["delivery_date"].strftime("%Y-%m-%d")
            if hasattr(r.get("next_renewal_date"), "strftime"):
                r["next_renewal_date"] = r["next_renewal_date"].strftime("%Y-%m-%d")
            r["is_expired"] = bool(r.get("is_expired"))
            if r["is_expired"]:
                expired_count += 1
            else:
                due_soon_count += 1

        return jsonify({
            "count": len(renewals),
            "expired_count": expired_count,
            "due_soon_count": due_soon_count,
            "renewals": renewals
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar renovaciones de EPP: {str(e)}"}), 500


# ==========================================================
# INSPECCIONES DE USO DE EPP EN PLANTA
# ==========================================================

@epp_bp.route("/epp/inspections", methods=["GET"])
def get_inspections():
    """Retorna el historial de inspecciones de EPP en planta."""
    try:
        worker_id = request.args.get("worker_id", type=int)
        is_compliant = request.args.get("is_compliant", type=str)
        area = request.args.get("area", type=str)

        conditions = ["1=1"]
        params = []

        if worker_id:
            conditions.append("ei.worker_id = %s")
            params.append(worker_id)

        if is_compliant is not None:
            if is_compliant.lower() in ("true", "1"):
                conditions.append("ei.is_compliant = TRUE")
            elif is_compliant.lower() in ("false", "0"):
                conditions.append("ei.is_compliant = FALSE")

        if area:
            conditions.append("LOWER(ei.area) LIKE %s")
            params.append(f"%{area.strip().lower()}%")

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT ei.id, ei.inspector_user_id, ei.worker_id, ei.inspection_date,
                   ei.area, ei.is_compliant, ei.deficiencies_found, ei.corrective_actions,
                   ei.created_at,
                   uw.name AS worker_name, uw.area AS worker_area,
                   ui.name AS inspector_name
            FROM epp_inspections ei
            JOIN users uw ON ei.worker_id = uw.id
            JOIN users ui ON ei.inspector_user_id = ui.id
            WHERE {where_clause}
            ORDER BY ei.inspection_date DESC, ei.id DESC
        """

        inspections = fetch_all(query, tuple(params)) or []

        for insp in inspections:
            if hasattr(insp.get("inspection_date"), "strftime"):
                insp["inspection_date"] = insp["inspection_date"].strftime("%Y-%m-%d")
            insp["is_compliant"] = bool(insp.get("is_compliant"))

        return jsonify({
            "count": len(inspections),
            "inspections": inspections
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar inspecciones: {str(e)}"}), 500


@epp_bp.route("/epp/inspections", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR")
def create_inspection():
    """
    Registra una ronda de inspección de EPP.
    TEST-005-B7: Retorna 201 con datos válidos.
    TEST-005-B8: Si is_compliant=False y no deficiencies_found -> 400 Bad Request.
    """
    try:
        data = request.get_json() or {}
        worker_id = data.get("worker_id")
        inspection_date_str = (data.get("inspection_date") or "").strip()
        area = (data.get("area") or "").strip()
        is_compliant = data.get("is_compliant", True)
        deficiencies_found = (data.get("deficiencies_found") or "").strip()
        corrective_actions = (data.get("corrective_actions") or "").strip()

        if not worker_id or not inspection_date_str or not area:
            return jsonify({"error": "Los campos 'worker_id', 'inspection_date' y 'area' son obligatorios"}), 400

        try:
            inspection_date = datetime.strptime(inspection_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Utilice YYYY-MM-DD"}), 400

        # TEST-005-B8: Validación estricta de no conformidad
        is_compliant_bool = bool(is_compliant)
        if not is_compliant_bool and not deficiencies_found:
            return jsonify({
                "error": "Si la inspección se califica como No Conforme, es obligatorio detallar las deficiencias encontradas"
            }), 400

        # Verificar trabajador
        worker = fetch_one("SELECT id FROM users WHERE id = %s", (worker_id,))
        if not worker:
            return jsonify({"error": "El trabajador seleccionado no existe"}), 404

        inspector_id = g.current_user["sub"]

        insert_sql = """
            INSERT INTO epp_inspections (inspector_user_id, worker_id, inspection_date, area, is_compliant, deficiencies_found, corrective_actions)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        res = execute_query(insert_sql, (
            inspector_id, worker_id, inspection_date, area,
            is_compliant_bool,
            deficiencies_found or None,
            corrective_actions or None
        ))
        new_id = res["last_id"]

        log_audit(inspector_id, "INSPECT_EPP", "EPP_INSPECTION", json.dumps({
            "inspection_id": new_id,
            "worker_id": worker_id,
            "is_compliant": is_compliant_bool
        }))

        created = fetch_one("""
            SELECT ei.*, uw.name AS worker_name, ui.name AS inspector_name
            FROM epp_inspections ei
            JOIN users uw ON ei.worker_id = uw.id
            JOIN users ui ON ei.inspector_user_id = ui.id
            WHERE ei.id = %s
        """, (new_id,))

        if created and hasattr(created.get("inspection_date"), "strftime"):
            created["inspection_date"] = created["inspection_date"].strftime("%Y-%m-%d")

        return jsonify({
            "message": "Inspección de EPP registrada exitosamente",
            "inspection": created
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar inspección: {str(e)}"}), 500


# ==========================================================
# RESUMEN Y MÉTRICAS EPP
# ==========================================================

@epp_bp.route("/epp/summary", methods=["GET"])
def get_epp_summary():
    """Retorna métricas consolidadas del módulo de EPP para el panel y tarjetas superiores."""
    try:
        today_str = date.today().isoformat()

        # 1. Dotaciones vencidas y próximas
        due_row = fetch_one(f"""
            SELECT 
                COUNT(CASE WHEN next_renewal_date <= '{today_str}' THEN 1 END) AS expired_count,
                COUNT(CASE WHEN next_renewal_date > '{today_str}' AND next_renewal_date <= DATE_ADD('{today_str}', INTERVAL 30 DAY) THEN 1 END) AS due_soon_count,
                COUNT(id) AS total_deliveries
            FROM epp_deliveries
        """)
        expired_count = int(due_row["expired_count"]) if due_row else 0
        due_soon_count = int(due_row["due_soon_count"]) if due_row else 0
        total_deliveries = int(due_row["total_deliveries"]) if due_row else 0

        # 2. Entregas del mes en curso
        now = datetime.now()
        month_row = fetch_one("""
            SELECT COUNT(id) AS month_deliveries
            FROM epp_deliveries
            WHERE MONTH(delivery_date) = %s AND YEAR(delivery_date) = %s
        """, (now.month, now.year))
        month_deliveries = int(month_row["month_deliveries"]) if month_row else 0

        # 3. Tasa de cumplimiento en inspecciones
        insp_row = fetch_one("""
            SELECT COUNT(id) AS total_inspections,
                   COUNT(CASE WHEN is_compliant = TRUE THEN 1 END) AS compliant_count
            FROM epp_inspections
        """)
        total_insp = int(insp_row["total_inspections"]) if insp_row else 0
        compliant_insp = int(insp_row["compliant_count"]) if insp_row else 0
        compliance_rate = round((compliant_insp / total_insp) * 100.0, 1) if total_insp > 0 else 100.0

        # 4. Total ítems en catálogo y stock bajo (< 10)
        cat_row = fetch_one("""
            SELECT COUNT(id) AS total_catalog,
                   COUNT(CASE WHEN stock_quantity < 10 THEN 1 END) AS low_stock_count
            FROM epp_catalog
            WHERE is_active = TRUE
        """)
        total_catalog = int(cat_row["total_catalog"]) if cat_row else 0
        low_stock_count = int(cat_row["low_stock_count"]) if cat_row else 0

        return jsonify({
            "expired_count": expired_count,
            "due_soon_count": due_soon_count,
            "month_deliveries": month_deliveries,
            "total_deliveries": total_deliveries,
            "compliance_rate": compliance_rate,
            "total_inspections": total_insp,
            "total_catalog": total_catalog,
            "low_stock_count": low_stock_count
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar resumen de EPP: {str(e)}"}), 500
