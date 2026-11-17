# Especificación Técnica - 005: Elementos de Protección Personal (EPP)

## 1. Visión General
El control de los Elementos de Protección Personal (EPP) es vital para mitigar los peligros identificados en planta. Este módulo permite gestionar el catálogo de EPP requeridos, registrar entregas de dotación a los trabajadores, controlar vidas útiles o fechas de recambio e inspeccionar el estado de uso en planta.

## 2. Requerimientos Funcionales
1. **Catálogo de EPP**:
   - Categorías: Cabeza (cascos), Visual/Facial (gafas, caretas), Auditiva (tapones, orejeras), Respiratoria (mascarillas, respiradores), Manos (guantes nitrilo/carnaza), Pies (botas de seguridad), Cuerpo (delantales impermeables).
   - Vida útil estimada (días).
   - Stock disponible.
2. **Asignación y Entrega de Dotación**:
   - Registro de entrega de EPP a un trabajador (`users`).
   - Fecha de entrega y cálculo automático de la fecha de reposición recomendada (`delivery_date + lifespan_days`).
   - Motivo (Dotación periódica, Daño o deterioro, Pérdida, Ingreso nuevo).
   - Confirmación de entrega.
3. **Inspecciones de EPP en Planta**:
   - Verificaciones periódicas por parte de supervisores durante recorridos de planta.
   - Calificación de cumplimiento: Conforme, No conforme, Requiere cambio urgente.
4. **Alertas de Renovación**:
   - Identificación de EPP vencidos o próximos a vencer.

## 3. Modelo de Datos (MySQL)

```sql
CREATE TABLE epp_catalog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    category ENUM('CABEZA', 'VISUAL', 'AUDITIVA', 'RESPIRATORIA', 'MANOS', 'PIES', 'CUERPO') NOT NULL,
    standard_code VARCHAR(50) NULL,
    lifespan_days INT NOT NULL DEFAULT 90,
    description TEXT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE epp_deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    epp_id INT NOT NULL,
    worker_id INT NOT NULL,
    delivered_by_user_id INT NOT NULL,
    delivery_date DATE NOT NULL,
    next_renewal_date DATE NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    reason ENUM('DOTACION_PERIODICA', 'INGRESO_NUEVO', 'DETERIORO', 'PERDIDA') NOT NULL DEFAULT 'DOTACION_PERIODICA',
    worker_signature_confirmed BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (epp_id) REFERENCES epp_catalog(id),
    FOREIGN KEY (worker_id) REFERENCES users(id),
    FOREIGN KEY (delivered_by_user_id) REFERENCES users(id)
);

CREATE TABLE epp_inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspector_user_id INT NOT NULL,
    worker_id INT NOT NULL,
    inspection_date DATE NOT NULL,
    area VARCHAR(100) NOT NULL,
    is_compliant BOOLEAN NOT NULL DEFAULT TRUE,
    deficiencies_found TEXT NULL,
    corrective_actions TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspector_user_id) REFERENCES users(id),
    FOREIGN KEY (worker_id) REFERENCES users(id)
);
```

## 4. Endpoints de la API en Python (Flask / FastAPI)
- `GET /api/epp/catalog`: Catálogo de EPP con filtros por categoría.
- `POST /api/epp/catalog`: Añadir nuevo elemento al catálogo.
- `GET /api/epp/deliveries`: Historial de entregas con filtros por trabajador y fechas.
- `POST /api/epp/deliveries`: Registrar entrega de EPP (calcula automáticamente `next_renewal_date` según `lifespan_days`).
- `GET /api/epp/inspections`: Historial de inspecciones en planta.
- `POST /api/epp/inspections`: Registrar inspección de uso de EPP.
- `GET /api/epp/renewals-due`: Listado de dotaciones vencidas para reposición.

## 5. Frontend (HTML + CSS + JavaScript)
- **Vista**: `frontend/pages/epp.html`.
- **Estilos**: `frontend/css/epp.css`.
- **Lógica JS**: `frontend/js/epp.js` con:
  - Pestañas: Entregas, Catálogo de EPP e Inspecciones.
  - Alerta de dotaciones vencidas resaltada en rojo/amarillo.
  - Formulario de entrega con autoselección de trabajador y cálculo de recambio.

---

## ✅ Seguimiento de Tareas

> Marca cada tarea cuando esté completada. Actualiza la fecha entre paréntesis al finalizar.

### Base de Datos MySQL
- [ ] Incluir DDL de `epp_catalog`, `epp_deliveries` y `epp_inspections` en `schema.sql`
- [ ] Crear catálogo base de EPP en `seed.sql` (cascos, botas, gafas, guantes, respiradores)

### Backend en Python
- [ ] Crear `backend/routes/epp_routes.py`
- [ ] Endpoints para catálogo de EPP (`/api/epp/catalog`)
- [ ] Endpoint `POST /api/epp/deliveries` con cálculo automático de fecha de renovación
- [ ] Endpoint `GET /api/epp/deliveries` filtrado por colaborador y fechas
- [ ] Endpoint `POST /api/epp/inspections` y `GET /api/epp/inspections`
- [ ] Endpoint `GET /api/epp/renewals-due` para alertar vencimientos próximos

### Frontend en HTML / CSS / JavaScript
- [ ] Maquetar la página `frontend/pages/epp.html` con pestañas (Entregas / Catálogo / Inspecciones)
- [ ] Modal para registrar entrega de dotación a un operario
- [ ] Modal para registrar inspección rápida de EPP durante recorridos
- [ ] Desarrollar `frontend/js/epp.js` con lógica de renderizado y peticiones a la API
- [ ] Banner de alerta para dotaciones vencidas o por vencer en 30 días


---

## 🧪 Tests de Funcionalidad

> Ejecuta estas pruebas una vez que el módulo esté implementado para verificar que todo funciona según la especificación. Marca cada test cuando lo hayas validado.

### Backend (API Python)

- [ ] **TEST-005-B1**: `GET /api/epp/catalog` → retorna `200` con el catálogo de EPP sembrado (al menos cascos, botas, guantes, gafas y respiradores).
- [ ] **TEST-005-B2**: `GET /api/epp/catalog?category=MANOS` → retorna solo los EPP de la categoría "MANOS".
- [ ] **TEST-005-B3**: `POST /api/epp/catalog` con datos válidos → retorna `201` con el nuevo EPP creado.
- [ ] **TEST-005-B4**: `POST /api/epp/deliveries` con `epp_id`, `worker_id`, `delivery_date` y `reason` válidos → retorna `201` con `next_renewal_date = delivery_date + lifespan_days` calculado correctamente.
- [ ] **TEST-005-B5**: Verificar el cálculo de `next_renewal_date`: si `delivery_date = 2026-11-17` y `lifespan_days = 90`, entonces `next_renewal_date` debe ser `2027-02-15`.
- [ ] **TEST-005-B6**: `GET /api/epp/deliveries?worker_id=<id>` → retorna solo las entregas del trabajador especificado.
- [ ] **TEST-005-B7**: `POST /api/epp/inspections` con datos válidos → retorna `201`.
- [ ] **TEST-005-B8**: `POST /api/epp/inspections` con `is_compliant=false` sin `deficiencies_found` → retorna `400 Bad Request` (si no cumple, debe especificar las deficiencias).
- [ ] **TEST-005-B9**: `GET /api/epp/renewals-due` → retorna solo las entregas cuya `next_renewal_date` es menor o igual a la fecha actual (vencidas) o dentro de los próximos 30 días.

### Base de Datos MySQL

- [ ] **TEST-005-D1**: Verificar que el seed carga al menos 7 EPP, uno por cada categoría (CABEZA, VISUAL, AUDITIVA, RESPIRATORIA, MANOS, PIES, CUERPO).
- [ ] **TEST-005-D2**: Confirmar que un `epp_delivery` con `worker_id` inexistente falla por clave foránea.

### Frontend (HTML + CSS + JS)

- [ ] **TEST-005-F1**: La página `epp.html` carga con 3 pestañas funcionales: "Entregas", "Catálogo" y "Inspecciones".
- [ ] **TEST-005-F2**: El modal de nueva entrega muestra un dropdown de trabajadores y otro de EPP del catálogo cargados desde la API.
- [ ] **TEST-005-F3**: Al seleccionar un EPP en el modal, el campo "Próxima renovación" se calcula y muestra automáticamente en la pantalla.
- [ ] **TEST-005-F4**: Registrar una entrega → aparece en la tabla de la pestaña "Entregas" sin recargar la página.
- [ ] **TEST-005-F5**: Si hay EPP vencidos, aparece el banner de alerta rojo/amarillo en la parte superior de la página con el conteo de dotaciones a reponer.
- [ ] **TEST-005-F6**: El formulario de inspección permite seleccionar trabajador, área y estado de cumplimiento; si se marca "No conforme", aparece un campo adicional para escribir las deficiencias encontradas.
- [ ] **TEST-005-F7**: La página es usable en celular (375px): las pestañas se mantienen visibles y los formularios son accesibles con el teclado táctil.
