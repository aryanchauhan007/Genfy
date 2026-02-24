"use client"

import { useState, useEffect } from "react"
import { useSession } from "@/contexts/session-context"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { copyToClipboard } from "@/lib/utils"
import { PromptDetailModal } from "@/components/prompt-detail-modal"
import {
  History,
  Clock,
  Trash2,
  Search,
  X,
  Sparkles,
  Eye,
  ExternalLink,
  RefreshCw
} from "lucide-react"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"

interface HistoryItem {
  id: string
  session_id: string
  prompt_text: string
  category: string
  created_at: string
  model_used?: string
  word_count?: number
}

interface HistorySidebarProps {
  onSelectPrompt?: (prompt: HistoryItem) => void
}

export function HistorySidebar({ onSelectPrompt }: HistorySidebarProps = {}) {
  const { sessionId, user } = useSession()
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedItem, setSelectedItem] = useState<string | null>(null)
  const { toast } = useToast()

  // ✅ Modal state
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedPrompt, setSelectedPrompt] = useState<HistoryItem | null>(null)

  useEffect(() => {
    loadHistory()
  }, [user, sessionId]) // ✅ Added sessionId to trigger refresh on session change


  const loadHistory = async () => {
    setIsLoading(true)
    try {
      // Pass user?.id to getHistory
      const response = await apiClient.getHistory(50, user?.id)
      console.log("📜 Raw history response:", response)

      const mappedHistory = (response.history || []).map((item: any) => {
        const promptText = item.prompt_text ||
          item.final_prompt ||
          item.text ||
          item.prompt ||
          item.content ||
          "No content available"

        const category = item.category ||
          item.selected_category ||
          item.type ||
          "Uncategorized"

        const createdAt = item.created_at ||
          item.timestamp ||
          item.date ||
          new Date().toISOString()

        const modelUsed = item.model_used ||
          item.selected_llm ||
          item.llm ||
          item.model ||
          "Unknown"

        const wordCount = item.word_count ||
          promptText.split(/\s+/).filter(Boolean).length

        return {
          id: item.id || item.session_id || `history-${Date.now()}`,
          session_id: item.session_id || item.id,
          prompt_text: promptText,
          category: category,
          created_at: createdAt,
          model_used: modelUsed,
          word_count: wordCount,
        }
      })

      console.log("✅ Mapped history:", mappedHistory)
      setHistory(mappedHistory)
    } catch (error) {
      console.error("❌ Failed to load history:", error)
      setHistory([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (itemId: string) => {
    try {
      await apiClient.deleteHistoryItem(Number(itemId))
      setHistory(prev => prev.filter(item => item.id !== itemId))
      toast({
        title: "Deleted",
        description: "Prompt removed from history",
      })
    } catch (error) {
      console.error("Delete error:", error)
      toast({
        title: "Error",
        description: "Failed to delete prompt",
        variant: "destructive",
      })
    }
  }

  // ✅ UPDATED: Open modal instead of toast
  const handleItemClick = (item: HistoryItem) => {
    setSelectedItem(item.id)
    setSelectedPrompt(item)
    setModalOpen(true)

    // Optional: Callback to parent component
    if (onSelectPrompt) {
      onSelectPrompt(item)
    }
  }

  // ✅ Eye button - Quick copy without opening modal
  const handleViewPrompt = async (item: HistoryItem, e: React.MouseEvent) => {
    e.stopPropagation()

    const promptText = item.prompt_text || "No content available"

    // Copy to clipboard
    const success = await copyToClipboard(promptText)
    if (success) {
      toast({
        title: "✓ Copied to Clipboard",
        description: `"${item.category}" prompt copied`,
      })
    } else {
      toast({
        title: "Copy Failed",
        description: "Could not copy to clipboard",
        variant: "destructive",
      })
    }
  }

  const filteredHistory = history.filter(item => {
    if (!item) return false

    const promptText = item.prompt_text || ""
    const category = item.category || ""
    const query = searchQuery.toLowerCase()

    return promptText.toLowerCase().includes(query) ||
      category.toLowerCase().includes(query)
  })

  const formatDate = (dateString: string) => {
    if (!dateString) return "Unknown"

    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return "Unknown"

      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 1) return "Just now"
      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      return date.toLocaleDateString()
    } catch {
      return "Unknown"
    }
  }

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <History className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">History</h2>
              <p className="text-xs text-gray-500">{history.length} prompts</p>
            </div>
          </div>
          {/* Refresh Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => loadHistory()}
            disabled={isLoading}
            className="h-8 w-8 p-0"
            title="Refresh history"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search prompts..."
            className="pl-9 pr-9 bg-white text-gray-900"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="w-4 h-4 text-gray-400 hover:text-gray-600" />
            </button>
          )}
        </div>
      </div>

      {/* History List - ✅ FIXED: Changed from ScrollArea to div */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center space-y-2">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-sm text-gray-500">Loading history...</p>
            </div>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-3">
              <History className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-sm text-gray-600 text-center font-medium">
              {searchQuery ? "No matching prompts found" : "No prompt history yet"}
            </p>
            <p className="text-xs text-gray-400 mt-2 text-center">
              {searchQuery ? "Try a different search term" : "Generate a prompt to see it here"}
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {filteredHistory.map((item) => (
              <div
                key={item.id}
                className={`group p-3 rounded-xl border transition-all cursor-pointer hover:shadow-md relative ${selectedItem === item.id
                  ? "bg-blue-50 border-blue-200"
                  : "bg-white border-gray-200 hover:border-blue-300"
                  }`}
                onClick={() => handleItemClick(item)}
              >
                {/* Category Badge & Actions */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                    {item.category}
                  </span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {/* Copy Button */}
                    <button
                      onClick={(e) => handleViewPrompt(item, e)}
                      className="p-1.5 hover:bg-blue-50 rounded transition-colors"
                      title="Copy prompt"
                    >
                      <Eye className="w-3.5 h-3.5 text-blue-600" />
                    </button>
                    {/* Delete Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(item.id)
                      }}
                      className="p-1.5 hover:bg-red-50 rounded transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5 text-red-500" />
                    </button>
                  </div>
                </div>

                {/* Prompt Preview */}
                <p className="text-sm text-gray-700 line-clamp-3 mb-2 leading-relaxed">
                  {item.prompt_text || "No content"}
                </p>

                {/* Metadata */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatDate(item.created_at)}</span>
                  </div>
                  <span className="font-medium">{item.word_count || 0} words</span>
                </div>

                {/* Model Badge */}
                {item.model_used && item.model_used !== "Unknown" && (
                  <div className="mt-2 pt-2 border-t border-gray-100">
                    <span className="text-xs text-purple-600 bg-purple-50 px-2 py-0.5 rounded">
                      {item.model_used}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      {/* ✅ FIXED: Changed from </ScrollArea> to </div> */}

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <Button
          onClick={loadHistory}
          className="w-full bg-white border border-gray-300 text-black hover:bg-gray-100"
          size="sm"
        >
          <History className="w-4 h-4 mr-2" />
          Refresh History
        </Button>
      </div>

      {/* ✅ Modal */}
      <PromptDetailModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false)
          setSelectedPrompt(null)
          setSelectedItem(null)
        }}
        prompt={selectedPrompt}
      />
    </div>
  )
}
