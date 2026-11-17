# Especificación Técnica - 006: Dashboard General, Indicadores y Reportes

## 1. Visión General
El Dashboard de EcoSafe Plant es el centro de mando principal donde convergen todos los datos de la planta: control ambiental (residuos y consumo de recursos) y seguridad laboral (riesgos, incidentes y EPP). Provee visualizaciones interactivas con gráficos y cálculo de indicadores clave para la toma de decisiones.

## 2. Requerimientos Funcionales
1. **Indicadores Clave de Desempeño (KPIs)**:
   - **Ambientales**:
     - Total de residuos generados en el mes y tendencia histórica.
     - % de residuos valorizados (aprovechados/compostados vs disposición final).
     - Consumo total de agua ($m^3$) vs meta mensual.
     - Consumo total de energía ($kWh$) vs meta mensual.
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
