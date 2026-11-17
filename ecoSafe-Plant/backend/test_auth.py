"""
==========================================================
TESTS FUNCIONALES AUTOMATIZADOS - SPEC 001 (AUTENTICACIÓN)
==========================================================
Ejecuta la suite de pruebas para verificar TEST-001-B1 hasta TEST-001-B8.
"""

import unittest
import json
from app import app

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_health_check(self):
        """Verifica que el servicio responda en /api/health"""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "online")
        print("[TEST PASS] /api/health -> Status Online")

    def test_b4_login_wrong_password(self):
        """TEST-001-B4: Login con contraseña incorrecta retorna 401"""
        res = self.client.post("/api/auth/login", json={
            "email": "admin@ecosafe.com",
            "password": "PasswordEquivocada123"
        })
        self.assertEqual(res.status_code, 401)
        print("[TEST PASS] TEST-001-B4: Login con contraseña incorrecta -> 401 Unauthorized")

    def test_b6_me_without_token(self):
        """TEST-001-B6: GET /api/auth/me sin token retorna 401"""
        res = self.client.get("/api/auth/me")
        self.assertEqual(res.status_code, 401)
        print("[TEST PASS] TEST-001-B6: /api/auth/me sin token -> 401 Unauthorized")

    def test_b1_register_validation(self):
        """TEST-001-B1: Validación de campos obligatorios en registro"""
        res = self.client.post("/api/auth/register", json={
            "email": "incompleto@ecosafe.com"
        })
        self.assertEqual(res.status_code, 400)
        print("[TEST PASS] TEST-001-B1: Registro con campos faltantes -> 400 Bad Request")

if __name__ == "__main__":
    print("\nIniciando Suite de Pruebas Unitarias de Spec 001...")
    unittest.main(verbosity=2)
