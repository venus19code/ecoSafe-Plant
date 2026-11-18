/**
 * Módulo de Dashboard General, Indicadores y Reportes (Spec 006)
 * Orquesta la carga de KPIs en tiempo real, gráficos analíticos con Chart.js,
 * filtros temporales/área y exportación ejecutiva a CSV e impresión/PDF.
 */

let wasteChartInstance = null;
let utilitiesChartInstance = null;
let riskChartInstance = null;
let incidentsChartInstance = null;

let currentKpisData = null;

document.addEventListener("DOMContentLoaded", () => {
    // 1. Proteger ruta mediante autenticación JWT
    const currentUser = requireAuthPage();
    if (!currentUser) return;

    // 2. Control de sidebar móvil
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }

    // 3. Inicializar fechas por defecto (Mes actual)
    initDateFilters();

    // 4. Configurar escuchadores de eventos
    setupEventListeners();

    // 5. Cargar datos del dashboard
    loadAllDashboardData();
});

/**
 * Inicializa los campos de fecha con el primer y último día del mes corriente.
 */
function initDateFilters() {
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);

    const filterStartDate = document.getElementById("filterStartDate");
    const filterEndDate = document.getElementById("filterEndDate");

    if (filterStartDate && filterEndDate) {
        filterStartDate.value = formatDateToISO(firstDay);
        filterEndDate.value = formatDateToISO(lastDay);
    }
}

function formatDateToISO(d) {
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${d.getFullYear()}-${month}-${day}`;
}

/**
 * Configuración de eventos para controles del dashboard
 */
function setupEventListeners() {
    // Selector rápido de período
    const periodSelect = document.getElementById("periodSelect");
    const filterStartDate = document.getElementById("filterStartDate");
    const filterEndDate = document.getElementById("filterEndDate");
    const filterArea = document.getElementById("filterArea");

    if (periodSelect) {
        periodSelect.addEventListener("change", (e) => {
            const val = e.target.value;
            const now = new Date();

            if (val === "current_month") {
                const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
                const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                filterStartDate.value = formatDateToISO(firstDay);
                filterEndDate.value = formatDateToISO(lastDay);
            } else if (val === "last_3_months") {
                const threeMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 2, 1);
                const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                filterStartDate.value = formatDateToISO(threeMonthsAgo);
                filterEndDate.value = formatDateToISO(lastDay);
            } else if (val === "current_year") {
                const firstDay = new Date(now.getFullYear(), 0, 1);
                const lastDay = new Date(now.getFullYear(), 11, 31);
                filterStartDate.value = formatDateToISO(firstDay);
                filterEndDate.value = formatDateToISO(lastDay);
            }

            loadAllDashboardData();
        });
    }

    if (filterStartDate) filterStartDate.addEventListener("change", loadAllDashboardData);
    if (filterEndDate) filterEndDate.addEventListener("change", loadAllDashboardData);
    if (filterArea) filterArea.addEventListener("change", loadAllDashboardData);

    // Botón refrescar
    const btnRefresh = document.getElementById("btnRefresh");
    if (btnRefresh) {
        btnRefresh.addEventListener("click", () => {
            loadAllDashboardData();
        });
    }

    // Botón imprimir / PDF
    const btnPrint = document.getElementById("btnPrint");
    if (btnPrint) {
        btnPrint.addEventListener("click", () => {
            window.print();
        });
    }

    // Botón exportar CSV
    const btnExportCSV = document.getElementById("btnExportCSV");
    if (btnExportCSV) {
        btnExportCSV.addEventListener("click", exportSummaryCSV);
    }
}

/**
 * Carga concurrente de todos los componentes del Dashboard
 */
async function loadAllDashboardData() {
    const startDate = document.getElementById("filterStartDate")?.value || "";
    const endDate = document.getElementById("filterEndDate")?.value || "";
    const area = document.getElementById("filterArea")?.value || "";

    const queryParams = new URLSearchParams();
    if (startDate) queryParams.append("start_date", startDate);
    if (endDate) queryParams.append("end_date", endDate);
    if (area) queryParams.append("area", area);

    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : "";

    // Actualizar indicador de última sincronización
    const syncTimeEl = document.getElementById("syncTime");
    if (syncTimeEl) syncTimeEl.textContent = "Sincronizando...";

    try {
        await Promise.all([
            fetchKPIs(queryString),
            fetchWasteChartData(queryString),
            fetchUtilitiesChartData(),
            fetchSafetyStatsData()
        ]);

        if (syncTimeEl) {
            const now = new Date();
            syncTimeEl.textContent = `Actualizado: ${now.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`;
        }
    } catch (err) {
        console.error("Error al cargar datos del dashboard:", err);
        if (syncTimeEl) syncTimeEl.textContent = "Error al sincronizar";
    }
}

/**
 * Carga y renderizado de tarjetas de KPIs principales
 */
async function fetchKPIs(queryString) {
    try {
        const res = await apiFetch(`/dashboard/kpis${queryString}`);
        if (!res.success) return;

        const data = res.data;
        currentKpisData = data;

        // Residuos
        document.getElementById("kpiTotalWaste").textContent = `${Number(data.waste.total_waste_kg).toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kg`;
        document.getElementById("kpiHazardousWaste").textContent = `Peligrosos: ${Number(data.waste.hazardous_waste_kg).toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kg`;
        
        const valorizationEl = document.getElementById("kpiValorization");
        valorizationEl.textContent = `${data.waste.valorization_rate}%`;
        const valSubEl = document.getElementById("kpiValorizationSub");
        valSubEl.textContent = `${Number(data.waste.valorized_waste_kg).toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kg aprovechados`;

        // Servicios Públicos
        const waterConsumption = Number(data.utilities.water_consumption_m3);
        const waterTarget = Number(data.utilities.water_target_m3);
        document.getElementById("kpiWaterConsumption").textContent = `${waterConsumption.toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} m³`;
        document.getElementById("kpiWaterTarget").textContent = `Meta: ${waterTarget > 0 ? waterTarget.toLocaleString("es-CO") + " m³" : "Sin meta"}`;
        
        const energyConsumption = Number(data.utilities.energy_consumption_kwh);
        const energyTarget = Number(data.utilities.energy_target_kwh);
        document.getElementById("kpiEnergyConsumption").textContent = `${energyConsumption.toLocaleString("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kWh`;
        document.getElementById("kpiEnergyTarget").textContent = `Meta: ${energyTarget > 0 ? energyTarget.toLocaleString("es-CO") + " kWh" : "Sin meta"}`;

        // Seguridad SST
        document.getElementById("kpiDaysWithoutAccidents").textContent = `${data.safety.days_without_accidents} días`;
        document.getElementById("kpiOpenIncidents").textContent = `${data.safety.open_incidents_count} casos`;
        document.getElementById("kpiCriticalHazards").textContent = `${data.safety.critical_hazards_count} identificados`;

        // Control EPP
        document.getElementById("kpiEppCompliance").textContent = `${data.epp.compliance_rate}%`;
        document.getElementById("kpiEppExpired").textContent = `${data.epp.expired_deliveries} vencidas / ${data.epp.total_deliveries} dotaciones`;

    } catch (err) {
        console.error("Error al obtener KPIs:", err);
    }
}

/**
 * Carga datos y dibuja el gráfico de Residuos por Categoría
 */
async function fetchWasteChartData(queryString) {
    try {
        const res = await apiFetch(`/dashboard/waste-chart${queryString}`);
        if (!res.success) return;

        const data = res.data;
        const labels = data.map(d => d.category_name);
        const totals = data.map(d => d.total_kg);
        const colors = data.map(d => d.color_code || "#10b981");

        renderWasteChart(labels, totals, colors);
    } catch (err) {
        console.error("Error al cargar gráfico de residuos:", err);
    }
}

function renderWasteChart(labels, values, bgColors) {
    const ctx = document.getElementById("wasteChart");
    if (!ctx) return;

    if (wasteChartInstance) {
        wasteChartInstance.destroy();
    }

    if (labels.length === 0) {
        labels = ["Sin registros en período"];
        values = [0];
        bgColors = ["#cbd5e1"];
    }

    wasteChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Kilogramos (kg)",
                data: values,
                backgroundColor: bgColors,
                borderRadius: 6,
                borderWidth: 1,
                borderColor: "rgba(0,0,0,0.1)"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.parsed.y.toLocaleString("es-CO")} kg`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => `${value.toLocaleString("es-CO")} kg`
                    }
                }
            }
        }
    });
}

/**
 * Carga datos y dibuja el gráfico de balance de Recursos vs Metas
 */
async function fetchUtilitiesChartData() {
    try {
        const res = await apiFetch("/dashboard/utilities-chart?months=6");
        if (!res.success) return;

        const rawData = res.data;
        
        // Obtener meses únicos ordenados
        const months = [...new Set(rawData.map(d => d.month))].sort();

        // Extraer series para Agua
        const waterActual = months.map(m => {
            const item = rawData.find(d => d.month === m && d.service_type === "AGUA");
            return item ? item.actual_consumption : 0;
        });
        const waterTarget = months.map(m => {
            const item = rawData.find(d => d.month === m && d.service_type === "AGUA");
            return item ? item.target_consumption : 0;
        });

        // Extraer series para Energía
        const energyActual = months.map(m => {
            const item = rawData.find(d => d.month === m && d.service_type === "ENERGIA");
            return item ? item.actual_consumption : 0;
        });

        renderUtilitiesChart(months, waterActual, waterTarget, energyActual);
    } catch (err) {
        console.error("Error al cargar gráfico de recursos:", err);
    }
}

function renderUtilitiesChart(months, waterActual, waterTarget, energyActual) {
    const ctx = document.getElementById("utilitiesChart");
    if (!ctx) return;

    if (utilitiesChartInstance) {
        utilitiesChartInstance.destroy();
    }

    utilitiesChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: months,
            datasets: [
                {
                    label: "Agua Consumo (m³)",
                    data: waterActual,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    yAxisID: "yWater"
                },
                {
                    label: "Agua Meta (m³)",
                    data: waterTarget,
                    borderColor: "#93c5fd",
                    borderDash: [5, 5],
                    borderWidth: 2,
                    fill: false,
                    yAxisID: "yWater"
                },
                {
                    label: "Energía Consumo (kWh)",
                    data: energyActual,
                    borderColor: "#f59e0b",
                    backgroundColor: "rgba(245, 158, 11, 0.1)",
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    yAxisID: "yEnergy"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                legend: { position: "top" }
            },
            scales: {
                yWater: {
                    type: "linear",
                    display: true,
                    position: "left",
                    title: { display: true, text: "Agua (m³)" },
                    beginAtZero: true
                },
                yEnergy: {
                    type: "linear",
                    display: true,
                    position: "right",
                    title: { display: true, text: "Energía (kWh)" },
                    grid: { drawOnChartArea: false },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Carga datos de SST y genera gráficos de dona para Riesgos e Incidentes
 */
async function fetchSafetyStatsData() {
    try {
        const res = await apiFetch("/dashboard/safety-stats");
        if (!res.success) return;

        const data = res.data;

        // 1. Gráfico de Riesgos IPVR
        renderRiskChart(data.risk_distribution);

        // 2. Gráfico de Incidentes
        renderIncidentsChart(data.incident_status_distribution);

    } catch (err) {
        console.error("Error al cargar estadísticas de seguridad:", err);
    }
}

function renderRiskChart(riskList) {
    const ctx = document.getElementById("riskDistributionChart");
    if (!ctx) return;

    if (riskChartInstance) {
        riskChartInstance.destroy();
    }

    const labels = ["BAJO", "MEDIO", "ALTO", "CRITICO"];
    const colorMap = {
        "BAJO": "#10b981",
        "MEDIO": "#f59e0b",
        "ALTO": "#f97316",
        "CRITICO": "#ef4444"
    };

    const counts = labels.map(lbl => {
        const item = riskList.find(r => r.risk_level === lbl);
        return item ? item.count : 0;
    });

    riskChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Bajo", "Medio", "Alto", "Crítico"],
            datasets: [{
                data: counts,
                backgroundColor: labels.map(lbl => colorMap[lbl]),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

function renderIncidentsChart(incidentList) {
    const ctx = document.getElementById("incidentsStatusChart");
    if (!ctx) return;

    if (incidentsChartInstance) {
        incidentsChartInstance.destroy();
    }

    const labels = ["REPORTADO", "INVESTIGACION", "ACCION_CORRECTIVA", "RESUELTO"];
    const displayLabels = ["Reportados", "En Investigación", "Acción Correctiva", "Resueltos"];
    const colors = ["#ef4444", "#f59e0b", "#3b82f6", "#10b981"];

    const counts = labels.map(lbl => {
        const item = incidentList.find(i => i.status === lbl);
        return item ? item.count : 0;
    });

    incidentsChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: displayLabels,
            datasets: [{
                data: counts,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

/**
 * Exportación consolidada de métricas clave a CSV
 */
function exportSummaryCSV() {
    if (!currentKpisData) {
        alert("Los datos aún no se han cargado por completo.");
        return;
    }

    const d = currentKpisData;
    const period = document.getElementById("periodSelect")?.value || "personalizado";
    const startDate = document.getElementById("filterStartDate")?.value || "";
    const endDate = document.getElementById("filterEndDate")?.value || "";

    const rows = [
        ["REPORTE EJECUTIVO INTEGRAL - ECOSAFE PLANT"],
        [`Fecha de Emisión: ${new Date().toLocaleString("es-CO")}`],
        [`Período de Análisis: ${startDate} al ${endDate} (${period})`],
        [],
        ["INDICADOR / KPI", "VALOR", "UNIDAD", "ESTADO / META"],
        ["Total Residuos Generados", d.waste.total_waste_kg, "kg", "-"],
        ["Residuos Peligrosos", d.waste.hazardous_waste_kg, "kg", "-"],
        ["Residuos Aprovechados / Valorizados", d.waste.valorized_waste_kg, "kg", "-"],
        ["Tasa de Valorización de Residuos", `${d.waste.valorization_rate}%`, "%", "Meta Planta: >60%"],
        ["Consumo de Agua", d.utilities.water_consumption_m3, "m³", `Meta: ${d.utilities.water_target_m3} m³`],
        ["Consumo de Energía Eléctrica", d.utilities.energy_consumption_kwh, "kWh", `Meta: ${d.utilities.energy_target_kwh} kWh`],
        ["Días Consecutivos sin Accidentes", d.safety.days_without_accidents, "días", "Cero Accidentes"],
        ["Incidentes SST Abiertos / En Proceso", d.safety.open_incidents_count, "casos", "-"],
        ["Peligros Críticos en Matriz IPVR", d.safety.critical_hazards_count, "peligros", "Atención Inmediata"],
        ["Tasa de Cumplimiento de EPP", `${d.epp.compliance_rate}%`, "%", "Meta: 100%"],
        ["Dotaciones EPP Activas", d.epp.active_deliveries, "dotaciones", "-"],
        ["Dotaciones EPP Vencidas", d.epp.expired_deliveries, "dotaciones", "Reposición Pendiente"],
        ["Total Dotaciones Asignadas", d.epp.total_deliveries, "dotaciones", "-"]
    ];

    const csvContent = "\uFEFF" + rows.map(e => e.join(";")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `EcoSafe_Reporte_Ejecutivo_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
