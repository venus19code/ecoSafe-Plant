/**
 * ==========================================================
 * ECOSAFE PLANT - CONTROLADOR DE EPP Y DOTACIONES (SPEC 005)
 * ==========================================================
 */

let currentView = "deliveries"; // 'deliveries' | 'renewals' | 'catalog' | 'inspections'
let catalogList = [];
let deliveriesList = [];
let renewalsList = [];
let inspectionsList = [];
let workersList = [];
let summaryData = null;
let currentUser = null;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Autenticación obligatoria
    currentUser = requireAuthPage();
    if (!currentUser) return;

    // Menú móvil
    initSidebarToggle();

    // 2. Establecer fechas por defecto en modales
    const today = new Date().toISOString().split("T")[0];
    const deliveryDateInput = document.getElementById("deliveryDateInput");
    const inspectionDateInput = document.getElementById("inspectionDateInput");
    if (deliveryDateInput) deliveryDateInput.value = today;
    if (inspectionDateInput) inspectionDateInput.value = today;

    // 3. Inicializar eventos
    initEventListeners();

    // 4. Cargar datos
    await loadWorkers();
    await loadCatalog();
    await loadSummary();
    await loadDeliveries();
    await loadRenewals();
    await loadInspections();
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

function initEventListeners() {
    // Navegación de pestañas
    const tabDeliveries = document.getElementById("tabDeliveriesBtn");
    const tabRenewals = document.getElementById("tabRenewalsBtn");
    const tabCatalog = document.getElementById("tabCatalogBtn");
    const tabInspections = document.getElementById("tabInspectionsBtn");
    const btnBannerRenewals = document.getElementById("btnViewRenewalsFromBanner");

    if (tabDeliveries) tabDeliveries.addEventListener("click", () => switchTab("deliveries"));
    if (tabRenewals) tabRenewals.addEventListener("click", () => switchTab("renewals"));
    if (tabCatalog) tabCatalog.addEventListener("click", () => switchTab("catalog"));
    if (tabInspections) tabInspections.addEventListener("click", () => switchTab("inspections"));
    if (btnBannerRenewals) btnBannerRenewals.addEventListener("click", () => switchTab("renewals"));

    // Filtros de Entregas
    const searchDeliv = document.getElementById("searchDeliveriesInput");
    const selectCatDeliv = document.getElementById("selectDeliveryCategory");
    const selectReasonDeliv = document.getElementById("selectDeliveryReason");

    if (searchDeliv) searchDeliv.addEventListener("input", filterAndRenderDeliveries);
    if (selectCatDeliv) selectCatDeliv.addEventListener("change", filterAndRenderDeliveries);
    if (selectReasonDeliv) selectReasonDeliv.addEventListener("change", filterAndRenderDeliveries);

    // Filtros Catálogo
    const searchCat = document.getElementById("searchCatalogInput");
    const selectCatCat = document.getElementById("selectCatalogCategory");
    if (searchCat) searchCat.addEventListener("input", filterAndRenderCatalog);
    if (selectCatCat) selectCatCat.addEventListener("change", filterAndRenderCatalog);

    // Filtros Inspecciones
    const searchInsp = document.getElementById("searchInspectionsInput");
    const selectCompInsp = document.getElementById("selectInspectionCompliance");
    if (searchInsp) searchInsp.addEventListener("input", filterAndRenderInspections);
    if (selectCompInsp) selectCompInsp.addEventListener("change", filterAndRenderInspections);

    // Modal Asignar Dotación
    const btnOpenDeliv = document.getElementById("btnOpenDeliveryModal");
    const btnCloseDeliv = document.getElementById("btnCloseDeliveryModal");
    const btnCancelDeliv = document.getElementById("btnCancelDeliveryModal");
    const delivModal = document.getElementById("deliveryModal");
    const delivForm = document.getElementById("deliveryForm");
    const delivEppSelect = document.getElementById("deliveryEppSelect");
    const delivDateInput = document.getElementById("deliveryDateInput");

    if (btnOpenDeliv) btnOpenDeliv.addEventListener("click", () => openDeliveryModal());
    if (btnCloseDeliv) btnCloseDeliv.addEventListener("click", closeDeliveryModal);
    if (btnCancelDeliv) btnCancelDeliv.addEventListener("click", closeDeliveryModal);
    if (delivModal) {
        delivModal.addEventListener("click", (e) => {
            if (e.target === delivModal) closeDeliveryModal();
        });
    }

    if (delivEppSelect) delivEppSelect.addEventListener("change", calculateRenewalDateInForm);
    if (delivDateInput) delivDateInput.addEventListener("change", calculateRenewalDateInForm);
    if (delivForm) delivForm.addEventListener("submit", handleDeliverySubmit);

    // Modal Catálogo
    const btnOpenCat = document.getElementById("btnOpenCatalogModal");
    const btnCloseCat = document.getElementById("btnCloseCatalogModal");
    const btnCancelCat = document.getElementById("btnCancelCatalogModal");
    const catModal = document.getElementById("catalogModal");
    const catForm = document.getElementById("catalogForm");

    if (btnOpenCat) btnOpenCat.addEventListener("click", openCatalogModal);
    if (btnCloseCat) btnCloseCat.addEventListener("click", closeCatalogModal);
    if (btnCancelCat) btnCancelCat.addEventListener("click", closeCatalogModal);
    if (catModal) {
        catModal.addEventListener("click", (e) => {
            if (e.target === catModal) closeCatalogModal();
        });
    }
    if (catForm) catForm.addEventListener("submit", handleCatalogSubmit);

    // Modal Inspección
    const btnOpenInsp = document.getElementById("btnOpenInspectionModal");
    const btnCloseInsp = document.getElementById("btnCloseInspectionModal");
    const btnCancelInsp = document.getElementById("btnCancelInspectionModal");
    const inspModal = document.getElementById("inspectionModal");
    const inspForm = document.getElementById("inspectionForm");
    const radioTrue = document.getElementById("radioCompliantTrue");
    const radioFalse = document.getElementById("radioCompliantFalse");

    if (btnOpenInsp) btnOpenInsp.addEventListener("click", openInspectionModal);
    if (btnCloseInsp) btnCloseInsp.addEventListener("click", closeInspectionModal);
    if (btnCancelInsp) btnCancelInsp.addEventListener("click", closeInspectionModal);
    if (inspModal) {
        inspModal.addEventListener("click", (e) => {
            if (e.target === inspModal) closeInspectionModal();
        });
    }

    if (radioTrue && radioFalse) {
        radioTrue.addEventListener("change", toggleNonCompliantFields);
        radioFalse.addEventListener("change", toggleNonCompliantFields);
    }
    if (inspForm) inspForm.addEventListener("submit", handleInspectionSubmit);

    // Exportar CSV
    const btnExport = document.getElementById("btnExportDeliveriesCsv");
    if (btnExport) btnExport.addEventListener("click", exportDeliveriesToCSV);
}

function switchTab(view) {
    currentView = view;
    const views = ["deliveries", "renewals", "catalog", "inspections"];

    views.forEach(v => {
        const tabBtn = document.getElementById(`tab${v.charAt(0).toUpperCase() + v.slice(1)}Btn`);
        const viewEl = document.getElementById(`view${v.charAt(0).toUpperCase() + v.slice(1)}`);
        if (tabBtn && viewEl) {
            if (v === view) {
                tabBtn.classList.add("active");
                viewEl.style.display = "block";
            } else {
                tabBtn.classList.remove("active");
                viewEl.style.display = "none";
            }
        }
    });
}

/**
 * Carga usuarios/trabajadores para selects
 */
async function loadWorkers() {
    const res = await apiFetch("/users");
    if (res.ok && res.data) {
        workersList = res.data.users || [];
        populateWorkerSelects();
    }
}

function populateWorkerSelects() {
    const delivSelect = document.getElementById("deliveryWorkerSelect");
    const inspSelect = document.getElementById("inspectionWorkerSelect");

    const options = workersList.map(w => `<option value="${w.id}">${escapeHtml(w.name)} (${w.role} - ${escapeHtml(w.area)})</option>`).join("");

    if (delivSelect) delivSelect.innerHTML = `<option value="">-- Seleccionar colaborador --</option>` + options;
    if (inspSelect) inspSelect.innerHTML = `<option value="">-- Seleccionar trabajador --</option>` + options;
}

/**
 * Carga catálogo de EPP
 */
async function loadCatalog() {
    const res = await apiFetch("/epp/catalog");
    if (res.ok && res.data) {
        catalogList = res.data.catalog || [];
        populateEppSelect();
        filterAndRenderCatalog();
    }
}

function populateEppSelect() {
    const eppSelect = document.getElementById("deliveryEppSelect");
    if (!eppSelect) return;

    eppSelect.innerHTML = '<option value="">-- Seleccionar elemento del catálogo --</option>';

    const grouped = {};
    catalogList.forEach(item => {
        if (!grouped[item.category]) grouped[item.category] = [];
        grouped[item.category].push(item);
    });

    Object.keys(grouped).forEach(cat => {
        const group = document.createElement("optgroup");
        group.label = cat;
        grouped[cat].forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = `${item.name} (${item.lifespan_days} días) - Stock: ${item.stock_quantity}`;
            opt.dataset.lifespan = item.lifespan_days;
            group.appendChild(opt);
        });
        eppSelect.appendChild(group);
    });
}

/**
 * Carga resumen de métricas
 */
async function loadSummary() {
    const res = await apiFetch("/epp/summary");
    if (!res.ok || !res.data) return;

    summaryData = res.data;

    // Vencidos
    const expiredEl = document.getElementById("kpiExpiredCount");
    const dueSoonEl = document.getElementById("kpiDueSoonCount");
    const cardExpired = document.getElementById("kpiCardExpired");
    const banner = document.getElementById("eppAlertBanner");
    const bannerText = document.getElementById("eppAlertBannerText");
    const tabRenewalsBadge = document.getElementById("tabRenewalsBadge");

    const expiredCount = summaryData.expired_count || 0;
    const dueSoonCount = summaryData.due_soon_count || 0;
    const totalRenewalsAlert = expiredCount + dueSoonCount;

    if (expiredEl) expiredEl.textContent = expiredCount;
    if (dueSoonEl) dueSoonEl.textContent = dueSoonCount;
    if (tabRenewalsBadge) tabRenewalsBadge.textContent = totalRenewalsAlert;

    if (banner && bannerText) {
        if (expiredCount > 0) {
            banner.style.display = "flex";
            bannerText.textContent = `Hay ${expiredCount} dotación(es) con vida útil expirada en planta que requieren cambio inmediato.`;
        } else if (dueSoonCount > 0) {
            banner.style.display = "flex";
            bannerText.textContent = `Hay ${dueSoonCount} dotación(es) que vencerán en los próximos 30 días. Programe su recambio.`;
        } else {
            banner.style.display = "none";
        }
    }

    if (cardExpired) {
        cardExpired.className = expiredCount > 0 ? "kpi-card kpi-danger" : "kpi-card kpi-success";
    }

    // Entregas del mes
    const monthDelivEl = document.getElementById("kpiMonthDeliveries");
    const totalDelivEl = document.getElementById("kpiTotalDeliveriesText");
    if (monthDelivEl) monthDelivEl.textContent = summaryData.month_deliveries || 0;
    if (totalDelivEl) totalDelivEl.textContent = `Total histórico: ${summaryData.total_deliveries || 0}`;

    // Cumplimiento inspecciones
    const complEl = document.getElementById("kpiComplianceRate");
    const totalInspEl = document.getElementById("kpiTotalInspectionsText");
    if (complEl) complEl.textContent = `${summaryData.compliance_rate || 100}%`;
    if (totalInspEl) totalInspEl.textContent = `En ${summaryData.total_inspections || 0} inspecciones en planta`;
}

// ==========================================================
// VISTA: ENTREGAS
// ==========================================================

async function loadDeliveries() {
    const tbody = document.getElementById("deliveriesTableBody");
    if (tbody) tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-muted);">Cargando entregas...</td></tr>`;

    const res = await apiFetch("/epp/deliveries");
    if (!res.ok) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--danger);">Error al cargar entregas</td></tr>`;
        return;
    }

    deliveriesList = (res.data && res.data.deliveries) ? res.data.deliveries : [];
    filterAndRenderDeliveries();
}

function filterAndRenderDeliveries() {
    const tbody = document.getElementById("deliveriesTableBody");
    if (!tbody) return;

    const searchTerm = (document.getElementById("searchDeliveriesInput")?.value || "").toLowerCase().trim();
    const catFilter = (document.getElementById("selectDeliveryCategory")?.value || "").toUpperCase().trim();
    const reasonFilter = (document.getElementById("selectDeliveryReason")?.value || "").toUpperCase().trim();

    const filtered = deliveriesList.filter(d => {
        if (catFilter && d.epp_category !== catFilter) return false;
        if (reasonFilter && d.reason !== reasonFilter) return false;

        if (searchTerm) {
            const wName = (d.worker_name || "").toLowerCase();
            const wArea = (d.worker_area || "").toLowerCase();
            const eName = (d.epp_name || "").toLowerCase();
            const notes = (d.notes || "").toLowerCase();
            return wName.includes(searchTerm) || wArea.includes(searchTerm) || eName.includes(searchTerm) || notes.includes(searchTerm);
        }

        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📦</div>
                    <strong>No se encontraron entregas con estos filtros</strong>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filtered.map(d => {
        const catBadgeClass = `badge-epp-${(d.epp_category || 'cuerpo').toLowerCase()}`;
        const isExpired = d.is_expired;
        const daysLeft = d.days_until_renewal;

        let statusBadge = "";
        if (isExpired) {
            statusBadge = `<span class="badge-renewal-expired">🔴 Vencida (${Math.abs(daysLeft)}d atraso)</span>`;
        } else if (daysLeft <= 30) {
            statusBadge = `<span class="badge-renewal-due-soon">🟡 Vence en ${daysLeft} días</span>`;
        } else {
            statusBadge = `<span class="badge-renewal-ok">🟢 Vigente (${daysLeft} días)</span>`;
        }

        return `
            <tr>
                <td style="font-weight: 600; white-space: nowrap;">${d.delivery_date}</td>
                <td>
                    <strong style="color: var(--primary);">${escapeHtml(d.worker_name)}</strong>
                </td>
                <td style="font-size: 0.825rem; color: var(--text-muted);">${escapeHtml(d.worker_area)}</td>
                <td>
                    <div style="font-weight: 600;">${escapeHtml(d.epp_name)}</div>
                    <small style="color: var(--text-muted);">Cantidad: ${d.quantity} | Motivo: ${formatReason(d.reason)}</small>
                </td>
                <td>
                    <span class="badge-epp-category ${catBadgeClass}">
                        ${escapeHtml(d.epp_category)}
                    </span>
                </td>
                <td style="font-weight: 700; white-space: nowrap;">${d.next_renewal_date}</td>
                <td style="white-space: nowrap;">${statusBadge}</td>
                <td style="font-size: 0.825rem;">${escapeHtml(d.delivered_by_name || 'Supervisor')}</td>
            </tr>
        `;
    }).join("");
}

function formatReason(r) {
    switch (r) {
        case "DOTACION_PERIODICA": return "Periódica";
        case "INGRESO_NUEVO": return "Nuevo Ingreso";
        case "DETERIORO": return "Deterioro";
        case "PERDIDA": return "Pérdida";
        default: return r;
    }
}

// ==========================================================
// VISTA: ALERTAS DE REPOSICIÓN
// ==========================================================

async function loadRenewals() {
    const tbody = document.getElementById("renewalsTableBody");
    if (tbody) tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 2rem; color: var(--text-muted);">Cargando alertas de renovación...</td></tr>`;

    const res = await apiFetch("/epp/renewals-due");
    if (!res.ok) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 2rem; color: var(--danger);">Error al cargar renovaciones</td></tr>`;
        return;
    }

    renewalsList = (res.data && res.data.renewals) ? res.data.renewals : [];
    renderRenewalsTable();
}

function renderRenewalsTable() {
    const tbody = document.getElementById("renewalsTableBody");
    if (!tbody) return;

    if (renewalsList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎉</div>
                    <strong>¡Excelente! No hay dotaciones vencidas ni próximas a vencer</strong>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">Todos los colaboradores cuentan con EPP dentro de su vida útil.</div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = renewalsList.map(r => {
        const isExpired = r.is_expired;
        const days = r.days_left;
        const stock = r.stock_quantity || 0;

        return `
            <tr style="${isExpired ? 'background-color: #fef2f2;' : ''}">
                <td style="white-space: nowrap;">
                    ${isExpired 
                        ? `<span class="badge-renewal-expired">🔴 VENCIDO</span>` 
                        : `<span class="badge-renewal-due-soon">🟡 POR VENCER</span>`}
                </td>
                <td>
                    <strong style="color: var(--primary);">${escapeHtml(r.worker_name)}</strong>
                </td>
                <td style="font-size: 0.825rem; color: var(--text-muted);">${escapeHtml(r.worker_area)}</td>
                <td>
                    <strong>${escapeHtml(r.epp_name)}</strong>
                    <div style="font-size: 0.775rem; color: var(--text-muted);">${escapeHtml(r.epp_category)}</div>
                </td>
                <td>${r.delivery_date}</td>
                <td style="font-weight: 700; color: ${isExpired ? '#991b1b' : '#b45309'};">${r.next_renewal_date}</td>
                <td style="font-weight: 700;">
                    ${isExpired ? `<span style="color: #991b1b;">+${Math.abs(days)} días de retraso</span>` : `<span style="color: #b45309;">${days} días restantes</span>`}
                </td>
                <td>
                    <span style="font-weight: 700; color: ${stock > 0 ? 'var(--primary)' : 'var(--danger)'};">
                        ${stock} unidades
                    </span>
                </td>
                <td style="text-align: right; white-space: nowrap;">
                    <button onclick="openDeliveryModalWithData(${r.worker_id}, ${r.epp_id})" class="btn-sm-action" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">
                        🔄 Reemplazar Dotación
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

// ==========================================================
// VISTA: CATÁLOGO
// ==========================================================

function filterAndRenderCatalog() {
    const tbody = document.getElementById("catalogTableBody");
    if (!tbody) return;

    const searchTerm = (document.getElementById("searchCatalogInput")?.value || "").toLowerCase().trim();
    const catFilter = (document.getElementById("selectCatalogCategory")?.value || "").toUpperCase().trim();

    const filtered = catalogList.filter(item => {
        if (catFilter && item.category !== catFilter) return false;
        if (searchTerm) {
            const name = (item.name || "").toLowerCase();
            const std = (item.standard_code || "").toLowerCase();
            const desc = (item.description || "").toLowerCase();
            return name.includes(searchTerm) || std.includes(searchTerm) || desc.includes(searchTerm);
        }
        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">No se encontraron elementos en el catálogo</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(item => {
        const catBadgeClass = `badge-epp-${item.category.toLowerCase()}`;
        return `
            <tr>
                <td><span class="badge-epp-category ${catBadgeClass}">${item.category}</span></td>
                <td><strong style="color: var(--primary);">${escapeHtml(item.name)}</strong></td>
                <td><code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${escapeHtml(item.standard_code || 'N/A')}</code></td>
                <td><strong>${item.lifespan_days} días</strong> (~${Math.round(item.lifespan_days / 30)} meses)</td>
                <td>
                    <strong style="color: ${item.stock_quantity < 10 ? 'var(--danger)' : 'var(--primary)'};">
                        ${item.stock_quantity} uds ${item.stock_quantity < 10 ? '⚠️' : ''}
                    </strong>
                </td>
                <td style="font-size: 0.825rem; color: var(--text-muted);">${escapeHtml(item.description || '-')}</td>
            </tr>
        `;
    }).join("");
}

// ==========================================================
// VISTA: INSPECCIONES
// ==========================================================

async function loadInspections() {
    const tbody = document.getElementById("inspectionsTableBody");
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Cargando inspecciones...</td></tr>`;

    const res = await apiFetch("/epp/inspections");
    if (!res.ok) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--danger);">Error al cargar inspecciones</td></tr>`;
        return;
    }

    inspectionsList = (res.data && res.data.inspections) ? res.data.inspections : [];
    filterAndRenderInspections();
}

function filterAndRenderInspections() {
    const tbody = document.getElementById("inspectionsTableBody");
    if (!tbody) return;

    const searchTerm = (document.getElementById("searchInspectionsInput")?.value || "").toLowerCase().trim();
    const compFilter = document.getElementById("selectInspectionCompliance")?.value;

    const filtered = inspectionsList.filter(insp => {
        if (compFilter === "true" && !insp.is_compliant) return false;
        if (compFilter === "false" && insp.is_compliant) return false;

        if (searchTerm) {
            const wName = (insp.worker_name || "").toLowerCase();
            const area = (insp.area || "").toLowerCase();
            const def = (insp.deficiencies_found || "").toLowerCase();
            return wName.includes(searchTerm) || area.includes(searchTerm) || def.includes(searchTerm);
        }
        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">No se encontraron inspecciones con estos filtros</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(insp => {
        return `
            <tr>
                <td style="white-space: nowrap; font-weight: 600;">${insp.inspection_date}</td>
                <td><strong style="color: var(--primary);">${escapeHtml(insp.worker_name)}</strong></td>
                <td>${escapeHtml(insp.area)}</td>
                <td>
                    ${insp.is_compliant 
                        ? `<span class="badge-renewal-ok">🟢 Conforme</span>` 
                        : `<span class="badge-renewal-expired">🔴 No Conforme</span>`}
                </td>
                <td style="font-size: 0.825rem; color: ${insp.is_compliant ? 'var(--text-muted)' : '#991b1b'};">
                    ${escapeHtml(insp.deficiencies_found || 'Ninguna deficiencia')}
                </td>
                <td style="font-size: 0.825rem; color: var(--primary);">
                    ${escapeHtml(insp.corrective_actions || 'Mantener buenas prácticas')}
                </td>
                <td style="font-size: 0.825rem;">${escapeHtml(insp.inspector_name || 'Supervisor')}</td>
            </tr>
        `;
    }).join("");
}

// ==========================================================
// MODALES Y FORMULARIOS
// ==========================================================

function openDeliveryModal() {
    const modal = document.getElementById("deliveryModal");
    const form = document.getElementById("deliveryForm");
    const alertBox = document.getElementById("deliveryModalAlert");

    if (form) form.reset();
    if (alertBox) alertBox.style.display = "none";

    const deliveryDateInput = document.getElementById("deliveryDateInput");
    if (deliveryDateInput) deliveryDateInput.value = new Date().toISOString().split("T")[0];

    calculateRenewalDateInForm();

    if (modal) modal.classList.add("active");
}

window.openDeliveryModalWithData = function(workerId, eppId) {
    openDeliveryModal();
    const workerSelect = document.getElementById("deliveryWorkerSelect");
    const eppSelect = document.getElementById("deliveryEppSelect");
    const reasonSelect = document.getElementById("deliveryReasonSelect");

    if (workerSelect) workerSelect.value = workerId;
    if (eppSelect) eppSelect.value = eppId;
    if (reasonSelect) reasonSelect.value = "DOTACION_PERIODICA";

    calculateRenewalDateInForm();
};

function closeDeliveryModal() {
    const modal = document.getElementById("deliveryModal");
    if (modal) modal.classList.remove("active");
}

function calculateRenewalDateInForm() {
    const eppSelect = document.getElementById("deliveryEppSelect");
    const dateInput = document.getElementById("deliveryDateInput");
    const lifespanText = document.getElementById("calcLifespanText");
    const renewalText = document.getElementById("calcNextRenewalDateText");

    const eppId = parseInt(eppSelect?.value, 10);
    const epp = catalogList.find(item => item.id === eppId);
    const dateVal = dateInput?.value;

    if (!epp || !dateVal) {
        if (lifespanText) lifespanText.textContent = "-";
        if (renewalText) renewalText.textContent = "Selecciona EPP y fecha";
        return;
    }

    const lifespan = parseInt(epp.lifespan_days, 10) || 90;
    if (lifespanText) lifespanText.textContent = `${lifespan} días`;

    const d = new Date(dateVal + "T00:00:00");
    d.setDate(d.getDate() + lifespan);

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    const resultDate = `${year}-${month}-${day}`;

    if (renewalText) renewalText.textContent = resultDate;
}

async function handleDeliverySubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("deliveryModalAlert");
    const btnSave = document.getElementById("btnSaveDelivery");

    const payload = {
        worker_id: parseInt(document.getElementById("deliveryWorkerSelect").value, 10),
        epp_id: parseInt(document.getElementById("deliveryEppSelect").value, 10),
        delivery_date: document.getElementById("deliveryDateInput").value,
        quantity: parseInt(document.getElementById("deliveryQuantityInput").value, 10) || 1,
        reason: document.getElementById("deliveryReasonSelect").value,
        notes: document.getElementById("deliveryNotesInput").value.trim()
    };

    if (!payload.worker_id || !payload.epp_id || !payload.delivery_date) {
        showModalAlert(alertBox, "Complete todos los campos obligatorios.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = "Guardando...";

    const res = await apiFetch("/epp/deliveries", { method: "POST", body: JSON.stringify(payload) });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar Asignación";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "Error al asignar dotación");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeDeliveryModal();
    showGlobalAlert("Dotación asignada exitosamente con fecha de reposición calculada.", "success");
    await loadSummary();
    await loadCatalog();
    await loadDeliveries();
    await loadRenewals();
}

function openCatalogModal() {
    const modal = document.getElementById("catalogModal");
    const form = document.getElementById("catalogForm");
    const alertBox = document.getElementById("catalogModalAlert");

    if (form) form.reset();
    if (alertBox) alertBox.style.display = "none";
    if (modal) modal.classList.add("active");
}

function closeCatalogModal() {
    const modal = document.getElementById("catalogModal");
    if (modal) modal.classList.remove("active");
}

async function handleCatalogSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("catalogModalAlert");
    const btnSave = document.getElementById("btnSaveCatalog");

    const payload = {
        name: document.getElementById("catalogNameInput").value.trim(),
        category: document.getElementById("catalogCategorySelect").value,
        standard_code: document.getElementById("catalogStandardInput").value.trim(),
        lifespan_days: parseInt(document.getElementById("catalogLifespanInput").value, 10),
        stock_quantity: parseInt(document.getElementById("catalogStockInput").value, 10) || 0,
        description: document.getElementById("catalogDescriptionInput").value.trim()
    };

    if (!payload.name || !payload.category || !payload.lifespan_days) {
        showModalAlert(alertBox, "Complete los campos obligatorios.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = "Guardando...";

    const res = await apiFetch("/epp/catalog", { method: "POST", body: JSON.stringify(payload) });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar en Catálogo";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "Error al crear elemento");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeCatalogModal();
    showGlobalAlert("Elemento agregado exitosamente al catálogo de EPP.", "success");
    await loadCatalog();
    await loadSummary();
}

function openInspectionModal() {
    const modal = document.getElementById("inspectionModal");
    const form = document.getElementById("inspectionForm");
    const alertBox = document.getElementById("inspectionModalAlert");

    if (form) form.reset();
    if (alertBox) alertBox.style.display = "none";

    const dateInput = document.getElementById("inspectionDateInput");
    if (dateInput) dateInput.value = new Date().toISOString().split("T")[0];

    const radioTrue = document.getElementById("radioCompliantTrue");
    if (radioTrue) radioTrue.checked = true;
    toggleNonCompliantFields();

    if (modal) modal.classList.add("active");
}

function closeInspectionModal() {
    const modal = document.getElementById("inspectionModal");
    if (modal) modal.classList.remove("active");
}

function toggleNonCompliantFields() {
    const radioFalse = document.getElementById("radioCompliantFalse");
    const fieldsBox = document.getElementById("nonCompliantFields");
    if (fieldsBox) {
        fieldsBox.style.display = (radioFalse && radioFalse.checked) ? "block" : "none";
    }
}

async function handleInspectionSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("inspectionModalAlert");
    const btnSave = document.getElementById("btnSaveInspection");

    const isCompliant = document.getElementById("radioCompliantTrue").checked;
    const deficiencies = document.getElementById("inspectionDeficiencies").value.trim();

    if (!isCompliant && !deficiencies) {
        showModalAlert(alertBox, "Si la inspección no es conforme, debe especificar las deficiencias encontradas.", "danger");
        return;
    }

    const payload = {
        worker_id: parseInt(document.getElementById("inspectionWorkerSelect").value, 10),
        inspection_date: document.getElementById("inspectionDateInput").value,
        area: document.getElementById("inspectionAreaInput").value.trim(),
        is_compliant: isCompliant,
        deficiencies_found: deficiencies,
        corrective_actions: document.getElementById("inspectionActions").value.trim()
    };

    if (!payload.worker_id || !payload.inspection_date || !payload.area) {
        showModalAlert(alertBox, "Complete todos los campos requeridos.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = "Guardando...";

    const res = await apiFetch("/epp/inspections", { method: "POST", body: JSON.stringify(payload) });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar Inspección";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "Error al registrar inspección");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeInspectionModal();
    showGlobalAlert("Ronda de inspección de EPP guardada correctamente.", "success");
    await loadInspections();
    await loadSummary();
}

function exportDeliveriesToCSV() {
    if (!deliveriesList || deliveriesList.length === 0) {
        alert("No hay entregas disponibles para exportar.");
        return;
    }

    const headers = ["ID", "Fecha Entrega", "Colaborador", "Área", "EPP", "Categoría", "Cantidad", "Motivo", "Próxima Renovación", "Vencida", "Entregado Por", "Notas"];
    const rows = deliveriesList.map(d => [
        d.id,
        `"${d.delivery_date}"`,
        `"${(d.worker_name || '').replace(/"/g, '""')}"`,
        `"${(d.worker_area || '').replace(/"/g, '""')}"`,
        `"${(d.epp_name || '').replace(/"/g, '""')}"`,
        `"${d.epp_category}"`,
        d.quantity,
        `"${d.reason}"`,
        `"${d.next_renewal_date}"`,
        d.is_expired ? "SÍ" : "NO",
        `"${(d.delivered_by_name || '').replace(/"/g, '""')}"`,
        `"${(d.notes || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(e => e.join(","))].join("\r\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `ecosafe_dotaciones_epp_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
