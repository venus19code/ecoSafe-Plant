# Plan de Implementación - 006: Dashboard General, Indicadores y Reportes

## 1. Objetivo
Unificar la información ambiental y de SST en un panel de control intuitivo, visualmente atractivo, interactivo y con capacidad de exportación e impresión, construido con Python, MySQL y frontend en HTML/CSS/JS.

## 2. Enfoque de Visualización
- **Chart.js**: Librería estándar para gráficos en JavaScript sin necesidad de Node/NPM. Se incluye mediante CDN o archivo local estático.
- **Diseño responsive con CSS Grid/Flexbox**: Adaptado a teléfonos, tablets y computadores de planta.
- **Modo Impresión**: Hoja de estilos con `@media print` para generar reportes ejecutivos en PDF limpios con un clic.

## 3. Fases de Ejecución

### Fase 1: Backend en Python (Consultas de Agregación)
- Implementar `backend/routes/dashboard_routes.py`.
- Consultas SQL optimizadas en MySQL para obtener KPIs y series temporales sin sobrecargar la base de datos.

### Fase 2: Frontend en HTML / CSS / JS
- Maquetar `frontend/pages/dashboard.html`.
- Integrar Chart.js en `frontend/js/dashboard.js`.
- Configurar interactividad: filtros de fecha y área que refrescan los gráficos y tarjetas dinámicamente.

### Fase 3: Exportación e Impresión
- Implementar la función de descarga de resumen CSV.
- Diseñar la vista de impresión en CSS para emitir reportes formales en PDF.
