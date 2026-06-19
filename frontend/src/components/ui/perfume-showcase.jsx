import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ChevronRight, Sparkles, Droplet, Wind, Clock, Star } from "lucide-react";
import { formatPrice } from "../../utils/formatPrice";
import { getProductImageBase } from "../../utils/productImages";

const EXTENSIONS = [".png", ".webp", ".jpg", ".svg"];

const PERFUME_DATA = {
  left: {
    id: "left",
    label: "Clásico",
    title: "Bleu de Chanel",
    brand: "Chanel",
    description:
      "Una fragancia amaderada y cítrica que encarna la libertad y la elegancia masculina. Notas de pomelo, jengibre y cedro se funden en un acorde vibrante y sofisticado.",
    price: 105990,
    fragrance: "Amaderado Cítrico",
    image: getProductImageBase({ brand: "Chanel", name: "Bleu de Chanel" }),
    colors: {
      gradient: "from-blue-600 to-indigo-900",
      glow: "bg-blue-500",
      ring: "border-l-blue-500/50",
    },
    stats: { intensity: "Alta", longevity: "8-10 horas" },
    notes: [
      { label: "Salida", value: 92, icon: Sparkles, note: "Pomelo, Limón, Menta" },
      { label: "Corazón", value: 85, icon: Droplet, note: "Jengibre, Nuez moscada, Jazmín" },
      { label: "Fondo", value: 78, icon: Wind, note: "Cedro, Sándalo, Ámbar, Pachulí" },
    ],
  },
  right: {
    id: "right",
    label: "Dupe Árabe",
    title: "Club de Nuit Iconic",
    brand: "Armaf",
    description:
      "La alternativa árabe que compite directamente con los grandes lanzamientos. Una fragancia amaderada y cítrica con la misma esencia que el clásico, pero a una fracción del precio. Calidad premium sin pagar el nombre.",
    price: 25990,
    fragrance: "Amaderado Cítrico",
    image: "/images/club-de-nuit-iconic",
    colors: {
      gradient: "from-emerald-800 to-amber-900",
      glow: "bg-emerald-500",
      ring: "border-r-emerald-500/50",
    },
    stats: { intensity: "Alta", longevity: "8-10 horas" },
    notes: [
      { label: "Salida", value: 94, icon: Sparkles, note: "Pomelo, Bergamota, Limón" },
      { label: "Corazón", value: 86, icon: Droplet, note: "Jengibre, Menta, Jazmín" },
      { label: "Fondo", value: 80, icon: Wind, note: "Cedro, Sándalo, Almizcle, Ámbar" },
    ],
  },
};

const ANIMATIONS = {
  container: {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } },
    exit: { opacity: 0, transition: { duration: 0.2 } },
  },
  item: {
    hidden: { opacity: 0, y: 20, filter: "blur(10px)" },
    visible: { opacity: 1, y: 0, filter: "blur(0px)", transition: { type: "spring", stiffness: 100, damping: 20 } },
    exit: { opacity: 0, y: -10, filter: "blur(5px)" },
  },
  image: (isLeft) => ({
    initial: { opacity: 0, scale: 1.5, filter: "blur(15px)", rotate: isLeft ? -15 : 15, x: isLeft ? -80 : 80 },
    animate: { opacity: 1, scale: 1, filter: "blur(0px)", rotate: 0, x: 0, transition: { type: "spring", stiffness: 260, damping: 20 } },
    exit: { opacity: 0, scale: 0.6, filter: "blur(20px)", transition: { duration: 0.25 } },
  }),
};

function BackgroundGradient({ isLeft }) {
  return (
    <div className="fixed inset-0 pointer-events-none">
      <motion.div
        animate={{
          background: isLeft
            ? "radial-gradient(circle at 30% 50%, rgba(59, 130, 246, 0.08), transparent 50%), radial-gradient(circle at 70% 50%, rgba(139, 92, 246, 0.05), transparent 50%)"
            : "radial-gradient(circle at 70% 50%, rgba(217, 119, 6, 0.08), transparent 50%), radial-gradient(circle at 30% 50%, rgba(190, 24, 93, 0.05), transparent 50%)",
        }}
        transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
        className="absolute inset-0"
      />
    </div>
  );
}

function ProductImage({ data, isLeft }) {
  const base = data.image;
  const [src, setSrc] = useState(null);
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    setSrc(base + EXTENSIONS[0]);
    setIdx(0);
  }, [data.id]);

  useEffect(() => {
    if (idx < EXTENSIONS.length) setSrc(base + EXTENSIONS[idx]);
    else setSrc(null);
  }, [idx]);

  return (
    <motion.div layout="position" className="relative group shrink-0">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className={`absolute inset-[-15%] rounded-full border border-dashed border-white/5 ${data.colors.ring}`}
      />
      <motion.div
        animate={{ scale: [1, 1.04, 1] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
        className={`absolute inset-[-5%] rounded-full bg-gradient-to-br ${data.colors.gradient} blur-3xl opacity-20`}
      />

      <div className="relative h-72 w-72 md:h-[400px] md:w-[400px] rounded-full shadow-2xl flex items-center justify-center overflow-hidden">
        <div className="absolute inset-2 rounded-full bg-white" />
        <motion.div
          animate={{ y: [-4, 4, -4] }}
          transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
          className="relative z-10 w-full h-full flex items-center justify-center p-8"
        >
          <AnimatePresence mode="wait">
            <motion.img
              key={data.id}
              src={src}
              alt={data.title}
              variants={ANIMATIONS.image(isLeft)}
              initial="initial"
              animate="animate"
              exit="exit"
              className="w-full h-full object-contain drop-shadow-[0_20px_50px_rgba(0,0,0,0.3)]"
              draggable={false}
              onError={() => setIdx((p) => p + 1)}
            />
          </AnimatePresence>
        </motion.div>
      </div>

      <motion.div layout="position" className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
        <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-charcoal-400 dark:text-zinc-500 bg-white/80 dark:bg-zinc-950/80 px-4 py-2 rounded-full border border-ivory-200 dark:border-white/5 backdrop-blur">
          <span className={`h-1.5 w-1.5 rounded-full ${data.colors.glow} animate-pulse`} />
          {data.fragrance}
        </div>
      </motion.div>
    </motion.div>
  );
}

function NoteBar({ note, index, isLeft }) {
  const barColor = isLeft ? "bg-blue-500" : "bg-amber-500";
  const IconComponent = note.icon;
  return (
    <div className="group">
      <div className="flex items-center justify-between mb-2 text-sm">
        <div className="flex items-center gap-2 text-charcoal-600 dark:text-zinc-300">
          {IconComponent && <IconComponent size={14} />} <span className="font-medium">{note.label}</span>
        </div>
        <div className="text-right">
          <span className="font-mono text-xs text-charcoal-400 dark:text-zinc-500">{note.value}%</span>
        </div>
      </div>
      <div className="relative h-1.5 w-full bg-ivory-100 dark:bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${note.value}%` }}
          transition={{ duration: 1, delay: 0.3 + index * 0.15, ease: [0.16, 1, 0.3, 1] }}
          className={`absolute top-0 bottom-0 left-0 ${barColor} opacity-80 rounded-full`}
        />
      </div>
      <p className="text-[11px] text-charcoal-400 dark:text-zinc-500 mt-1 italic">{note.note}</p>
    </div>
  );
}

function ProductDetails({ data, isLeft }) {
  const alignClass = isLeft ? "items-start text-left" : "items-end text-right";
  const flexDirClass = isLeft ? "flex-row" : "flex-row-reverse";
  const navigate = useNavigate();

  return (
    <motion.div
      variants={ANIMATIONS.container}
      initial="hidden"
      animate="visible"
      exit="exit"
      className={`flex flex-col ${alignClass}`}
    >
      <motion.p variants={ANIMATIONS.item} className="text-[10px] font-bold uppercase tracking-[0.25em] text-gold-500 dark:text-gold-400 mb-2">
        {data.label}
      </motion.p>
      <motion.h1
        variants={ANIMATIONS.item}
        className="text-3xl md:text-5xl font-display font-bold tracking-tight mb-1 text-charcoal-800 dark:text-white"
      >
        {data.title}
      </motion.h1>
      <motion.p
        variants={ANIMATIONS.item}
        className="text-gold-600 dark:text-gold-400 text-sm tracking-[0.15em] uppercase font-medium mb-4"
      >
        {data.brand}
      </motion.p>
      <motion.p
        variants={ANIMATIONS.item}
        className={`text-charcoal-500 dark:text-zinc-400 mb-6 max-w-sm leading-relaxed text-sm ${isLeft ? "mr-auto" : "ml-auto"}`}
      >
        {data.description}
      </motion.p>

      <motion.div variants={ANIMATIONS.item} className={`flex items-center gap-6 mb-6 ${flexDirClass}`}>
        <span className="font-display text-2xl font-bold text-charcoal-800 dark:text-white">{formatPrice(data.price)}</span>
        <div className="flex items-center gap-3 text-xs text-charcoal-400 dark:text-zinc-500">
          <span className="flex items-center gap-1"><Clock size={12} />{data.stats.longevity}</span>
          <span className="flex items-center gap-1"><Star size={12} />{data.stats.intensity}</span>
        </div>
      </motion.div>

      <motion.div variants={ANIMATIONS.item} className="w-full space-y-5 bg-ivory-50/80 dark:bg-zinc-900/40 p-6 rounded-2xl border border-ivory-200 dark:border-white/5 backdrop-blur-sm">
        <p className="text-[10px] uppercase tracking-[0.2em] text-charcoal-400 dark:text-zinc-500 font-medium">Pirámide Olfativa</p>
        {data.notes.map((note, idx) => (
          <NoteBar key={note.label} note={note} index={idx} isLeft={isLeft} />
        ))}

        <div className={`pt-3 flex ${isLeft ? "justify-start" : "justify-end"}`}>
          <button
            type="button"
            onClick={() => navigate("/catalog")}
            className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-charcoal-500 dark:text-zinc-300 hover:text-charcoal-800 dark:hover:text-white transition-colors group"
          >
            Ver Colección Completa
            <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

function Switcher({ activeId, onToggle }) {
  const options = [
    { id: "left", label: PERFUME_DATA.left.label },
    { id: "right", label: PERFUME_DATA.right.label },
  ];

  return (
    <div className="fixed bottom-10 inset-x-0 flex justify-center z-50 pointer-events-none">
      <motion.div
        layout
        className="pointer-events-auto flex items-center gap-1 p-1 rounded-full bg-white/90 dark:bg-zinc-900/80 backdrop-blur-2xl border border-ivory-200 dark:border-white/10 shadow-lg"
      >
        {options.map((opt) => (
          <motion.button
            key={opt.id}
            onClick={() => onToggle(opt.id)}
            whileTap={{ scale: 0.96 }}
            className="relative w-28 h-10 rounded-full flex items-center justify-center text-sm font-medium focus:outline-none"
          >
            {activeId === opt.id && (
              <motion.div
                layoutId="island-surface"
                className={`absolute inset-0 rounded-full ${activeId === "left" ? "bg-blue-500/10 dark:bg-blue-500/20" : "bg-amber-500/10 dark:bg-amber-500/20"}`}
                transition={{ type: "spring", stiffness: 220, damping: 22 }}
              />
            )}
            <span className={`relative z-10 text-xs font-semibold tracking-wider uppercase transition-colors duration-300 ${
              activeId === opt.id
                ? activeId === "left" ? "text-blue-600 dark:text-blue-400" : "text-amber-600 dark:text-amber-400"
                : "text-charcoal-400 dark:text-zinc-500"
            }`}>
              {opt.label}
            </span>
          </motion.button>
        ))}
      </motion.div>
    </div>
  );
}

export default function PerfumeShowcase() {
  const [activeSide, setActiveSide] = useState("left");
  const currentData = PERFUME_DATA[activeSide];
  const isLeft = activeSide === "left";

  return (
    <div className="relative w-full bg-cream-50 dark:bg-black text-charcoal-800 dark:text-zinc-100 overflow-hidden selection:bg-gold-200/40 dark:selection:bg-zinc-800 flex flex-col items-center justify-center min-h-[calc(100vh-64px)]">
      <BackgroundGradient isLeft={isLeft} />

      <main className="relative z-10 w-full px-6 py-8 flex flex-col justify-center flex-1 max-w-7xl mx-auto">
        <motion.div
          layout
          transition={{ type: "spring", bounce: 0, duration: 0.9 }}
          className={`flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 lg:gap-24 w-full ${
            isLeft ? "md:flex-row" : "md:flex-row-reverse"
          }`}
        >
          <ProductImage data={currentData} isLeft={isLeft} />

          <motion.div layout="position" className="w-full max-w-md">
            <AnimatePresence mode="wait">
              <ProductDetails key={activeSide} data={currentData} isLeft={isLeft} />
            </AnimatePresence>
          </motion.div>
        </motion.div>
      </main>

      <Switcher activeId={activeSide} onToggle={setActiveSide} />
    </div>
  );
}
