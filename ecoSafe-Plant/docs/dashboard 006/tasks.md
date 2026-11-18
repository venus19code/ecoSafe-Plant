# Lista de Tareas - 006: Dashboard General, Indicadores y Reportes

- [x] **1. Backend en Python - Consultas y Agregaciones**
  - [x] 1.1 Crear `backend/routes/dashboard_routes.py`. ✅ Implementado con 4 endpoints completos
  - [x] 1.2 Implementar consulta agregada de KPIs principales (`/api/dashboard/kpis`). ✅ Retorna todos los campos: waste_total_kg, waste_valorization_percent, water_consumption_m3, water_target_m3, energy_consumption_kwh, energy_target_kwh, days_without_accidents, open_incidents, epp_compliance_percent, critical_hazards_count
  - [x] 1.3 Implementar endpoint de series históricas de residuos (`/api/dashboard/waste-chart`). ✅ Retorna array de 12 meses con totales por categoría de residuo
  - [x] 1.4 Implementar endpoint de series de agua y energía vs metas (`/api/dashboard/utilities-chart`). ✅ Retorna consumo mensual de agua y energía para cada mes del año, junto con las metas definidas
  - [x] 1.5 Implementar endpoint de indicadores de SST y días sin accidentes (`/api/dashboard/safety-stats`). ✅ Incluye days_without_accidents calculado con DATEDIFF frente al último accidente

- [x] **2. Frontend en HTML / CSS / JavaScript**
  - [x] 2.1 Maquetar la página `frontend/pages/dashboard.html`. ✅ Página completa con 8 KPIs, 3 gráficos y barra de filtros
  - [x] 2.2 Diseñar la cuadrícula de tarjetas KPI principales con CSS Grid. ✅ Layout kpi-grid con Grid responsive
  - [x] 2.3 Crear contenedor de gráficos con canvas para Chart.js. ✅ 3 canvas identificados: wasteChart, utilitiesChart, riskDistributionChart
  - [x] 2.4 Programar `frontend/js/dashboard.js` para renderizar gráficos de barras, líneas y donas. ✅ Código implementado con renderWasteChart(), renderUtilitiesChart(), renderRiskChart(), renderIncidentsChart()
  - [x] 2.5 Conectar los selectores de fecha y área para actualizar los datos en tiempo real. ✅ Event listeners en periodSelect, filterStartDate, filterEndDate, filterArea
  - [x] 2.6 Implementar botón de exportación CSV e impresión PDF. ✅ exportSummaryCSV() function + btnPrint → window.print() + @media print en styles.css
