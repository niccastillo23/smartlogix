import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useCartDrawer } from "../context/CartDrawerContext";
import { useTheme } from "../context/ThemeContext";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { LiquidButton } from "./ui/liquid-glass-button";

function Header() {
  const { user, logout } = useAuth();
  const { count } = useCart();
  const { openDrawer } = useCartDrawer();
  const { dark, toggle } = useTheme();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const links = [
    { href: "/", label: "Inicio" },
    { href: "/catalog", label: "Colección" },
    { href: "/orders", label: "Pedidos" },
  ];

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "bg-white/90 backdrop-blur-lg shadow-sm dark:bg-charcoal-900/90 dark:shadow-black/20"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          <Link to="/" className="flex items-center gap-2 group">
            <span className="font-display text-xl md:text-2xl font-bold text-charcoal-800 tracking-[0.15em] dark:text-cream-50">
              PERFUMER
            </span>
            <span className="font-display text-xl md:text-2xl font-light text-gold-500 italic">IA</span>
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            {links.map((link) => (
              <Link
                key={link.href}
                to={link.href}
                className={`relative text-sm tracking-[0.12em] uppercase font-medium transition-colors duration-300 ${
                  location.pathname === link.href
                    ? "text-charcoal-800 dark:text-cream-50"
                    : "text-charcoal-400 hover:text-charcoal-700 dark:text-charcoal-400 dark:hover:text-cream-300"
                }`}
              >
                {link.label}
                {location.pathname === link.href && (
                  <motion.span layoutId="nav-underline" className="absolute -bottom-1 left-0 right-0 h-[1.5px] bg-charcoal-800 dark:bg-gold-400" />
                )}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            {/* Dark mode toggle */}
            <motion.button
              onClick={toggle}
              whileTap={{ scale: 0.9 }}
              className="relative p-2 text-charcoal-500 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-gold-400 transition-colors duration-300"
              aria-label={dark ? "Modo claro" : "Modo oscuro"}
            >
              <AnimatePresence mode="wait">
                {dark ? (
                  <motion.svg key="sun" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.3 }}
                    width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                    <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                  </motion.svg>
                ) : (
                  <motion.svg key="moon" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.3 }}
                    width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                  </motion.svg>
                )}
              </AnimatePresence>
            </motion.button>

            {/* Cart */}
            <button onClick={openDrawer} className="relative p-2 text-charcoal-500 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-cream-50 transition-colors duration-300">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
              </svg>
              <AnimatePresence>
                {count > 0 && (
                  <motion.span
                    key={count}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-charcoal-800 dark:bg-gold-500 text-white dark:text-charcoal-900 text-[9px] font-bold flex items-center justify-center rounded-full"
                  >
                    {count}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>

            <div className="hidden md:flex items-center gap-3 pl-4 border-l border-ivory-200 dark:border-charcoal-700">
              <span className="text-xs text-charcoal-400 dark:text-charcoal-400 font-medium">{user?.username}</span>
              <LiquidButton onClick={logout} variant="default" size="sm" className="!px-3 !py-1 text-xs">
                Salir
              </LiquidButton>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}

export default Header;
