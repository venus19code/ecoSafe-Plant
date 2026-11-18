from flask import Blueprint, request, jsonify, g
from database import fetch_one, fetch_all, execute_query
from utils.auth import login_required, role_required, log_audit
from datetime import datetime
import json

utility_bp = Blueprint("utilities", __name__)

@utility_bp.route("/utilities/meters", methods=["GET"])
def get_meters():
    """
    Retorna la lista de medidores configurados con su última lectura registrada.
    TEST-003-B1: Retorna 200 con los medidores iniciales.
    """
    try:
        resource_type = request.args.get("resource_type", type=str)
        is_active = request.args.get("is_active", default="true", type=str).lower() == "true"

        conditions = ["is_active = %s"]
        params = [is_active]

        if resource_type:
            res_clean = resource_type.strip().upper()
            if res_clean in ("AGUA", "ENERGIA"):
                conditions.append("resource_type = %s")
                params.append(res_clean)

        where_clause = " AND ".join(conditions)
        meters_query = f"""
            SELECT id, resource_type, code, name, location_area,
                   CAST(multiplier AS DOUBLE) AS multiplier, unit, is_active, created_at
            FROM utility_meters
            WHERE {where_clause}
            ORDER BY resource_type ASC, id ASC
        """
        meters = fetch_all(meters_query, tuple(params)) or []

        # Obtener última lectura de cada medidor para prellenado en frontend
        for m in meters:
            latest = fetch_one("""
                SELECT reading_value, reading_date, unit
                FROM utility_readings
                WHERE meter_id = %s
                ORDER BY reading_date DESC, id DESC
                LIMIT 1
            """, (m["id"],))

            if latest:
                m["latest_reading_value"] = float(latest["reading_value"])
                m["latest_reading_date"] = latest["reading_date"].strftime("%Y-%m-%d") if hasattr(latest["reading_date"], "strftime") else str(latest["reading_date"])
            else:
                m["latest_reading_value"] = None
                m["latest_reading_date"] = None

        return jsonify({
            "count": len(meters),
            "meters": meters
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar medidores: {str(e)}"}), 500


@utility_bp.route("/utilities/meters", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR")
def create_or_update_meter():
    """Crea o edita un punto de medición."""
    try:
        data = request.get_json() or {}
        code = (data.get("code") or "").strip().upper()
        name = (data.get("name") or "").strip()
        resource_type = (data.get("resource_type") or "").strip().upper()
        location_area = (data.get("location_area") or "").strip()
        multiplier = float(data.get("multiplier", 1.0))
        unit = (data.get("unit") or ("m3" if resource_type == "AGUA" else "kWh")).strip()

        if not code or not name or resource_type not in ("AGUA", "ENERGIA") or not location_area:
            return jsonify({"error": "Los campos 'code', 'name', 'resource_type' y 'location_area' son obligatorios"}), 400

        existing = fetch_one("SELECT id FROM utility_meters WHERE code = %s", (code,))
        if existing:
            execute_query("""
                UPDATE utility_meters 
                SET name=%s, resource_type=%s, location_area=%s, multiplier=%s, unit=%s, is_active=TRUE
                WHERE id=%s
            """, (name, resource_type, location_area, multiplier, unit, existing["id"]))
            meter_id = existing["id"]
        else:
            res = execute_query("""
                INSERT INTO utility_meters (code, name, resource_type, location_area, multiplier, unit, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """, (code, name, resource_type, location_area, multiplier, unit))
            meter_id = res["last_id"]

        log_audit(g.current_user["sub"], "SAVE_METER", "UTILITY_METER", json.dumps({"meter_id": meter_id, "code": code}))

        return jsonify({"message": "Medidor guardado exitosamente", "meter_id": meter_id}), 201
    except Exception as e:
        return jsonify({"error": f"Error al guardar medidor: {str(e)}"}), 500


@utility_bp.route("/utilities/readings", methods=["GET"])
def get_readings():
    """
    Retorna el listado de lecturas de consumo con filtros.
    TEST-003-B5: Retorna lecturas filtradas por recurso (AGUA/ENERGIA) y periodo (mes/año).
    """
    try:
        resource_type = request.args.get("resource_type", type=str)
        meter_id = request.args.get("meter_id", type=int)
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)
        search = request.args.get("search", type=str)

        conditions = ["1=1"]
        params = []

        if resource_type:
            res_clean = resource_type.strip().upper()
            if res_clean in ("AGUA", "ENERGIA"):
                conditions.append("um.resource_type = %s")
                params.append(res_clean)

        if meter_id:
            conditions.append("ur.meter_id = %s")
            params.append(meter_id)

        if month:
            conditions.append("MONTH(ur.reading_date) = %s")
            params.append(month)

        if year:
            conditions.append("YEAR(ur.reading_date) = %s")
            params.append(year)

        if search:
            s = f"%{search.strip().lower()}%"
            conditions.append("""
                (LOWER(um.name) LIKE %s OR LOWER(um.code) LIKE %s 
                 OR LOWER(um.location_area) LIKE %s OR LOWER(COALESCE(ur.notes, '')) LIKE %s)
            """)
            params.extend([s, s, s, s])

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT ur.id, ur.meter_id, ur.recorded_by_user_id, ur.reading_date,
                   CAST(ur.reading_value AS DOUBLE) AS reading_value,
                   CAST(ur.consumption AS DOUBLE) AS consumption,
                   ur.unit,
                   CAST(COALESCE(ur.cost_amount, 0) AS DOUBLE) AS cost_amount,
                   ur.notes, ur.created_at,
                   um.code AS meter_code, um.name AS meter_name,
                   um.resource_type, um.location_area,
                   u.name AS recorded_by_name
            FROM utility_readings ur
            JOIN utility_meters um ON ur.meter_id = um.id
            JOIN users u ON ur.recorded_by_user_id = u.id
            WHERE {where_clause}
            ORDER BY ur.reading_date DESC, ur.id DESC
        """

        readings = fetch_all(query, tuple(params)) or []

        for r in readings:
            if hasattr(r.get("reading_date"), "strftime"):
                r["reading_date"] = r["reading_date"].strftime("%Y-%m-%d")
            if hasattr(r.get("created_at"), "strftime"):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "count": len(readings),
            "readings": readings
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar lecturas: {str(e)}"}), 500


@utility_bp.route("/utilities/readings", methods=["POST"])
@login_required
def create_reading():
    """
    Registra una nueva lectura calculando automáticamente el consumo acumulado.
    TEST-003-B2: Primera lectura -> consumption = reading_value.
    TEST-003-B3: Segunda lectura -> consumption = lectura_actual - lectura_anterior.
    TEST-003-B4: Si lectura_actual < lectura_anterior -> 400 Bad Request.
    """
    try:
        data = request.get_json() or {}
        meter_id = data.get("meter_id")
        reading_date = (data.get("reading_date") or "").strip()
        reading_value = data.get("reading_value")
        cost_amount = data.get("cost_amount")
        notes = (data.get("notes") or "").strip()

        if not meter_id or not reading_date or reading_value is None:
            return jsonify({"error": "Los campos 'meter_id', 'reading_date' y 'reading_value' son obligatorios"}), 400

        try:
            curr_value = float(reading_value)
            if curr_value < 0:
                return jsonify({"error": "La lectura del medidor no puede ser un número negativo"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "El valor de lectura debe ser un número válido"}), 400

        cost_val = 0.0
        if cost_amount not in (None, ""):
            try:
                cost_val = float(cost_amount)
            except ValueError:
                cost_val = 0.0

        try:
            parsed_date = datetime.strptime(reading_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Utilice YYYY-MM-DD"}), 400

        # Verificar existencia del medidor
        meter = fetch_one("SELECT id, multiplier, unit, resource_type FROM utility_meters WHERE id = %s", (meter_id,))
        if not meter:
            return jsonify({"error": f"El medidor con ID {meter_id} no existe"}), 404

        multiplier = float(meter.get("multiplier", 1.0))
        unit = meter.get("unit") or ("m3" if meter["resource_type"] == "AGUA" else "kWh")

        # Buscar la lectura previa más reciente para este medidor
        prev_reading = fetch_one("""
            SELECT id, reading_value, reading_date
            FROM utility_readings
            WHERE meter_id = %s
            ORDER BY reading_date DESC, id DESC
            LIMIT 1
        """, (meter_id,))

        if not prev_reading:
            # TEST-003-B2: Primera lectura -> consumo = lectura actual
            consumption = round(curr_value * multiplier, 2)
            prev_value = None
        else:
            prev_val = float(prev_reading["reading_value"])
            prev_value = prev_val

            # TEST-003-B4: El medidor no puede retroceder
            if curr_value < prev_val:
                return jsonify({
                    "error": f"La lectura actual ({curr_value}) no puede ser menor a la lectura anterior registrada ({prev_val}). Verifique el número ingresado."
                }), 400

            # TEST-003-B3: Consumo automático = (lectura actual - lectura anterior) * multiplicador
            consumption = round((curr_value - prev_val) * multiplier, 2)

        user_id = g.current_user["sub"]

        insert_sql = """
            INSERT INTO utility_readings (meter_id, recorded_by_user_id, reading_date, reading_value, consumption, unit, cost_amount, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        res = execute_query(insert_sql, (
            meter_id,
            user_id,
            parsed_date,
            curr_value,
            consumption,
            unit,
            cost_val,
            notes or None
        ))
        new_id = res["last_id"]

        # Auditoría
        log_audit(user_id, "CREATE", "UTILITY_READING", json.dumps({
            "reading_id": new_id,
            "meter_id": meter_id,
            "reading_value": curr_value,
            "consumption": consumption
        }))

        # Retornar registro creado completo
        new_record = fetch_one("""
            SELECT ur.id, ur.meter_id, ur.recorded_by_user_id, ur.reading_date,
                   CAST(ur.reading_value AS DOUBLE) AS reading_value,
                   CAST(ur.consumption AS DOUBLE) AS consumption,
                   ur.unit,
                   CAST(COALESCE(ur.cost_amount, 0) AS DOUBLE) AS cost_amount,
                   ur.notes,
                   um.code AS meter_code, um.name AS meter_name, um.resource_type, um.location_area
            FROM utility_readings ur
            JOIN utility_meters um ON ur.meter_id = um.id
            WHERE ur.id = %s
        """, (new_id,))

        if new_record and hasattr(new_record.get("reading_date"), "strftime"):
            new_record["reading_date"] = new_record["reading_date"].strftime("%Y-%m-%d")

        return jsonify({
            "message": "Lectura registrada exitosamente",
            "reading": new_record,
            "previous_reading_value": prev_value,
            "calculated_consumption": consumption
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar lectura: {str(e)}"}), 500


@utility_bp.route("/utilities/summary", methods=["GET"])
def get_summary():
    """
    Retorna consolidados de Agua y Energía, comparativa frente a metas y costos.
    TEST-003-B6: Consumo total de agua y energía, costos y porcentaje de meta cumplida.
    """
    try:
        now = datetime.now()
        month = request.args.get("month", default=now.month, type=int)
        year = request.args.get("year", default=now.year, type=int)

        prev_month = 12 if month == 1 else month - 1
        prev_year = year - 1 if month == 1 else year

        def calculate_resource_summary(resource):
            # Consumo actual del mes
            row = fetch_one("""
                SELECT COALESCE(SUM(ur.consumption), 0) AS total_consumption,
                       COALESCE(SUM(ur.cost_amount), 0) AS total_cost,
                       COUNT(ur.id) AS readings_count
                FROM utility_readings ur
                JOIN utility_meters um ON ur.meter_id = um.id
                WHERE um.resource_type = %s
                  AND MONTH(ur.reading_date) = %s AND YEAR(ur.reading_date) = %s
            """, (resource, month, year))

            total_consumption = float(row["total_consumption"]) if row else 0.0
            total_cost = float(row["total_cost"]) if row else 0.0
            readings_count = int(row["readings_count"]) if row else 0

            # Consumo mes anterior
            prev_row = fetch_one("""
                SELECT COALESCE(SUM(ur.consumption), 0) AS total_consumption
                FROM utility_readings ur
                JOIN utility_meters um ON ur.meter_id = um.id
                WHERE um.resource_type = %s
                  AND MONTH(ur.reading_date) = %s AND YEAR(ur.reading_date) = %s
            """, (resource, prev_month, prev_year))

            prev_consumption = float(prev_row["total_consumption"]) if prev_row else 0.0

            if prev_consumption > 0:
                diff_percent = round(((total_consumption - prev_consumption) / prev_consumption) * 100.0, 1)
            else:
                diff_percent = 0.0

            # Meta ambiental configurada
            target_row = fetch_one("""
                SELECT target_consumption
                FROM utility_targets
                WHERE resource_type = %s AND target_year = %s AND target_month = %s
            """, (resource, year, month))

            target_val = float(target_row["target_consumption"]) if target_row else 0.0

            if target_val > 0:
                target_percent = round((total_consumption / target_val) * 100.0, 1)
                is_exceeded = total_consumption > target_val
            else:
                target_percent = 0.0
                is_exceeded = False

            return {
                "resource_type": resource,
                "unit": "m3" if resource == "AGUA" else "kWh",
                "total_consumption": round(total_consumption, 2),
                "previous_month_consumption": round(prev_consumption, 2),
                "diff_percent": diff_percent,
                "target_consumption": target_val,
                "target_percent": target_percent,
                "is_exceeded": is_exceeded,
                "total_cost": round(total_cost, 2),
                "readings_count": readings_count
            }

        water_summary = calculate_resource_summary("AGUA")
        energy_summary = calculate_resource_summary("ENERGIA")
        total_combined_cost = water_summary["total_cost"] + energy_summary["total_cost"]

        return jsonify({
            "month": month,
            "year": year,
            "water": water_summary,
            "energy": energy_summary,
            "total_combined_cost": round(total_combined_cost, 2)
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar resumen de recursos: {str(e)}"}), 500


@utility_bp.route("/utilities/targets", methods=["GET"])
def get_targets():
    """Retorna las metas ambientales de consumo."""
    try:
        year = request.args.get("year", type=int)
        month = request.args.get("month", type=int)

        conditions = ["1=1"]
        params = []
        if year:
            conditions.append("target_year = %s")
            params.append(year)
        if month:
            conditions.append("target_month = %s")
            params.append(month)

        query = f"""
            SELECT id, resource_type, target_year, target_month,
                   CAST(target_consumption AS DOUBLE) AS target_consumption, created_at
            FROM utility_targets
            WHERE {' AND '.join(conditions)}
            ORDER BY target_year DESC, target_month DESC, resource_type ASC
        """
        targets = fetch_all(query, tuple(params)) or []
        return jsonify({"targets": targets}), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar metas: {str(e)}"}), 500


@utility_bp.route("/utilities/targets", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR")
def set_target():
    """
    Establece o edita la meta ambiental de un mes/año.
    TEST-003-B7: Retorna 201 al crear.
    TEST-003-B8: Realiza upsert sin duplicar si ya existe la combinación recurso/año/mes.
    """
    try:
        data = request.get_json() or {}
        resource_type = (data.get("resource_type") or "").strip().upper()
        target_year = data.get("target_year")
        target_month = data.get("target_month")
        target_consumption = data.get("target_consumption")

        if resource_type not in ("AGUA", "ENERGIA") or not target_year or not target_month or target_consumption is None:
            return jsonify({
                "error": "Los campos 'resource_type' (AGUA/ENERGIA), 'target_year', 'target_month' y 'target_consumption' son requeridos"
            }), 400

        try:
            qty_val = float(target_consumption)
            if qty_val <= 0:
                return jsonify({"error": "La meta de consumo debe ser un número positivo mayor a cero"}), 400
        except ValueError:
            return jsonify({"error": "Valor de meta inválido"}), 400

        user_id = g.current_user["sub"]

        upsert_query = """
            INSERT INTO utility_targets (resource_type, target_year, target_month, target_consumption)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE target_consumption = VALUES(target_consumption);
        """
        execute_query(upsert_query, (resource_type, int(target_year), int(target_month), qty_val))

        log_audit(user_id, "SET_TARGET", "UTILITY_TARGET", json.dumps({
            "resource_type": resource_type,
            "year": target_year,
            "month": target_month,
            "target": qty_val
        }))

        return jsonify({
            "message": f"Meta de {resource_type} para {target_month}/{target_year} guardada correctamente",
            "target": {
                "resource_type": resource_type,
                "target_year": int(target_year),
                "target_month": int(target_month),
                "target_consumption": qty_val
            }
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al guardar meta: {str(e)}"}), 500
