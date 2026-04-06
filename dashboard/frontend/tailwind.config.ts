import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "orchestra-bg": "#f4efe2",
        "orchestra-card": "#fffaf0",
        "orchestra-ink": "#2f2a1f",
        "orchestra-accent": "#0e7490"
      }
    }
  },
  plugins: []
};

export default config;
