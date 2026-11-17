# Plan de Implementación - 005: Elementos de Protección Personal (EPP)

## 1. Objetivo
Gestionar el ciclo de vida de los EPP en la planta: catálogo, asignación a trabajadores, control de vigencias y rondas de inspección, utilizando Python, MySQL y frontend en HTML/CSS/JS.

## 2. Enfoque de Implementación
- **Cálculo de fechas en Python/MySQL**: Al registrar la entrega, la aplicación calcula de forma automática `delivery_date + INTERVAL lifespan_days DAY`.
- **Panel de control para supervisores**: Identificar con un solo clic qué trabajadores tienen EPP vencidos.

## 3. Fases de Ejecución

### Fase 1: Base de Datos MySQL
- Incluir tablas `epp_catalog`, `epp_deliveries` y `epp_inspections` en `schema.sql`.
- Precargar en `seed.sql` el catálogo típico: botas dieléctricas, cascos de seguridad, protección auditiva de inserción y de copa, gafas antiempañantes, guantes de nitrilo y carnaza, delantales de caucho.

### Fase 2: Backend en Python
- Implementar `backend/routes/epp_routes.py`.
- Endpoints de catálogo, entregas e inspecciones.
- Lógica de consulta de EPP vencidos (`WHERE next_renewal_date <= CURRENT_DATE`).

### Fase 3: Frontend en HTML / CSS / JS
- Maquetar `frontend/pages/epp.html`.
- Desarrollar `frontend/js/epp.js` para consumir la API y permitir el registro ágil de dotaciones e inspecciones.
