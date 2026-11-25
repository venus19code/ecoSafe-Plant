/**
 * ==========================================================
 * ECOSAFE PLANT - CLIENTE DE API HTTP (FETCH WRAPPER)
 * ==========================================================
 */

// Base de rutas del frontend: funciona abriendo los HTML directamente (file://) o servidos por Flask
const APP_ROOT = window.location.pathname.replace(/\\/g, "/").includes("/pages/") ? "../" : "./";

const API_CONFIG = {
    // URL del backend:
    // - En producción (Flask sirviendo este frontend) usa /api del mismo origen.
    // - Al abrir los HTML directamente o con Live Server, apunta al backend local.
    // - Se puede sobrescribir definiendo window.ECOSAFE_API_URL antes de cargar este script.
    BASE_URL: (() => {
        if (window.ECOSAFE_API_URL) {
            return String(window.ECOSAFE_API_URL).replace(/\/$/, "");
        }
        const { protocol, hostname, port } = window.location;
        const isLocal = hostname === "localhost" || hostname === "127.0.0.1";
        if (!window.ECOSAFE_API_URL && /\.netlify\.app$/.test(hostname)) {
            console.error("[EcoSafe] Falta configurar window.ECOSAFE_API_URL en js/config.js con la URL del backend desplegado.");
        }
        if (protocol === "file:") return "http://localhost:5000/api";
        if (isLocal && port && port !== "5000") return "http://localhost:5000/api";
        return "/api";
    })()
};

// Almacenamiento local seguro
const AuthStorage = {
    getToken() {
        return localStorage.getItem("ecosafe_token");
    },
    setToken(token) {
        localStorage.setItem("ecosafe_token", token);
    },
    removeToken() {
        localStorage.removeItem("ecosafe_token");
        localStorage.removeItem("ecosafe_user");
    },
    getUser() {
        const data = localStorage.getItem("ecosafe_user");
        try {
            return data ? JSON.parse(data) : null;
        } catch {
            return null;
        }
    },
    setUser(user) {
        localStorage.setItem("ecosafe_user", JSON.stringify(user));
    },
    isAuthenticated() {
        return !!this.getToken();
    }
};

/**
 * Petición genérica con fetch y manejo centralizado de JWT
 */
async function apiFetch(endpoint, options = {}) {
    const url = endpoint.startsWith("http") ? endpoint : `${API_CONFIG.BASE_URL}${endpoint}`;
    
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    const token = AuthStorage.getToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // Manejo de expiración o token inválido
        if (response.status === 401 && !endpoint.includes("/auth/login")) {
            console.warn("Sesión expirada o token no autorizado. Redirigiendo a login...");
            AuthStorage.removeToken();
            if (!window.location.pathname.endsWith("index.html") && window.location.pathname !== "/") {
                window.location.href = APP_ROOT + "index.html";
            }
            return { error: "Sesión expirada", status: 401 };
        }

        const data = await response.json().catch(() => ({}));
        
        return {
            ok: response.ok,
            status: response.status,
            data
        };
    } catch (err) {
        console.error(`[Error de red al consultar ${url}]:`, err);
        return {
            ok: false,
            status: 0,
            error: "No se pudo conectar con el servidor (API). Verifica tu conexión o que el backend esté en línea."
        };
    }
}
