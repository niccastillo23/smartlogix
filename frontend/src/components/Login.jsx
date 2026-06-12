import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { motion, AnimatePresence } from "framer-motion";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      if (isRegister) {
        await register(username, password);
        setSuccess("Registro exitoso. Ahora inicia sesión.");
        setIsRegister(false);
      } else {
        await login(username, password);
        navigate("/");
      }
    } catch (err) {
      setError(err.response?.data?.message || "Ocurrió un error. Intenta de nuevo.");
    }
  };

  return (
    <div className="min-h-screen bg-cream-50 dark:bg-charcoal-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="w-full max-w-sm"
      >
        <div className="text-center mb-10">
          <h1 className="font-display text-4xl font-bold text-charcoal-800 dark:text-cream-50 tracking-[0.15em]">
            PERFUMER<span className="font-light text-gold-500 italic">IA</span>
          </h1>
          <p className="mt-2 text-charcoal-400 text-sm tracking-[0.2em] uppercase">Perfumes de Lujo</p>
          <div className="mt-4 w-12 h-[1px] bg-ivory-300 dark:bg-charcoal-600 mx-auto" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="username" className="block text-xs text-charcoal-500 tracking-[0.15em] uppercase mb-1.5">Usuario</label>
            <input
              id="username" type="text" value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ingresa tu usuario" required
              className="input-field"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-xs text-charcoal-500 tracking-[0.15em] uppercase mb-1.5">Contraseña</label>
            <input
              id="password" type="password" value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ingresa tu contraseña" required
              className="input-field"
            />
          </div>

          <AnimatePresence>
            {error && (
              <motion.p initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="text-rose-500 text-xs text-center bg-rose-50 dark:bg-rose-900/30 py-2 px-3">
                {error}
              </motion.p>
            )}
            {success && (
              <motion.p initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="text-emerald-600 text-xs text-center bg-emerald-50 dark:bg-emerald-900/30 py-2 px-3">
                {success}
              </motion.p>
            )}
          </AnimatePresence>

          <button type="submit" className="btn-primary w-full">
            {isRegister ? "Registrarse" : "Iniciar Sesión"}
          </button>
        </form>

            <p className="mt-6 text-center text-xs text-charcoal-400 dark:text-charcoal-400">
          {isRegister ? "¿Ya tienes una cuenta?" : "¿No tienes cuenta?"}{" "}
          <button type="button" onClick={() => { setIsRegister(!isRegister); setError(""); setSuccess(""); }}
            className="text-charcoal-700 underline underline-offset-4 hover:text-charcoal-900 transition-colors">
            {isRegister ? "Iniciar Sesión" : "Registrarse"}
          </button>
        </p>
      </motion.div>
    </div>
  );
}

export default Login;
