/**
 * ==========================================================
 * ECOSAFE PLANT - CLIENTE DE API HTTP (FETCH WRAPPER)
 * ==========================================================
 */

const API_CONFIG = {
    // Si la app se sirve desde el mismo servidor de Python, usa ruta relativa /api
    // Si se abre desde Live Server u otro puerto, apunta a http://localhost:5000/api
    BASE_URL: (window.location.port === "5000") 
        ? "/api" 
        : "http://localhost:5000/api"
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
                window.location.href = "/index.html";
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
            error: "No se pudo conectar con el servidor backend en Python (http://localhost:5000). Verifica que esté encendido."
        };
    }
}
