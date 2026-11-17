# Especificación Técnica - 006: Dashboard General, Indicadores y Reportes

## 1. Visión General
El Dashboard de EcoSafe Plant es el centro de mando principal donde convergen todos los datos de la planta: control ambiental (residuos y consumo de recursos) y seguridad laboral (riesgos, incidentes y EPP). Provee visualizaciones interactivas con gráficos y cálculo de indicadores clave para la toma de decisiones.

## 2. Requerimientos Funcionales
1. **Indicadores Clave de Desempeño (KPIs)**:
   - **Ambientales**:
     - Total de residuos generados en el mes y tendencia histórica.
     - % de residuos valorizados (aprovechados/compostados vs disposición final).
     - Consumo total de agua (m³) vs meta mensual.
     - Consumo total de energía (kWh) vs meta mensual.
   - **Seguridad y Salud en el Trabajo (SST)**:
     - Días sin accidentes de trabajo.
     - Número de incidentes y condiciones inseguras abiertas vs resueltas.
     - % de cumplimiento en inspecciones de EPP.
     - Peligros críticos activos en la planta.
2. **Visualizaciones Gráficas (Frontend HTML/JS con Chart.js)**:
   - Gráfico de barras mensual de residuos por tipo (Cáscara de cacao, mucílago, cartón, plástico, etc.).
   - Gráfico de líneas temporales de consumo de agua y energía eléctrica con línea de meta objetivo.
   - Gráfico circular / dona de distribución de riesgos por clasificación (Físico, Mecánico, Biológico, etc.).
   - Tarjetas KPI con variación porcentual e insignias de estado.
3. **Filtros Temporales y de Área**:
   - Selector global de periodo: Mes actual, Últimos 3 meses, Año en curso.
   - Filtro por área de la planta: Toda la planta, Beneficio, Fermentación, Secado, Empaque, etc.
4. **Exportación e Impresión**:
   - Botón para imprimir reporte ejecutivo o guardarlo en PDF mediante estilos de impresión CSS (`@media print`).
   - Exportación de resúmenes a CSV descargable.

## 3. Modelo de Agregaciones en MySQL
- Consultas agregadas con `GROUP BY YEAR(record_date), MONTH(record_date)`.
- Consulta para el contador de días sin accidentes: `DATEDIFF(CURRENT_DATE, MAX(incident_date))` para incidentes calificados como accidentes.

## 4. Endpoints de la API en Python (Flask / FastAPI)
- `GET /api/dashboard/kpis`: Valores consolidados de los KPIs clave para las tarjetas principales.
- `GET /api/dashboard/waste-chart`: Series de tiempo y categorías de residuos.
- `GET /api/dashboard/utilities-chart`: Consumos mensuales de agua y energía vs metas.
- `GET /api/dashboard/safety-stats`: Días sin accidentes, peligros por nivel y tasa de resolución.

## 5. Frontend (HTML + CSS + JavaScript)
- **Vista**: `frontend/pages/dashboard.html`.
- **Estilos**: `frontend/css/dashboard.css`.
- **Lógica JS**: `frontend/js/dashboard.js` con:
  - Inicialización de gráficos interactivos usando Chart.js vía CDN (`chart.umd.min.js`).
  - Actualización reactiva al cambiar el selector de mes o área.

---

## ✅ Seguimiento de Tareas

> Marca cada tarea cuando esté completada. Actualiza la fecha entre paréntesis al finalizar.

### Backend en Python — Consultas y Agregaciones
- [ ] Crear `backend/routes/dashboard_routes.py`
- [ ] Implementar consulta agregada de KPIs principales (`/api/dashboard/kpis`)
- [ ] Implementar endpoint de series históricas de residuos (`/api/dashboard/waste-chart`)
- [ ] Implementar endpoint de series de agua y energía vs metas (`/api/dashboard/utilities-chart`)
- [ ] Implementar endpoint de indicadores de SST y días sin accidentes (`/api/dashboard/safety-stats`)

### Frontend en HTML / CSS / JavaScript
- [ ] Maquetar la página `frontend/pages/dashboard.html`
- [ ] Diseñar cuadrícula de tarjetas KPI principales con CSS Grid
- [ ] Integrar Chart.js (vía CDN) en `frontend/js/dashboard.js`
- [ ] Programar gráfico de barras de residuos mensuales por tipo
- [ ] Programar gráfico de líneas de consumo de agua y energía con línea meta
- [ ] Programar gráfico de dona de distribución de riesgos SST
- [ ] Conectar selectores de fecha y área para actualizar datos en tiempo real
- [ ] Implementar botón de exportación CSV e impresión PDF con `@media print`


---

## 🧪 Tests de Funcionalidad

> Ejecuta estas pruebas una vez que el módulo esté implementado para verificar que todo funciona según la especificación. Marca cada test cuando lo hayas validado.

### Backend (API Python)

- [ ] **TEST-006-B1**: `GET /api/dashboard/kpis` → retorna `200` con los campos: `waste_total_kg`, `waste_valorization_percent`, `water_consumption_m3`, `water_target_m3`, `energy_consumption_kwh`, `energy_target_kwh`, `days_without_accidents`, `open_incidents`, `epp_compliance_percent`, `critical_hazards_count`.
- [ ] **TEST-006-B2**: `GET /api/dashboard/kpis?month=11&year=2026` → retorna KPIs filtrados para noviembre 2026.
- [ ] **TEST-006-B3**: `GET /api/dashboard/waste-chart?year=2026` → retorna array de 12 meses con totales por categoría de residuo (incluyendo meses con valor 0).
- [ ] **TEST-006-B4**: `GET /api/dashboard/utilities-chart?year=2026` → retorna consumo mensual de agua y energía para cada mes del año, junto con las metas definidas.
- [ ] **TEST-006-B5**: `GET /api/dashboard/safety-stats` → incluye `days_without_accidents` calculado correctamente como `DATEDIFF(hoy, fecha_del_último_accidente)`.
- [ ] **TEST-006-B6**: Con cero accidentes registrados, `days_without_accidents` retorna un valor alto (ej. días desde la fecha del primer registro del sistema) o un mensaje indicativo.
- [ ] **TEST-006-B7**: Todos los endpoints de dashboard son de solo lectura (no aceptan `POST`, `PUT` ni `DELETE`) → retornan `405 Method Not Allowed`.

### Integración entre Módulos

- [ ] **TEST-006-I1**: Registrar 3 residuos y verificar que `GET /api/dashboard/kpis` refleja el nuevo total inmediatamente.
- [ ] **TEST-006-I2**: Registrar una lectura de agua y verificar que `GET /api/dashboard/utilities-chart` actualiza el consumo del mes correspondiente.
- [ ] **TEST-006-I3**: Reportar un incidente de tipo `ACCIDENTE_GRAVE` y verificar que `days_without_accidents` se reinicia a 0.

### Frontend (HTML + CSS + JS con Chart.js)

- [ ] **TEST-006-F1**: La página `dashboard.html` carga sin errores de consola y muestra todas las tarjetas KPI con valores numéricos.
- [ ] **TEST-006-F2**: El gráfico de barras de residuos se renderiza correctamente con Chart.js y muestra etiquetas de mes en el eje X.
- [ ] **TEST-006-F3**: El gráfico de líneas de agua/energía muestra dos líneas (consumo real y meta) con colores diferenciados.
- [ ] **TEST-006-F4**: El gráfico de dona de peligros SST se renderiza con colores por tipo (Físico, Mecánico, Biológico, etc.) y leyenda visible.
- [ ] **TEST-006-F5**: Cambiar el selector de periodo (Mes actual → Últimos 3 meses) → todos los gráficos y tarjetas KPI se actualizan con los nuevos datos.
- [ ] **TEST-006-F6**: Cambiar el filtro de área → los KPIs se actualizan mostrando solo los datos del área seleccionada.
- [ ] **TEST-006-F7**: Hacer clic en "Exportar CSV" → se descarga un archivo `.csv` con los datos del periodo actual.
- [ ] **TEST-006-F8**: Hacer clic en "Imprimir / PDF" → se abre el diálogo de impresión del navegador con un layout limpio (sin menús laterales, solo el contenido del dashboard).
- [ ] **TEST-006-F9**: En pantalla de celular (375px), las tarjetas KPI se apilan verticalmente y los gráficos son legibles (sin texto desbordado).
