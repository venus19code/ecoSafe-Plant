# Plan de Implementación - 003: Consumo de Recursos (Agua y Energía)

## 1. Objetivo
Implementar el módulo para monitorear el consumo de agua y energía eléctrica, calcular consumos netos en el backend de Python y presentar gráficos/alertas en el frontend de HTML/CSS/JS.

## 2. Enfoque de Implementación
- **Cálculo automático de diferencial**: En el backend de Python, cuando se inserta una lectura para un medidor, una consulta SQL previa obtiene la lectura anterior más reciente para calcular `consumption = lectura_actual - lectura_anterior`.
- **Alertas visuales en CSS**: Clases de estilo dinámicas (`.kpi-success`, `.kpi-warning`, `.kpi-danger`) para indicar si el consumo del mes está dentro de la meta o sobrepasado.

## 3. Fases de Ejecución

### Fase 1: Base de Datos MySQL
- Crear tablas `utility_meters`, `utility_readings` y `utility_targets`.
- Insertar en `seed.sql` los medidores iniciales: Medidor General Agua y Medidor General Energía Eléctrica.

### Fase 2: Backend en Python
- Implementar blueprint `backend/routes/utility_routes.py`.
- Lógica de obtención de lectura previa y cálculo de consumo neto.
- Endpoints de consulta agregada mensual y porcentaje de cumplimiento frente a la meta.

### Fase 3: Frontend en HTML / CSS / JS
- Maquetar `frontend/pages/recursos.html` con pestañas para Agua y Energía.
- Formulario de captura rápida con autocompletado de la última lectura registrada.
- Renderizado de tablas de historial y tarjetas de consumo mensual acumulado.
