import os
import pymysql
from config import Config
from utils.auth import hash_password

def run_init_db():
    print("=" * 60)
    print("ECOSAFE PLANT - INICIALIZADOR DE BASE DE DATOS (SPEC 001)")
    print("=" * 60)
    print(f"Conectando al servidor MySQL en {Config.DB_HOST}:{Config.DB_PORT} como '{Config.DB_USER}'...")

    try:
        # 1. Conectar sin base de datos para crearla si no existe
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset="utf8mb4",
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"[OK] Base de datos '{Config.DB_NAME}' verificada/creada exitosamente.")
        conn.close()

        # 2. Conectar a la base de datos ecoSafe_db para ejecutar schema
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset="utf8mb4",
            autocommit=True
        )

        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, "schema.sql")

        print(f"Leyendo archivo de esquema: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # Ejecutar sentencias del schema (separadas por ;)
        with conn.cursor() as cursor:
            statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
            for stmt in statements:
                if not stmt.upper().startswith("CREATE DATABASE") and not stmt.upper().startswith("USE"):
                    cursor.execute(stmt)
            print("[OK] Tablas 'users' y 'audit_logs' creadas o verificadas correctamente.")

        # 3. Insertar o actualizar usuarios semilla con hash bcrypt nativo
        seed_users = [
            ("Administrador EcoSafe", "admin@ecosafe.com", "Admin123*", "ADMIN", "Dirección General"),
            ("Supervisor de Planta", "supervisor@ecosafe.com", "Supervisor123*", "SUPERVISOR", "Beneficio y Fermentación"),
            ("Operario de Producción", "operario@ecosafe.com", "Operario123*", "OPERARIO", "Secado y Empaque")
        ]

        with conn.cursor() as cursor:
            for name, email, password, role, area in seed_users:
                # Verificar si ya existe
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                existing = cursor.fetchone()
                hashed = hash_password(password)

                if existing:
                    cursor.execute("""
                        UPDATE users SET name=%s, password_hash=%s, role=%s, area=%s, is_active=TRUE
                        WHERE email=%s
                    """, (name, hashed, role, area, email))
                    print(f"  -> Usuario actualizado: {email} (Rol: {role}) | Clave: {password}")
                else:
                    cursor.execute("""
                        INSERT INTO users (name, email, password_hash, role, area, is_active)
                        VALUES (%s, %s, %s, %s, %s, TRUE)
                    """, (name, email, hashed, role, area))
                    print(f"  -> Usuario creado: {email} (Rol: {role}) | Clave: {password}")

            # Registro de auditoría
            cursor.execute("""
                INSERT INTO audit_logs (user_id, action, entity, details)
                SELECT id, 'INITIALIZE', 'SYSTEM', '{"event": "Semillas inicializadas desde init_db.py"}'
                FROM users WHERE email = 'admin@ecosafe.com' LIMIT 1;
            """)

        conn.close()
        print("=" * 60)
        print("¡INICIALIZACIÓN COMPLETADA CON ÉXITO!")
        print("=" * 60)

    except pymysql.MySQLError as e:
        print(f"\n[ERROR MySQL] No se pudo inicializar la base de datos:")
        print(f"  Detalle: {e}")
        print("\nVerifica que el servicio de MySQL esté iniciado (ej. desde XAMPP o servicio local de Windows).")

if __name__ == "__main__":
    run_init_db()
