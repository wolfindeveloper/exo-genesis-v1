import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { BottomNav } from "./components/BottomNav"
import { Hangar } from "./pages/Hangar"
import { Galaxy } from "@/pages/Galaxy"

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-space-900">
        <Routes>
          <Route path="/" element={<Navigate to="/hangar" replace />} />
          <Route path="/hangar" element={<Hangar />} />
          <Route path="/galaxy" element={<Galaxy />} />
          <Route path="/lab" element={<div className="p-10 text-center text-gray-500">Lab Page (Soon)</div>} />
        </Routes>
        <BottomNav />
      </div>
    </BrowserRouter>
  )
}

export default App