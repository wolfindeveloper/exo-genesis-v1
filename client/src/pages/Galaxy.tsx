// client/src/pages/Galaxy.tsx
import { useState, useEffect } from "react"
import { withTelegramAuth } from "@/utils/telegram"

interface Zone {
  id: string
  name: string
  risk: number
  minDuration: number
  maxDuration: number
  rewardMultiplier: number
}

const ZONES: Zone[] = [
  { id: "asteroid_belt", name: "Asteroid Belt", risk: 15, minDuration: 30, maxDuration: 90, rewardMultiplier: 1.0 },
  { id: "nebula_edge", name: "Nebula Edge", risk: 35, minDuration: 60, maxDuration: 180, rewardMultiplier: 2.5 },
  { id: "black_hole", name: "Black Hole", risk: 75, minDuration: 120, maxDuration: 240, rewardMultiplier: 5.0 },
]

export function Galaxy() {
  const [zones] = useState<Zone[]>(ZONES)
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null)
  const [duration, setDuration] = useState(60)
  const [launching, setLaunching] = useState(false)
  const [claiming, setClaiming] = useState(false)
  const [activeExp, setActiveExp] = useState<{
    id: string
    endTime: string
    progress: number
    canClaim: boolean
    loot?: any
    reward?: any
  } | null>(null)
  const [showLoot, setShowLoot] = useState(false)

  // Проверка активной экспедиции при загрузке
  useEffect(() => {
    const checkActive = async () => {
      try {
        // TODO: реализовать GET /api/expeditions/active на бэкенде
        // Пока заглушка — можно расширить позже
      } catch (e) {
        console.error("Failed to check active expedition", e)
      }
    }
    checkActive()
  }, [])

  const handleLaunch = async () => {
    if (!selectedZone) return
    const shipId = localStorage.getItem("ship_id")
    if (!shipId) {
      alert("⚠️ Ship not found. Please open Hangar first.")
      return
    }
    setLaunching(true)
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
      const res = await fetch(`${API_URL}/api/expeditions/start`, {
        method: "POST",
        headers: {
          ...withTelegramAuth(),
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ship_id: localStorage.getItem("ship_id") || "",
          zone_config_id: selectedZone.id,
          zone_risk: selectedZone.risk,
          duration_min: duration
        })
      })
      
      if (res.ok) {
        const data = await res.json()
        setActiveExp({
          id: data.expedition_id,
          endTime: data.end_time,
          progress: 0,
          canClaim: false
        })
      } else {
        const err = await res.json()
        alert(`Launch failed: ${err.detail || "Unknown error"}`)
      }
    } catch (e) {
      console.error("Launch failed", e)
      alert("Network error. Check console.")
    } finally {
      setLaunching(false)
    }
  }

  const handleClaim = async () => {
    if (!activeExp) return
    setClaiming(true)
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
      const res = await fetch(`${API_URL}/api/expeditions/${activeExp.id}/claim`, {
        method: "POST",
        headers: {
          ...withTelegramAuth(),
          "Content-Type": "application/json"
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setActiveExp(prev => prev ? { ...prev, loot: data.loot, reward: data, canClaim: false } : null)
        setShowLoot(true)
        
        // Авто-обновление баланса в Ангаре (через localStorage или события)
        localStorage.setItem("hangar_refresh", Date.now().toString())
      } else {
        const err = await res.json()
        alert(`Claim failed: ${err.detail || "Unknown error"}`)
      }
    } catch (e) {
      console.error("Claim failed", e)
      alert("Network error. Check console.")
    } finally {
      setClaiming(false)
    }
  }

  // Таймер обновления прогресса
  useEffect(() => {
    if (!activeExp || activeExp.canClaim) return
    
    const interval = setInterval(async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
        const res = await fetch(`${API_URL}/api/expeditions/${activeExp.id}/status`, {
          headers: withTelegramAuth()
        })
        if (res.ok) {
          const data = await res.json()
          if (data.completed || data.status === "completed" || data.status === "damaged" || data.status === "destroyed") {
            setActiveExp(prev => prev ? { ...prev, progress: 1, canClaim: true } : null)
          } else {
            setActiveExp(prev => prev ? { ...prev, progress: data.progress || 0 } : null)
          }
        }
      } catch (e) {
        console.error("Status check failed", e)
      }
    }, 5000)
    
    return () => clearInterval(interval)
  }, [activeExp])

  // Экран показа лута
  if (showLoot && activeExp?.reward) {
    const { loot, rare, xgen_earned, ship_destroyed } = activeExp.reward
    return (
      <div className="min-h-screen bg-space-900 text-white flex flex-col items-center justify-center p-4">
        <div className="bg-space-800 border border-neon-green rounded-2xl p-6 max-w-md w-full shadow-[0_0_30px_rgba(0,255,100,0.3)] animate-pulse">
          <h2 className="text-2xl font-bold text-center mb-4 text-neon-green">🎁 MISSION COMPLETE!</h2>
          
          {ship_destroyed ? (
            <div className="text-center py-4">
              <p className="text-neon-red text-lg font-bold mb-2">💥 SHIP DESTROYED</p>
              <p className="text-sm text-gray-400">Your vessel was lost in the void...</p>
            </div>
          ) : (
            <div className="space-y-3 mb-6">
              <p className="text-sm text-gray-400">Loot acquired:</p>
              {loot && Object.entries(loot).map(([item, amount]) => (
                <div key={item} className="flex justify-between items-center bg-space-900/50 p-3 rounded-lg">
                  <span className="capitalize">{item.replace("_", " ")}</span>
                  <span className="font-mono text-neon-blue">+{String(amount)}</span>
                </div>
              ))}
              {rare && rare.length > 0 && (
                <div className="border-t border-space-700 pt-3 mt-3">
                  <p className="text-xs text-neon-purple mb-2">✨ Rare drops:</p>
                  {rare.map((item: string) => (
                    <div key={item} className="flex justify-between items-center bg-neon-purple/10 p-2 rounded">
                      <span className="capitalize">{item.replace("_", " ")}</span>
                      <span className="text-neon-purple">★</span>
                    </div>
                  ))}
                </div>
              )}
              <div className="bg-neon-blue/10 p-3 rounded-lg border border-neon-blue/30">
                <p className="text-sm text-gray-400">XGEN earned</p>
                <p className="text-xl font-bold text-neon-blue">+{xgen_earned?.toFixed(2) || "0.00"}</p>
              </div>
            </div>
          )}
          
          <button 
            onClick={() => { setShowLoot(false); setActiveExp(null); }}
            className="w-full py-3 rounded-xl font-bold bg-gradient-to-r from-neon-green to-green-700"
          >
            ✅ RETURN TO HANGAR
          </button>
        </div>
      </div>
    )
  }

  // Экран активной экспедиции (таймер)
  if (activeExp) {
    return (
      <div className="min-h-screen bg-space-900 text-white flex flex-col items-center justify-center p-4">
        <div className="bg-space-800 border border-neon-blue rounded-2xl p-6 max-w-md w-full shadow-[0_0_30px_rgba(0,240,255,0.2)]">
          <h2 className="text-xl font-bold text-center mb-4 text-neon-blue">🚀 EXPEDITION IN PROGRESS</h2>
          
          <div className="mb-6">
            <p className="text-sm text-gray-400 mb-2">Progress</p>
            <div className="h-3 bg-space-900 rounded-full overflow-hidden border border-space-700">
              <div 
                className="h-full bg-gradient-to-r from-neon-blue to-neon-purple transition-all duration-500"
                style={{ width: `${activeExp.progress * 100}%` }}
              />
            </div>
            <p className="text-xs text-center text-gray-500 mt-1">
              {Math.round(activeExp.progress * 100)}% complete
            </p>
          </div>
          
          <button 
            onClick={handleClaim}
            disabled={!activeExp.canClaim || claiming}
            className="w-full py-3 rounded-xl font-bold bg-gradient-to-r from-neon-green to-green-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-gray-600 disabled:to-gray-700"
          >
            {claiming ? "⏳ CLAIMING..." : activeExp.canClaim ? "🎁 CLAIM REWARDS" : "⏳ RETURNING..."}
          </button>
          
          {!activeExp.canClaim && (
            <p className="text-xs text-center text-gray-500 mt-3">
              Rewards will be available upon completion
            </p>
          )}
        </div>
      </div>
    )
  }

  // Основной экран: выбор зоны
  return (
    <div className="min-h-screen bg-space-900 text-white pb-20">
      <div className="max-w-md mx-auto px-4 pt-6">
        <h1 className="text-2xl font-bold mb-6 text-center text-neon-blue">🌌 GALAXY MAP</h1>
        
        {/* Список зон */}
        <div className="space-y-3 mb-6">
          {zones.map(zone => (
            <button
              key={zone.id}
              onClick={() => setSelectedZone(zone)}
              className={`w-full p-4 rounded-xl border text-left transition-all ${
                selectedZone?.id === zone.id 
                  ? "border-neon-blue bg-space-800 shadow-[0_0_15px_rgba(0,240,255,0.3)]" 
                  : "border-space-700 bg-space-800/50 hover:border-neon-purple/50"
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="font-bold">{zone.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  zone.risk < 30 ? "bg-neon-green/20 text-neon-green" :
                  zone.risk < 60 ? "bg-yellow-400/20 text-yellow-400" :
                  "bg-neon-red/20 text-neon-red"
                }`}>
                  Risk: {zone.risk}%
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Duration: {zone.minDuration}-{zone.maxDuration} min • x{zone.rewardMultiplier} rewards
              </p>
            </button>
          ))}
        </div>
        
        {/* Настройка длительности */}
        {selectedZone && (
          <div className="bg-space-800 border border-space-700 rounded-xl p-4 mb-6">
            <p className="text-sm text-gray-400 mb-2">Mission Duration</p>
            <input
              type="range"
              min={selectedZone.minDuration}
              max={selectedZone.maxDuration}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full accent-neon-blue"
            />
            <p className="text-center font-mono text-neon-blue mt-1">{duration} minutes</p>
          </div>
        )}
        
        {/* Кнопка запуска */}
        <button
          onClick={handleLaunch}
          disabled={!selectedZone || launching}
          className="w-full py-4 rounded-xl font-bold text-lg bg-gradient-to-r from-neon-blue via-cyan-500 to-neon-purple disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(0,240,255,0.4)] active:scale-95 transition-transform"
        >
          {launching ? "🚀 LAUNCHING..." : "⚡ LAUNCH EXPEDITION"}
        </button>
      </div>
    </div>
  )
}