/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        space: {
          900: '#05050A', // Глубокий космос (фон)
          800: '#0A0A12', // Карточки
          700: '#13131F', // Бордеры
        },
        neon: {
          blue: '#00F0FF',  // Акцент 1 (Materia/Speed)
          purple: '#BD00FF', // Акцент 2 (Button/XP)
          green: '#00FF94',  // Status Active
          red: '#FF2A2A',    // Status Damage
        }
      },
      fontFamily: {
        mono: ['Courier New', 'monospace'], // Для цифр
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'neon-blue': '0 0 10px rgba(0, 240, 255, 0.5)',
        'neon-purple': '0 0 15px rgba(189, 0, 255, 0.4)',
      }
    },
  },
  plugins: [],
}