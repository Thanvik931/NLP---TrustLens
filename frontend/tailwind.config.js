/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          sidebar: '#020617',
          bg: '#0F172A',
          card: '#1E293B',
          border: '#334155'
        },
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          glow: 'rgba(59, 130, 246, 0.5)'
        },
        accent: {
          emerald: '#10B981',
          rose: '#F43F5E',
          indigo: '#6366F1'
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif']
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        }
      }
    },
  },
  plugins: [],
}
