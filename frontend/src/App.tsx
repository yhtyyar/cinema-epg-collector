import { Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/layout/Header'
import HomePage from './pages/HomePage'
import MovieDetailPage from './pages/MovieDetailPage'
import SearchPage from './pages/SearchPage'

export default function App() {
  return (
    <div className="min-h-full flex flex-col">
      <Header />
      <main className="flex-1 container-responsive py-6">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/movie/:id" element={<MovieDetailPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="border-t border-gray-200/10 py-6 text-center text-sm text-gray-500">
        IPTV Movies · © {new Date().getFullYear()}
      </footer>
    </div>
  )
}
