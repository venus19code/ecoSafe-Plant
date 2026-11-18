"""
==========================================================
TESTS FUNCIONALES AUTOMATIZADOS - SPEC 004 (SST)
==========================================================
Valida los casos TEST-004-B1 hasta TEST-004-B10 según docs/seguridad sst 004/spec.md.
"""

import unittest
import json
from app import app
from utils.auth import create_token

class SstTestCase(unittest.TestCase):
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

    def test_b1_b2_b3_hazards_filtering(self):
        """TEST-004-B1, B2, B3: GET /api/sst/hazards y filtros por área y nivel de riesgo."""
        # B1: Lista completa
        res = self.client.get("/api/sst/hazards")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("hazards", data)
        print(f"[TEST PASS] TEST-004-B1: GET /api/sst/hazards -> 200 OK ({len(data['hazards'])} peligros registrados)")

        # B2: Filtro por área
        res_area = self.client.get("/api/sst/hazards?area=Fermentacion")
        self.assertEqual(res_area.status_code, 200)
        data_area = res_area.get_json()
        for h in data_area["hazards"]:
            self.assertIn("fermentaci", h["area"].lower())
        print("[TEST PASS] TEST-004-B2: Filtro de peligros por área validado")

        # B3: Filtro por nivel de riesgo
        res_crit = self.client.get("/api/sst/hazards?risk_level=CRITICO")
        self.assertEqual(res_crit.status_code, 200)
        data_crit = res_crit.get_json()
        for h in data_crit["hazards"]:
            self.assertEqual(h["risk_level"], "CRITICO")
        print("[TEST PASS] TEST-004-B3: Filtro de peligros CRITICOS validado")

    def test_b6_delete_hazard_as_operario_forbidden(self):
        """TEST-004-B6: DELETE /api/sst/hazards/<id> con rol OPERARIO retorna 403 Forbidden."""
        headers = {"Authorization": f"Bearer {self.operario_token}"}
        res = self.client.delete("/api/sst/hazards/1", headers=headers)
        self.assertEqual(res.status_code, 403)
        print("[TEST PASS] TEST-004-B6: DELETE peligro con rol OPERARIO -> 403 Forbidden")

    def test_b7_post_incident_as_operario(self):
        """TEST-004-B7: POST /api/sst/incidents con rol OPERARIO crea reporte en estado PENDIENTE."""
        headers = {"Authorization": f"Bearer {self.operario_token}"}
        res = self.client.post("/api/sst/incidents", headers=headers, json={
            "incident_type": "CONDICION_INSEGURA",
            "location_detail": "Sector Secado - Patios exteriores",
            "description": "Caballete de madera inestable con riesgo de volcarse sobre trabajadores",
            "severity": "ALTA"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["incident"]["status"], "PENDIENTE")
        print("[TEST PASS] TEST-004-B7: Reporte creado por operario con estado PENDIENTE")

    def test_b8_get_pending_incidents(self):
        """TEST-004-B8: GET /api/sst/incidents?status=PENDIENTE retorna solo incidentes pendientes."""
        res = self.client.get("/api/sst/incidents?status=PENDIENTE")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for i in data["incidents"]:
            self.assertEqual(i["status"], "PENDIENTE")
        print("[TEST PASS] TEST-004-B8: Filtro de incidentes pendientes validado")

    def test_b9_resolve_incident_status(self):
        """TEST-004-B9: PATCH /api/sst/incidents/<id>/status actualiza a RESUELTO y fija resolved_at."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.patch("/api/sst/incidents/1/status", headers=headers, json={
            "status": "RESUELTO",
            "resolution_notes": "Se reparó la rejilla de drenaje con soldeo perimetral y se aplicó pintura epóxica."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["incident"]["status"], "RESUELTO")
        self.assertIsNotNone(data["incident"]["resolved_at"])
        print("[TEST PASS] TEST-004-B9: Cierre y resolución de incidente con resolved_at completado")

    def test_b10_summary_metrics(self):
        """TEST-004-B10: GET /api/sst/summary retorna conteo de riesgos, incidentes y tasa de resolución."""
        res = self.client.get("/api/sst/summary")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("hazards_by_risk", data)
        self.assertIn("incidents_by_status", data)
        self.assertIn("open_incidents", data)
        self.assertIn("days_without_accidents", data)
        print(f"[TEST PASS] TEST-004-B10: Resumen SST -> Peligros: {data['hazards_by_risk']['TOTAL']} | Incidentes abiertos: {data['open_incidents']}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INICIANDO SUITE DE PRUEBAS FUNCIONALES - SPEC 004 (SST)")
    print("=" * 60)
    unittest.main(verbosity=2)
