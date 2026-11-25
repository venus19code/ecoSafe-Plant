"""
Pruebas Unitarias y de Integración para el Módulo de Dashboard General (Spec 006)
Cubre casos de prueba:
- TEST-006-B1: Obtener KPIs consolidados de la planta (200 OK)
- TEST-006-B2: Filtrado de KPIs por periodo (200 OK)
- TEST-006-B3: Obtener series de residuos por categoría (12 meses)
- TEST-006-B4: Obtener consumo mensual de agua/energía vs metas
- TEST-006-B5: Obtener estadísticas de seguridad SST
- TEST-006-B6: Sin accidentes registrados -> valor base alto
- TEST-006-B7: Rechazo de métodos no permitidos (405 Method Not Allowed)
- Acceso no autorizado sin token JWT (401 Unauthorized)
"""

import unittest
from datetime import date, timedelta
from unittest.mock import patch
from app import app
from utils.auth import create_token


def _make_token(user_id, name, email, role, area):
    return create_token({
        "id": user_id,
        "name": name,
        "email": email,
        "role": role,
        "area": area,
    })


class TestDashboardModule(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Tokens para diferentes roles
        self.admin_headers = {
            "Authorization": f"Bearer {_make_token(1, 'Administrador', 'admin@ecosafe.com', 'ADMIN', 'Dirección General')}",
            "Content-Type": "application/json"
        }
        self.supervisor_headers = {
            "Authorization": f"Bearer {_make_token(2, 'Supervisor', 'supervisor@ecosafe.com', 'SUPERVISOR', 'Beneficio')}",
            "Content-Type": "application/json"
        }
        self.operario_headers = {
            "Authorization": f"Bearer {_make_token(3, 'Operario', 'operario@ecosafe.com', 'OPERARIO', 'Empaque')}",
            "Content-Type": "application/json"
        }

    # Acceso no autorizado
    def test_endpoints_require_token(self):
        for endpoint in ("/api/dashboard/kpis", "/api/dashboard/waste-chart",
                         "/api/dashboard/utilities-chart", "/api/dashboard/safety-stats"):
            response = self.app.get(endpoint)
            self.assertEqual(response.status_code, 401, endpoint)

    # TEST-006-B7: Métodos no permitidos
    def test_method_not_allowed(self):
        response = self.app.post("/api/dashboard/kpis", headers=self.admin_headers, json={})
        self.assertEqual(response.status_code, 405)

        response = self.app.delete("/api/dashboard/waste-chart", headers=self.admin_headers)
        self.assertEqual(response.status_code, 405)

    # TEST-006-B1: Obtener KPIs consolidados
    @patch("routes.dashboard_routes.fetch_one")
    def test_get_kpis_success(self, mock_fetch_one):
        # Respuestas en el mismo orden en que el endpoint consulta los KPIs
        mock_fetch_one.side_effect = [
            {"total_kg": 12500.5, "valorized_kg": 8500.0},          # Residuos
            {"total_water": 450.2},                                  # Agua
            {"target_consumption": 500.0},                           # Meta agua
            {"total_energy": 3200.0},                                # Energía
            {"target_consumption": 3500.0},                          # Meta energía
            {"last_accident_date": date.today() - timedelta(days=45)},  # SST
            {"open_count": 2},                                       # Incidentes abiertos
            {"total_inspections": 20, "compliant_count": 18},        # EPP
            {"crit_count": 3},                                       # Peligros críticos
        ]

        response = self.app.get("/api/dashboard/kpis", headers=self.supervisor_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["waste_total_kg"], 12500.5)
        self.assertAlmostEqual(data["waste_valorization_percent"], 68.0, places=1)
        self.assertEqual(data["water_consumption_m3"], 450.2)
        self.assertEqual(data["water_target_m3"], 500.0)
        self.assertEqual(data["energy_consumption_kwh"], 3200.0)
        self.assertEqual(data["energy_target_kwh"], 3500.0)
        self.assertEqual(data["days_without_accidents"], 45)
        self.assertEqual(data["open_incidents"], 2)
        self.assertEqual(data["epp_compliance_percent"], 90.0)
        self.assertEqual(data["critical_hazards_count"], 3)

    # TEST-006-B2: Filtrado de KPIs por periodo
    @patch("routes.dashboard_routes.fetch_one")
    def test_get_kpis_with_date_filter(self, mock_fetch_one):
        mock_fetch_one.side_effect = [
            {"total_kg": 5000.0, "valorized_kg": 3000.0},
            {"total_water": 200.0},
            {"target_consumption": 250.0},
            {"total_energy": 1500.0},
            {"target_consumption": 1600.0},
            {"last_accident_date": date.today() - timedelta(days=12)},
            {"open_count": 1},
            {"total_inspections": 10, "compliant_count": 10},
            {"crit_count": 1},
        ]

        response = self.app.get(
            "/api/dashboard/kpis?month=11&year=2026",
            headers=self.operario_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["month"], 11)
        self.assertEqual(data["year"], 2026)
        self.assertEqual(data["waste_total_kg"], 5000.0)

    # TEST-006-B3: Series de residuos por categoría (12 meses)
    @patch("routes.dashboard_routes.fetch_all")
    def test_get_waste_chart_data(self, mock_fetch_all):
        categories = [
            {"id": 1, "name": "Aprovechables", "color_code": "#2E7D32"},
            {"id": 2, "name": "No Aprovechables", "color_code": "#424242"},
            {"id": 3, "name": "Peligrosos", "color_code": "#C62828"},
        ]
        rows = [
            {"month_num": 11, "category_id": 1, "category_name": "Aprovechables", "total_kg": 8500.0},
            {"month_num": 11, "category_id": 2, "category_name": "No Aprovechables", "total_kg": 2500.0},
            {"month_num": 11, "category_id": 3, "category_name": "Peligrosos", "total_kg": 1500.0},
        ]
        mock_fetch_all.side_effect = [categories, rows]

        response = self.app.get("/api/dashboard/waste-chart?year=2026", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["year"], 2026)
        self.assertEqual(len(data["labels"]), 12)
        self.assertEqual(len(data["datasets"]), 3)

        first = data["datasets"][0]
        self.assertEqual(first["category_name"], "Aprovechables")
        self.assertEqual(len(first["data"]), 12)
        self.assertEqual(first["data"][10], 8500.0)  # Noviembre (índice 10)
        self.assertEqual(data["monthly_totals"][10], 12500.0)

    # TEST-006-B4: Consumo mensual de agua/energía vs metas
    @patch("routes.dashboard_routes.fetch_all")
    def test_get_utilities_chart_data(self, mock_fetch_all):
        water_rows = [{"month_num": 11, "total_water": 628.0}]
        energy_rows = [{"month_num": 11, "total_energy": 2400.0}]
        target_rows = [
            {"resource_type": "AGUA", "target_month": 11, "target_consumption": 450.0},
            {"resource_type": "ENERGIA", "target_month": 11, "target_consumption": 3200.0},
        ]
        mock_fetch_all.side_effect = [water_rows, energy_rows, target_rows]

        response = self.app.get("/api/dashboard/utilities-chart?year=2026", headers=self.supervisor_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(len(data["labels"]), 12)
        self.assertEqual(data["water"]["unit"], "m3")
        self.assertEqual(data["water"]["consumption"][10], 628.0)
        self.assertEqual(data["water"]["targets"][10], 450.0)
        self.assertEqual(data["energy"]["unit"], "kWh")
        self.assertEqual(data["energy"]["consumption"][10], 2400.0)
        self.assertEqual(data["energy"]["targets"][10], 3200.0)

    # TEST-006-B5: Estadísticas de seguridad SST
    @patch("routes.dashboard_routes.fetch_all")
    @patch("routes.dashboard_routes.fetch_one")
    def test_get_safety_stats(self, mock_fetch_one, mock_fetch_all):
        mock_fetch_one.side_effect = [
            {"last_accident_date": date.today() - timedelta(days=120)},
            {"expired_count": 1, "due_soon_count": 1, "total_deliveries": 5},
        ]
        mock_fetch_all.side_effect = [
            [
                {"general_type": "Mecánico", "count": 2},
                {"general_type": "Físico", "count": 2},
                {"general_type": "Químico", "count": 1},
                {"general_type": "Biológico", "count": 1},
            ],
            [
                {"status": "PENDIENTE", "count": 1},
                {"status": "EN_ATENCION", "count": 1},
                {"status": "RESUELTO", "count": 1},
            ],
        ]

        response = self.app.get("/api/dashboard/safety-stats", headers=self.supervisor_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["days_without_accidents"], 120)
        self.assertEqual(len(data["hazards_distribution"]), 4)
        self.assertEqual(sum(data["incidents_summary"].values()), 3)
        self.assertEqual(data["epp_summary"]["total_deliveries"], 5)
        self.assertEqual(data["epp_summary"]["expired"], 1)

    # TEST-006-B6: Sin accidentes -> valor base alto
    @patch("routes.dashboard_routes.fetch_all")
    @patch("routes.dashboard_routes.fetch_one")
    def test_safety_stats_without_accidents(self, mock_fetch_one, mock_fetch_all):
        mock_fetch_one.side_effect = [
            {"last_accident_date": None},
            {"expired_count": 0, "due_soon_count": 0, "total_deliveries": 0},
        ]
        mock_fetch_all.side_effect = [[], []]

        response = self.app.get("/api/dashboard/safety-stats", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.get_json()["days_without_accidents"], 142)


if __name__ == "__main__":
    unittest.main()
