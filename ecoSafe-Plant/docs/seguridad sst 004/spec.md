# Especificación Técnica - 004: Seguridad Laboral y Gestión de Riesgos (SST)

## 1. Visión General
EcoSafe Plant aborda el pilar de Seguridad y Salud en el Trabajo (SST). Este módulo permite identificar peligros en las actividades de la planta, valorar riesgos, registrar medidas de control preventivas y reportar incidentes o condiciones inseguras para prevenir accidentes.

## 2. Requerimientos Funcionales
1. **Matriz de Identificación de Peligros y Valoración de Riesgos (IPVR)**:
   - Clasificación según normas estándar de SST (ej. GTC 45 / ISO 45001):
     - *Clasificación del peligro*: Físico (ruido, iluminación, calor/frío), Químico (polvos orgánicos, químicos de limpieza), Biológico (hongos, bacterias), Biomecánico (manipulación de cargas, posturas prolongadas), Mecánico/Seguridad (maquinaria, atrapamientos, caídas, trabajo en alturas, eléctrico), Psicosocial.
   - Proceso, Área y Actividad evaluada.
   - Efectos posibles en la salud.
   - Nivel de Riesgo (Bajo, Medio, Alto, Crítico).
   - Medidas de control existentes y recomendadas (Eliminación, Sustitución, Ingeniería, Señalización, EPP).
2. **Reporte Rápido de Condiciones Inseguras e Incidentes**:
   - Orientado a que cualquier trabajador u operario con acceso desde su móvil pueda reportar un peligro o casi-accidente en segundos.
   - Campos: Fecha, Lugar exacto en planta, Descripción del peligro o incidente, Nivel de urgencia (Baja, Media, Alta), Estado (Pendiente, En Atención, Resuelto).
3. **Planes de Acción y Seguimiento**:
   - Asignación de responsable para corregir la condición.
   - Fecha de solución y notas de cierre.

## 3. Modelo de Datos (MySQL)

```sql
CREATE TABLE sst_hazards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(100) NOT NULL,
    activity VARCHAR(150) NOT NULL,
    hazard_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    potential_consequences TEXT NULL,
    risk_level ENUM('BAJO', 'MEDIO', 'ALTO', 'CRITICO') NOT NULL DEFAULT 'MEDIO',
    controls_in_place TEXT NULL,
    recommended_actions TEXT NULL,
    status ENUM('ACTIVO', 'CONTROLADO', 'EN_REVISION') NOT NULL DEFAULT 'ACTIVO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sst_incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reported_by_user_id INT NOT NULL,
    incident_type ENUM('CONDICION_INSEGURA', 'ACTO_INSEGURO', 'CASI_ACCIDENTE', 'ACCIDENTE_LEVE', 'ACCIDENTE_GRAVE') NOT NULL,
    incident_date DATETIME NOT NULL,
    location_detail VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    evidence_photo_url VARCHAR(255) NULL,
    severity ENUM('BAJA', 'MEDIA', 'ALTA') NOT NULL DEFAULT 'MEDIA',
    status ENUM('PENDIENTE', 'EN_ATENCION', 'RESUELTO', 'DESESTIMADO') NOT NULL DEFAULT 'PENDIENTE',
    assigned_to_user_id INT NULL,
    resolution_notes TEXT NULL,
    resolved_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(id)
);
```

## 4. Endpoints de la API en Python (Flask / FastAPI)
- `GET /api/sst/hazards`: Listado de la matriz de peligros con filtros por área y nivel de riesgo.
- `POST /api/sst/hazards`: Crear registro de peligro en la matriz.
- `PUT /api/sst/hazards/<id>`: Actualizar evaluación o controles de un peligro.
- `DELETE /api/sst/hazards/<id>`: Eliminar peligro (ADMIN).
- `GET /api/sst/incidents`: Listar reportes de incidentes / condiciones inseguras.
- `POST /api/sst/incidents`: Crear nuevo reporte (abierto a operarios).
- `PATCH /api/sst/incidents/<id>/status`: Cambiar estado y registrar solución del incidente.
- `GET /api/sst/summary`: Estadísticas de peligros por nivel de riesgo e incidentes pendientes.

## 5. Frontend (HTML + CSS + JavaScript)
- **Vista**: `frontend/pages/seguridad.html`.
- **Estilos**: `frontend/css/seguridad.css`.
- **Lógica JS**: `frontend/js/seguridad.js` con:
  - Vista de matriz interactiva con etiquetas de color según nivel de riesgo.
  - Formulario ágil de reporte de incidentes para celulares.
  - Panel de control de incidentes con cambio de estado rápido.

---

## ✅ Seguimiento de Tareas

> Marca cada tarea cuando esté completada. Actualiza la fecha entre paréntesis al finalizar.

### Base de Datos MySQL
- [x] Incluir sentencias DDL de `sst_hazards` y `sst_incidents` en `schema.sql` (18/11/2026)
- [x] Agregar datos semilla en `seed.sql` con matriz de peligros típica de plantas de producción (18/11/2026)

### Backend en Python
- [x] Crear `backend/routes/sst_routes.py` (18/11/2026)
- [x] Endpoints CRUD para la matriz de peligros (`/api/sst/hazards`) (18/11/2026)
- [x] Endpoint para reportar incidentes `POST /api/sst/incidents` (18/11/2026)
- [x] Endpoint `GET /api/sst/incidents` con filtros por severidad y estado (18/11/2026)
- [x] Endpoint `PATCH /api/sst/incidents/<id>/status` para cierre de acciones correctivas (18/11/2026)
- [x] Endpoint `GET /api/sst/summary` con métricas de seguridad para el dashboard (18/11/2026)

### Frontend en HTML / CSS / JavaScript
- [x] Maquetar la página `frontend/pages/seguridad.html` (18/11/2026)
- [x] Crear visualizador de matriz de peligros con filtros y códigos de color según severidad (18/11/2026)
- [x] Crear modal de registro de nuevo peligro en la matriz (18/11/2026)
- [x] Crear formulario táctil para reporte de incidentes y condiciones inseguras (18/11/2026)
- [x] Desarrollar `frontend/js/seguridad.js` con la lógica interactiva completa (18/11/2026)


---

## 🧪 Tests de Funcionalidad

> Ejecuta estas pruebas una vez que el módulo esté implementado para verificar que todo funciona según la especificación. Marca cada test cuando lo hayas validado.

### Backend (API Python)

- [x] **TEST-004-B1**: `GET /api/sst/hazards` → retorna `200` con la lista de peligros sembrados en la base de datos.
- [x] **TEST-004-B2**: `GET /api/sst/hazards?area=Fermentacion` → retorna únicamente peligros del área de Fermentación.
- [x] **TEST-004-B3**: `GET /api/sst/hazards?risk_level=CRITICO` → retorna solo peligros con nivel CRÍTICO.
- [x] **TEST-004-B4**: `POST /api/sst/hazards` con datos válidos (área, actividad, tipo de peligro, descripción, nivel de riesgo) → retorna `201` con el peligro creado.
- [x] **TEST-004-B5**: `PUT /api/sst/hazards/<id>` actualizando `risk_level` y `controls_in_place` → retorna `200` con los valores actualizados.
- [x] **TEST-004-B6**: `DELETE /api/sst/hazards/<id>` con rol `OPERARIO` → retorna `403 Forbidden`.
- [x] **TEST-004-B7**: `POST /api/sst/incidents` con rol `OPERARIO` y datos válidos → retorna `201` con estado inicial `PENDIENTE`.
- [x] **TEST-004-B8**: `GET /api/sst/incidents?status=PENDIENTE` → retorna solo incidentes sin resolver.
- [x] **TEST-004-B9**: `PATCH /api/sst/incidents/<id>/status` cambiando a `RESUELTO` con `resolution_notes` → retorna `200` y el campo `resolved_at` se rellena con la fecha y hora actual.
- [x] **TEST-004-B10**: `GET /api/sst/summary` → retorna conteo de peligros por nivel de riesgo e incidentes por estado, incluyendo el total de incidentes `PENDIENTE` y `EN_ATENCION`.

### Base de Datos MySQL

- [x] **TEST-004-D1**: Confirmar que la semilla carga al menos 5 peligros de distintas categorías (Físico, Mecánico, Biológico, Químico, Biomecánico).
- [x] **TEST-004-D2**: Verificar que un incidente con `assigned_to_user_id` inexistente falla por clave foránea.

### Frontend (HTML + CSS + JS)

- [x] **TEST-004-F1**: La página `seguridad.html` carga con dos secciones visibles: "Matriz de Peligros" e "Incidentes Reportados".
- [x] **TEST-004-F2**: Cada peligro en la matriz muestra el badge de nivel de riesgo con el color correcto (🟢 Bajo, 🟡 Medio, 🟠 Alto, 🔴 Crítico).
- [x] **TEST-004-F3**: El filtro por área actualiza la lista de peligros sin recargar la página.
- [x] **TEST-004-F4**: El formulario de reporte de incidente es accesible con el rol `OPERARIO` y solo requiere 3 campos mínimos (descripción, lugar, urgencia).
- [x] **TEST-004-F5**: Enviar el formulario de reporte → el incidente aparece en la lista de incidentes con estado `PENDIENTE`.
- [x] **TEST-004-F6**: Un supervisor puede cambiar el estado de un incidente a `EN_ATENCION` y luego a `RESUELTO` desde la interfaz.
- [x] **TEST-004-F7**: El formulario de reporte es cómodo de usar en celular (botones grandes, campos con suficiente espacio táctil).
