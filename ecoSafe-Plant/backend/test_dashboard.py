"""
Pruebas Unitarias y de Integración para el Módulo de Dashboard General (Spec 006)
Cubre casos de prueba:
- TEST-006-B1: Obtener KPIs consolidados de la planta (200 OK)
- TEST-006-B2: Filtrado de KPIs por rango de fecha (200 OK)
- TEST-006-B3: Obtener datos para gráfico de residuos por categoría (200 OK)
- TEST-006-B4: Obtener datos para gráfico de consumo vs metas (200 OK)
- TEST-006-B5: Obtener estadísticas de seguridad SST (200 OK)
- TEST-006-B6: Rechazo de métodos no permitidos (POST/PUT/DELETE deben dar 405 Method Not Allowed)
- TEST-006-B7: Acceso no autorizado sin token JWT (401 Unauthorized)
"""

import unittest
from unittest.mock import patch, MagicMock
from app import app
from utils.auth import generate_token

class TestDashboardModule(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Generar tokens para diferentes roles
        self.admin_token = generate_token({"id": 1, "username": "admin", "role": "admin"})
        self.supervisor_token = generate_token({"id": 2, "username": "supervisor_sst", "role": "supervisor"})
        self.operario_token = generate_token({"id": 3, "username": "operario1", "role": "operario"})
        
        self.admin_headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        self.supervisor_headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "Content-Type": "application/json"
        }
        self.operario_headers = {
            "Authorization": f"Bearer {self.operario_token}",
            "Content-Type": "application/json"
        }

    # TEST-006-B7: Rechazo sin token
    def test_kpis_unauthorized(self):
        response = self.app.get("/api/dashboard/kpis")
        self.assertEqual(response.status_code, 401)

    # TEST-006-B6: Métodos no permitidos
    def test_method_not_allowed(self):
        response = self.app.post("/api/dashboard/kpis", headers=self.admin_headers, json={})
        self.assertEqual(response.status_code, 405)
        
        response = self.app.delete("/api/dashboard/waste-chart", headers=self.admin_headers)
        self.assertEqual(response.status_code, 405)

    # TEST-006-B1: Obtener KPIs consolidados
    @patch("routes.dashboard_routes.fetch_one")
    def test_get_kpis_success(self, mock_fetch_one):
        # Simular respuestas secuenciales de fetch_one para cada consulta de KPI
        mock_fetch_one.side_effect = [
            {"total_kg": 12500.5, "hazardous_kg": 1500.0, "valorized_kg": 8500.0},  # Residuos
            {"water_m3": 450.2},  # Agua
            {"water_target_m3": 500.0},  # Meta Agua
            {"energy_kwh": 3200.0},  # Energía
            {"energy_target_kwh": 3500.0},  # Meta Energía
            {"days_since_accident": 45},  # Días sin accidentes
            {"open_incidents": 2},  # Incidentes abiertos
            {"total_deliveries": 20, "active_count": 18, "expired_count": 2},  # Cumplimiento EPP
            {"critical_hazards": 3}  # Peligros críticos
        ]

        response = self.app.get("/api/dashboard/kpis", headers=self.supervisor_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        kpis = data["data"]
        self.assertIn("waste", kpis)
        self.assertIn("utilities", kpis)
        self.assertIn("safety", kpis)
        self.assertIn("epp", kpis)
        self.assertEqual(kpis["waste"]["total_waste_kg"], 12500.5)
        self.assertAlmostEqual(kpis["waste"]["valorization_rate"], 68.0, places=1)
        self.assertEqual(kpis["safety"]["days_without_accidents"], 45)
        self.assertEqual(kpis["safety"]["critical_hazards_count"], 3)
        self.assertEqual(kpis["epp"]["compliance_rate"], 90.0)

    # TEST-006-B2: Filtrado de KPIs con parámetros start_date y end_date
    @patch("routes.dashboard_routes.fetch_one")
    def test_get_kpis_with_date_filter(self, mock_fetch_one):
        mock_fetch_one.side_effect = [
            {"total_kg": 5000.0, "hazardous_kg": 500.0, "valorized_kg": 3000.0},
            {"water_m3": 200.0},
            {"water_target_m3": 250.0},
            {"energy_kwh": 1500.0},
            {"energy_target_kwh": 1600.0},
            {"days_since_accident": 12},
            {"open_incidents": 1},
            {"total_deliveries": 10, "active_count": 10, "expired_count": 0},
            {"critical_hazards": 1}
        ]

        response = self.app.get("/api/dashboard/kpis?start_date=2026-11-01&end_date=2026-11-30", headers=self.operario_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["waste"]["total_waste_kg"], 5000.0)

    # TEST-006-B3: Gráfico de residuos por categoría
    @patch("routes.dashboard_routes.fetch_all")
    def test_get_waste_chart_data(self, mock_fetch_all):
        mock_fetch_all.return_value = [
            {"category_name": "Aprovechables", "color_code": "#2E7D32", "total_kg": 8500.0, "percentage": 68.0},
            {"category_name": "No Aprovechables", "color_code": "#424242", "total_kg": 2500.0, "percentage": 20.0},
            {"category_name": "Peligrosos", "color_code": "#C62828", "total_kg": 1500.0, "percentage": 12.0}
        ]

        response = self.app.get("/api/dashboard/waste-chart", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 3)
        self.assertEqual(data["data"][0]["category_name"], "Aprovechables")

    # TEST-006-B4: Gráfico de consumo de servicios públicos
    @patch("routes.dashboard_routes.fetch_all")
    def test_get_utilities_chart_data(self, mock_fetch_all):
        mock_fetch_all.return_value = [
            {"month": "2026-09", "service_type": "AGUA", "actual_consumption": 410.0, "target_consumption": 450.0},
            {"month": "2026-09", "service_type": "ENERGIA", "actual_consumption": 3100.0, "target_consumption": 3500.0},
            {"month": "2026-10", "service_type": "AGUA", "actual_consumption": 430.0, "target_consumption": 450.0},
            {"month": "2026-10", "service_type": "ENERGIA", "actual_consumption": 3300.0, "target_consumption": 3500.0}
        ]

        response = self.app.get("/api/dashboard/utilities-chart?months=6", headers=self.supervisor_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["data"]), 0)

    # TEST-006-B5: Estadísticas de seguridad SST
    @patch("routes.dashboard_routes.fetch_all")
    @patch("routes.dashboard_routes.fetch_one")
    def test_get_safety_stats(self, mock_fetch_one, mock_fetch_all):
        mock_fetch_one.return_value = {"days_without_accident": 120}
        mock_fetch_all.side_effect = [
            [
                {"risk_level": "BAJO", "count": 2},
                {"risk_level": "MEDIO", "count": 2},
                {"risk_level": "ALTO", "count": 1},
                {"risk_level": "CRITICO", "count": 1}
            ],
            [
                {"status": "REPORTADO", "count": 2},
                {"status": "INVESTIGACION", "count": 1},
                {"status": "RESUELTO", "count": 5}
            ]
        ]

        response = self.app.get("/api/dashboard/safety-stats", headers=self.supervisor_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["days_without_accident"], 120)
        self.assertEqual(len(data["data"]["risk_distribution"]), 4)
        self.assertEqual(len(data["data"]["incident_status_distribution"]), 3)

if __name__ == "__main__":
    unittest.main()
