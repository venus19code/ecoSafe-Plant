# Plan de Implementación - 004: Seguridad Laboral y Gestión de Riesgos (SST)

## 1. Objetivo
Dotar a EcoSafe Plant de un módulo de SST para la consulta de la matriz de peligros y el reporte ágil de incidentes en planta, conectando Python, MySQL y frontend responsivo en HTML/CSS/JS.

## 2. Enfoque de Experiencia de Usuario (UX)
- **Consulta inmediata en campo**: Un operario puede filtrar rápidamente su área de trabajo para ver los peligros específicos y precauciones.
- **Reporte rápido**: Interfaz limpia sin campos innecesarios para que reportar un casi-accidente tome menos de 30 segundos.

## 3. Fases de Ejecución

### Fase 1: Base de Datos MySQL
- Crear tablas `sst_hazards` y `sst_incidents` en `schema.sql`.
- Precargar en `seed.sql` peligros reales de agroindustria (atrapamiento en bandas transportadoras, polvo orgánico respirable, pisos húmedos y resbaladizos, ruido en molienda).

### Fase 2: Backend en Python
- Crear `backend/routes/sst_routes.py`.
- Endpoints de consulta de matriz y creación de reportes.
- Manejo de actualización de estados para el seguimiento de incidentes.

### Fase 3: Frontend en HTML / CSS / JS
- Maquetar `frontend/pages/seguridad.html` con dos vistas: "Matriz de Peligros" e "Incidentes Reportados".
- Programar en `frontend/js/seguridad.js` la interacción con la API y los filtros dinámicos.
