/**
 * ==========================================================
 * ECOSAFE PLANT - CONTROLADOR DE SEGURIDAD SST (SPEC 004)
 * Matriz de Peligros (IPVR) y Reportes de Incidentes
 * ==========================================================
 */

let currentView = "hazards"; // 'hazards' | 'incidents'
let hazardsList = [];
let incidentsList = [];
let summaryData = null;
let currentUser = null;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Verificar autenticación obligatoria
    currentUser = requireAuthPage();
    if (!currentUser) return;

    // Configurar menú móvil
    initSidebarToggle();

    // 2. Establecer fecha/hora actual en modal de incidente
    setIncidentDefaultDateTime();

    // 3. Inicializar escuchadores de eventos
    initEventListeners();

    // 4. Cargar datos iniciales
    await loadSummary();
    await loadHazards();
    await loadIncidents();
});

function initSidebarToggle() {
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }
}

function setIncidentDefaultDateTime() {
    const dateInput = document.getElementById("incidentDate");
    if (dateInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.value = now.toISOString().slice(0, 16);
    }
}

function initEventListeners() {
    // Pestañas Matriz vs Incidentes
    const tabHazards = document.getElementById("tabHazardsBtn");
    const tabIncidents = document.getElementById("tabIncidentsBtn");

    if (tabHazards && tabIncidents) {
        tabHazards.addEventListener("click", () => switchView("hazards"));
        tabIncidents.addEventListener("click", () => switchView("incidents"));
    }

    // Filtros de Matriz IPVR
    const searchHazard = document.getElementById("searchHazardInput");
    const selectArea = document.getElementById("selectHazardArea");
    const selectRisk = document.getElementById("selectRiskLevel");

    if (searchHazard) searchHazard.addEventListener("input", filterAndRenderHazards);
    if (selectArea) selectArea.addEventListener("change", filterAndRenderHazards);
    if (selectRisk) selectRisk.addEventListener("change", filterAndRenderHazards);

    // Filtros de Incidentes
    const searchIncident = document.getElementById("searchIncidentInput");
    const selectStatus = document.getElementById("selectIncidentStatus");
    const selectSeverity = document.getElementById("selectIncidentSeverity");

    if (searchIncident) searchIncident.addEventListener("input", filterAndRenderIncidents);
    if (selectStatus) selectStatus.addEventListener("change", filterAndRenderIncidents);
    if (selectSeverity) selectSeverity.addEventListener("change", filterAndRenderIncidents);

    // Modal Peligros
    const btnOpenHazard = document.getElementById("btnOpenHazardModal");
    const btnCloseHazard = document.getElementById("btnCloseHazardModal");
    const btnCancelHazard = document.getElementById("btnCancelHazardModal");
    const hazardModal = document.getElementById("hazardModal");
    const hazardForm = document.getElementById("hazardForm");

    if (btnOpenHazard) btnOpenHazard.addEventListener("click", openCreateHazardModal);
    if (btnCloseHazard) btnCloseHazard.addEventListener("click", closeHazardModal);
    if (btnCancelHazard) btnCancelHazard.addEventListener("click", closeHazardModal);

    if (hazardModal) {
        hazardModal.addEventListener("click", (e) => {
            if (e.target === hazardModal) closeHazardModal();
        });
    }
    if (hazardForm) hazardForm.addEventListener("submit", handleHazardSubmit);

    // Modal Reporte Incidente
    const btnOpenIncident = document.getElementById("btnOpenIncidentModal");
    const btnCloseIncident = document.getElementById("btnCloseIncidentModal");
    const btnCancelIncident = document.getElementById("btnCancelIncidentModal");
    const incidentModal = document.getElementById("incidentModal");
    const incidentForm = document.getElementById("incidentForm");

    if (btnOpenIncident) btnOpenIncident.addEventListener("click", openIncidentModal);
    if (btnCloseIncident) btnCloseIncident.addEventListener("click", closeIncidentModal);
    if (btnCancelIncident) btnCancelIncident.addEventListener("click", closeIncidentModal);

    if (incidentModal) {
        incidentModal.addEventListener("click", (e) => {
            if (e.target === incidentModal) closeIncidentModal();
        });
    }
    if (incidentForm) incidentForm.addEventListener("submit", handleIncidentSubmit);

    // Modal Resolver Incidente
    const btnCloseResolve = document.getElementById("btnCloseResolveModal");
    const btnCancelResolve = document.getElementById("btnCancelResolveModal");
    const resolveModal = document.getElementById("resolveModal");
    const resolveForm = document.getElementById("resolveForm");

    if (btnCloseResolve) btnCloseResolve.addEventListener("click", closeResolveModal);
    if (btnCancelResolve) btnCancelResolve.addEventListener("click", closeResolveModal);

    if (resolveModal) {
        resolveModal.addEventListener("click", (e) => {
            if (e.target === resolveModal) closeResolveModal();
        });
    }
    if (resolveForm) resolveForm.addEventListener("submit", handleResolveSubmit);

    // Exportar CSV
    const btnExportHazards = document.getElementById("btnExportHazardsCsv");
    if (btnExportHazards) btnExportHazards.addEventListener("click", exportHazardsToCSV);
}

/**
 * Conmuta entre la vista de Matriz de Peligros y la de Reportes de Incidentes
 */
function switchView(view) {
    currentView = view;
    const tabHazards = document.getElementById("tabHazardsBtn");
    const tabIncidents = document.getElementById("tabIncidentsBtn");
    const viewHazards = document.getElementById("viewHazards");
    const viewIncidents = document.getElementById("viewIncidents");

    if (view === "hazards") {
        tabHazards.classList.add("active");
        tabIncidents.classList.remove("active");
        viewHazards.style.display = "block";
        viewIncidents.style.display = "none";
    } else {
        tabIncidents.classList.add("active");
        tabHazards.classList.remove("active");
        viewIncidents.style.display = "block";
        viewHazards.style.display = "none";
    }
}

/**
 * Carga el resumen de métricas SST
 */
async function loadSummary() {
    const res = await apiFetch("/sst/summary");
    if (!res.ok || !res.data) return;

    summaryData = res.data;

    // Días sin accidentes
    const daysEl = document.getElementById("kpiDaysWithoutAccidents");
    if (daysEl) daysEl.textContent = summaryData.days_without_accidents || 142;

    // Incidentes abiertos
    const openEl = document.getElementById("kpiOpenIncidents");
    const pendingTextEl = document.getElementById("kpiPendingText");
    const cardOpen = document.getElementById("kpiCardOpenIncidents");
    const tabBadge = document.getElementById("tabIncidentBadge");

    const pendingCount = summaryData.incidents_by_status?.PENDIENTE || 0;
    const inProgressCount = summaryData.incidents_by_status?.EN_ATENCION || 0;
    const openTotal = summaryData.open_incidents || 0;

    if (openEl) openEl.textContent = openTotal;
    if (tabBadge) tabBadge.textContent = openTotal;
    if (pendingTextEl) pendingTextEl.textContent = `${pendingCount} pendientes, ${inProgressCount} en atención`;

    if (cardOpen) {
        cardOpen.className = openTotal > 0 ? "kpi-card kpi-danger" : "kpi-card kpi-success";
    }

    // Peligros Críticos y Altos
    const critEl = document.getElementById("kpiCriticalHazards");
    const critCount = (summaryData.hazards_by_risk?.CRITICO || 0) + (summaryData.hazards_by_risk?.ALTO || 0);
    if (critEl) critEl.textContent = critCount;

    // Tasa de resolución
    const rateEl = document.getElementById("kpiResolutionRate");
    const resCountEl = document.getElementById("kpiResolvedCount");
    if (rateEl) rateEl.textContent = `${summaryData.resolution_rate || 100}%`;
    if (resCountEl) resCountEl.textContent = `${summaryData.resolved_incidents || 0} resueltos`;
}

// ==========================================================
// MATRIZ DE PELIGROS (IPVR)
// ==========================================================

async function loadHazards() {
    const tbody = document.getElementById("hazardsTableBody");
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Cargando matriz de peligros...</td></tr>`;
    }

    const res = await apiFetch("/sst/hazards");
    if (!res.ok) {
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--danger);">Error al cargar peligros: ${res.error || 'Verifica el servidor'}</td></tr>`;
        }
        return;
    }

    hazardsList = (res.data && res.data.hazards) ? res.data.hazards : [];
    filterAndRenderHazards();
}

function filterAndRenderHazards() {
    const tbody = document.getElementById("hazardsTableBody");
    if (!tbody) return;

    const searchTerm = (document.getElementById("searchHazardInput")?.value || "").toLowerCase().trim();
    const areaFilter = (document.getElementById("selectHazardArea")?.value || "").toLowerCase().trim();
    const riskFilter = (document.getElementById("selectRiskLevel")?.value || "").toUpperCase().trim();

    const filtered = hazardsList.filter(h => {
        if (areaFilter && !h.area.toLowerCase().includes(areaFilter)) return false;
        if (riskFilter && h.risk_level !== riskFilter) return false;

        if (searchTerm) {
            const area = (h.area || "").toLowerCase();
            const act = (h.activity || "").toLowerCase();
            const type = (h.hazard_type || "").toLowerCase();
            const desc = (h.description || "").toLowerCase();
            const controls = (h.controls_in_place || "").toLowerCase();
            return area.includes(searchTerm) || act.includes(searchTerm) || type.includes(searchTerm) || desc.includes(searchTerm) || controls.includes(searchTerm);
        }

        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛡️</div>
                    <strong>No se encontraron peligros que coincidan con los filtros</strong>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">Ajuste los criterios de búsqueda o agregue un nuevo peligro.</div>
                </td>
            </tr>
        `;
        return;
    }

    const isAdminOrSupervisor = currentUser && (currentUser.role === "ADMIN" || currentUser.role === "SUPERVISOR");
    const isAdmin = currentUser && currentUser.role === "ADMIN";

    tbody.innerHTML = filtered.map(h => {
        const riskClass = `risk-${h.risk_level.toLowerCase()}`;
        const riskIcon = h.risk_level === "CRITICO" ? "🔴" : (h.risk_level === "ALTO" ? "🟠" : (h.risk_level === "MEDIO" ? "🟡" : "🟢"));

        return `
            <tr>
                <td>
                    <span class="risk-badge ${riskClass}">
                        ${riskIcon} ${h.risk_level}
                    </span>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">
                        Estado: <strong>${escapeHtml(h.status)}</strong>
                    </div>
                </td>
                <td>
                    <strong style="color: var(--primary); display: block;">${escapeHtml(h.area)}</strong>
                    <div style="font-size: 0.825rem; color: var(--text-dark);">${escapeHtml(h.activity)}</div>
                </td>
                <td>
                    <span style="font-size: 0.775rem; font-weight: 700; color: var(--accent); display: block; text-transform: uppercase;">
                        ${escapeHtml(h.hazard_type)}
                    </span>
                    <div style="font-size: 0.85rem;">${escapeHtml(h.description)}</div>
                </td>
                <td style="font-size: 0.825rem; color: #7f1d1d;">
                    ${escapeHtml(h.potential_consequences || 'No especificadas')}
                </td>
                <td style="font-size: 0.825rem; color: var(--text-muted);">
                    ${escapeHtml(h.controls_in_place || 'Sin controles documentados')}
                </td>
                <td style="font-size: 0.825rem; color: var(--primary); font-weight: 500;">
                    ${escapeHtml(h.recommended_actions || 'Mantener medidas preventivas')}
                </td>
                <td style="text-align: right; white-space: nowrap;">
                    <div class="action-buttons" style="justify-content: flex-end;">
                        ${isAdminOrSupervisor ? `
                            <button onclick="handleEditHazard(${h.id})" class="btn-action-icon" title="Editar peligro">
                                ✏️
                            </button>
                        ` : ''}
                        ${isAdmin ? `
                            <button onclick="handleDeleteHazard(${h.id})" class="btn-action-icon btn-action-danger" title="Eliminar de la matriz (Solo Admin)">
                                🗑️
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function openCreateHazardModal() {
    const modal = document.getElementById("hazardModal");
    const form = document.getElementById("hazardForm");
    const alertBox = document.getElementById("hazardModalAlert");
    const idInput = document.getElementById("hazardId");
    const title = document.getElementById("hazardModalTitle");

    if (form) form.reset();
    if (idInput) idInput.value = "";
    if (alertBox) alertBox.style.display = "none";
    if (title) title.textContent = "Registrar Peligro en Matriz IPVR";

    if (modal) modal.classList.add("active");
}

function closeHazardModal() {
    const modal = document.getElementById("hazardModal");
    if (modal) modal.classList.remove("active");
}

window.handleEditHazard = function(id) {
    const hazard = hazardsList.find(h => h.id === id);
    if (!hazard) return;

    const modal = document.getElementById("hazardModal");
    const title = document.getElementById("hazardModalTitle");
    const alertBox = document.getElementById("hazardModalAlert");

    if (alertBox) alertBox.style.display = "none";
    if (title) title.textContent = `Editar Peligro #${hazard.id}`;

    document.getElementById("hazardId").value = hazard.id;
    document.getElementById("hazardArea").value = hazard.area;
    document.getElementById("hazardActivity").value = hazard.activity;
    document.getElementById("hazardType").value = hazard.hazard_type;
    document.getElementById("hazardDescription").value = hazard.description;
    document.getElementById("hazardRiskLevel").value = hazard.risk_level;
    document.getElementById("hazardStatus").value = hazard.status;
    document.getElementById("hazardConsequences").value = hazard.potential_consequences || "";
    document.getElementById("hazardControls").value = hazard.controls_in_place || "";
    document.getElementById("hazardRecommended").value = hazard.recommended_actions || "";

    if (modal) modal.classList.add("active");
};

async function handleHazardSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("hazardModalAlert");
    const btnSave = document.getElementById("btnSaveHazard");
    const hazardId = document.getElementById("hazardId").value;
    const isEdit = !!hazardId;

    const payload = {
        area: document.getElementById("hazardArea").value.trim(),
        activity: document.getElementById("hazardActivity").value.trim(),
        hazard_type: document.getElementById("hazardType").value,
        description: document.getElementById("hazardDescription").value.trim(),
        risk_level: document.getElementById("hazardRiskLevel").value,
        status: document.getElementById("hazardStatus").value,
        potential_consequences: document.getElementById("hazardConsequences").value.trim(),
        controls_in_place: document.getElementById("hazardControls").value.trim(),
        recommended_actions: document.getElementById("hazardRecommended").value.trim()
    };

    if (!payload.area || !payload.activity || !payload.hazard_type || !payload.description) {
        showModalAlert(alertBox, "Por favor complete los campos obligatorios.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = isEdit ? "Actualizando..." : "Guardando...";

    const url = isEdit ? `/sst/hazards/${hazardId}` : "/sst/hazards";
    const method = isEdit ? "PUT" : "POST";

    const res = await apiFetch(url, { method, body: JSON.stringify(payload) });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar Peligro";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "Error al procesar peligro");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeHazardModal();
    showGlobalAlert(isEdit ? "Peligro actualizado correctamente." : "Peligro agregado a la matriz IPVR con éxito.", "success");
    await loadSummary();
    await loadHazards();
}

window.handleDeleteHazard = async function(id) {
    if (!confirm(`¿Estás seguro de eliminar el peligro #${id} de la matriz? Esta acción no se puede deshacer.`)) {
        return;
    }

    const res = await apiFetch(`/sst/hazards/${id}`, { method: "DELETE" });
    if (!res.ok) {
        const msg = (res.data && res.data.error) ? res.data.error : (res.error || "No se pudo eliminar el peligro");
        showGlobalAlert(msg, "danger");
        return;
    }

    showGlobalAlert(`Peligro #${id} eliminado de la matriz.`, "success");
    await loadSummary();
    await loadHazards();
};

function exportHazardsToCSV() {
    if (!hazardsList || hazardsList.length === 0) {
        alert("No hay peligros en la matriz para exportar.");
        return;
    }

    const headers = ["ID", "Nivel de Riesgo", "Área", "Actividad", "Tipo de Peligro", "Descripción", "Consecuencias Salud", "Controles en Sitio", "Acciones Recomendadas", "Estado"];
    const rows = hazardsList.map(h => [
        h.id,
        `"${h.risk_level}"`,
        `"${(h.area || '').replace(/"/g, '""')}"`,
        `"${(h.activity || '').replace(/"/g, '""')}"`,
        `"${(h.hazard_type || '').replace(/"/g, '""')}"`,
        `"${(h.description || '').replace(/"/g, '""')}"`,
        `"${(h.potential_consequences || '').replace(/"/g, '""')}"`,
        `"${(h.controls_in_place || '').replace(/"/g, '""')}"`,
        `"${(h.recommended_actions || '').replace(/"/g, '""')}"`,
        `"${h.status}"`
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(e => e.join(","))].join("\r\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `ecosafe_matriz_peligros_ipvr_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ==========================================================
// INCIDENTES Y CONDICIONES INSEGURAS
// ==========================================================

async function loadIncidents() {
    const container = document.getElementById("incidentsListContainer");
    if (container) {
        container.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Cargando reportes de incidentes...</div>`;
    }

    const res = await apiFetch("/sst/incidents");
    if (!res.ok) {
        if (container) {
            container.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--danger);">Error al cargar incidentes: ${res.error || 'Verifica la conexión'}</div>`;
        }
        return;
    }

    incidentsList = (res.data && res.data.incidents) ? res.data.incidents : [];
    filterAndRenderIncidents();
}

function filterAndRenderIncidents() {
    const container = document.getElementById("incidentsListContainer");
    if (!container) return;

    const searchTerm = (document.getElementById("searchIncidentInput")?.value || "").toLowerCase().trim();
    const statusFilter = (document.getElementById("selectIncidentStatus")?.value || "").toUpperCase().trim();
    const severityFilter = (document.getElementById("selectIncidentSeverity")?.value || "").toUpperCase().trim();

    const filtered = incidentsList.filter(inc => {
        if (statusFilter && inc.status !== statusFilter) return false;
        if (severityFilter && inc.severity !== severityFilter) return false;

        if (searchTerm) {
            const loc = (inc.location_detail || "").toLowerCase();
            const desc = (inc.description || "").toLowerCase();
            const notes = (inc.resolution_notes || "").toLowerCase();
            const reporter = (inc.reported_by_name || "").toLowerCase();
            return loc.includes(searchTerm) || desc.includes(searchTerm) || notes.includes(searchTerm) || reporter.includes(searchTerm);
        }

        return true;
    });

    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; background: var(--surface); border-radius: var(--radius-md); border: 1px solid var(--border);">
                <div style="font-size: 2.25rem; margin-bottom: 0.5rem;">🎉</div>
                <strong>No hay incidentes ni condiciones inseguras reportadas con estos filtros</strong>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.35rem;">
                    ¡Excelente trabajo! La planta mantiene sus estándares de seguridad activos.
                </div>
            </div>
        `;
        return;
    }

    const isSupervisorOrAdmin = currentUser && (currentUser.role === "ADMIN" || currentUser.role === "SUPERVISOR");

    container.innerHTML = filtered.map(inc => {
        const statusBadgeClass = `status-${inc.status.toLowerCase().replace(/_/g, '-')}`;
        const severityColor = inc.severity === "ALTA" ? "var(--danger)" : (inc.severity === "MEDIA" ? "var(--warning)" : "var(--info)");

        return `
            <article class="incident-card severity-${inc.severity}">
                <div class="incident-card-header">
                    <div>
                        <span class="status-badge ${statusBadgeClass}">
                            ● ${formatIncidentStatus(inc.status)}
                        </span>
                        <span style="font-size: 0.775rem; font-weight: 700; color: ${severityColor}; margin-left: 0.5rem; text-transform: uppercase;">
                            Severidad ${inc.severity}
                        </span>
                        <span style="font-size: 0.8rem; color: var(--text-muted); margin-left: 0.5rem;">
                            #${inc.id}
                        </span>
                    </div>

                    ${isSupervisorOrAdmin ? `
                        <button onclick="openResolveModal(${inc.id})" class="btn-sm-action" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">
                            🛠️ Gestionar Incidente
                        </button>
                    ` : ''}
                </div>

                <h4 style="font-size: 1rem; font-weight: 700; color: var(--primary); margin-bottom: 0.35rem;">
                    📍 ${escapeHtml(inc.location_detail)}
                </h4>

                <p style="font-size: 0.9rem; color: var(--text-dark); margin-bottom: 0.6rem;">
                    ${escapeHtml(inc.description)}
                </p>

                ${inc.resolution_notes ? `
                    <div style="background-color: #f0fdf4; border-left: 4px solid var(--success); padding: 0.65rem 0.85rem; border-radius: 4px; font-size: 0.825rem; margin-bottom: 0.5rem;">
                        <strong style="color: #065f46;">Solución / Acción Correctiva:</strong>
                        <div style="color: #1e293b; margin-top: 2px;">${escapeHtml(inc.resolution_notes)}</div>
                        ${inc.resolved_at ? `<small style="color: #059669; display: block; margin-top: 2px;">Fecha de cierre: ${inc.resolved_at}</small>` : ''}
                    </div>
                ` : ''}

                <div class="incident-meta">
                    <span>👤 Reportado por: <strong>${escapeHtml(inc.reported_by_name || 'Operario')}</strong></span>
                    <span>📅 Fecha: <strong>${inc.incident_date}</strong></span>
                    <span>🏷️ Tipo: <strong>${formatIncidentType(inc.incident_type)}</strong></span>
                    ${inc.assigned_to_name ? `<span>👷 Responsable: <strong>${escapeHtml(inc.assigned_to_name)}</strong></span>` : ''}
                </div>
            </article>
        `;
    }).join("");
}

function formatIncidentStatus(status) {
    switch (status) {
        case "PENDIENTE": return "Pendiente de atención";
        case "EN_ATENCION": return "En atención técnica";
        case "RESUELTO": return "Resuelto y verificado";
        case "DESESTIMADO": return "Desestimado";
        default: return status;
    }
}

function formatIncidentType(type) {
    switch (type) {
        case "CONDICION_INSEGURA": return "Condición Insegura";
        case "ACTO_INSEGURO": return "Acto Inseguro";
        case "CASI_ACCIDENTE": return "Casi Accidente";
        case "ACCIDENTE_LEVE": return "Accidente Leve";
        case "ACCIDENTE_GRAVE": return "Accidente Grave";
        default: return type;
    }
}

function openIncidentModal() {
    const modal = document.getElementById("incidentModal");
    const form = document.getElementById("incidentForm");
    const alertBox = document.getElementById("incidentModalAlert");

    if (form) form.reset();
    if (alertBox) alertBox.style.display = "none";
    setIncidentDefaultDateTime();

    if (modal) modal.classList.add("active");
}

function closeIncidentModal() {
    const modal = document.getElementById("incidentModal");
    if (modal) modal.classList.remove("active");
}

async function handleIncidentSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("incidentModalAlert");
    const btnSave = document.getElementById("btnSaveIncident");

    const payload = {
        incident_type: document.getElementById("incidentType").value,
        location_detail: document.getElementById("incidentLocation").value.trim(),
        description: document.getElementById("incidentDescription").value.trim(),
        severity: document.getElementById("incidentSeverity").value,
        incident_date: document.getElementById("incidentDate").value || undefined
    };

    if (!payload.location_detail || !payload.description) {
        showModalAlert(alertBox, "Por favor complete el lugar y la descripción.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = "Enviando...";

    const res = await apiFetch("/sst/incidents", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    btnSave.disabled = false;
    btnSave.textContent = "Enviar Reporte Inmediato";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "No se pudo registrar el incidente");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeIncidentModal();
    showGlobalAlert("🚨 Reporte de condición insegura registrado exitosamente. El supervisor ha sido notificado.", "success");
    await loadSummary();
    await loadIncidents();
}

window.openResolveModal = function(id) {
    const inc = incidentsList.find(i => i.id === id);
    if (!inc) return;

    const modal = document.getElementById("resolveModal");
    const alertBox = document.getElementById("resolveModalAlert");

    if (alertBox) alertBox.style.display = "none";

    document.getElementById("resolveIncidentId").value = inc.id;
    document.getElementById("resolveIncidentIdText").textContent = inc.id;
    document.getElementById("resolveIncidentDescription").textContent = inc.description;
    document.getElementById("resolveIncidentMeta").textContent = `Lugar: ${inc.location_detail} | Reportado por: ${inc.reported_by_name || 'Operario'} (${inc.incident_date})`;

    document.getElementById("resolveStatusSelect").value = inc.status === "PENDIENTE" ? "EN_ATENCION" : inc.status;
    document.getElementById("resolveNotes").value = inc.resolution_notes || "";

    if (modal) modal.classList.add("active");
};

function closeResolveModal() {
    const modal = document.getElementById("resolveModal");
    if (modal) modal.classList.remove("active");
}

async function handleResolveSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("resolveModalAlert");
    const btnSave = document.getElementById("btnSaveResolve");
    const incidentId = document.getElementById("resolveIncidentId").value;

    const payload = {
        status: document.getElementById("resolveStatusSelect").value,
        resolution_notes: document.getElementById("resolveNotes").value.trim()
    };

    if (!payload.resolution_notes) {
        showModalAlert(alertBox, "Por favor indique las notas de resolución o acciones tomadas.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = "Actualizando...";

    const res = await apiFetch(`/sst/incidents/${incidentId}/status`, {
        method: "PATCH",
        body: JSON.stringify(payload)
    });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar Gestión";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "Error al actualizar estado");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeResolveModal();
    showGlobalAlert(`Incidente #${incidentId} actualizado correctamente.`, "success");
    await loadSummary();
    await loadIncidents();
}

function showModalAlert(alertBox, message, type = "danger") {
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type}`;
    alertBox.style.display = "block";
}

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

function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
