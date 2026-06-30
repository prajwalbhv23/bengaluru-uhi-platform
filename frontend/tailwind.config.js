/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        climate: {
          dark: '#030712', // slate-950
          card: '#0f172a', // slate-900
          border: '#1e293b', // slate-800
          accent: '#10b981', // emerald-500
          secondary: '#38bdf8', // sky-400
          warning: '#f97316', // orange-500
          critical: '#ef4444', // red-500
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
