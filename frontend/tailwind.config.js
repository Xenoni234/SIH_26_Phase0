/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        express: "#dc2626",
        local: "#2563eb",
        memu: "#0d9488",
        freight: "#d97706",
        passenger: "#64748b",
        yard: "#7c3aed",
      },
    },
  },
  plugins: [],
};
