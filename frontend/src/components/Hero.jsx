import { motion } from "framer-motion";

function Hero() {
  return (
    <motion.section
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      className="relative -mx-4 sm:-mx-6 lg:-mx-8 mb-16 overflow-hidden"
    >
      <div className="relative h-[50vh] md:h-[60vh] bg-gradient-to-br from-charcoal-900 via-charcoal-800 to-charcoal-900 flex items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(201,169,122,0.08)_0%,_transparent_70%)]" />
        <div className="relative z-10 text-center px-6 max-w-2xl">
          <motion.p
            initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.7 }}
            className="text-gold-400/80 text-xs tracking-[0.3em] uppercase mb-4"
          >
            Colección 2024
          </motion.p>
          <motion.h2
            initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.35, duration: 0.7 }}
            className="font-display text-3xl md:text-5xl lg:text-6xl font-light text-white tracking-wide leading-tight"
          >
            La Elegancia de<br />
            <span className="font-semibold text-gold-400">Cada Nota</span>
          </motion.h2>
          <motion.div
            initial={{ scaleX: 0 }} animate={{ scaleX: 1 }}
            transition={{ delay: 0.6, duration: 0.8, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="mt-6 w-16 h-[1px] bg-gold-500/50 mx-auto origin-center"
          />
          <motion.p
            initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.7 }}
            className="mt-6 text-charcoal-300 text-sm md:text-base font-light max-w-md mx-auto leading-relaxed"
          >
            Descubre una selección curada de las fragancias más emblemáticas del mundo.
          </motion.p>
        </div>
      </div>
    </motion.section>
  );
}

export default Hero;
