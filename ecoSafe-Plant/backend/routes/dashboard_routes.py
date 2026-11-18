from flask import Blueprint, request, jsonify
from database import fetch_one, fetch_all
from datetime import datetime, date

dashboard_bp = Blueprint("dashboard", __name__)

MONTH_NAMES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

@dashboard_bp.route("/dashboard/kpis", methods=["GET"])
def get_dashboard_kpis():
    """
    Retorna los valores consolidados de los KPIs clave para las tarjetas principales.
    TEST-006-B1: Retorna 200 con todos los campos requeridos:
      waste_total_kg, waste_valorization_percent, water_consumption_m3, water_target_m3,
      energy_consumption_kwh, energy_target_kwh, days_without_accidents, open_incidents,
      epp_compliance_percent, critical_hazards_count.
    TEST-006-B2: Filtro por mes y año.
    """
    try:
        now = datetime.now()
        month = request.args.get("month", default=now.month, type=int)
        year = request.args.get("year", default=now.year, type=int)
        area = request.args.get("area", type=str)

        area_filter_waste = ""
        params_waste = [month, year]
        if area:
            area_filter_waste = "AND LOWER(wr.area) LIKE %s"
            params_waste.append(f"%{area.strip().lower()}%")

        # 1. Residuos: total y valorizados
        waste_row = fetch_one(f"""
            SELECT 
                COALESCE(SUM(wr.quantity), 0) AS total_kg,
                COALESCE(SUM(CASE 
                    WHEN LOWER(wr.disposal_method) IN ('compostaje', 'lombricultura', 'alimentación animal', 'alimentacion animal', 'venta como subproducto', 'reciclaje', 'reciclaje / gestor autorizado', 'reutilización', 'reutilizacion')
                         OR (wt.category_id IN (1, 2) AND LOWER(wr.disposal_method) NOT LIKE '%%relleno%%')
                    THEN wr.quantity ELSE 0 
                END), 0) AS valorized_kg
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            WHERE MONTH(wr.record_date) = %s AND YEAR(wr.record_date) = %s
            {area_filter_waste}
        """, tuple(params_waste))

        waste_total_kg = float(waste_row["total_kg"]) if waste_row else 0.0
        waste_valorized_kg = float(waste_row["valorized_kg"]) if waste_row else 0.0
        waste_valorization_percent = round((waste_valorized_kg / waste_total_kg) * 100.0, 1) if waste_total_kg > 0 else 0.0

        # 2. Agua
        water_row = fetch_one("""
            SELECT COALESCE(SUM(ur.consumption), 0) AS total_water
            FROM utility_readings ur
            JOIN utility_meters um ON ur.meter_id = um.id
            WHERE um.resource_type = 'AGUA'
              AND MONTH(ur.reading_date) = %s AND YEAR(ur.reading_date) = %s
        """, (month, year))
        water_consumption_m3 = float(water_row["total_water"]) if water_row else 0.0

        water_target_row = fetch_one("""
            SELECT target_consumption FROM utility_targets
            WHERE resource_type = 'AGUA' AND target_year = %s AND target_month = %s
        """, (year, month))
        water_target_m3 = float(water_target_row["target_consumption"]) if water_target_row else 450.0

        # 3. Energía
        energy_row = fetch_one("""
            SELECT COALESCE(SUM(ur.consumption), 0) AS total_energy
            FROM utility_readings ur
            JOIN utility_meters um ON ur.meter_id = um.id
            WHERE um.resource_type = 'ENERGIA'
              AND MONTH(ur.reading_date) = %s AND YEAR(ur.reading_date) = %s
        """, (month, year))
        energy_consumption_kwh = float(energy_row["total_energy"]) if energy_row else 0.0

        energy_target_row = fetch_one("""
            SELECT target_consumption FROM utility_targets
            WHERE resource_type = 'ENERGIA' AND target_year = %s AND target_month = %s
        """, (year, month))
        energy_target_kwh = float(energy_target_row["target_consumption"]) if energy_target_row else 3200.0

        # 4. SST: Días sin accidentes
        today = date.today()
        accident_row = fetch_one("""
            SELECT MAX(incident_date) AS last_accident_date
            FROM sst_incidents
            WHERE incident_type IN ('ACCIDENTE_LEVE', 'ACCIDENTE_GRAVE')
        """)
        if accident_row and accident_row.get("last_accident_date"):
            last_date = accident_row["last_accident_date"]
            if hasattr(last_date, "date"):
                last_date = last_date.date()
            days_without_accidents = (today - last_date).days
        else:
            days_without_accidents = 142  # Registro histórico base positivo

        # 5. Incidentes abiertos (PENDIENTE o EN_ATENCION)
        incidents_open_row = fetch_one("""
            SELECT COUNT(id) AS open_count
            FROM sst_incidents
            WHERE status IN ('PENDIENTE', 'EN_ATENCION')
        """)
        open_incidents = int(incidents_open_row["open_count"]) if incidents_open_row else 0

        # 6. Cumplimiento EPP
        epp_insp_row = fetch_one("""
            SELECT 
                COUNT(id) AS total_inspections,
                COUNT(CASE WHEN is_compliant = TRUE THEN 1 END) AS compliant_count
            FROM epp_inspections
        """)
        total_insp = int(epp_insp_row["total_inspections"]) if epp_insp_row else 0
        compliant_insp = int(epp_insp_row["compliant_count"]) if epp_insp_row else 0
        epp_compliance_percent = round((compliant_insp / total_insp) * 100.0, 1) if total_insp > 0 else 100.0

        # 7. Peligros críticos activos en la planta
        crit_hazards_row = fetch_one("""
            SELECT COUNT(id) AS crit_count
            FROM sst_hazards
            WHERE risk_level = 'CRITICO' AND status != 'CONTROLADO'
        """)
        critical_hazards_count = int(crit_hazards_row["crit_count"]) if crit_hazards_row else 0

        return jsonify({
            "month": month,
            "year": year,
            "waste_total_kg": round(waste_total_kg, 2),
            "waste_valorization_percent": waste_valorization_percent,
            "water_consumption_m3": round(water_consumption_m3, 2),
            "water_target_m3": round(water_target_m3, 2),
            "energy_consumption_kwh": round(energy_consumption_kwh, 2),
            "energy_target_kwh": round(energy_target_kwh, 2),
            "days_without_accidents": days_without_accidents,
            "open_incidents": open_incidents,
            "epp_compliance_percent": epp_compliance_percent,
            "critical_hazards_count": critical_hazards_count
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar KPIs del dashboard: {str(e)}"}), 500


@dashboard_bp.route("/dashboard/waste-chart", methods=["GET"])
def get_waste_chart():
    """
    Retorna series mensuales de residuos para el año indicado agrupadas por categoría.
    TEST-006-B3: Retorna array de 12 meses con totales por categoría de residuo (incluye meses con 0).
    """
    try:
        now = datetime.now()
        year = request.args.get("year", default=now.year, type=int)
        area = request.args.get("area", type=str)

        categories = fetch_all("SELECT id, name, color_code FROM waste_categories ORDER BY id ASC") or []

        area_filter = ""
        params_base = [year]
        if area:
            area_filter = "AND LOWER(wr.area) LIKE %s"
            params_base.append(f"%{area.strip().lower()}%")

        # Consultar agrupado por mes y categoría
        query = f"""
            SELECT 
                MONTH(wr.record_date) AS month_num,
                wc.id AS category_id,
                wc.name AS category_name,
                COALESCE(SUM(wr.quantity), 0) AS total_kg
            FROM waste_records wr
            JOIN waste_types wt ON wr.waste_type_id = wt.id
            JOIN waste_categories wc ON wt.category_id = wc.id
            WHERE YEAR(wr.record_date) = %s
            {area_filter}
            GROUP BY MONTH(wr.record_date), wc.id, wc.name
            ORDER BY month_num ASC, wc.id ASC
        """
        rows = fetch_all(query, tuple(params_base)) or []

        # Estructurar datasets de 12 meses por cada categoría
        datasets = []
        for cat in categories:
            data_12_months = [0.0] * 12
            for r in rows:
                if r["category_id"] == cat["id"]:
                    m_idx = int(r["month_num"]) - 1
                    if 0 <= m_idx < 12:
                        data_12_months[m_idx] = round(float(r["total_kg"]), 2)

            datasets.append({
                "category_id": cat["id"],
                "category_name": cat["name"],
                "color_code": cat.get("color_code", "#2d6a4f"),
                "data": data_12_months
            })

        # Totales mensuales generales
        monthly_totals = [0.0] * 12
        for ds in datasets:
            for idx, val in enumerate(ds["data"]):
                monthly_totals[idx] += val
        monthly_totals = [round(x, 2) for x in monthly_totals]

        return jsonify({
            "year": year,
            "labels": MONTH_NAMES_ES,
            "datasets": datasets,
            "monthly_totals": monthly_totals
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar gráfico de residuos: {str(e)}"}), 500


@dashboard_bp.route("/dashboard/utilities-chart", methods=["GET"])
def get_utilities_chart():
    """
    Retorna consumos mensuales de agua y energía eléctrica junto con sus metas para cada mes del año.
    TEST-006-B4: Retorna consumo mensual de agua y energía de los 12 meses junto con metas.
    """
    try:
        now = datetime.now()
        year = request.args.get("year", default=now.year, type=int)

        # Consumo de Agua mensual
        water_rows = fetch_all("""
            SELECT MONTH(ur.reading_date) AS month_num,
                   COALESCE(SUM(ur.consumption), 0) AS total_water
            FROM utility_readings ur
            JOIN utility_meters um ON ur.meter_id = um.id
            WHERE um.resource_type = 'AGUA' AND YEAR(ur.reading_date) = %s
            GROUP BY MONTH(ur.reading_date)
            ORDER BY month_num ASC
        """, (year,)) or []

        water_data = [0.0] * 12
        for r in water_rows:
            idx = int(r["month_num"]) - 1
            if 0 <= idx < 12:
                water_data[idx] = round(float(r["total_water"]), 2)

        # Consumo de Energía mensual
        energy_rows = fetch_all("""
            SELECT MONTH(ur.reading_date) AS month_num,
                   COALESCE(SUM(ur.consumption), 0) AS total_energy
            FROM utility_readings ur
            JOIN utility_meters um ON ur.meter_id = um.id
            WHERE um.resource_type = 'ENERGIA' AND YEAR(ur.reading_date) = %s
            GROUP BY MONTH(ur.reading_date)
            ORDER BY month_num ASC
        """, (year,)) or []

        energy_data = [0.0] * 12
        for r in energy_rows:
            idx = int(r["month_num"]) - 1
            if 0 <= idx < 12:
                energy_data[idx] = round(float(r["total_energy"]), 2)

        # Metas de Agua y Energía para el año
        target_rows = fetch_all("""
            SELECT resource_type, target_month, target_consumption
            FROM utility_targets
            WHERE target_year = %s
        """, (year,)) or []

        water_targets = [450.0] * 12  # Valor estándar por defecto
        energy_targets = [3200.0] * 12

        for t in target_rows:
            m_idx = int(t["target_month"]) - 1
            if 0 <= m_idx < 12:
                if t["resource_type"] == "AGUA":
                    water_targets[m_idx] = round(float(t["target_consumption"]), 2)
                elif t["resource_type"] == "ENERGIA":
                    energy_targets[m_idx] = round(float(t["target_consumption"]), 2)

        return jsonify({
            "year": year,
            "labels": MONTH_NAMES_ES,
            "water": {
                "unit": "m3",
                "consumption": water_data,
                "targets": water_targets
            },
            "energy": {
                "unit": "kWh",
                "consumption": energy_data,
                "targets": energy_targets
            }
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al generar gráfico de recursos: {str(e)}"}), 500


@dashboard_bp.route("/dashboard/safety-stats", methods=["GET"])
def get_safety_stats():
    """
    Retorna métricas de SST para visualizaciones de dona y resumen ejecutivo.
    TEST-006-B5: Días sin accidentes calculado con DATEDIFF frente al último accidente.
    """
    try:
        today = date.today()

        # Días sin accidentes
        accident_row = fetch_one("""
            SELECT MAX(incident_date) AS last_accident_date
            FROM sst_incidents
            WHERE incident_type IN ('ACCIDENTE_LEVE', 'ACCIDENTE_GRAVE')
        """)
        if accident_row and accident_row.get("last_accident_date"):
            last_date = accident_row["last_accident_date"]
            if hasattr(last_date, "date"):
                last_date = last_date.date()
            days_without_accidents = (today - last_date).days
        else:
            days_without_accidents = 142

        # Distribución de peligros por clasificación
        hazard_types = fetch_all("""
            SELECT 
                SUBSTRING_INDEX(hazard_type, ' /', 1) AS general_type,
                COUNT(id) AS count
            FROM sst_hazards
            GROUP BY general_type
            ORDER BY count DESC
        """) or []

        # Incidentes por estado
        incident_rows = fetch_all("""
            SELECT status, COUNT(id) AS count
            FROM sst_incidents
            GROUP BY status
        """) or []
        incident_status_map = {"PENDIENTE": 0, "EN_ATENCION": 0, "RESUELTO": 0, "DESESTIMADO": 0}
        for ir in incident_rows:
            incident_status_map[ir["status"]] = int(ir["count"])

        # EPP resumen
        today_str = today.isoformat()
        epp_row = fetch_one(f"""
            SELECT 
                COUNT(CASE WHEN next_renewal_date <= '{today_str}' THEN 1 END) AS expired_count,
                COUNT(CASE WHEN next_renewal_date > '{today_str}' AND next_renewal_date <= DATE_ADD('{today_str}', INTERVAL 30 DAY) THEN 1 END) AS due_soon_count,
                COUNT(id) AS total_deliveries
            FROM epp_deliveries
        """)

        return jsonify({
            "days_without_accidents": days_without_accidents,
            "hazards_distribution": [
                {"label": h["general_type"], "count": int(h["count"])} for h in hazard_types
            ],
            "incidents_summary": incident_status_map,
            "epp_summary": {
                "expired": int(epp_row["expired_count"]) if epp_row else 0,
                "due_soon": int(epp_row["due_soon_count"]) if epp_row else 0,
                "total_deliveries": int(epp_row["total_deliveries"]) if epp_row else 0
            }
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar estadísticas de seguridad: {str(e)}"}), 500
