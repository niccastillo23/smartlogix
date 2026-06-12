/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        cream: { 50: "#fdfcfa", 100: "#faf7f0", 200: "#f0ead9", 300: "#e0d4b8", 400: "#d4bf9a", 500: "#c9a97a", 600: "#b8925e", 700: "#9a784c", 800: "#806340", 900: "#6a5238" },
        ivory: { 50: "#fefdfb", 100: "#fcf9f2", 200: "#f5eee0", 300: "#ebe0c8", 400: "#d9cbaa", 500: "#c9b890", 600: "#b09d7a", 700: "#928064", 800: "#796954", 900: "#645647" },
        charcoal: { 50: "#f5f5f5", 100: "#e6e6e6", 200: "#cccccc", 300: "#a3a3a3", 400: "#7a7a7a", 500: "#525252", 600: "#3d3d3d", 700: "#2a2a2a", 800: "#1a1a1a", 900: "#0d0d0d" },
        gold: { 50: "#fdf8ed", 100: "#f9efd1", 200: "#f2dda0", 300: "#e8c56a", 400: "#d4a54a", 500: "#c9943a", 600: "#b07d2e", 700: "#936128", 800: "#7a4f26", 900: "#664224" },
        rose: { 50: "#fdf2f4", 100: "#fce7ea", 200: "#f9d0d8", 300: "#f4a9b8", 400: "#ec7a94", 500: "#e05074", 600: "#cc2f5a", 700: "#ab2047", 800: "#8f1c3c", 900: "#7a1b36" },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
        display: ['"Playfair Display"', "Georgia", "serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.7s ease-out forwards",
        "fade-in-up": "fadeInUp 0.7s ease-out forwards",
        "slide-in-right": "slideInRight 0.4s ease-out forwards",
        "scale-in": "scaleIn 0.4s ease-out forwards",
        shimmer: "shimmer 2s infinite linear",
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        fadeInUp: { from: { opacity: 0, transform: "translateY(30px)" }, to: { opacity: 1, transform: "translateY(0)" } },
        slideInRight: { from: { opacity: 0, transform: "translateX(40px)" }, to: { opacity: 1, transform: "translateX(0)" } },
        scaleIn: { from: { opacity: 0, transform: "scale(0.95)" }, to: { opacity: 1, transform: "scale(1)" } },
        shimmer: { "0%": { backgroundPosition: "-200% center" }, "100%": { backgroundPosition: "200% center" } },
      },
    },
  },
  plugins: [],
};
