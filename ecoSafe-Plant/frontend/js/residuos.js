/**
 * ==========================================================
 * ECOSAFE PLANT - CONTROLADOR DE RESIDUOS (SPEC 002)
 * ==========================================================
 */

// Estado global de la vista
let currentRecords = [];
let wasteCatalog = [];
let currentUser = null;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Verificar autenticación obligatoria
    currentUser = requireAuthPage();
    if (!currentUser) return;

    // Configurar menú móvil
    initSidebarToggle();

    // 2. Establecer fecha por defecto en el formulario (hoy)
    const today = new Date().toISOString().split("T")[0];
    const recordDateInput = document.getElementById("recordDate");
    if (recordDateInput) recordDateInput.value = today;

    // 3. Sincronizar selectores de mes y año al mes actual si no están seleccionados
    const now = new Date();
    const selectMonth = document.getElementById("selectMonth");
    const selectYear = document.getElementById("selectYear");
    if (selectMonth) selectMonth.value = (now.getMonth() + 1).toString();
    if (selectYear) selectYear.value = now.getFullYear().toString();

    // 4. Inicializar eventos
    initEventListeners();

    // 5. Cargar catálogo de tipos y datos iniciales
    await loadWasteCatalog();
    await loadSummaryAndRecords();
});

/**
 * Inicializa el toggle del menú responsive
 */
function initSidebarToggle() {
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }
}

/**
 * Configura los escuchadores de eventos para filtros, modal y acciones
 */
function initEventListeners() {
    // Filtros de fecha y categoría
    const selectMonth = document.getElementById("selectMonth");
    const selectYear = document.getElementById("selectYear");
    const selectCategory = document.getElementById("selectCategory");
    const searchInput = document.getElementById("searchInput");

    if (selectMonth) selectMonth.addEventListener("change", loadSummaryAndRecords);
    if (selectYear) selectYear.addEventListener("change", loadSummaryAndRecords);
    if (selectCategory) selectCategory.addEventListener("change", filterAndRenderTable);
    if (searchInput) searchInput.addEventListener("input", filterAndRenderTable);

    // Botones del Modal
    const btnOpenCreate = document.getElementById("btnOpenCreateModal");
    const btnCloseModal = document.getElementById("btnCloseModal");
    const btnCancelModal = document.getElementById("btnCancelModal");
    const wasteModal = document.getElementById("wasteModal");
    const wasteForm = document.getElementById("wasteForm");

    if (btnOpenCreate) {
        btnOpenCreate.addEventListener("click", () => openModalForCreate());
    }

    if (btnCloseModal) {
        btnCloseModal.addEventListener("click", closeModal);
    }

    if (btnCancelModal) {
        btnCancelModal.addEventListener("click", closeModal);
    }

    // Cerrar modal al hacer click fuera del cuadro de diálogo
    if (wasteModal) {
        wasteModal.addEventListener("click", (e) => {
            if (e.target === wasteModal) closeModal();
        });
    }

    // Auto-asignar unidad predeterminada según tipo de residuo seleccionado
    const wasteTypeSelect = document.getElementById("wasteTypeSelect");
    const unitSelect = document.getElementById("unit");
    if (wasteTypeSelect && unitSelect) {
        wasteTypeSelect.addEventListener("change", () => {
            const selectedId = parseInt(wasteTypeSelect.value, 10);
            const found = wasteCatalog.find(t => t.id === selectedId);
            if (found && found.default_unit) {
                unitSelect.value = found.default_unit;
            }
        });
    }

    // Envío del formulario
    if (wasteForm) {
        wasteForm.addEventListener("submit", handleFormSubmit);
    }

    // Exportar CSV
    const btnExportCsv = document.getElementById("btnExportCsv");
    if (btnExportCsv) {
        btnExportCsv.addEventListener("click", exportCurrentRecordsToCSV);
    }
}

/**
 * Carga el catálogo de categorías y tipos de residuos desde la API
 */
async function loadWasteCatalog() {
    const res = await apiFetch("/waste/types");
    const selectEl = document.getElementById("wasteTypeSelect");
    if (!selectEl) return;

    if (!res.ok || !res.data) {
        console.error("Error al cargar catálogo de tipos:", res.error);
        return;
    }

    wasteCatalog = res.data.types || [];
    const categories = res.data.categories || [];

    // Limpiar opciones anteriores
    selectEl.innerHTML = '<option value="">-- Seleccione un residuo --</option>';

    // Crear grupos por categoría
    categories.forEach(cat => {
        const group = document.createElement("optgroup");
        group.label = cat.name;

        (cat.types || []).forEach(typeItem => {
            const opt = document.createElement("option");
            opt.value = typeItem.id;
            opt.textContent = `${typeItem.name} (${typeItem.default_unit})${typeItem.is_hazardous ? ' ⚠️' : ''}`;
            group.appendChild(opt);
        });

        selectEl.appendChild(group);
    });
}

/**
 * Carga tanto las métricas de resumen (KPIs) como la lista de registros
 */
async function loadSummaryAndRecords() {
    const month = document.getElementById("selectMonth")?.value || (new Date().getMonth() + 1);
    const year = document.getElementById("selectYear")?.value || new Date().getFullYear();

    // 1. Cargar KPIs
    loadKPIs(month, year);

    // 2. Cargar tabla
    await loadTableRecords(month, year);
}

/**
 * Consulta el endpoint /api/waste/summary y actualiza las tarjetas KPI
 */
async function loadKPIs(month, year) {
    const res = await apiFetch(`/waste/summary?month=${month}&year=${year}`);
    if (!res.ok || !res.data) {
        console.warn("No se pudo obtener el resumen de KPIs:", res.error);
        return;
    }

    const data = res.data;

    // Total Generado
    const kpiTotalQty = document.getElementById("kpiTotalQty");
    if (kpiTotalQty) {
        kpiTotalQty.textContent = Number(data.total_quantity || 0).toLocaleString("es-CO", {
            minimumFractionDigits: 1,
            maximumFractionDigits: 2
        });
    }

    // Comparativa mes anterior
    const kpiDiffPercent = document.getElementById("kpiDiffPercent");
    if (kpiDiffPercent) {
        const diff = Number(data.diff_percent || 0);
        const prefix = diff > 0 ? "+" : "";
        kpiDiffPercent.textContent = `${prefix}${diff}%`;
        kpiDiffPercent.style.color = diff > 0 ? "var(--warning)" : "var(--success)";
    }

    // Tasa de Valorización / Aprovechamiento
    const kpiValorizationPercent = document.getElementById("kpiValorizationPercent");
    if (kpiValorizationPercent) {
        kpiValorizationPercent.textContent = `${data.valorization_percent || 0}%`;
    }

    const kpiValorizedQty = document.getElementById("kpiValorizedQty");
    if (kpiValorizedQty) {
        kpiValorizedQty.textContent = `${Number(data.valorized_quantity || 0).toLocaleString("es-CO")} kg`;
    }

    // Peligrosos (RESPEL)
    const kpiHazardousQty = document.getElementById("kpiHazardousQty");
    if (kpiHazardousQty) {
        kpiHazardousQty.textContent = Number(data.hazardous_quantity || 0).toLocaleString("es-CO", {
            minimumFractionDigits: 1,
            maximumFractionDigits: 2
        });
    }

    // Cantidad de Lotes Registrados
    const kpiRecordsCount = document.getElementById("kpiRecordsCount");
    if (kpiRecordsCount) {
        kpiRecordsCount.textContent = data.total_records || 0;
    }
}

/**
 * Consulta los registros del mes y año seleccionados
 */
async function loadTableRecords(month, year) {
    const tbody = document.getElementById("wasteTableBody");
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-muted);">Cargando registros...</td></tr>`;
    }

    const res = await apiFetch(`/waste/records?month=${month}&year=${year}`);
    if (!res.ok) {
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--danger);">Error al cargar los registros: ${res.error || 'Verifica la conexión con el servidor'}</td></tr>`;
        }
        return;
    }

    currentRecords = (res.data && res.data.records) ? res.data.records : [];
    filterAndRenderTable();
}

/**
 * Filtra los registros en memoria por texto y categoría, y renderiza la tabla HTML
 */
function filterAndRenderTable() {
    const tbody = document.getElementById("wasteTableBody");
    if (!tbody) return;

    const searchTerm = (document.getElementById("searchInput")?.value || "").toLowerCase().trim();
    const categoryFilter = document.getElementById("selectCategory")?.value || "";

    const filtered = currentRecords.filter(r => {
        // Filtro por categoría
        if (categoryFilter && r.category_id != categoryFilter) {
            return false;
        }

        // Filtro por texto libre
        if (searchTerm) {
            const wasteName = (r.waste_type_name || "").toLowerCase();
            const area = (r.area || "").toLowerCase();
            const disposal = (r.disposal_method || "").toLowerCase();
            const notes = (r.notes || "").toLowerCase();
            const catName = (r.category_name || "").toLowerCase();
            return wasteName.includes(searchTerm) || area.includes(searchTerm) || 
                   disposal.includes(searchTerm) || notes.includes(searchTerm) ||
                   catName.includes(searchTerm);
        }

        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🍃</div>
                    <strong>No se encontraron registros de residuos</strong>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">Prueba modificando los filtros o registra un nuevo lote con el botón superior.</div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filtered.map(r => {
        const catColor = r.category_color || "#2d6a4f";
        const isHazardous = r.is_hazardous;
        const isAdmin = currentUser && currentUser.role === "ADMIN";

        return `
            <tr data-id="${r.id}">
                <td style="font-weight: 600; white-space: nowrap;">${r.record_date}</td>
                <td>
                    <span class="badge-category" style="background-color: ${catColor}15; color: ${catColor}; border: 1px solid ${catColor}40;">
                        ● ${escapeHtml(r.category_name)}
                    </span>
                    ${isHazardous ? '<span class="badge-hazard">RESPEL ⚠️</span>' : ''}
                </td>
                <td style="font-weight: 600; color: var(--primary);">
                    ${escapeHtml(r.waste_type_name)}
                    ${r.notes ? `<div style="font-size: 0.775rem; color: var(--text-muted); font-weight: normal; margin-top: 2px;">💬 ${escapeHtml(r.notes)}</div>` : ''}
                </td>
                <td style="font-weight: 700; white-space: nowrap;">
                    ${Number(r.quantity).toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 2 })}
                    <small style="color: var(--text-muted); font-weight: 500;">${r.unit}</small>
                </td>
                <td>${escapeHtml(r.area)}</td>
                <td>
                    <span style="display: inline-block; padding: 0.2rem 0.5rem; background: #f1f5f9; border-radius: 4px; font-size: 0.8rem; font-weight: 500;">
                        ${escapeHtml(r.disposal_method)}
                    </span>
                </td>
                <td>
                    <div style="font-size: 0.825rem; font-weight: 600;">${escapeHtml(r.recorded_by_name || 'Usuario')}</div>
                </td>
                <td style="text-align: right; white-space: nowrap;">
                    <div class="action-buttons" style="justify-content: flex-end;">
                        <button onclick="handleEditRecord(${r.id})" class="btn-action-icon" title="Editar registro">
                            ✏️
                        </button>
                        ${isAdmin ? `
                            <button onclick="handleDeleteRecord(${r.id})" class="btn-action-icon btn-action-danger" title="Eliminar registro (Solo Admin)">
                                🗑️
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

/**
 * Abre el modal para registrar un nuevo residuo
 */
function openModalForCreate() {
    const modal = document.getElementById("wasteModal");
    const modalTitle = document.getElementById("modalTitle");
    const form = document.getElementById("wasteForm");
    const alertBox = document.getElementById("modalAlert");
    const recordId = document.getElementById("recordId");
    const recordDate = document.getElementById("recordDate");

    if (form) form.reset();
    if (recordId) recordId.value = "";
    if (alertBox) {
        alertBox.style.display = "none";
        alertBox.textContent = "";
    }
    if (modalTitle) modalTitle.textContent = "Registrar Nuevo Residuo";

    // Poner fecha de hoy
    if (recordDate) {
        recordDate.value = new Date().toISOString().split("T")[0];
    }

    if (modal) modal.classList.add("active");
}

/**
 * Abre el modal en modo edición cargando los datos del registro
 */
window.handleEditRecord = function(id) {
    const record = currentRecords.find(r => r.id === id);
    if (!record) return;

    const modal = document.getElementById("wasteModal");
    const modalTitle = document.getElementById("modalTitle");
    const alertBox = document.getElementById("modalAlert");

    if (alertBox) alertBox.style.display = "none";
    if (modalTitle) modalTitle.textContent = `Editar Registro #${record.id}`;

    // Llenar campos
    document.getElementById("recordId").value = record.id;
    document.getElementById("wasteTypeSelect").value = record.waste_type_id;
    document.getElementById("recordDate").value = record.record_date;
    document.getElementById("quantity").value = record.quantity;
    document.getElementById("unit").value = record.unit;
    document.getElementById("area").value = record.area;
    document.getElementById("disposalMethod").value = record.disposal_method;
    document.getElementById("notes").value = record.notes || "";

    if (modal) modal.classList.add("active");
};

/**
 * Cierra el modal
 */
function closeModal() {
    const modal = document.getElementById("wasteModal");
    if (modal) modal.classList.remove("active");
}

/**
 * Procesa el envío del formulario para crear o actualizar un registro
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("modalAlert");
    const btnSave = document.getElementById("btnSaveRecord");
    const recordId = document.getElementById("recordId").value;
    const isEdit = !!recordId;

    const payload = {
        waste_type_id: parseInt(document.getElementById("wasteTypeSelect").value, 10),
        record_date: document.getElementById("recordDate").value,
        quantity: parseFloat(document.getElementById("quantity").value),
        unit: document.getElementById("unit").value,
        area: document.getElementById("area").value.trim(),
        disposal_method: document.getElementById("disposalMethod").value,
        notes: document.getElementById("notes").value.trim()
    };

    // Validación local básica
    if (!payload.waste_type_id) {
        showModalAlert("Por favor seleccione un tipo de residuo.", "danger");
        return;
    }

    if (isNaN(payload.quantity) || payload.quantity <= 0) {
        showModalAlert("La cantidad debe ser un número positivo mayor a cero.", "danger");
        return;
    }

    if (!payload.record_date || !payload.area || !payload.disposal_method) {
        showModalAlert("Por favor completa todos los campos requeridos.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = isEdit ? "Actualizando..." : "Guardando...";

    const url = isEdit ? `/waste/records/${recordId}` : "/waste/records";
    const method = isEdit ? "PUT" : "POST";

    const res = await apiFetch(url, {
        method,
        body: JSON.stringify(payload)
    });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar Registro";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "Error al procesar la solicitud");
        showModalAlert(errorMsg, "danger");
        return;
    }

    // Éxito: cerrar modal y refrescar
    closeModal();
    showGlobalAlert(
        isEdit ? "Registro de residuo actualizado correctamente." : "Residuo registrado exitosamente.",
        "success"
    );
    await loadSummaryAndRecords();
}

/**
 * Elimina un registro de residuo (Requiere permisos de Administrador)
 */
window.handleDeleteRecord = async function(id) {
    if (!confirm(`¿Estás seguro de que deseas eliminar el registro #${id}? Esta acción no se puede deshacer.`)) {
        return;
    }

    const res = await apiFetch(`/waste/records/${id}`, {
        method: "DELETE"
    });

    if (!res.ok) {
        const msg = (res.data && res.data.error) ? res.data.error : (res.error || "No se pudo eliminar el registro");
        showGlobalAlert(msg, "danger");
        return;
    }

    showGlobalAlert(`Registro #${id} eliminado correctamente.`, "success");
    await loadSummaryAndRecords();
};

/**
 * Exporta la tabla de registros visible a un archivo CSV descargable
 */
function exportCurrentRecordsToCSV() {
    if (!currentRecords || currentRecords.length === 0) {
        alert("No hay registros disponibles para exportar.");
        return;
    }

    const headers = ["ID", "Fecha", "Categoría", "Tipo de Residuo", "Es Peligroso (RESPEL)", "Cantidad", "Unidad", "Área", "Disposición Final", "Registrado Por", "Notas"];
    const rows = currentRecords.map(r => [
        r.id,
        `"${r.record_date}"`,
        `"${(r.category_name || '').replace(/"/g, '""')}"`,
        `"${(r.waste_type_name || '').replace(/"/g, '""')}"`,
        r.is_hazardous ? "SÍ" : "NO",
        r.quantity,
        `"${r.unit}"`,
        `"${(r.area || '').replace(/"/g, '""')}"`,
        `"${(r.disposal_method || '').replace(/"/g, '""')}"`,
        `"${(r.recorded_by_name || '').replace(/"/g, '""')}"`,
        `"${(r.notes || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(e => e.join(","))].join("\r\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const month = document.getElementById("selectMonth")?.value || "mes";
    const year = document.getElementById("selectYear")?.value || "2026";
    link.setAttribute("href", url);
    link.setAttribute("download", `ecosafe_residuos_${year}_${month}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Muestra alertas dentro del modal
 */
function showModalAlert(message, type = "danger") {
    const alertBox = document.getElementById("modalAlert");
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type}`;
    alertBox.style.display = "block";
}

/**
 * Muestra alertas globales en la parte superior del contenido
 */
function showGlobalAlert(message, type = "success") {
    const alertBox = document.getElementById("globalAlert");
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type}`;
    alertBox.style.display = "block";
    setTimeout(() => {
        alertBox.style.display = "none";
    }, 4500);
}

/**
 * Función utilitaria para sanitizar cadenas HTML
 */
function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
