/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'Inter', 'sans-serif'],
      },
      colors: {
        ink: '#08111f',
        ocean: '#0f4c81',
        aqua: '#1bb3a7',
        mist: '#eef6fb',
        ember: '#ff8a5b',
        lime: '#8ed081',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(255,255,255,0.08), 0 20px 60px rgba(8,17,31,0.22)',
      },
    },
  },
  plugins: [],
}
