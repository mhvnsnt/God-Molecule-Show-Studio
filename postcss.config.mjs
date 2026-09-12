// Tailwind v4 through PostCSS. The Vite plugin (@tailwindcss/vite) does not
// apply here -- Next compiles CSS with its own PostCSS pipeline.
const config = {
  plugins: { '@tailwindcss/postcss': {} },
};

export default config;
