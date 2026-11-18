"""
==========================================================
TESTS FUNCIONALES AUTOMATIZADOS - SPEC 005 (EPP)
==========================================================
Valida los casos TEST-005-B1 hasta TEST-005-B9 según docs/epp 005/spec.md.
"""

import unittest
import json
from app import app
from utils.auth import create_token

class EppTestCase(unittest.TestCase):
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
        self.supervisor_user = {
            "id": 2,
            "name": "Supervisor de Planta",
            "email": "supervisor@ecosafe.com",
            "role": "SUPERVISOR",
            "area": "Beneficio y Fermentación"
        }
        self.operario_user = {
            "id": 3,
            "name": "Operario de Producción",
            "email": "operario@ecosafe.com",
            "role": "OPERARIO",
            "area": "Secado y Empaque"
        }

        self.admin_token = create_token(self.admin_user)
        self.supervisor_token = create_token(self.supervisor_user)
        self.operario_token = create_token(self.operario_user)

    def test_b1_and_b2_catalog_and_category_filter(self):
        """TEST-005-B1 y TEST-005-B2: Catálogo de EPP y filtro por categoría (MANOS)."""
        res = self.client.get("/api/epp/catalog")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("catalog", data)
        self.assertGreaterEqual(len(data["catalog"]), 7)
        print(f"[TEST PASS] TEST-005-B1: Catálogo EPP sembrado -> 200 OK ({len(data['catalog'])} elementos)")

        res_manos = self.client.get("/api/epp/catalog?category=MANOS")
        self.assertEqual(res_manos.status_code, 200)
        data_manos = res_manos.get_json()
        for item in data_manos["catalog"]:
            self.assertEqual(item["category"], "MANOS")
        print("[TEST PASS] TEST-005-B2: Filtro de categoría MANOS validado")

    def test_b3_create_catalog_item(self):
        """TEST-005-B3: POST /api/epp/catalog con datos válidos crea elemento con status 201."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.post("/api/epp/catalog", headers=headers, json={
            "name": "Arnés de Seguridad Multipropósito para Alturas",
            "category": "CUERPO",
            "standard_code": "ANSI Z359.11",
            "lifespan_days": 365,
            "description": "Arnés de cuerpo entero con 4 argollas para mantenimiento en silos",
            "stock_quantity": 8
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["item"]["category"], "CUERPO")
        print("[TEST PASS] TEST-005-B3: Creación de EPP en catálogo -> 201 Created")

    def test_b4_and_b5_delivery_renewal_calculation(self):
        """TEST-005-B4 y TEST-005-B5: Cálculo automático de next_renewal_date = delivery_date + lifespan_days."""
        headers = {"Authorization": f"Bearer {self.supervisor_token}"}
        # EPP con ID 6 (Guantes de carnaza reforzada) tiene lifespan_days = 90
        res = self.client.post("/api/epp/deliveries", headers=headers, json={
            "epp_id": 6,
            "worker_id": 3,
            "delivery_date": "2026-11-17",
            "quantity": 1,
            "reason": "DOTACION_PERIODICA"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        delivery = data["delivery"]
        # TEST-005-B5: 2026-11-17 + 90 días = 2027-02-15
        self.assertEqual(delivery["next_renewal_date"], "2027-02-15")
        print(f"[TEST PASS] TEST-005-B4 & B5: Próxima renovación calculada con exactitud matemática: 2026-11-17 + 90d = {delivery['next_renewal_date']}")

    def test_b6_filter_deliveries_by_worker(self):
        """TEST-005-B6: GET /api/epp/deliveries?worker_id=3 retorna solo entregas del trabajador 3."""
        res = self.client.get("/api/epp/deliveries?worker_id=3")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for d in data["deliveries"]:
            self.assertEqual(d["worker_id"], 3)
        print("[TEST PASS] TEST-005-B6: Filtro de entregas por colaborador validado")

    def test_b8_inspection_non_compliant_without_deficiencies_error(self):
        """TEST-005-B8: POST /api/epp/inspections con is_compliant=false sin deficiencies_found retorna 400."""
        headers = {"Authorization": f"Bearer {self.supervisor_token}"}
        res = self.client.post("/api/epp/inspections", headers=headers, json={
            "worker_id": 3,
            "inspection_date": "2026-11-18",
            "area": "Despulpado y Fermentación",
            "is_compliant": False
            # Falta deficiencies_found
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)
        print(f"[TEST PASS] TEST-005-B8: Inspección no conforme sin detalles rechazada -> 400 Bad Request ({data['error']})")

    def test_b7_inspection_valid(self):
        """TEST-005-B7: POST /api/epp/inspections con datos válidos retorna 201."""
        headers = {"Authorization": f"Bearer {self.supervisor_token}"}
        res = self.client.post("/api/epp/inspections", headers=headers, json={
            "worker_id": 3,
            "inspection_date": "2026-11-18",
            "area": "Secado y Empaque",
            "is_compliant": True,
            "corrective_actions": "Uso de EPP 100% conforme durante la ronda de supervisión"
        })
        self.assertEqual(res.status_code, 201)
        print("[TEST PASS] TEST-005-B7: Inspección de EPP registrada -> 201 Created")

    def test_b9_renewals_due(self):
        """TEST-005-B9: GET /api/epp/renewals-due retorna dotaciones vencidas y próximas."""
        res = self.client.get("/api/epp/renewals-due")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("renewals", data)
        self.assertIn("expired_count", data)
        self.assertIn("due_soon_count", data)
        self.assertGreaterEqual(data["expired_count"], 1)
        print(f"[TEST PASS] TEST-005-B9: Consulta de renovaciones pendientes -> {data['expired_count']} vencidas, {data['due_soon_count']} próximas a vencer")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INICIANDO SUITE DE PRUEBAS FUNCIONALES - SPEC 005 (EPP)")
    print("=" * 60)
    unittest.main(verbosity=2)
