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
