# Plan de Implementación - 002: Gestión de Residuos

## 1. Objetivo
Desarrollar el módulo integral para el control, registro y seguimiento de residuos sólidos y orgánicos de la planta utilizando Python, MySQL y frontend en HTML/CSS/JS.

## 2. Enfoque de Diseño
- **Mobile-first en el registro**: Los operarios o supervisores suelen estar en el patio de compostaje o en planta de beneficio con un celular; el formulario debe ser rápido (mínimos clics, selectores desplegables dinámicos).
- **Consistencia en MySQL**: Tablas normalizadas con integridad referencial (claves foráneas) y tipos de residuos estándar precargados.

## 3. Fases de Ejecución

### Fase 1: Base de Datos MySQL
- Incorporar sentencias DDL para `waste_categories`, `waste_types` y `waste_records` en el script SQL de inicialización.
- Precargar en `seed.sql` residuos representativos:
  - Orgánicos: Cáscara de cacao, mucílago de cacao, pulpa de café, mucílago de café.
  - Reciclables: Cartón, plástico de empaque, chatarra metálica.
  - Peligrosos: Envases de agroquímicos, aceites usados, baterías.

### Fase 2: Backend en Python
- Implementar blueprint o router `waste_routes.py`.
- Funciones de consulta SQL parametrizadas para evitar inyección SQL.
- Lógica de cálculo para el resumen mensual (% aprovechado vs total).

### Fase 3: Frontend en HTML / CSS / JS
- Maquetar `frontend/pages/residuos.html` con sidebar y área de trabajo.
- Diseñar modal emergente para nuevo registro en CSS puro.
- Crear `frontend/js/residuos.js` para poblar el dropdown de tipos de residuo, gestionar el envío del formulario vía `fetch` con JWT y renderizar la tabla de datos.
