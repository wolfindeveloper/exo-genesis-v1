import { useState } from "react"

// Mock данные (пока)
const MOCK_SHIP = {
  name: "STELLA",
  rank: 3,
  materia: 1250,
  speed: 8.5,
  status: "ACTIVE",
  hp: 78,
  hpMax: 100,
  boosts: ["+12% Scan Range", "+5% Speed"],
}

export function Hangar() {
  const [repairing, setRepairing] = useState(false)
  
  const hpPercent = (MOCK_SHIP.hp / MOCK_SHIP.hpMax) * 100
  const hpColor = hpPercent > 60 ? "bg-neon-green" : hpPercent > 30 ? "bg-yellow-400" : "bg-neon-red"

  return (
    <div className="min-h-screen bg-space-900 text-white pb-20 relative overflow-hidden">
      {/* Звёздный фон (CSS паттерн) */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" 
           style={{ backgroundImage: "radial-gradient(white 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
      
      <div className="relative z-10 max-w-md mx-auto px-4 pt-6">
        {/* Top Bar */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-space-700 border border-neon-blue flex items-center justify-center text-lg">👤</div>
            <div>
              <p className="text-sm text-gray-400">Commander</p>
              <p className="font-mono text-neon-blue">12,450 $XGEN</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400">LVL 5</p>
            <div className="w-24 h-1.5 bg-space-700 rounded-full mt-1 overflow-hidden">
              <div className="h-full bg-neon-purple w-3/4 shadow-[0_0_10px_#BD00FF]" />
            </div>
            <p className="text-[10px] text-right text-gray-500 mt-0.5">3250/5000 XP</p>
          </div>
        </div>

        {/* Hangar Card */}
        <div className="bg-space-800 border border-space-700 rounded-2xl p-5 shadow-[0_0_20px_rgba(0,240,255,0.1)] relative">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold tracking-wider text-white">HANGAR</h2>
            <span className="text-neon-blue animate-pulse">⚡</span>
          </div>

          {/* Ship Display */}
          <div className="relative bg-space-900 rounded-xl p-4 mb-4 border border-space-700 overflow-hidden">
            <div className="absolute top-3 left-3 bg-space-800 px-2 py-0.5 rounded text-xs font-bold border border-neon-blue">
              {MOCK_SHIP.name} <span className="text-yellow-400 ml-1">T{MOCK_SHIP.rank}</span>
            </div>
            
            {/* Placeholder for Ship Image */}
            <div className="h-40 flex items-center justify-center">
              <div className="w-24 h-24 relative">
                <div className="absolute inset-0 bg-neon-blue opacity-20 blur-xl rounded-full" />
                <svg viewBox="0 0 24 24" className="w-full h-full text-neon-blue drop-shadow-[0_0_8px_#00F0FF]" fill="currentColor">
                  <path d="M12 2L2 22h20L12 2zm0 4l6 12H6l6-12z" />
                </svg>
                <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-12 h-4 bg-orange-500 blur-md opacity-60" />
              </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-3 mt-2">
              <div className="bg-space-900/50 p-2 rounded-lg border border-space-700">
                <p className="text-[10px] text-gray-400 uppercase">Materia</p>
                <p className="font-mono font-bold">{MOCK_SHIP.materia}</p>
              </div>
              <div className="bg-space-900/50 p-2 rounded-lg border border-space-700">
                <p className="text-[10px] text-gray-400 uppercase">Speed</p>
                <p className="font-mono font-bold">{MOCK_SHIP.speed}</p>
              </div>
              <div className="bg-space-900/50 p-2 rounded-lg border border-space-700">
                <p className="text-[10px] text-gray-400 uppercase">Status</p>
                <p className={`font-bold text-xs ${MOCK_SHIP.status === "ACTIVE" ? "text-neon-green" : "text-neon-red"}`}>
                  {MOCK_SHIP.status}
                </p>
              </div>
            </div>
          </div>

          {/* Boosts */}
          <div className="mb-4">
            <p className="text-[10px] text-gray-500 uppercase mb-1">Active Boosts</p>
            <div className="flex flex-wrap gap-2">
              {MOCK_SHIP.boosts.map((b, i) => (
                <span key={i} className="text-[10px] bg-neon-purple/10 text-neon-purple px-2 py-0.5 rounded border border-neon-purple/30">
                  {b}
                </span>
              ))}
            </div>
          </div>

          {/* Action Button */}
          <button className="w-full h-12 bg-gradient-to-r from-gray-600 via-neon-purple to-purple-800 rounded-xl font-bold text-lg tracking-widest shadow-neon-purple active:scale-95 transition-transform mb-3">
            ⚡ TAP TO MINE ⚡
          </button>

          {/* HP Bar */}
          <div className="mb-2">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>HULL INTEGRITY</span>
              <span>{MOCK_SHIP.hp}/{MOCK_SHIP.hpMax}</span>
            </div>
            <div className="h-2 bg-space-900 rounded-full overflow-hidden border border-space-700">
              <div className={`h-full ${hpColor} transition-all duration-500`} style={{ width: `${hpPercent}%` }} />
            </div>
          </div>

          {/* Repair Button */}
          <button
            onClick={() => setRepairing(true)}
            disabled={repairing || MOCK_SHIP.hp === MOCK_SHIP.hpMax}
            className="w-full py-2 text-xs font-medium text-gray-400 border border-space-700 rounded-lg hover:bg-space-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {repairing ? "⏳ Repairing..." : `🔧 Repair (250 $XGEN)`}
          </button>
        </div>
      </div>
    </div>
  )
}