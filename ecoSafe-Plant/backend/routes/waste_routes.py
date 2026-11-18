from flask import Blueprint, request, jsonify, g
from database import fetch_one, fetch_all, execute_query
from utils.auth import login_required, role_required, log_audit
from datetime import datetime
import json

waste_bp = Blueprint("waste", __name__)

VALORIZED_METHODS = {
    "compostaje",
    "lombricultura",
    "alimentación animal",
    "alimentacion animal",
    "venta como subproducto",
    "reciclaje",
    "reciclaje / gestor autorizado",
    "reutilización",
    "reutilizacion"
}

@waste_bp.route("/waste/types", methods=["GET"])
def get_waste_types():
    """
    Retorna el catálogo completo de categorías y tipos de residuos.
    TEST-002-B1: Retorna 200 con categorías y tipos precargados.
    """
    try:
        categories_query = "SELECT id, name, description, color_code FROM waste_categories ORDER BY id ASC"
        categories = fetch_all(categories_query) or []

        types_query = """
            SELECT wt.id, wt.category_id, wt.name, wt.default_unit, wt.is_hazardous,
                   wc.name AS category_name, wc.color_code AS category_color
            FROM waste_types wt
            JOIN waste_categories wc ON wt.category_id = wc.id
            ORDER BY wt.category_id ASC, wt.name ASC
        """
        waste_types = fetch_all(types_query) or []

        # Agrupar tipos por categoría para facilitar selectores en el frontend
        grouped = []
        for cat in categories:
            cat_types = [t for t in waste_types if t["category_id"] == cat["id"]]
            grouped.append({
                "id": cat["id"],
                "name": cat["name"],
                "description": cat.get("description"),
                "color_code": cat.get("color_code", "#2d6a4f"),
                "types": cat_types
            })

        return jsonify({
            "categories": grouped,
            "types": waste_types
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar tipos de residuos: {str(e)}"}), 500


@waste_bp.route("/waste/records", methods=["GET"])
def get_waste_records():
    """
    Retorna la lista de registros de residuos con filtros opcionales.
    Filtros soportados:
    - month: 1-12
    - year: e.g. 2026
    - category: nombre o id de categoría (ej. PELIGROSO, ORGANICO)
    - waste_type_id: ID específico del tipo de residuo
    - area: nombre o coincidencia del área
    - search: texto para buscar en notas, tipo, área o método de disposición
    """
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)
        category = request.args.get("category", type=str)
        waste_type_id = request.args.get("waste_type_id", type=int)
        area = request.args.get("area", type=str)
        search = request.args.get("search", type=str)

        conditions = ["1=1"]
        params = []

        if month:
            conditions.append("MONTH(wr.record_date) = %s")
            params.append(month)

        if year:
            conditions.append("YEAR(wr.record_date) = %s")
            params.append(year)

        if category:
            cat_clean = category.strip().lower()
            if cat_clean.isdigit():
                conditions.append("wc.id = %s")
                params.append(int(cat_clean))
            else:
                # Permite buscar 'PELIGROSO', 'ORGANICO', etc.
                conditions.append("(LOWER(wc.name) LIKE %s OR (wt.is_hazardous = TRUE AND %s LIKE '%%peligros%%'))")
                params.append(f"%{cat_clean}%")
                params.append(cat_clean)

        if waste_type_id:
            conditions.append("wr.waste_type_id = %s")
            params.append(waste_type_id)

        if area:
            conditions.append("LOWER(wr.area) LIKE %s")
            params.append(f"%{area.strip().lower()}%")

        if search:
            s = f"%{search.strip().lower()}%"
            conditions.append("""
                (LOWER(wt.name) LIKE %s OR LOWER(wr.area) LIKE %s 
                 OR LOWER(wr.disposal_method) LIKE %s OR LOWER(COALESCE(wr.notes, '')) LIKE %s)
            """)
            params.extend([s, s, s, s])

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT wr.id, wr.waste_type_id, wr.recorded_by_user_id, wr.record_date,
                   CAST(wr.quantity AS DOUBLE) AS quantity, wr.unit, wr.area,
                   wr.disposal_method, wr.disposal_certificate_url, wr.notes, wr.created_at,
                   wt.name AS waste_type_name, wt.is_hazardous,
                   wc.id AS category_id, wc.name AS category_name, wc.color_code AS category_color,
                   u.name AS recorded_by_name, u.role AS recorded_by_role
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            JOIN waste_categories wc ON wt.category_id = wc.id
            JOIN users u ON wr.recorded_by_user_id = u.id
            WHERE {where_clause}
            ORDER BY wr.record_date DESC, wr.id DESC
        """

        records = fetch_all(query, tuple(params)) or []

        # Formatear record_date a ISO string (YYYY-MM-DD)
        for r in records:
            if hasattr(r.get("record_date"), "strftime"):
                r["record_date"] = r["record_date"].strftime("%Y-%m-%d")
            if hasattr(r.get("created_at"), "strftime"):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "count": len(records),
            "records": records
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar registros de residuos: {str(e)}"}), 500


@waste_bp.route("/waste/records", methods=["POST"])
@login_required
def create_waste_record():
    """
    Crea un nuevo registro de residuo.
    TEST-002-B2: Retorna 201 con el registro creado.
    TEST-002-B3: Validación de cantidad negativa o menor a cero -> 400 Bad Request.
    TEST-002-B4: Sin token JWT -> 401 Unauthorized (garantizado por @login_required).
    """
    try:
        data = request.get_json() or {}

        waste_type_id = data.get("waste_type_id")
        record_date = (data.get("record_date") or "").strip()
        quantity = data.get("quantity")
        unit = (data.get("unit") or "kg").strip()
        area = (data.get("area") or "").strip()
        disposal_method = (data.get("disposal_method") or "").strip()
        notes = (data.get("notes") or "").strip()
        disposal_certificate_url = (data.get("disposal_certificate_url") or "").strip()

        # Validación de campos requeridos
        if not waste_type_id or not record_date or not area or not disposal_method:
            return jsonify({
                "error": "Los campos 'waste_type_id', 'record_date', 'quantity', 'area' y 'disposal_method' son obligatorios"
            }), 400

        # Validación numérica de cantidad (TEST-002-B3)
        try:
            quantity_val = float(quantity)
            if quantity_val <= 0:
                return jsonify({
                    "error": "La cantidad generada debe ser un valor numérico positivo mayor a cero"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "error": "La cantidad ingresada no es válida. Debe ser un número mayor a cero"
            }), 400

        # Validar formato de fecha (YYYY-MM-DD)
        try:
            parsed_date = datetime.strptime(record_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Utilice el formato YYYY-MM-DD"}), 400

        # Verificar existencia del tipo de residuo
        waste_type = fetch_one(
            "SELECT id, default_unit, category_id FROM waste_types WHERE id = %s",
            (waste_type_id,)
        )
        if not waste_type:
            return jsonify({"error": f"El tipo de residuo con ID {waste_type_id} no existe en la base de datos"}), 404

        unit_final = unit or waste_type.get("default_unit", "kg")
        user_id = g.current_user["sub"]

        insert_sql = """
            INSERT INTO waste_records 
            (waste_type_id, recorded_by_user_id, record_date, quantity, unit, area, disposal_method, disposal_certificate_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        result = execute_query(insert_sql, (
            waste_type_id,
            user_id,
            parsed_date,
            quantity_val,
            unit_final,
            area,
            disposal_method,
            disposal_certificate_url or None,
            notes or None
        ))
        new_id = result["last_id"]

        # Auditoría
        log_audit(user_id, "CREATE", "WASTE_RECORD", json.dumps({
            "record_id": new_id,
            "waste_type_id": waste_type_id,
            "quantity": quantity_val,
            "unit": unit_final,
            "area": area
        }))

        # Retornar registro creado completo
        new_record = fetch_one("""
            SELECT wr.id, wr.waste_type_id, wr.recorded_by_user_id, wr.record_date,
                   CAST(wr.quantity AS DOUBLE) AS quantity, wr.unit, wr.area,
                   wr.disposal_method, wr.disposal_certificate_url, wr.notes, wr.created_at,
                   wt.name AS waste_type_name, wt.is_hazardous,
                   wc.id AS category_id, wc.name AS category_name, wc.color_code AS category_color,
                   u.name AS recorded_by_name
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            JOIN waste_categories wc ON wt.category_id = wc.id
            JOIN users u ON wr.recorded_by_user_id = u.id
            WHERE wr.id = %s
        """, (new_id,))

        if new_record and hasattr(new_record.get("record_date"), "strftime"):
            new_record["record_date"] = new_record["record_date"].strftime("%Y-%m-%d")
        if new_record and hasattr(new_record.get("created_at"), "strftime"):
            new_record["created_at"] = new_record["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "message": "Registro de residuo creado exitosamente",
            "record": new_record
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al crear registro de residuo: {str(e)}"}), 500


@waste_bp.route("/waste/records/<int:record_id>", methods=["GET"])
def get_waste_record_by_id(record_id):
    """Retorna un registro de residuo por ID."""
    try:
        record = fetch_one("""
            SELECT wr.id, wr.waste_type_id, wr.recorded_by_user_id, wr.record_date,
                   CAST(wr.quantity AS DOUBLE) AS quantity, wr.unit, wr.area,
                   wr.disposal_method, wr.disposal_certificate_url, wr.notes, wr.created_at,
                   wt.name AS waste_type_name, wt.is_hazardous,
                   wc.id AS category_id, wc.name AS category_name, wc.color_code AS category_color,
                   u.name AS recorded_by_name, u.role AS recorded_by_role
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            JOIN waste_categories wc ON wt.category_id = wc.id
            JOIN users u ON wr.recorded_by_user_id = u.id
            WHERE wr.id = %s
        """, (record_id,))

        if not record:
            return jsonify({"error": f"Registro de residuo #{record_id} no encontrado"}), 404

        if hasattr(record.get("record_date"), "strftime"):
            record["record_date"] = record["record_date"].strftime("%Y-%m-%d")
        if hasattr(record.get("created_at"), "strftime"):
            record["created_at"] = record["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify(record), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar el registro: {str(e)}"}), 500


@waste_bp.route("/waste/records/<int:record_id>", methods=["PUT"])
@login_required
def update_waste_record(record_id):
    """
    Modifica un registro existente.
    TEST-002-B7: Retorna 200 con los datos modificados.
    """
    try:
        existing = fetch_one("SELECT id FROM waste_records WHERE id = %s", (record_id,))
        if not existing:
            return jsonify({"error": f"Registro #{record_id} no encontrado"}), 404

        data = request.get_json() or {}

        # Validar cantidad si se provee
        if "quantity" in data:
            try:
                qty = float(data["quantity"])
                if qty <= 0:
                    return jsonify({"error": "La cantidad debe ser mayor a cero"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "La cantidad ingresada no es válida"}), 400

        # Validar fecha si se provee
        if "record_date" in data:
            try:
                datetime.strptime(data["record_date"], "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Formato de fecha inválido. Utilice YYYY-MM-DD"}), 400

        # Validar tipo de residuo si se actualiza
        if "waste_type_id" in data:
            wt = fetch_one("SELECT id FROM waste_types WHERE id = %s", (data["waste_type_id"],))
            if not wt:
                return jsonify({"error": "El tipo de residuo indicado no existe"}), 404

        fields = []
        params = []
        updatable_fields = [
            "waste_type_id", "record_date", "quantity", "unit",
            "area", "disposal_method", "disposal_certificate_url", "notes"
        ]

        for field in updatable_fields:
            if field in data:
                fields.append(f"{field} = %s")
                params.append(data[field])

        if not fields:
            return jsonify({"message": "No se enviaron campos para actualizar"}), 200

        params.append(record_id)
        update_sql = f"UPDATE waste_records SET {', '.join(fields)} WHERE id = %s"
        execute_query(update_sql, tuple(params))

        # Registrar auditoría
        log_audit(g.current_user["sub"], "UPDATE", "WASTE_RECORD", json.dumps({"record_id": record_id, "fields": list(data.keys())}))

        # Retornar registro actualizado
        updated_record = fetch_one("""
            SELECT wr.id, wr.waste_type_id, wr.recorded_by_user_id, wr.record_date,
                   CAST(wr.quantity AS DOUBLE) AS quantity, wr.unit, wr.area,
                   wr.disposal_method, wr.disposal_certificate_url, wr.notes, wr.created_at,
                   wt.name AS waste_type_name, wt.is_hazardous,
                   wc.id AS category_id, wc.name AS category_name, wc.color_code AS category_color,
                   u.name AS recorded_by_name
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            JOIN waste_categories wc ON wt.category_id = wc.id
            JOIN users u ON wr.recorded_by_user_id = u.id
            WHERE wr.id = %s
        """, (record_id,))

        if updated_record and hasattr(updated_record.get("record_date"), "strftime"):
            updated_record["record_date"] = updated_record["record_date"].strftime("%Y-%m-%d")

        return jsonify({
            "message": "Registro actualizado exitosamente",
            "record": updated_record
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar el registro: {str(e)}"}), 500


@waste_bp.route("/waste/records/<int:record_id>", methods=["DELETE"])
@role_required("ADMIN")
def delete_waste_record(record_id):
    """
    Elimina un registro de residuo. Solo permitido para usuarios con rol ADMIN.
    TEST-002-B8: OPERARIO -> 403 Forbidden.
    TEST-002-B9: ADMIN -> 200 y registro eliminado.
    """
    try:
        existing = fetch_one("SELECT id, waste_type_id, quantity FROM waste_records WHERE id = %s", (record_id,))
        if not existing:
            return jsonify({"error": f"Registro #{record_id} no encontrado"}), 404

        execute_query("DELETE FROM waste_records WHERE id = %s", (record_id,))

        # Registrar auditoría
        log_audit(g.current_user["sub"], "DELETE", "WASTE_RECORD", json.dumps({"deleted_record_id": record_id}))

        return jsonify({
            "message": f"Registro #{record_id} eliminado exitosamente"
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al eliminar registro: {str(e)}"}), 500


@waste_bp.route("/waste/summary", methods=["GET"])
def get_waste_summary():
    """
    Retorna métricas y agregaciones mensuales para KPIs y dashboard.
    TEST-002-B10: Retorna totales mensuales y valorization_percent (residuos aprovechados / total * 100).
    """
    try:
        now = datetime.now()
        month = request.args.get("month", default=now.month, type=int)
        year = request.args.get("year", default=now.year, type=int)

        # Mes anterior para comparativa
        prev_month = 12 if month == 1 else month - 1
        prev_year = year - 1 if month == 1 else year

        # 1. Total del mes actual
        curr_total_row = fetch_one("""
            SELECT COALESCE(SUM(quantity), 0) AS total_kg,
                   COUNT(id) AS total_records
            FROM waste_records
            WHERE MONTH(record_date) = %s AND YEAR(record_date) = %s
        """, (month, year))
        total_quantity = float(curr_total_row["total_kg"]) if curr_total_row else 0.0
        total_records = int(curr_total_row["total_records"]) if curr_total_row else 0

        # 2. Total del mes anterior para variación porcentual
        prev_total_row = fetch_one("""
            SELECT COALESCE(SUM(quantity), 0) AS total_kg
            FROM waste_records
            WHERE MONTH(record_date) = %s AND YEAR(record_date) = %s
        """, (prev_month, prev_year))
        prev_total = float(prev_total_row["total_kg"]) if prev_total_row else 0.0

        if prev_total > 0:
            diff_percent = round(((total_quantity - prev_total) / prev_total) * 100.0, 1)
        else:
            diff_percent = 0.0

        # 3. Residuos peligrosos (RESPEL)
        hazardous_row = fetch_one("""
            SELECT COALESCE(SUM(wr.quantity), 0) AS hazardous_kg
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            JOIN waste_categories wc ON wt.category_id = wc.id
            WHERE MONTH(wr.record_date) = %s AND YEAR(wr.record_date) = %s
              AND (wt.is_hazardous = TRUE OR LOWER(wc.name) LIKE '%%peligros%%')
        """, (month, year))
        hazardous_quantity = float(hazardous_row["hazardous_kg"]) if hazardous_row else 0.0

        # 4. Residuos valorizados / aprovechados:
        # Son aquellos con métodos como Compostaje, Lombricultura, Alimentación animal, Reciclaje, Subproducto
        # o que pertenezcan a categorías Orgánicos / Reciclables y NO vayan a relleno sanitario
        valorized_row = fetch_one("""
            SELECT COALESCE(SUM(wr.quantity), 0) AS valorized_kg
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            JOIN waste_categories wc ON wt.category_id = wc.id
            WHERE MONTH(wr.record_date) = %s AND YEAR(wr.record_date) = %s
              AND wt.is_hazardous = FALSE
              AND (
                  LOWER(wr.disposal_method) IN ('compostaje', 'lombricultura', 'alimentación animal', 'alimentacion animal', 'venta como subproducto', 'reciclaje', 'reciclaje / gestor autorizado', 'reutilización', 'reutilizacion')
                  OR (wc.id IN (1, 2) AND LOWER(wr.disposal_method) NOT LIKE '%%relleno%%')
              )
        """, (month, year))
        valorized_quantity = float(valorized_row["valorized_kg"]) if valorized_row else 0.0

        # Cálculo de porcentaje de aprovechamiento / valorización
        if total_quantity > 0:
            valorization_percent = round((valorized_quantity / total_quantity) * 100.0, 2)
        else:
            valorization_percent = 0.0

        # 5. Desglose por categoría
        categories_rows = fetch_all("""
            SELECT wc.id, wc.name, wc.color_code,
                   COALESCE(SUM(wr.quantity), 0) AS total_kg,
                   COUNT(wr.id) AS count
            FROM waste_categories wc
            LEFT JOIN waste_types wt ON wt.category_id = wc.id
            LEFT JOIN waste_records wr ON wr.waste_type_id = wt.id 
                 AND MONTH(wr.record_date) = %s AND YEAR(wr.record_date) = %s
            GROUP BY wc.id, wc.name, wc.color_code
            ORDER BY wc.id ASC
        """, (month, year)) or []

        categories_summary = []
        for cat in categories_rows:
            cat_kg = float(cat["total_kg"])
            pct = round((cat_kg / total_quantity) * 100.0, 1) if total_quantity > 0 else 0.0
            categories_summary.append({
                "category_id": cat["id"],
                "name": cat["name"],
                "color_code": cat["color_code"],
                "total_kg": cat_kg,
                "count": int(cat["count"]),
                "percent": pct
            })

        # 6. Desglose por método de disposición
        disposal_rows = fetch_all("""
            SELECT wr.disposal_method,
                   COALESCE(SUM(wr.quantity), 0) AS total_kg,
                   COUNT(wr.id) AS count
            FROM waste_records wr
            WHERE MONTH(wr.record_date) = %s AND YEAR(wr.record_date) = %s
            GROUP BY wr.disposal_method
            ORDER BY total_kg DESC
        """, (month, year)) or []

        disposal_summary = []
        for d in disposal_rows:
            d_kg = float(d["total_kg"])
            pct = round((d_kg / total_quantity) * 100.0, 1) if total_quantity > 0 else 0.0
            disposal_summary.append({
                "method": d["disposal_method"],
                "total_kg": d_kg,
                "count": int(d["count"]),
                "percent": pct
            })

        return jsonify({
            "month": month,
            "year": year,
            "total_quantity": round(total_quantity, 2),
            "previous_month_total": round(prev_total, 2),
            "diff_percent": diff_percent,
            "valorized_quantity": round(valorized_quantity, 2),
            "valorization_percent": valorization_percent,
            "hazardous_quantity": round(hazardous_quantity, 2),
            "total_records": total_records,
            "categories_summary": categories_summary,
            "disposal_summary": disposal_summary
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar resumen de residuos: {str(e)}"}), 500
