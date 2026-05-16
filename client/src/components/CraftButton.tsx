// client/src/components/CraftButton.tsx
import { useState } from "react"
import { Button } from "@/components/ui/button" // shadcn/ui кнопка
import { withTelegramAuth } from "@/utils/telegram"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface CraftResult {
  artifact_id: number
  name_ru: string
  rarity: string
  effect: Record<string, number>
}

export function CraftButton() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<CraftResult | null>(null)

  const handleCraft = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
        const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
        const res = await fetch(`${API_URL}/api/lab/craft`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...withTelegramAuth(),
        },
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Ошибка сервера")
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-sm mx-auto">
      <CardHeader>
        <CardTitle>🧪 Лаборатория: Слепой крафт</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button onClick={handleCraft} disabled={loading} className="w-full">
          {loading ? "Крафтится..." : "Скрафтить артефакт"}
        </Button>

        {error && (
          <div className="p-2 bg-red-50 text-red-600 rounded text-sm">
            ❌ {error}
          </div>
        )}

        {result && (
          <div className="p-3 bg-green-50 rounded text-sm space-y-1">
            <p className="font-semibold">✨ {result.name_ru}</p>
            <p className="text-muted-foreground">Редкость: {result.rarity}</p>
            <p className="text-xs text-muted-foreground">
              Эффект: {JSON.stringify(result.effect)}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}