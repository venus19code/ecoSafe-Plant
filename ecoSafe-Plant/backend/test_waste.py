"""
==========================================================
TESTS FUNCIONALES AUTOMATIZADOS - SPEC 002 (RESIDUOS)
==========================================================
Ejecuta la suite de pruebas unitarias y de integración para validar
TEST-002-B1 hasta TEST-002-B10 según docs/residuos 002/spec.md.
"""

import unittest
import json
from app import app
from utils.auth import create_token

class WasteTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Tokens JWT simulados para roles de prueba
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

    def test_b1_get_waste_types(self):
        """TEST-002-B1: GET /api/waste/types retorna 200 con categorías y tipos precargados."""
        res = self.client.get("/api/waste/types")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("categories", data)
        self.assertIn("types", data)
        print("[TEST PASS] TEST-002-B1: GET /api/waste/types -> 200 OK con categorías y tipos")

    def test_b4_post_record_without_token(self):
        """TEST-002-B4: POST /api/waste/records sin token JWT retorna 401 Unauthorized."""
        res = self.client.post("/api/waste/records", json={
            "waste_type_id": 1,
            "record_date": "2026-11-18",
            "quantity": 100.5,
            "area": "Despulpado",
            "disposal_method": "Compostaje"
        })
        self.assertEqual(res.status_code, 401)
        print("[TEST PASS] TEST-002-B4: POST sin token JWT -> 401 Unauthorized")

    def test_b3_post_record_negative_quantity(self):
        """TEST-002-B3: POST /api/waste/records con quantity negativa retorna 400 Bad Request."""
        headers = {"Authorization": f"Bearer {self.operario_token}"}
        res = self.client.post("/api/waste/records", headers=headers, json={
            "waste_type_id": 1,
            "record_date": "2026-11-18",
            "quantity": -45.0,
            "area": "Despulpado",
            "disposal_method": "Compostaje"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)
        print(f"[TEST PASS] TEST-002-B3: Cantidad negativa -> 400 Bad Request ({data['error']})")

    def test_b8_delete_as_operario_forbidden(self):
        """TEST-002-B8: DELETE /api/waste/records/<id> con rol OPERARIO retorna 403 Forbidden."""
        headers = {"Authorization": f"Bearer {self.operario_token}"}
        res = self.client.delete("/api/waste/records/1", headers=headers)
        self.assertEqual(res.status_code, 403)
        print("[TEST PASS] TEST-002-B8: DELETE con rol OPERARIO -> 403 Forbidden")

    def test_b10_summary_kpis(self):
        """TEST-002-B10: GET /api/waste/summary retorna totales y valorization_percent."""
        res = self.client.get("/api/waste/summary?month=11&year=2026")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_quantity", data)
        self.assertIn("valorization_percent", data)
        self.assertIn("hazardous_quantity", data)
        self.assertIn("categories_summary", data)
        self.assertIn("disposal_summary", data)
        self.assertIsInstance(data["valorization_percent"], (int, float))
        print(f"[TEST PASS] TEST-002-B10: Summary KPIs -> Total: {data['total_quantity']}kg | Aprovechamiento: {data['valorization_percent']}%")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INICIANDO SUITE DE PRUEBAS FUNCIONALES - SPEC 002 (RESIDUOS)")
    print("=" * 60)
    unittest.main(verbosity=2)
