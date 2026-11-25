/**
 * ==========================================================
 * ECOSAFE PLANT - GESTIÓN DE USUARIOS Y ROLES (SPEC 007)
 * ==========================================================
 */

let currentUser = null;
let usersList = [];
let statsData = null;
let editingUserId = null;
let passwordTargetId = null;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Autenticación obligatoria
    currentUser = requireAuthPage();
    if (!currentUser) return;

    // 2. Control de acceso: solo ADMIN
    if (currentUser.role !== "ADMIN") {
        alert("La gestión de usuarios está reservada para administradores.");
        window.location.href = "dashboard.html";
        return;
    }

    // 3. Menú móvil
    initSidebarToggle();

    // 4. Eventos
    initEventListeners();

    // 5. Cargar datos
    await Promise.all([loadStats(), loadUsers()]);
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
    // Filtros (client-side)
    const searchInput = document.getElementById("searchUsersInput");
    const roleFilter = document.getElementById("selectRoleFilter");
    const statusFilter = document.getElementById("selectStatusFilter");
    if (searchInput) searchInput.addEventListener("input", applyFilters);
    if (roleFilter) roleFilter.addEventListener("change", applyFilters);
    if (statusFilter) statusFilter.addEventListener("change", applyFilters);

    // Botones principales
    const btnOpen = document.getElementById("btnOpenUserModal");
    const btnExport = document.getElementById("btnExportUsersCsv");
    if (btnOpen) btnOpen.addEventListener("click", () => openUserModal(null));
    if (btnExport) btnExport.addEventListener("click", exportUsersCsv);

    // Modal de usuario
    const btnCloseUser = document.getElementById("btnCloseUserModal");
    const btnCancelUser = document.getElementById("btnCancelUserModal");
    if (btnCloseUser) btnCloseUser.addEventListener("click", closeUserModal);
    if (btnCancelUser) btnCancelUser.addEventListener("click", closeUserModal);
    const userForm = document.getElementById("userForm");
    if (userForm) userForm.addEventListener("submit", submitUserForm);

    // Modal de contraseña
    const btnClosePwd = document.getElementById("btnClosePasswordModal");
    const btnCancelPwd = document.getElementById("btnCancelPasswordModal");
    if (btnClosePwd) btnClosePwd.addEventListener("click", closePasswordModal);
    if (btnCancelPwd) btnCancelPwd.addEventListener("click", closePasswordModal);
    const passwordForm = document.getElementById("passwordForm");
    if (passwordForm) passwordForm.addEventListener("submit", submitPasswordForm);

    // Delegación de acciones en la tabla
    const tbody = document.getElementById("usersTableBody");
    if (tbody) tbody.addEventListener("click", handleTableAction);
}

// ==========================================================
// CARGA DE DATOS
// ==========================================================

async function loadStats() {
    const res = await apiFetch("/users/stats");
    if (!res.ok || !res.data) return;
    statsData = res.data;
    renderStats();
}

function renderStats() {
    if (!statsData) return;
    setText("kpiTotalUsers", statsData.total ?? 0);
    setText("kpiActiveUsers", statsData.active ?? 0);
    setText("kpiInactiveUsers", statsData.inactive ?? 0);
    setText("kpiAdminUsers", (statsData.by_role && statsData.by_role.ADMIN) || 0);
}

async function loadUsers() {
    const res = await apiFetch("/users");
    const tbody = document.getElementById("usersTableBody");

    if (!res.ok || !res.data) {
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:var(--danger);">
                No se pudieron cargar los usuarios. ${escapeHtml((res.data && res.data.error) || res.error || "")}
            </td></tr>`;
        }
        return;
    }

    usersList = res.data.users || [];
    applyFilters();
}

// ==========================================================
// FILTRADO Y RENDERIZADO
// ==========================================================

function applyFilters() {
    const search = (document.getElementById("searchUsersInput")?.value || "").trim().toLowerCase();
    const role = document.getElementById("selectRoleFilter")?.value || "";
    const status = document.getElementById("selectStatusFilter")?.value || "";

    const filtered = usersList.filter((u) => {
        const matchesSearch = !search ||
            u.name.toLowerCase().includes(search) ||
            u.email.toLowerCase().includes(search) ||
            (u.area || "").toLowerCase().includes(search);
        const matchesRole = !role || u.role === role;
        const matchesStatus = status === "" || String(u.is_active) === status;
        return matchesSearch && matchesRole && matchesStatus;
    });

    renderUsers(filtered);
}

function renderUsers(users) {
    const tbody = document.getElementById("usersTableBody");
    if (!tbody) return;

    if (!users.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:var(--text-muted);">
            No se encontraron usuarios con los filtros seleccionados.
        </td></tr>`;
        return;
    }

    tbody.innerHTML = users.map((u) => {
        const isSelf = currentUser && currentUser.id === u.id;
        const toggleLabel = u.is_active ? "Desactivar" : "Activar";
        const toggleColor = u.is_active ? "var(--danger)" : "var(--success)";
        const created = u.created_at ? String(u.created_at).split(" ")[0] : "-";

        return `
            <tr>
                <td>
                    <strong>${escapeHtml(u.name)}</strong>
                    ${isSelf ? '<span class="badge-role badge-role-self">Tú</span>' : ""}
                </td>
                <td style="color: var(--text-muted);">${escapeHtml(u.email)}</td>
                <td>${renderRoleBadge(u.role)}</td>
                <td>${escapeHtml(u.area)}</td>
                <td>${renderStatusBadge(u.is_active)}</td>
                <td style="color: var(--text-muted); font-size: 0.82rem;">${escapeHtml(created)}</td>
                <td style="text-align: right; white-space: nowrap;">
                    <button class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"
                            data-action="edit" data-id="${u.id}">✏️ Editar</button>
                    <button class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; color: ${toggleColor};"
                            data-action="toggle" data-id="${u.id}" ${isSelf ? "disabled title='No puedes desactivar tu propia cuenta'" : ""}>
                            ${u.is_active ? "⛔" : "✅"} ${toggleLabel}
                    </button>
                    <button class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"
                            data-action="password" data-id="${u.id}">🔑 Contraseña</button>
                </td>
            </tr>
        `;
    }).join("");
}

function renderRoleBadge(role) {
    const map = {
        ADMIN: { label: "ADMIN", cls: "badge-role-admin" },
        SUPERVISOR: { label: "SUPERVISOR", cls: "badge-role-supervisor" },
        OPERARIO: { label: "OPERARIO", cls: "badge-role-operario" },
    };
    const info = map[role] || { label: role, cls: "badge-role-operario" };
    return `<span class="badge-role ${info.cls}">${info.label}</span>`;
}

function renderStatusBadge(isActive) {
    return isActive
        ? `<span class="badge-role status-activo">● Activo</span>`
        : `<span class="badge-role status-inactivo">● Inactivo</span>`;
}

function handleTableAction(event) {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;
    const action = btn.getAttribute("data-action");
    const id = parseInt(btn.getAttribute("data-id"), 10);
    const user = usersList.find((u) => u.id === id);
    if (!user) return;

    if (action === "edit") {
        openUserModal(user);
    } else if (action === "toggle") {
        toggleUserStatus(user);
    } else if (action === "password") {
        openPasswordModal(user);
    }
}

// ==========================================================
// MODAL CREAR / EDITAR
// ==========================================================

function openUserModal(user) {
    editingUserId = user ? user.id : null;

    setText("userModalTitle", user ? "✏️ Editar Usuario" : "👤 Nuevo Usuario");
    setValue("userNameInput", user ? user.name : "");
    setValue("userEmailInput", user ? user.email : "");
    setValue("userRoleSelect", user ? user.role : "OPERARIO");
    setValue("userAreaInput", user ? user.area : "");
    setValue("userPasswordInput", "");

    const passwordGroup = document.getElementById("passwordFieldGroup");
    const passwordInput = document.getElementById("userPasswordInput");
    if (passwordGroup && passwordInput) {
        const isCreate = !user;
        passwordGroup.style.display = isCreate ? "block" : "none";
        passwordInput.required = isCreate;
    }

    hideAlert("userModalAlert");
    showModal("userModal");
    document.getElementById("userNameInput")?.focus();
}

function closeUserModal() {
    hideModal("userModal");
    editingUserId = null;
}

async function submitUserForm(event) {
    event.preventDefault();
    hideAlert("userModalAlert");

    const isEdit = !!editingUserId;
    const payload = {
        name: getValue("userNameInput").trim(),
        email: getValue("userEmailInput").trim(),
        role: getValue("userRoleSelect"),
        area: getValue("userAreaInput").trim(),
    };

    if (!payload.name || !payload.email || !payload.area) {
        showAlert("userModalAlert", "Nombre, correo y área son obligatorios.");
        return;
    }

    const btn = document.getElementById("btnSaveUser");
    if (btn) { btn.disabled = true; btn.textContent = "Guardando..."; }

    let res;
    if (editingUserId) {
        res = await apiFetch(`/users/${editingUserId}`, {
            method: "PUT",
            body: JSON.stringify(payload),
        });
    } else {
        payload.password = getValue("userPasswordInput");
        if (payload.password.length < 8) {
            if (btn) { btn.disabled = false; btn.textContent = "Guardar Usuario"; }
            showAlert("userModalAlert", "La contraseña debe tener al menos 8 caracteres.");
            return;
        }
        res = await apiFetch("/users", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    }

    if (btn) { btn.disabled = false; btn.textContent = "Guardar Usuario"; }

    if (!res.ok) {
        showAlert("userModalAlert", (res.data && res.data.error) || res.error || "No se pudo guardar el usuario.");
        return;
    }

    closeUserModal();
    showGlobalAlert("success", isEdit ? "Usuario actualizado correctamente." : "Usuario creado correctamente.");
    await Promise.all([loadStats(), loadUsers()]);
}

// ==========================================================
// ACTIVAR / DESACTIVAR
// ==========================================================

async function toggleUserStatus(user) {
    const turningOff = user.is_active;
    const message = turningOff
        ? `¿Desactivar a ${user.name}? No podrá iniciar sesión, pero su historial se conserva.`
        : `¿Activar a ${user.name}? Recuperará el acceso al sistema.`;

    if (!confirm(message)) return;

    const res = await apiFetch(`/users/${user.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !user.is_active }),
    });

    if (!res.ok) {
        showGlobalAlert("danger", (res.data && res.data.error) || res.error || "No se pudo cambiar el estado.");
        return;
    }

    showGlobalAlert("success", res.data.message || "Estado actualizado.");
    await Promise.all([loadStats(), loadUsers()]);
}

// ==========================================================
// RESTABLECER CONTRASEÑA
// ==========================================================

function openPasswordModal(user) {
    passwordTargetId = user.id;
    setText("passwordTargetName", `${user.name} (${user.email})`);
    setValue("newPasswordInput", "");
    setValue("confirmPasswordInput", "");
    hideAlert("passwordModalAlert");
    showModal("passwordModal");
    document.getElementById("newPasswordInput")?.focus();
}

function closePasswordModal() {
    hideModal("passwordModal");
    passwordTargetId = null;
}

async function submitPasswordForm(event) {
    event.preventDefault();
    hideAlert("passwordModalAlert");

    const newPassword = getValue("newPasswordInput");
    const confirmPassword = getValue("confirmPasswordInput");

    if (newPassword.length < 8) {
        showAlert("passwordModalAlert", "La contraseña debe tener al menos 8 caracteres.");
        return;
    }
    if (newPassword !== confirmPassword) {
        showAlert("passwordModalAlert", "Las contraseñas no coinciden.");
        return;
    }

    const btn = document.getElementById("btnSavePassword");
    if (btn) { btn.disabled = true; btn.textContent = "Actualizando..."; }

    const res = await apiFetch(`/users/${passwordTargetId}/password`, {
        method: "PATCH",
        body: JSON.stringify({ new_password: newPassword }),
    });

    if (btn) { btn.disabled = false; btn.textContent = "Actualizar Contraseña"; }

    if (!res.ok) {
        showAlert("passwordModalAlert", (res.data && res.data.error) || res.error || "No se pudo actualizar la contraseña.");
        return;
    }

    closePasswordModal();
    showGlobalAlert("success", "Contraseña actualizada correctamente.");
}

// ==========================================================
// EXPORTACIÓN CSV
// ==========================================================

function exportUsersCsv() {
    if (!usersList.length) {
        showGlobalAlert("warning", "No hay usuarios para exportar.");
        return;
    }

    const rows = [
        ["USUARIOS - ECOSAFE PLANT"],
        [`Fecha de Emisión: ${new Date().toLocaleString("es-CO")}`],
        [],
        ["ID", "Nombre", "Correo", "Rol", "Área", "Estado", "Fecha Registro"],
        ...usersList.map((u) => [
            u.id,
            u.name,
            u.email,
            u.role,
            u.area,
            u.is_active ? "Activo" : "Inactivo",
            u.created_at ? String(u.created_at).split(" ")[0] : "",
        ]),
    ];

    const csvContent = "\uFEFF" + rows.map((r) => r.join(";")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `EcoSafe_Usuarios_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ==========================================================
// UTILIDADES DE UI
// ==========================================================

function showGlobalAlert(type, message) {
    const box = document.getElementById("globalAlert");
    if (!box) return;
    box.className = `alert alert-${type === "success" ? "success" : type === "warning" ? "warning" : "danger"}`;
    box.textContent = message;
    box.style.display = "block";
    if (type === "success") {
        setTimeout(() => { box.style.display = "none"; }, 4000);
    }
}

function showAlert(elementId, message) {
    const box = document.getElementById(elementId);
    if (!box) return;
    box.className = "alert alert-danger";
    box.textContent = message;
    box.style.display = "block";
}

function hideAlert(elementId) {
    const box = document.getElementById(elementId);
    if (!box) return;
    box.style.display = "none";
    box.textContent = "";
}

function showModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("active");
}

function hideModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("active");
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function setValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value;
}

function getValue(id) {
    const el = document.getElementById(id);
    return el ? el.value : "";
}

function escapeHtml(text) {
    return String(text ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
