# Cinema EPG Frontend

Modern React frontend for the Cinema EPG Collector application, built with Vite, TypeScript, and Tailwind CSS.

## 🚀 Technologies Used

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Axios** - HTTP client

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/          # Generic components (loading, errors, etc.)
│   ├── layout/          # Layout components (header, footer)
│   ├── movies/          # Movie-specific components
│   ├── ui/              # Primitive UI components
│   └── ...
├── context/             # React context providers
├── hooks/               # Custom React hooks
├── lib/                 # Utility functions and constants
├── pages/               # Page components
├── services/            # API service layer
├── styles/              # Global styles
├── types/               # TypeScript types
└── utils/               # Helper functions
```

## 🛠️ Development

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

### Development Server with Custom Host/Port

You can customize the host and port in several ways:

1. **Using environment variables**:
   Create a `.env` file in the frontend directory with:
   ```env
   VITE_HOST=0.0.0.0
   VITE_PORT=3000
   ```
   Then run:
   ```bash
   npm run dev
   ```

2. **Using command line arguments**:
   ```bash
   # To expose the server to all network interfaces
   npm run dev:host
   
   # On Unix-like systems, you can also specify host/port directly:
   VITE_HOST=0.0.0.0 VITE_PORT=3000 npm run dev
   ```

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 🎨 Styling

The application uses Tailwind CSS with custom variables defined in `src/styles/globals.css`. All colors are defined as CSS variables for easy theming.

## 🔄 API Integration

The frontend communicates with the backend API through the service layer in `src/services/api.ts`. All API calls are properly typed and handle errors gracefully.

## 🧪 Testing

React Query is used for server state management with automatic caching, background updates, and error handling.

## 📱 Responsive Design

The application is fully responsive and works on all device sizes.

## 🌙 Theme Support

The application supports dark mode with automatic detection of system preferences and manual toggle option.

## 🚀 Performance Optimizations

- Code splitting
- Lazy loading
- Memoization
- Efficient re-renders
- Image optimization
- Bundle size optimization

## 📦 Dependencies

Key dependencies include:
- `react` - UI library
- `react-router-dom` - Routing
- `@tanstack/react-query` - Server state management
- `axios` - HTTP client
- `tailwindcss` - CSS framework
- `classnames` - Conditional class names
- `react-lazy-load-image-component` - Image lazy loading

## 📝 Code Quality

- TypeScript for type safety
- ESLint for code linting
- Prettier for code formatting
- Strict TypeScript configuration
- Component memoization
- Proper error boundaries
- Consistent naming conventions

## 🚀 Deployment

The application can be deployed as a static site. The build process generates optimized assets in the `dist/` directory.

## 📚 Documentation

- All components are documented with JSDoc comments
- TypeScript types provide self-documenting code
- Clear folder structure and naming conventions