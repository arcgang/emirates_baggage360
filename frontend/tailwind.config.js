/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Emirates brand colors from wireframes
        'ek-red': '#E7002A',
        'ek-black': '#231F20',
        'ek-gold': '#D4AF37',
        'ek-gray-light': '#F5F5F5',
        'ek-gray-medium': '#CCCCCC',
        'ek-gray-dark': '#666666',
      },
    },
  },
  plugins: [],
}
