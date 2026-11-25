/**
 * ==========================================================
 * ECOSAFE PLANT - CONFIGURACIÓN DEL FRONTEND
 * ==========================================================
 * Aquí se define la URL del backend (API de Flask).
 *
 * - Desarrollo local con el backend Flask (http://localhost:5000):
 *      window.ECOSAFE_API_URL = "http://localhost:5000/api";
 *
 * - Backend desplegado en Render / Railway / cualquier servidor:
 *      window.ECOSAFE_API_URL = "https://tu-backend.onrender.com/api";
 *
 * - Si se deja vacío (""), se usa el mismo origen (/api), que es lo correcto
 *   cuando Flask sirve también el frontend.
 *
 * IMPORTANTE: no agregues una barra "/" al final de la URL.
 */
window.ECOSAFE_API_URL = "";
