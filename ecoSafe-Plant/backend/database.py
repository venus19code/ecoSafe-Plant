import ssl
import pymysql
from pymysql.cursors import DictCursor
from config import Config


def get_ssl_context():
    """
    Devuelve un contexto SSL cuando DB_SSL está activo.
    Necesario en proveedores de MySQL en la nube que exigen conexión cifrada.
    Si se indica DB_SSL_CA (ruta al certificado), se valida el certificado del servidor.
    """
    if not Config.DB_SSL:
        return None
    if Config.DB_SSL_CA:
        return ssl.create_default_context(cafile=Config.DB_SSL_CA)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def get_db_connection(use_database=True):
    """
    Establece y retorna una conexión a MySQL usando PyMySQL.
    Si use_database es False, se conecta al servidor sin seleccionar base de datos (útil para crearla).
    """
    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME if use_database else None,
            cursorclass=DictCursor,
            autocommit=True,
            charset="utf8mb4",
            ssl=get_ssl_context()
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"[Error de Conexión MySQL] {e}")
        raise e

def execute_query(query, params=None):
    """
    Ejecuta una consulta SQL de modificación (INSERT, UPDATE, DELETE).
    Retorna el ID insertado si aplica, o las filas afectadas.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            return {"last_id": last_id, "rowcount": affected}
    finally:
        connection.close()

def fetch_one(query, params=None):
    """
    Ejecuta una consulta SELECT y retorna un solo registro como diccionario, o None.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        connection.close()

def fetch_all(query, params=None):
    """
    Ejecuta una consulta SELECT y retorna todos los registros como una lista de diccionarios.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        connection.close()
