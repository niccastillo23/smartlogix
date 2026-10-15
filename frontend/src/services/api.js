import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Los errores de autenticación (login) no deben forzar una redirección: el formulario debe mostrar el mensaje.
    // axios recibe la ruta relativa a baseURL ("/api"), p. ej. "/auth/login".
    const esAutenticacion = /(^|\/)auth\//.test(error.config?.url || "");
    if (!esAutenticacion && error.response && (error.response.status === 401 || error.response.status === 403)) {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export default api;
