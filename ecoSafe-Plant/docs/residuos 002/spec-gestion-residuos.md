# Especificación Técnica - 002: Gestión de Residuos

## 1. Visión General
El módulo de residuos responde a la necesidad clave del README: registrar y controlar los residuos generados mensualmente en la planta de producción (como cáscaras y mucílago de cacao o café, además de residuos reciclables, ordinarios y peligrosos).

## 2. Requerimientos Funcionales
1. **Registro de Residuos**:
   - Registro periódico (diario/semanal/mensual).
   - Tipo de residuo:
     - *Orgánicos de proceso*: Cáscara de cacao, mucílago de cacao, pulpa de café, mucílago de café, cascarilla, etc.
     - *Aprovechables / Reciclables*: Cartón, plástico, chatarra, vidrio.
     - *No aprovechables / Ordinarios*: Basura común de planta.
     - *Peligrosos (RESPEL)*: Envases de químicos, aceites usados, baterías, luminarias.
   - Cantidad generada (valor numérico) y unidad de medida (kg, ton, litros, $\text{m}^3$).
   - Área o línea de proceso de origen (ej. Despulpado, Fermentación, Secado, Empaque).
   - Destino o Disposición Final: Compostaje, Lombricultura, Alimentación animal, Gestor autorizado, Relleno sanitario, Venta como subproducto.
   - Costo o ingreso asociado (opcional: venta de subproductos o pago a gestores).

2. **Filtros y Búsqueda**:
   - Filtrado por rango de fechas (mes/año).
   - Filtrado por tipo de residuo y área de producción.
   - Búsqueda por texto y exportación a CSV.

3. **Métricas de Residuos**:
   - Total generado en el mes seleccionado.
   - Comparación porcentual frente al mes anterior.
   - % de aprovechamiento (Residuos aprovechados vs Total generados).

## 3. Modelo de Datos (MySQL)

```sql
CREATE TABLE waste_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    color_code VARCHAR(7) NOT NULL DEFAULT '#2d6a4f',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE waste_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    default_unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    is_hazardous BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (category_id) REFERENCES waste_categories(id) ON DELETE CASCADE
);

CREATE TABLE waste_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    waste_type_id INT NOT NULL,
    recorded_by_user_id INT NOT NULL,
    record_date DATE NOT NULL,
    quantity DECIMAL(12, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    area VARCHAR(100) NOT NULL,
    disposal_method VARCHAR(100) NOT NULL,
    disposal_certificate_url VARCHAR(255) NULL,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (waste_type_id) REFERENCES waste_types(id),
    FOREIGN KEY (recorded_by_user_id) REFERENCES users(id)
);
```

## 4. Endpoints de la API en Python (Flask / FastAPI)
- `GET /api/waste/records`: Listado paginado con filtros (fecha, tipo, categoría, área).
- `POST /api/waste/records`: Crear un nuevo registro de residuo.
- `GET /api/waste/records/<id>`: Obtener detalle de un registro.
- `PUT /api/waste/records/<id>`: Modificar registro existente.
- `DELETE /api/waste/records/<id>`: Eliminar registro (solo ADMIN).
- `GET /api/waste/types`: Catálogo de categorías y tipos de residuos para listas desplegables.
- `GET /api/waste/summary`: Agregaciones mensuales por categoría y disposición final.

## 5. Frontend (HTML + CSS + JavaScript)
- **Vista**: `frontend/pages/residuos.html`.
- **Estilos**: `frontend/css/residuos.css` (o dentro de `styles.css`).
- **Lógica JS**: `frontend/js/residuos.js` con:
  - Carga asíncrona de datos mediante `fetch()`.
  - Tarjetas de resumen del mes actual (KPIs).
  - Modal accesible para registrar nuevos residuos sin recargar la página.
  - Tabla dinámica con badges de color según categoría.
