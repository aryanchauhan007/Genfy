"use client"

import { useState, useEffect } from "react"
import { useSession } from "@/contexts/session-context"
import { Button } from "@/components/ui/button"
import { RefreshCw, Loader2, Sparkles } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface SuggestionChipsProps {
  onSelect?: (suggestion: string) => void
  currentQuestion?: any
}

export function SuggestionChips({ onSelect, currentQuestion }: SuggestionChipsProps) {
  const { getSuggestions, toggleSuggestion, selectedSuggestions } = useSession()
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [refreshCount, setRefreshCount] = useState(0)
  const { toast } = useToast()

  useEffect(() => {
    loadSuggestions(0)
  }, [currentQuestion?.id])

  const loadSuggestions = async (refresh: number) => {
    setIsLoading(true)
    try {
      const newSuggestions = await getSuggestions(refresh)
      setSuggestions(newSuggestions || [])
    } catch (error) {
      console.error("Failed to load suggestions:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = () => {
    const newCount = refreshCount + 1
    setRefreshCount(newCount)
    loadSuggestions(newCount)
  }

  const handleChipClick = async (suggestion: string) => {
    try {
      await toggleSuggestion(suggestion)
      if (onSelect) {
        onSelect(suggestion)
      }
    } catch (error) {
      console.error("Error toggling suggestion:", error)
    }
  }

  if (isLoading && suggestions.length === 0) {
    return (
      <div className="flex items-center gap-2 text-gray-500 py-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-xs font-medium">Generating creative ideas...</span>
      </div>
    )
  }

  if (suggestions.length === 0) {
    return null
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-blue-600" />
          <span className="text-sm font-semibold text-gray-900">AI Suggestions</span>
          <span className="text-xs text-gray-500">(click to use)</span>
        </div>
        <Button
          onClick={handleRefresh}
          disabled={isLoading}
          variant="ghost"
          size="sm"
          className="h-7 px-2 text-gray-400 hover:text-gray-900 hover:bg-gray-100 transition-colors"
        >
          {isLoading ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <RefreshCw className="h-3 w-3" />
          )}
          <span className="ml-1.5 text-xs font-medium">Shuffle</span>
        </Button>
      </div>

      {/* Suggestions Grid */}
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, idx) => {
          const isSelected = selectedSuggestions.includes(suggestion);
          
          return (
            <Button
              key={idx}
              onClick={() => handleChipClick(suggestion)}
              variant="outline"
              size="sm"
              className={`
                text-xs transition-all duration-200 rounded-full px-4 py-1.5 h-auto whitespace-normal text-left border
                ${isSelected
                  ? "bg-black text-white border-black shadow-md hover:bg-gray-800 hover:text-white" 
                  : "bg-white text-gray-600 border-gray-200 hover:border-gray-400 hover:text-gray-900 hover:bg-gray-50 hover:shadow-sm"
                }
              `}
            >
              {suggestion}
            </Button>
          )
        })}
      </div>

      {/* Selected Count */}
      {selectedSuggestions.length > 0 && (
        <div className="text-xs text-blue-600 font-medium px-1 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
          {selectedSuggestions.length} selected
        </div>
      )}
    </div>
  )
}