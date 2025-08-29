import { Routes, Route, Navigate } from 'react-router-dom'
import HomePage from './pages/HomePage'
import MovieDetailPageNew from './pages/MovieDetailPageNew'

export default function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/movie/:id" element={<MovieDetailPageNew />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
