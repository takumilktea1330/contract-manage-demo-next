/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3182ce',
          dark: '#2c5282',
          darker: '#1a365d',
        },
        accent: {
          DEFAULT: '#e53e3e',
        },
      },
    },
  },
  plugins: [],
}
