# IPTV Movies Frontend

Modern minimal interface built with React 18 + TypeScript + Vite + Tailwind.

## Manual Deployment

For manual deployment on Ubuntu, follow these steps:

1. Install dependencies:
```bash
npm ci
```

2. Build the application:
```bash
npm run build
```

3. Serve the built files (in the `dist/` directory) with any web server.

## Development

For local development with backend proxy:

1. Install dependencies:
```bash
npm i
```

2. Start the development server (proxy to backend on /api is configured in vite.config.ts):
```bash
npm run dev
```

## Scripts
- dev — Local development
- build — Production build
- preview — Preview the built application

## Technology Stack
- React 18, React Router 6
- TypeScript
- Tailwind CSS (dark/light themes)
- React Query (request caching)
- Axios (API)
- react-helmet-async (SEO)

Structure can be found in the src/ directory. Dark theme by default, toggle switch is in the header.