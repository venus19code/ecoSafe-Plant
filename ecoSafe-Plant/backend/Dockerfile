# ==========================================================
# ECOSAFE PLANT - IMAGEN DEL BACKEND (Flask + Gunicorn)
# ==========================================================
# El contexto de build es la raíz del proyecto (ecoSafe-Plant/),
# porque Flask también sirve el frontend desde ../frontend.

FROM python:3.12-slim

# Salida de logs sin buffer y sin archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1) Dependencias primero (mejor uso de la caché de Docker)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 2) Código de la aplicación
COPY backend /app/backend
COPY frontend /app/frontend

# Usuario sin privilegios
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend

EXPOSE 5000

# Un solo worker: el arranque ejecuta la inicialización de BD (AUTO_INIT_DB)
# una única vez y evita condiciones de carrera entre workers.
CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "1", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
