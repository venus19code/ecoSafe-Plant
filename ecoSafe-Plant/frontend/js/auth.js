/**
 * ==========================================================
 * ECOSAFE PLANT - CONTROLADOR DE AUTENTICACIÓN (FRONTEND)
 * ==========================================================
 */

document.addEventListener("DOMContentLoaded", () => {
    // Si ya tiene sesión activa y está en la pantalla de login, redirigir a dashboard
    if (window.location.pathname.endsWith("index.html") || window.location.pathname === "/") {
        if (AuthStorage.isAuthenticated()) {
            window.location.href = "/pages/dashboard.html";
            return;
        }
        initLoginForm();
    }
});

function initLoginForm() {
    const loginForm = document.getElementById("loginForm");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const btnSubmit = document.getElementById("btnSubmit");
    const alertBox = document.getElementById("loginAlert");
    const togglePwdBtn = document.getElementById("togglePassword");

    if (!loginForm) return;

    // Conmutar visibilidad de contraseña
    if (togglePwdBtn && passwordInput) {
        togglePwdBtn.addEventListener("click", () => {
            const isPassword = passwordInput.getAttribute("type") === "password";
            passwordInput.setAttribute("type", isPassword ? "text" : "password");
            togglePwdBtn.textContent = isPassword ? "Ocultar" : "Mostrar";
        });
    }

    // Manejo de envío del formulario
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        showAlert("", false);

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            showAlert("Por favor ingresa tu correo y contraseña.");
            return;
        }

        btnSubmit.disabled = true;
        btnSubmit.innerHTML = `<span>Ingresando...</span>`;

        const res = await apiFetch("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password })
        });

        btnSubmit.disabled = false;
        btnSubmit.innerHTML = `<span>Iniciar Sesión</span>`;

        if (res.ok && res.data.token) {
            // Guardar token y perfil
            AuthStorage.setToken(res.data.token);
            AuthStorage.setUser(res.data.user);

            showAlert("Inicio exitoso. Redirigiendo...", true, "alert-success");
            setTimeout(() => {
                window.location.href = "/pages/dashboard.html";
            }, 500);
        } else {
            const errorMsg = (res.data && res.data.error) || res.error || "No se pudo iniciar sesión. Credenciales incorrectas.";
            showAlert(errorMsg);
        }
    });

    function showAlert(message, visible = true, alertType = "alert-danger") {
        if (!alertBox) return;
        alertBox.className = `alert ${alertType}`;
        alertBox.textContent = message;
        alertBox.style.display = visible ? "block" : "none";
    }
}

/**
 * Función para autocompletar credenciales de demostración
 */
function fillDemo(email, password) {
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    if (emailInput && passwordInput) {
        emailInput.value = email;
        passwordInput.value = password;
        // Efecto visual de resaltado
        emailInput.focus();
    }
}

/**
 * Cierre de sesión seguro
 */
function handleLogout() {
    AuthStorage.removeToken();
    window.location.href = "/index.html";
}

/**
 * Guardia de ruta protegida para páginas dentro de /pages/
 */
function requireAuthPage() {
    if (!AuthStorage.isAuthenticated()) {
        window.location.href = "/index.html";
        return null;
    }
    const user = AuthStorage.getUser();
    renderUserProfile(user);
    return user;
}

/**
 * Muestra el perfil y rol del usuario en la barra superior
 */
function renderUserProfile(user) {
    if (!user) return;
    const nameEl = document.getElementById("userName");
    const roleEl = document.getElementById("userRole");
    const areaEl = document.getElementById("userArea");

    if (nameEl) nameEl.textContent = user.name;
    if (roleEl) roleEl.textContent = user.role;
    if (areaEl) areaEl.textContent = user.area;
}
