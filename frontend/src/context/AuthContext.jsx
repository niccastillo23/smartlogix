import { createContext, useContext, useState, useCallback, useEffect } from "react";
import { login as apiLogin, register as apiRegister } from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setUser({ username: payload.sub });
      } catch { setToken(null); }
    }
    setLoading(false);
  }, [token]);

  const login = useCallback(async (username, password) => {
    const res = await apiLogin(username, password);
    const t = res.data.token;
    localStorage.setItem("token", t);
    setToken(t);
    const payload = JSON.parse(atob(t.split(".")[1]));
    setUser({ username: payload.sub });
  }, []);

  const register = useCallback(async (username, password) => {
    await apiRegister(username, password);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
