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
   - Cantidad generada (valor numérico) y unidad de medida (kg, ton, litros, m³).
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

---

## ✅ Seguimiento de Tareas

> Marca cada tarea cuando esté completada. Actualiza la fecha entre paréntesis al finalizar.

### Base de Datos MySQL
- [x] Crear migración para `waste_categories`, `waste_types` y `waste_records` en `schema.sql` (18/11/2026)
- [x] Agregar datos semilla en `seed.sql` con categorías estándar (Orgánico, Reciclable, Ordinario, Peligroso) (18/11/2026)
- [x] Agregar tipos de residuos semilla (cáscara de cacao, mucílago, pulpa de café, plásticos, aceites usados) (18/11/2026)

### Backend en Python
- [x] Crear `backend/routes/waste_routes.py` (18/11/2026)
- [x] Endpoint `GET /api/waste/types` para obtener categorías y tipos (18/11/2026)
- [x] Endpoint `POST /api/waste/records` con validación de datos numéricos y fechas (18/11/2026)
- [x] Endpoints `GET`, `PUT`, `DELETE` para `/api/waste/records/<id>` (18/11/2026)
- [x] Endpoint `GET /api/waste/summary` para agregaciones mensuales y % de aprovechamiento (18/11/2026)

### Frontend en HTML / CSS / JavaScript
- [x] Maquetar la página `frontend/pages/residuos.html` (18/11/2026)
- [x] Añadir tarjetas de KPIs superiores (Total generado, % valorizado, total peligroso) (18/11/2026)
- [x] Diseñar formulario modal en HTML/CSS para registrar un residuo (18/11/2026)
- [x] Implementar `frontend/js/residuos.js` con consumo de API mediante `fetch()` (18/11/2026)
- [x] Añadir buscador en tiempo real y filtros por fecha y categoría en la tabla (18/11/2026)


---

## 🧪 Tests de Funcionalidad

> Ejecuta estas pruebas una vez que el módulo esté implementado para verificar que todo funciona según la especificación. Marca cada test cuando lo hayas validado.

### Backend (API Python)

- [x] **TEST-002-B1**: `GET /api/waste/types` → retorna `200` con lista de categorías y tipos de residuos precargados (incluye Orgánicos, Reciclables, Ordinarios y Peligrosos).
- [x] **TEST-002-B2**: `POST /api/waste/records` con datos válidos (tipo, cantidad, área, método de disposición) → retorna `201` con el registro creado.
- [x] **TEST-002-B3**: `POST /api/waste/records` con `quantity` negativa → retorna `400 Bad Request` con mensaje de error descriptivo.
- [x] **TEST-002-B4**: `POST /api/waste/records` sin token JWT → retorna `401 Unauthorized`.
- [x] **TEST-002-B5**: `GET /api/waste/records?month=11&year=2026` → retorna solo registros del mes indicado.
- [x] **TEST-002-B6**: `GET /api/waste/records?category=PELIGROSO` → retorna solo registros de residuos peligrosos.
- [x] **TEST-002-B7**: `PUT /api/waste/records/<id>` con datos actualizados → retorna `200` con los datos modificados.
- [x] **TEST-002-B8**: `DELETE /api/waste/records/<id>` con rol `OPERARIO` → retorna `403 Forbidden`.
- [x] **TEST-002-B9**: `DELETE /api/waste/records/<id>` con rol `ADMIN` → retorna `200` y el registro desaparece de la base de datos.
- [x] **TEST-002-B10**: `GET /api/waste/summary` → retorna totales mensuales, el campo `valorization_percent` calculado correctamente (residuos aprovechados / total * 100).

### Base de Datos MySQL

- [x] **TEST-002-D1**: Verificar que insertar un `waste_record` con un `waste_type_id` inexistente falla por clave foránea.
- [x] **TEST-002-D2**: Confirmar que las semillas en `seed.sql` precargan al menos 4 categorías y 8 tipos de residuos.

### Frontend (HTML + CSS + JS)

- [x] **TEST-002-F1**: La página `residuos.html` carga y muestra las tarjetas KPI del mes con valores (aunque sean cero inicialmente).
- [x] **TEST-002-F2**: El dropdown de "Tipo de residuo" en el formulario modal se llena dinámicamente con los datos de `GET /api/waste/types`.
- [x] **TEST-002-F3**: Registrar un residuo desde el formulario modal → aparece inmediatamente en la tabla sin recargar la página.
- [x] **TEST-002-F4**: Escribir texto en el buscador → la tabla filtra registros en tiempo real.
- [x] **TEST-002-F5**: Cambiar el filtro de mes → la tabla y las tarjetas KPI se actualizan con los datos del mes seleccionado.
- [x] **TEST-002-F6**: Los badges de categoría muestran el color correcto (verde para Orgánicos, azul para Reciclables, rojo para Peligrosos).
- [x] **TEST-002-F7**: La página es usable en un celular de 375px de ancho (formulario, tabla y KPIs no se desbordan).
