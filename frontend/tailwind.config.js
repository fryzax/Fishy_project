export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ocean: {
          50: '#e0f7ff',
          100: '#b3e6ff',
          200: '#80d4ff',
          300: '#4dc2ff',
          400: '#26b5ff',
          500: '#00a8ff',
          600: '#0091e6',
          700: '#0077cc',
          800: '#005db3',
          900: '#003d80',
        }
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        'float-slower': 'float 10s ease-in-out infinite',
        'bubble': 'bubble 4s ease-in-out infinite',
        'bubble-slow': 'bubble 6s ease-in-out infinite',
        'bubble-slower': 'bubble 8s ease-in-out infinite',
        'swim': 'swim 15s linear infinite',
        'swim-fast': 'swim 10s linear infinite',
        'wiggle': 'wiggle 1s ease-in-out infinite',
        'wave': 'wave 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        bubble: {
          '0%': { transform: 'translateY(0) scale(0)', opacity: '0' },
          '10%': { opacity: '0.8' },
          '90%': { opacity: '0.8' },
          '100%': { transform: 'translateY(-100vh) scale(1.2)', opacity: '0' },
        },
        swim: {
          '0%': { transform: 'translateX(-100%) translateY(0) scaleX(1)' },
          '25%': { transform: 'translateX(25vw) translateY(-20px) scaleX(1)' },
          '49%': { transform: 'translateX(100vw) translateY(0) scaleX(1)' },
          '51%': { transform: 'translateX(100vw) translateY(0) scaleX(-1)' },
          '75%': { transform: 'translateX(25vw) translateY(20px) scaleX(-1)' },
          '100%': { transform: 'translateX(-100%) translateY(0) scaleX(-1)' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        wave: {
          '0%, 100%': { transform: 'translateX(0)' },
          '50%': { transform: 'translateX(20px)' },
        },
        'pulse-glow': {
          '0%, 100%': {
            boxShadow: '0 0 20px rgba(0, 168, 255, 0.5)',
            transform: 'scale(1)',
          },
          '50%': {
            boxShadow: '0 0 40px rgba(0, 168, 255, 0.8)',
            transform: 'scale(1.02)',
          },
        }
      }
    },
  },
  plugins: [],
}
