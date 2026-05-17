import { useState, useEffect } from "react"
import { withTelegramAuth } from "@/utils/telegram"

interface HangarData {
  player: { username: string; xgen_balance: number; xp: number; level: number; xp_to_next: number }
  ship: { name: string; rank: number; materia: number; speed: number; status: string; hp_current: number; hp_max: number; boosts: string[] }
  action: { type: string; text: string; timer_seconds: number }
}

export function Hangar() {
  const [data, setData] = useState<HangarData | null>(null)
  const [loading, setLoading] = useState(true)
  const [repairing, setRepairing] = useState(false)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
        const res = await fetch(`${API_URL}/api/hangar/status`, {
          headers: withTelegramAuth()
        })
        if (res.ok) setData(await res.json())
        if (res.ok) {
            const data = await res.json()
            setData(data)
            
            // 🔥 ДОБАВЬ ЭТО:
            if (data.ship?.id) {
                localStorage.setItem("ship_id", data.ship.id)
            }
            }
      } catch (e) {
        console.error("Failed to load hangar!!!", e)
      } finally {
        setLoading(false)
      }
    }
    
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    
    const handleStorageChange = () => {
        fetchStatus() // Перезагрузить данные при изменении в localStorage
    }
    window.addEventListener("storage", handleStorageChange)
    
    return () => {
        clearInterval(interval)
        window.removeEventListener("storage", handleStorageChange)  // ← и сюда добавь очистку
    }

  }, [])

  if (loading || !data) return <div className="min-h-screen bg-space-900 flex items-center justify-center text-neon-blue"> Loading Hangar...</div>

  const hpPercent = (data.ship.hp_current / data.ship.hp_max) * 100
  const hpColor = hpPercent > 60 ? "bg-neon-green" : hpPercent > 30 ? "bg-yellow-400" : "bg-neon-red"

  return (
    <div className="min-h-screen bg-space-900 text-white pb-20 relative overflow-hidden">
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: "radial-gradient(white 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
      
      <div className="relative z-10 max-w-md mx-auto px-4 pt-6">
        {/* Top Bar */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-space-700 border border-neon-blue flex items-center justify-center text-lg"></div>
            <div>
              <p className="text-sm text-gray-400">{data.player.username}</p>
              <p className="font-mono text-neon-blue">{data.player.xgen_balance.toLocaleString()} $XGEN</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400">LVL {data.player.level}</p>
            <div className="w-24 h-1.5 bg-space-700 rounded-full mt-1 overflow-hidden">
              <div className="h-full bg-neon-purple transition-all" style={{ width: `${(data.player.xp / data.player.xp_to_next) * 100}%` }} />
            </div>
            <p className="text-[10px] text-right text-gray-500 mt-0.5">{data.player.xp}/{data.player.xp_to_next} XP</p>
          </div>
        </div>

        {/* Hangar Card */}
        <div className="bg-space-800 border border-space-700 rounded-2xl p-5 shadow-[0_0_20px_rgba(0,240,255,0.1)] relative">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold tracking-wider text-white">HANGAR</h2>
            <span className="text-neon-blue animate-pulse"></span>
          </div>

          <div className="relative bg-space-900 rounded-xl p-4 mb-4 border border-space-700 overflow-hidden">
            <div className="absolute top-3 left-3 bg-space-800 px-2 py-0.5 rounded text-xs font-bold border border-neon-blue">
              {data.ship.name} <span className="text-yellow-400 ml-1">T{data.ship.rank}</span>
            </div>
            <div className="h-40 flex items-center justify-center">
              <div className="w-24 h-24 relative">
                <div className="absolute inset-0 bg-neon-blue opacity-20 blur-xl rounded-full" />
                <svg viewBox="0 0 24 24" className="w-full h-full text-neon-blue drop-shadow-[0_0_8px_#00F0FF]" fill="currentColor">
                  <path d="M12 2L2 22h20L12 2zm0 4l6 12H6l6-12z" />
                </svg>
                <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-12 h-4 bg-orange-500 blur-md opacity-60" />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 mt-2">
              <div className="bg-space-900/50 p-2 rounded-lg border border-space-700">
                <p className="text-[10px] text-gray-400 uppercase">Materia</p>
                <p className="font-mono font-bold">{data.ship.materia}</p>
              </div>
              <div className="bg-space-900/50 p-2 rounded-lg border border-space-700">
                <p className="text-[10px] text-gray-400 uppercase">Speed</p>
                <p className="font-mono font-bold">{data.ship.speed}</p>
              </div>
              <div className="bg-space-900/50 p-2 rounded-lg border border-space-700">
                <p className="text-[10px] text-gray-400 uppercase">Status</p>
                <p className={`font-bold text-xs ${data.ship.status === "Active" ? "text-neon-green" : "text-neon-red"}`}>{data.ship.status}</p>
              </div>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-[10px] text-gray-500 uppercase mb-1">Active Boosts</p>
            <div className="flex flex-wrap gap-2">
              {data.ship.boosts.map((b, i) => (
                <span key={i} className="text-[10px] bg-neon-purple/10 text-neon-purple px-2 py-0.5 rounded border border-neon-purple/30">{b}</span>
              ))}
            </div>
          </div>

          <button className={`w-full h-12 rounded-xl font-bold text-lg tracking-widest shadow-neon-purple active:scale-95 transition-transform mb-3 ${data.action.type === "expedition" ? "bg-gray-700 cursor-wait" : "bg-gradient-to-r from-gray-600 via-neon-purple to-purple-800"}`}>
            {data.action.text}
          </button>

          <div className="mb-2">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>HULL INTEGRITY</span>
              <span>{data.ship.hp_current}/{data.ship.hp_max}</span>
            </div>
            <div className="h-2 bg-space-900 rounded-full overflow-hidden border border-space-700">
              <div className={`h-full ${hpColor} transition-all duration-500`} style={{ width: `${hpPercent}%` }} />
            </div>
          </div>

          <button
            onClick={() => setRepairing(true)}
            disabled={repairing || data.ship.hp_current === data.ship.hp_max}
            className="w-full py-2 text-xs font-medium text-gray-400 border border-space-700 rounded-lg hover:bg-space-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {repairing ? "⏳ Repairing..." : `🔧 Repair (250 $XGEN)`}
          </button>
        </div>
      </div>
    </div>
  )
}