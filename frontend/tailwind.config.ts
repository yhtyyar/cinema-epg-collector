import type { Config } from 'tailwindcss'
import lineClamp from '@tailwindcss/line-clamp'

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: { light: '#ffffff', dark: '#0f1115' },
        fg: { light: '#0f1115', dark: '#e5e7eb' },
        accent: { DEFAULT: '#7c3aed' }
      },
      boxShadow: {
        soft: '0 2px 10px rgba(0,0,0,0.08)'
      },
      transitionProperty: {
        theme: 'background-color, color, border-color, fill, stroke'
      }
    }
  },
  plugins: [lineClamp],
} satisfies Config
