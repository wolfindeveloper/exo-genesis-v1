import { useLocation, useNavigate } from "react-router-dom"

const NAV_ITEMS = [
  { id: "hangar", label: "Hangar", icon: "🚀" },
  { id: "galaxy", label: "Galaxy", icon: "🌌" },
  { id: "lab", label: "Lab", icon: "🧪" },
]

export function BottomNav() {
  const location = useLocation()
  const navigate = useNavigate()
  
  return (
    <nav className="fixed bottom-0 left-0 right-0 h-16 bg-space-900 border-t border-space-700 flex justify-around items-center px-4 z-50">
      {NAV_ITEMS.map((item) => {
        const isActive = location.pathname === `/${item.id}`
        return (
          <button
            key={item.id}
            onClick={() => navigate(`/${item.id}`)}
            className={`flex flex-col items-center gap-1 transition-colors ${
              isActive ? "text-neon-blue" : "text-gray-500"
            }`}
          >
            <span className={`text-2xl ${isActive ? "drop-shadow-[0_0_8px_rgba(0,240,255,0.6)]" : ""}`}>
              {item.icon}
            </span>
            <span className="text-xs font-medium">{item.label}</span>
            {isActive && <div className="absolute -bottom-1 w-8 h-0.5 bg-neon-blue rounded-full shadow-neon-blue" />}
          </button>
        )
      })}
    </nav>
  )
}