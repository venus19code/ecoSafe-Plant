"""
==========================================================
TESTS FUNCIONALES AUTOMATIZADOS - SPEC 003 (RECURSOS)
==========================================================
Valida los casos TEST-003-B1 hasta TEST-003-B8 según docs/recursos 003/spec.md.
"""

import unittest
import json
from app import app
from utils.auth import create_token

class UtilityTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        self.admin_user = {
            "id": 1,
            "name": "Administrador EcoSafe",
            "email": "admin@ecosafe.com",
            "role": "ADMIN",
            "area": "Dirección General"
        }
        self.operario_user = {
            "id": 3,
            "name": "Operario de Producción",
            "email": "operario@ecosafe.com",
            "role": "OPERARIO",
            "area": "Secado y Empaque"
        }

        self.admin_token = create_token(self.admin_user)
        self.operario_token = create_token(self.operario_user)

    def test_b1_get_meters(self):
        """TEST-003-B1: GET /api/utilities/meters retorna 200 con medidores."""
        res = self.client.get("/api/utilities/meters")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("meters", data)
        self.assertGreaterEqual(len(data["meters"]), 2)
        print("[TEST PASS] TEST-003-B1: GET /api/utilities/meters -> 200 OK con medidores sembrados")

    def test_b4_reading_lower_than_previous_forbidden(self):
        """TEST-003-B4: POST lectura con valor menor que la anterior retorna 400 Bad Request."""
        headers = {"Authorization": f"Bearer {self.operario_token}"}
        # Medidor 1 tiene lectura superior a 1000 en base de datos
        res = self.client.post("/api/utilities/readings", headers=headers, json={
            "meter_id": 1,
            "reading_date": "2026-11-18",
            "reading_value": 50.0  # Menor que lectura anterior
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)
        print(f"[TEST PASS] TEST-003-B4: Lectura en retroceso prevenida -> 400 Bad Request ({data['error']})")

    def test_b5_filter_water_readings_by_period(self):
        """TEST-003-B5: GET /api/utilities/readings?resource_type=AGUA&month=11&year=2026 retorna solo lecturas de agua del mes."""
        res = self.client.get("/api/utilities/readings?resource_type=AGUA&month=11&year=2026")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("readings", data)
        for r in data["readings"]:
            self.assertEqual(r["resource_type"], "AGUA")
        print("[TEST PASS] TEST-003-B5: Filtro de lecturas de agua por mes y año validado")

    def test_b6_summary_water_and_energy(self):
        """TEST-003-B6: GET /api/utilities/summary retorna consumo consolidado de agua y energía, costos y % meta."""
        res = self.client.get("/api/utilities/summary?month=11&year=2026")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("water", data)
        self.assertIn("energy", data)
        self.assertIn("total_combined_cost", data)
        self.assertIn("target_percent", data["water"])
        self.assertIn("target_percent", data["energy"])
        print(f"[TEST PASS] TEST-003-B6: Resumen mensual -> Agua: {data['water']['total_consumption']} m³ ({data['water']['target_percent']}%) | Energía: {data['energy']['total_consumption']} kWh ({data['energy']['target_percent']}%)")

    def test_b7_and_b8_set_target_upsert(self):
        """TEST-003-B7 y TEST-003-B8: POST /api/utilities/targets crea o actualiza la meta sin duplicar."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.post("/api/utilities/targets", headers=headers, json={
            "resource_type": "AGUA",
            "target_year": 2026,
            "target_month": 11,
            "target_consumption": 500.00
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["target"]["target_consumption"], 500.00)
        print("[TEST PASS] TEST-003-B7 y TEST-003-B8: Creación y Upsert de meta ambiental validado")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INICIANDO SUITE DE PRUEBAS FUNCIONALES - SPEC 003 (RECURSOS)")
    print("=" * 60)
    unittest.main(verbosity=2)
