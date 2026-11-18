/**
 * ==========================================================
 * ECOSAFE PLANT - CONTROLADOR DE RECURSOS (SPEC 003)
 * Agua y Energía Eléctrica
 * ==========================================================
 */

let currentResource = "AGUA"; // 'AGUA' | 'ENERGIA'
let metersList = [];
let currentReadings = [];
let summaryData = null;
let currentUser = null;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Verificar autenticación
    currentUser = requireAuthPage();
    if (!currentUser) return;

    // Configurar toggle del sidebar en móviles
    initSidebarToggle();

    // 2. Establecer fecha por defecto (hoy)
    const today = new Date().toISOString().split("T")[0];
    const readingDateInput = document.getElementById("readingDate");
    if (readingDateInput) readingDateInput.value = today;

    // 3. Sincronizar selectores de mes y año
    const now = new Date();
    const selectMonth = document.getElementById("selectMonth");
    const selectYear = document.getElementById("selectYear");
    if (selectMonth) selectMonth.value = (now.getMonth() + 1).toString();
    if (selectYear) selectYear.value = now.getFullYear().toString();

    // 4. Inicializar eventos
    initEventListeners();

    // 5. Cargar medidores y datos iniciales
    await loadMeters();
    await loadSummaryAndReadings();
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
    // Conmutador de Pestañas (Agua / Energía)
    const tabWaterBtn = document.getElementById("tabWaterBtn");
    const tabEnergyBtn = document.getElementById("tabEnergyBtn");

    if (tabWaterBtn && tabEnergyBtn) {
        tabWaterBtn.addEventListener("click", () => switchResourceTab("AGUA"));
        tabEnergyBtn.addEventListener("click", () => switchResourceTab("ENERGIA"));
    }

    // Filtros de tabla y periodo
    const selectMonth = document.getElementById("selectMonth");
    const selectYear = document.getElementById("selectYear");
    const selectMeter = document.getElementById("selectMeter");
    const searchInput = document.getElementById("searchInput");

    if (selectMonth) selectMonth.addEventListener("change", loadSummaryAndReadings);
    if (selectYear) selectYear.addEventListener("change", loadSummaryAndReadings);
    if (selectMeter) selectMeter.addEventListener("change", filterAndRenderTable);
    if (searchInput) searchInput.addEventListener("input", filterAndRenderTable);

    // Modal de Lecturas
    const btnOpenReading = document.getElementById("btnOpenReadingModal");
    const btnCloseReading = document.getElementById("btnCloseReadingModal");
    const btnCancelReading = document.getElementById("btnCancelReadingModal");
    const readingModal = document.getElementById("readingModal");
    const readingForm = document.getElementById("readingForm");
    const meterSelect = document.getElementById("meterSelect");
    const readingValueInput = document.getElementById("readingValue");

    if (btnOpenReading) btnOpenReading.addEventListener("click", openReadingModal);
    if (btnCloseReading) btnCloseReading.addEventListener("click", closeReadingModal);
    if (btnCancelReading) btnCancelReading.addEventListener("click", closeReadingModal);

    if (readingModal) {
        readingModal.addEventListener("click", (e) => {
            if (e.target === readingModal) closeReadingModal();
        });
    }

    // Al cambiar medidor en el modal o escribir lectura: calcular en tiempo real
    if (meterSelect) meterSelect.addEventListener("change", handleMeterSelectionChange);
    if (readingValueInput) readingValueInput.addEventListener("input", calculateLiveConsumption);

    if (readingForm) readingForm.addEventListener("submit", handleReadingSubmit);

    // Modal de Metas Ambientales
    const btnOpenTarget = document.getElementById("btnOpenTargetModal");
    const btnCloseTarget = document.getElementById("btnCloseTargetModal");
    const btnCancelTarget = document.getElementById("btnCancelTargetModal");
    const targetModal = document.getElementById("targetModal");
    const targetForm = document.getElementById("targetForm");

    if (btnOpenTarget) btnOpenTarget.addEventListener("click", openTargetModal);
    if (btnCloseTarget) btnCloseTarget.addEventListener("click", closeTargetModal);
    if (btnCancelTarget) btnCancelTarget.addEventListener("click", closeTargetModal);

    if (targetModal) {
        targetModal.addEventListener("click", (e) => {
            if (e.target === targetModal) closeTargetModal();
        });
    }

    if (targetForm) targetForm.addEventListener("submit", handleTargetSubmit);

    // Exportar CSV
    const btnExportCsv = document.getElementById("btnExportCsv");
    if (btnExportCsv) btnExportCsv.addEventListener("click", exportReadingsToCSV);
}

/**
 * Conmuta la pestaña activa entre Agua y Energía
 */
function switchResourceTab(resource) {
    currentResource = resource;

    const tabWater = document.getElementById("tabWaterBtn");
    const tabEnergy = document.getElementById("tabEnergyBtn");

    if (resource === "AGUA") {
        tabWater.classList.add("active");
        tabEnergy.classList.remove("active");
    } else {
        tabEnergy.classList.add("active");
        tabWater.classList.remove("active");
    }

    // Actualizar selectores dependientes del recurso
    populateMetersSelects();
    loadSummaryAndReadings();
}

/**
 * Carga el catálogo de medidores desde el backend
 */
async function loadMeters() {
    const res = await apiFetch("/utilities/meters");
    if (res.ok && res.data) {
        metersList = res.data.meters || [];
        populateMetersSelects();
    }
}

/**
 * Llena los selects de medidores según el recurso activo
 */
function populateMetersSelects() {
    const filterSelect = document.getElementById("selectMeter");
    const modalSelect = document.getElementById("meterSelect");

    const filteredMeters = metersList.filter(m => m.resource_type === currentResource);

    if (filterSelect) {
        filterSelect.innerHTML = '<option value="">Todos los Medidores</option>';
        filteredMeters.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m.id;
            opt.textContent = `${m.code} - ${m.name}`;
            filterSelect.appendChild(opt);
        });
    }

    if (modalSelect) {
        modalSelect.innerHTML = '<option value="">-- Seleccione un medidor --</option>';
        filteredMeters.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m.id;
            opt.textContent = `${m.code} - ${m.name} (${m.unit})`;
            modalSelect.appendChild(opt);
        });
    }
}

/**
 * Carga tanto las métricas de resumen como las lecturas del periodo
 */
async function loadSummaryAndReadings() {
    const month = document.getElementById("selectMonth")?.value || (new Date().getMonth() + 1);
    const year = document.getElementById("selectYear")?.value || new Date().getFullYear();

    await loadSummaryKPIs(month, year);
    await loadTableReadings(month, year);
}

/**
 * Consulta las métricas de consumo y actualiza las tarjetas KPI
 */
async function loadSummaryKPIs(month, year) {
    const res = await apiFetch(`/utilities/summary?month=${month}&year=${year}`);
    if (!res.ok || !res.data) return;

    summaryData = res.data;
    const resourceData = currentResource === "AGUA" ? summaryData.water : summaryData.energy;
    const isWater = currentResource === "AGUA";

    // KPI 1: Consumo Total
    const labelEl = document.getElementById("kpiLabelConsumption");
    const iconEl = document.getElementById("kpiIconResource");
    const totalEl = document.getElementById("kpiTotalConsumption");
    const unitEl = document.getElementById("kpiUnitDisplay");
    const diffEl = document.getElementById("kpiDiffPercent");

    if (labelEl) labelEl.textContent = isWater ? "Consumo de Agua" : "Consumo de Energía";
    if (iconEl) iconEl.textContent = isWater ? "💧" : "⚡";
    if (unitEl) unitEl.textContent = resourceData.unit;
    if (totalEl) totalEl.textContent = Number(resourceData.total_consumption).toLocaleString("es-CO", { minimumFractionDigits: 1 });

    if (diffEl) {
        const diff = Number(resourceData.diff_percent || 0);
        const prefix = diff > 0 ? "+" : "";
        diffEl.textContent = `${prefix}${diff}%`;
        diffEl.style.color = diff > 0 ? "var(--warning)" : "var(--success)";
    }

    // KPI 2: Meta Ambiental y Barra de Progreso
    const targetPercentEl = document.getElementById("kpiTargetPercent");
    const targetDetailsEl = document.getElementById("kpiTargetDetails");
    const progressBar = document.getElementById("kpiProgressBar");
    const targetStatusText = document.getElementById("kpiTargetStatusText");
    const cardTarget = document.getElementById("kpiCardTarget");

    const pct = resourceData.target_percent || 0;
    const isExceeded = resourceData.is_exceeded;
    const targetQty = resourceData.target_consumption;

    if (targetPercentEl) targetPercentEl.textContent = `${pct}%`;
    if (targetDetailsEl) {
        targetDetailsEl.textContent = `${Number(resourceData.total_consumption).toLocaleString("es-CO")} / ${Number(targetQty).toLocaleString("es-CO")} ${resourceData.unit}`;
    }

    if (progressBar) {
        progressBar.style.width = `${Math.min(pct, 100)}%`;
        progressBar.className = "progress-bar";
        if (pct < 85) {
            progressBar.classList.add("progress-success");
        } else if (pct <= 100) {
            progressBar.classList.add("progress-warning");
        } else {
            progressBar.classList.add("progress-danger");
        }
    }

    if (targetStatusText && cardTarget) {
        if (isExceeded) {
            cardTarget.className = "kpi-card kpi-danger";
            targetStatusText.innerHTML = `<strong style="color: var(--danger);">⚠️ ¡Meta ambiental superada! (+${(pct - 100).toFixed(1)}%)</strong>`;
        } else if (pct >= 85) {
            cardTarget.className = "kpi-card kpi-warning";
            targetStatusText.innerHTML = `<span style="color: var(--warning);">⚡ Próximo al límite del presupuesto mensual</span>`;
        } else {
            cardTarget.className = "kpi-card kpi-success";
            targetStatusText.innerHTML = `<span style="color: var(--success);">🌱 Consumo dentro del límite sostenible</span>`;
        }
    }

    // KPI 3: Costo Facturado Estimado
    const costEl = document.getElementById("kpiTotalCost");
    const combinedEl = document.getElementById("kpiCombinedCost");
    if (costEl) costEl.textContent = `$${Number(resourceData.total_cost).toLocaleString("es-CO")}`;
    if (combinedEl) combinedEl.textContent = `$${Number(summaryData.total_combined_cost).toLocaleString("es-CO")}`;

    // KPI 4: Conteo de lecturas
    const countEl = document.getElementById("kpiReadingsCount");
    if (countEl) countEl.textContent = resourceData.readings_count || 0;
}

/**
 * Carga el historial de lecturas de la tabla
 */
async function loadTableReadings(month, year) {
    const tbody = document.getElementById("readingsTableBody");
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-muted);">Cargando lecturas...</td></tr>`;
    }

    const res = await apiFetch(`/utilities/readings?resource_type=${currentResource}&month=${month}&year=${year}`);
    if (!res.ok) {
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--danger);">Error al cargar lecturas: ${res.error || 'Verifica la conexión con el servidor'}</td></tr>`;
        }
        return;
    }

    currentReadings = (res.data && res.data.readings) ? res.data.readings : [];
    filterAndRenderTable();
}

/**
 * Filtra las lecturas en memoria y renderiza la tabla HTML
 */
function filterAndRenderTable() {
    const tbody = document.getElementById("readingsTableBody");
    if (!tbody) return;

    const searchTerm = (document.getElementById("searchInput")?.value || "").toLowerCase().trim();
    const meterFilter = document.getElementById("selectMeter")?.value || "";

    const filtered = currentReadings.filter(r => {
        if (meterFilter && r.meter_id != meterFilter) return false;

        if (searchTerm) {
            const mName = (r.meter_name || "").toLowerCase();
            const mCode = (r.meter_code || "").toLowerCase();
            const area = (r.location_area || "").toLowerCase();
            const notes = (r.notes || "").toLowerCase();
            return mName.includes(searchTerm) || mCode.includes(searchTerm) || area.includes(searchTerm) || notes.includes(searchTerm);
        }

        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔌</div>
                    <strong>No se encontraron registros de lecturas para este periodo</strong>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">Haz clic en "Registrar Lectura" para ingresar un nuevo corte de medidor.</div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filtered.map(r => {
        const isWater = r.resource_type === "AGUA";
        const badgeClass = isWater ? "badge-water" : "badge-energy";
        const icon = isWater ? "💧" : "⚡";

        return `
            <tr>
                <td style="font-weight: 600; white-space: nowrap;">${r.reading_date}</td>
                <td>
                    <strong style="color: var(--primary);">${escapeHtml(r.meter_code)}</strong>
                </td>
                <td>
                    <span class="${badgeClass}">
                        ${icon} ${escapeHtml(r.resource_type)}
                    </span>
                </td>
                <td>
                    <div>${escapeHtml(r.meter_name)}</div>
                    <small style="color: var(--text-muted);">${escapeHtml(r.location_area)}</small>
                </td>
                <td style="font-weight: 600;">
                    ${Number(r.reading_value).toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 2 })}
                    <small style="color: var(--text-muted);">${r.unit}</small>
                </td>
                <td style="font-weight: 800; color: ${isWater ? '#1d4ed8' : '#b45309'};">
                    +${Number(r.consumption).toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 2 })}
                    <small style="font-weight: 500;">${r.unit}</small>
                </td>
                <td style="font-weight: 600; white-space: nowrap;">
                    ${r.cost_amount > 0 ? '$' + Number(r.cost_amount).toLocaleString("es-CO") : '<span style="color: var(--text-muted); font-size: 0.8rem;">Sin costo</span>'}
                </td>
                <td>
                    <div style="font-size: 0.825rem; font-weight: 600;">${escapeHtml(r.recorded_by_name || 'Operario')}</div>
                    ${r.notes ? `<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">💬 ${escapeHtml(r.notes)}</div>` : ''}
                </td>
            </tr>
        `;
    }).join("");
}

/**
 * Abre el modal para registrar lectura
 */
function openReadingModal() {
    const modal = document.getElementById("readingModal");
    const form = document.getElementById("readingForm");
    const alertBox = document.getElementById("modalAlert");
    const readingDate = document.getElementById("readingDate");

    if (form) form.reset();
    if (alertBox) alertBox.style.display = "none";

    if (readingDate) {
        readingDate.value = new Date().toISOString().split("T")[0];
    }

    populateMetersSelects();
    handleMeterSelectionChange();

    if (modal) modal.classList.add("active");
}

function closeReadingModal() {
    const modal = document.getElementById("readingModal");
    if (modal) modal.classList.remove("active");
}

/**
 * Cuando se selecciona un medidor en el modal, muestra la última lectura registrada
 */
function handleMeterSelectionChange() {
    const meterSelect = document.getElementById("meterSelect");
    const prevReadingText = document.getElementById("prevReadingText");
    const calcBox = document.getElementById("calcBox");

    const meterId = parseInt(meterSelect?.value, 10);
    const meter = metersList.find(m => m.id === meterId);

    if (meter && meter.latest_reading_value !== null && meter.latest_reading_value !== undefined) {
        prevReadingText.textContent = `${Number(meter.latest_reading_value).toLocaleString("es-CO")} ${meter.unit} (Fecha: ${meter.latest_reading_date || 'anterior'})`;
        prevReadingText.style.color = "var(--primary)";
    } else if (meter) {
        prevReadingText.textContent = "Ninguna lectura previa. Esta será la lectura inicial (Consumo = Lectura).";
        prevReadingText.style.color = "var(--accent)";
    } else {
        prevReadingText.textContent = "Seleccione un medidor para ver el valor acumulado";
        prevReadingText.style.color = "var(--text-muted)";
    }

    calculateLiveConsumption();
}

/**
 * Calcula en tiempo real el consumo al escribir en el campo de lectura actual
 */
function calculateLiveConsumption() {
    const meterSelect = document.getElementById("meterSelect");
    const readingValueInput = document.getElementById("readingValue");
    const calcDisplay = document.getElementById("calcConsumptionDisplay");
    const calcBox = document.getElementById("calcBox");

    const meterId = parseInt(meterSelect?.value, 10);
    const meter = metersList.find(m => m.id === meterId);
    const currVal = parseFloat(readingValueInput?.value);

    if (!meter || isNaN(currVal)) {
        if (calcDisplay) calcDisplay.textContent = "0.00 " + (meter ? meter.unit : "");
        if (calcBox) {
            calcBox.style.backgroundColor = "#f0fdf4";
            calcBox.style.borderColor = "#bbf7d0";
            calcBox.style.color = "#166534";
        }
        return;
    }

    const prevVal = meter.latest_reading_value;

    if (prevVal === null || prevVal === undefined) {
        // Primera lectura
        if (calcDisplay) calcDisplay.textContent = `${Number(currVal).toLocaleString("es-CO")} ${meter.unit} (Lectura inicial)`;
    } else if (currVal < prevVal) {
        // Error: retroceso
        if (calcDisplay) calcDisplay.textContent = `⚠️ Lectura menor a la anterior (${prevVal} ${meter.unit})`;
        if (calcBox) {
            calcBox.style.backgroundColor = "#fee2e2";
            calcBox.style.borderColor = "#fca5a5";
            calcBox.style.color = "#991b1b";
        }
    } else {
        // Consumo normal
        const consumption = (currVal - prevVal) * (meter.multiplier || 1.0);
        if (calcDisplay) calcDisplay.textContent = `+${Number(consumption).toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 2 })} ${meter.unit}`;
        if (calcBox) {
            calcBox.style.backgroundColor = "#f0fdf4";
            calcBox.style.borderColor = "#bbf7d0";
            calcBox.style.color = "#166534";
        }
    }
}

/**
 * Envío del formulario de lectura
 */
async function handleReadingSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("modalAlert");
    const btnSave = document.getElementById("btnSaveReading");

    const payload = {
        meter_id: parseInt(document.getElementById("meterSelect").value, 10),
        reading_date: document.getElementById("readingDate").value,
        reading_value: parseFloat(document.getElementById("readingValue").value),
        cost_amount: document.getElementById("costAmount").value ? parseFloat(document.getElementById("costAmount").value) : 0,
        notes: document.getElementById("notes").value.trim()
    };

    if (!payload.meter_id || !payload.reading_date || isNaN(payload.reading_value)) {
        showModalAlert(alertBox, "Por favor complete los campos requeridos.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = "Registrando...";

    const res = await apiFetch("/utilities/readings", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar Lectura";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "Error al registrar la lectura");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeReadingModal();
    showGlobalAlert("Lectura de medidor registrada exitosamente.", "success");

    // Recargar medidores (para actualizar su latest_reading) y datos
    await loadMeters();
    await loadSummaryAndReadings();
}

/**
 * Modal de Configuración de Metas
 */
function openTargetModal() {
    const modal = document.getElementById("targetModal");
    const alertBox = document.getElementById("targetModalAlert");
    const targetResource = document.getElementById("targetResourceSelect");
    const targetMonth = document.getElementById("targetMonthInput");
    const targetYear = document.getElementById("targetYearInput");
    const targetQtyInput = document.getElementById("targetConsumptionInput");

    if (alertBox) alertBox.style.display = "none";
    if (targetResource) targetResource.value = currentResource;
    if (targetMonth) targetMonth.value = document.getElementById("selectMonth")?.value || (new Date().getMonth() + 1);
    if (targetYear) targetYear.value = document.getElementById("selectYear")?.value || new Date().getFullYear();

    // Precargar meta actual si existe
    if (summaryData) {
        const currentTarget = currentResource === "AGUA" ? summaryData.water.target_consumption : summaryData.energy.target_consumption;
        if (targetQtyInput && currentTarget > 0) {
            targetQtyInput.value = currentTarget;
        }
    }

    if (modal) modal.classList.add("active");
}

function closeTargetModal() {
    const modal = document.getElementById("targetModal");
    if (modal) modal.classList.remove("active");
}

async function handleTargetSubmit(e) {
    e.preventDefault();

    const alertBox = document.getElementById("targetModalAlert");
    const btnSave = document.getElementById("btnSaveTarget");

    const payload = {
        resource_type: document.getElementById("targetResourceSelect").value,
        target_month: parseInt(document.getElementById("targetMonthInput").value, 10),
        target_year: parseInt(document.getElementById("targetYearInput").value, 10),
        target_consumption: parseFloat(document.getElementById("targetConsumptionInput").value)
    };

    if (isNaN(payload.target_consumption) || payload.target_consumption <= 0) {
        showModalAlert(alertBox, "La meta debe ser un número mayor a cero.", "danger");
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = "Guardando...";

    const res = await apiFetch("/utilities/targets", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    btnSave.disabled = false;
    btnSave.textContent = "Guardar Meta";

    if (!res.ok) {
        const errorMsg = (res.data && res.data.error) ? res.data.error : (res.error || "No se pudo guardar la meta");
        showModalAlert(alertBox, errorMsg, "danger");
        return;
    }

    closeTargetModal();
    showGlobalAlert("Meta ambiental guardada exitosamente.", "success");
    await loadSummaryAndReadings();
}

/**
 * Exportar tabla a CSV
 */
function exportReadingsToCSV() {
    if (!currentReadings || currentReadings.length === 0) {
        alert("No hay lecturas disponibles para exportar en este periodo.");
        return;
    }

    const headers = ["ID", "Fecha", "Recurso", "Código Medidor", "Nombre Medidor", "Área", "Lectura Registrada", "Consumo Neto", "Unidad", "Costo ($ COP)", "Registrado Por", "Notas"];
    const rows = currentReadings.map(r => [
        r.id,
        `"${r.reading_date}"`,
        `"${r.resource_type}"`,
        `"${r.meter_code}"`,
        `"${(r.meter_name || '').replace(/"/g, '""')}"`,
        `"${(r.location_area || '').replace(/"/g, '""')}"`,
        r.reading_value,
        r.consumption,
        `"${r.unit}"`,
        r.cost_amount,
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
    link.setAttribute("download", `ecosafe_recursos_${currentResource.toLowerCase()}_${year}_${month}.csv`);
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
