# 📗 Manual de Usuario — EcoSafe Plant

> **EcoSafe Plant** es una aplicación web para el control ambiental y la seguridad laboral en plantas de producción. Accesible desde computador, tablet o celular.

---

## 1. ¿Cómo acceder a la aplicación?

1. Abre el navegador (Chrome, Edge o Firefox) en tu dispositivo.
2. Escribe la dirección del sistema que te proporcionó el administrador (ej. `http://192.168.1.100:5000`).
3. Aparecerá la pantalla de inicio de sesión de **EcoSafe Plant**.

> 💡 **Desde el celular**, puedes tocar el menú del navegador y seleccionar **"Agregar a pantalla de inicio"** para instalar EcoSafe Plant como una aplicación directamente en tu dispositivo.

---

## 2. Inicio de Sesión

| Campo       | Descripción                                        |
|-------------|--------------------------------------------------|
| **Correo**  | Tu correo institucional o personal registrado     |
| **Contraseña** | La contraseña asignada por el administrador   |

- Si es tu primer acceso, el **administrador del sistema** debe registrarte y asignarte un rol.
- Si olvidaste tu contraseña, contacta al administrador para restablecerla.

**Roles disponibles:**

| Rol         | Permisos |
|-------------|----------|
| **ADMIN**   | Acceso total: configurar usuarios, eliminar registros, gestionar catálogos |
| **SUPERVISOR** | Registrar y editar datos de todos los módulos, asignar responsables de incidentes |
| **OPERARIO**  | Registrar residuos, reportar condiciones inseguras, consultar su dotación de EPP |

---

## 3. Panel Principal — Dashboard

Al ingresar, verás el **Dashboard** con un resumen de la situación actual de la planta:

### 🌿 Indicadores Ambientales
- **Total de residuos del mes**: Cuántos kilogramos o toneladas se generaron.
- **% Valorizado**: Porcentaje de residuos que se aprovecharon (compostaje, venta, etc.) frente al total.
- **Consumo de Agua del mes**: m³ consumidos frente a la meta mensual establecida.
- **Consumo de Energía del mes**: kWh consumidos frente a la meta mensual.

### 🦺 Indicadores de Seguridad (SST)
- **Días sin accidentes**: Contador de días desde el último accidente con tiempo perdido registrado.
- **Incidentes abiertos**: Número de reportes de condiciones inseguras pendientes de solución.
- **Cumplimiento de EPP**: % de inspecciones de EPP con calificación "Conforme".
- **Peligros críticos activos**: Peligros identificados en la matriz con nivel CRÍTICO sin controlar.

### 📊 Gráficos
- **Barras**: Residuos generados por tipo en los últimos meses.
- **Líneas**: Tendencia de consumo de agua y energía con línea de meta.
- **Dona**: Distribución de los peligros por tipo (Físico, Mecánico, Biológico, etc.).

> **Filtros disponibles**: Puedes cambiar el periodo (Mes actual, Últimos 3 meses, Año en curso) y el área de la planta en la barra superior del Dashboard.

---

## 4. Módulo de Residuos

**Ruta en el menú:** 🗑️ *Residuos*

Este módulo permite llevar el control de todos los residuos generados en la planta.

### ¿Cómo registrar un residuo?
1. Haz clic en el botón **"+ Nuevo Registro"**.
2. Selecciona el **tipo de residuo** (cáscara de cacao, mucílago, plástico, aceite usado, etc.).
3. Ingresa la **cantidad** y la **unidad** (kg, toneladas, litros).
4. Selecciona el **área** de origen del residuo (Despulpado, Fermentación, Secado, Empaque).
5. Selecciona el **método de disposición** (Compostaje, Lombricultura, Gestor autorizado, Relleno sanitario).
6. Haz clic en **"Guardar"**.

### Tipos de residuos disponibles
| Categoría          | Ejemplos                                                  |
|--------------------|----------------------------------------------------------|
| 🍃 Orgánicos       | Cáscara de cacao, mucílago de cacao, pulpa de café        |
| ♻️ Reciclables     | Cartón, plástico de empaque, chatarra metálica, vidrio    |
| 🗑️ Ordinarios      | Basura común de oficinas y áreas de planta               |
| ⚠️ Peligrosos RESPEL | Envases de agroquímicos, aceites usados, baterías, lámparas |

### Consulta y filtros
- Filtra por **mes/año**, **tipo de residuo** o **área de producción**.
- Visualiza las **tarjetas KPI** con el total del mes y el porcentaje de aprovechamiento.
- Exporta los datos a **CSV** para informes externos.

---

## 5. Módulo de Consumo de Recursos

**Ruta en el menú:** 💧⚡ *Agua y Energía*

Permite registrar y hacer seguimiento al consumo de agua y energía eléctrica en la planta.

### ¿Cómo registrar una lectura?
1. Selecciona la pestaña **"Agua"** o **"Energía Eléctrica"**.
2. Haz clic en **"+ Nueva Lectura"**.
3. Selecciona el **medidor** (ej. Medidor General Agua, Caldera, Área de Tostado).
4. Ingresa la **lectura actual** del medidor. El sistema calculará automáticamente el consumo comparando con la lectura anterior.
5. Opcionalmente, ingresa el **costo de la factura** (valor en pesos o la moneda local).
6. Agrega **observaciones** si hay fugas, mantenimientos o paradas de planta.
7. Haz clic en **"Guardar"**.

### Indicadores de alerta
| Color    | Significado                                              |
|----------|----------------------------------------------------------|
| 🟢 Verde | Consumo dentro de la meta mensual establecida            |
| 🟡 Amarillo | Consumo entre el 85% y 100% de la meta               |
| 🔴 Rojo  | Consumo supera la meta mensual — se requiere revisión   |

> **Configurar metas**: Solo los usuarios con rol **ADMIN** o **SUPERVISOR** pueden definir las metas mensuales de consumo de agua y energía.

---

## 6. Módulo de Seguridad Laboral (SST)

**Ruta en el menú:** 🦺 *Seguridad*

### 6.1 Matriz de Peligros e Identificación de Riesgos
Consulta todos los peligros identificados en la planta con su nivel de riesgo y los controles establecidos.

- Filtra por **área** (ej. Fermentación, Secado) o por **tipo de peligro** (Físico, Mecánico, Químico).
- Los peligros se muestran con colores según su nivel de riesgo:
  - 🟢 **Bajo** | 🟡 **Medio** | 🟠 **Alto** | 🔴 **Crítico**
- Los supervisores y administradores pueden **agregar, editar o controlar** peligros en la matriz.

### 6.2 Reporte de Condiciones Inseguras e Incidentes
Cualquier trabajador puede reportar una condición peligrosa directamente desde su celular:

1. Haz clic en el botón **"Reportar"** (disponible en la parte inferior de la pantalla en celulares).
2. Selecciona el **tipo de reporte**:
   - Condición Insegura (piso mojado, cable pelado, etc.)
   - Acto Inseguro (trabajo sin EPP, operación incorrecta)
   - Casi-Accidente
   - Accidente Leve / Grave
3. Describe brevemente **qué ocurrió** y **dónde**.
4. Selecciona el **nivel de urgencia** (Baja / Media / Alta).
5. Haz clic en **"Enviar Reporte"**.

### 6.3 Seguimiento de Incidentes
Los supervisores pueden:
- Ver todos los reportes abiertos.
- **Asignar un responsable** para corregir la condición.
- Actualizar el estado: `Pendiente → En Atención → Resuelto`.
- Registrar las acciones correctivas tomadas.

---

## 7. Módulo de EPP (Elementos de Protección Personal)

**Ruta en el menú:** 🧤 *EPP*

### 7.1 Catálogo de EPP
Consulta todos los elementos de protección disponibles en la planta con sus especificaciones técnicas y norma de referencia.

### 7.2 Registrar Entrega de Dotación
1. Ve a la pestaña **"Entregas"**.
2. Haz clic en **"+ Nueva Entrega"**.
3. Selecciona el **trabajador** que recibe la dotación.
4. Selecciona el **EPP** entregado y la **cantidad**.
5. Indica el **motivo** (Dotación periódica, Ingreso nuevo, Deterioro o Pérdida).
6. El sistema calculará automáticamente la **fecha de próximo recambio** según la vida útil del EPP.
7. Haz clic en **"Confirmar Entrega"**.

### 7.3 Inspecciones de EPP
Durante los recorridos de planta, el supervisor puede registrar si los trabajadores usan correctamente su EPP:
1. Ve a la pestaña **"Inspecciones"**.
2. Selecciona el **trabajador** y el **área**.
3. Indica si está **Conforme** o **No Conforme** y describe las deficiencias encontradas.
4. Registra las acciones correctivas aplicadas.

### 7.4 Alertas de Vencimiento
En la parte superior del módulo aparecerá un **banner de alerta** cuando haya EPP vencidos o próximos a vencer (en los próximos 30 días) que requieran reposición.

---

## 8. Gestión de Usuarios *(Solo ADMIN)*

**Ruta en el menú:** 👤 *Usuarios*

- **Ver** la lista de usuarios registrados en el sistema.
- **Crear** nuevos usuarios asignando su nombre, correo, contraseña inicial, rol y área.
- **Editar** el rol o el área de un usuario.
- **Desactivar** usuarios que ya no forman parte de la planta (sin borrar su historial de registros).

---

## 9. Generación de Reportes e Impresión

Desde el **Dashboard** o desde cualquier módulo con datos, puedes:
- Presionar el botón **"Exportar CSV"** para descargar los datos en formato de tabla.
- Presionar **"Imprimir / Guardar PDF"** para obtener un reporte ejecutivo listo para presentar en comités de gerencia o visitas de autoridades ambientales y de trabajo.

> Los reportes impresos muestran únicamente la información relevante, ocultando los menús de navegación para una presentación limpia y profesional.

---

## 10. Preguntas Frecuentes

**¿Puedo usarla desde el celular?**
Sí. EcoSafe Plant es 100% responsive. Funciona en celulares, tablets y computadores. Además, puedes instalarla como si fuera una app nativa con la opción "Agregar a pantalla de inicio" de tu navegador.

**¿Qué pasa si no tengo internet en la planta?**
La aplicación requiere conexión a la red local (WiFi o LAN de la empresa) para funcionar, ya que los datos se almacenan en el servidor de la planta.

**¿Quién puede ver mis registros?**
Todos los usuarios con sesión activa pueden consultar los registros ambientales y de SST. Solo los **ADMIN** pueden eliminar datos.

**¿Se pierden los datos si se cierra la sesión?**
No. Todos los datos quedan guardados en la base de datos MySQL del servidor de la planta.

---

*Manual de usuario — EcoSafe Plant | Versión 1.0*
