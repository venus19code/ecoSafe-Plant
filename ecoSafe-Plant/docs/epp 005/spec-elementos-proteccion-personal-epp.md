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
