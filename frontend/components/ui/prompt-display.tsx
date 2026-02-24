"use client"

import { useState, useEffect } from "react"
import { useSession } from "@/contexts/session-context"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { copyToClipboard } from "@/lib/utils"
import {
  Copy,
  Download,
  Sparkles,
  RefreshCw,
  Check,
  Wand2,
  FileText,
  Loader2,
  Plus
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { motion } from "framer-motion"

interface PromptDisplayProps {
  onStartNew: () => void
}

export function PromptDisplay({ onStartNew }: PromptDisplayProps) {
  const { session, sessionId, refinePrompt, isLoading } = useSession()
  const [finalPrompt, setFinalPrompt] = useState("")
  const [isLoadingPrompt, setIsLoadingPrompt] = useState(true)
  const [refinementInput, setRefinementInput] = useState("")
  const [isRefining, setIsRefining] = useState(false)
  const [isCopied, setIsCopied] = useState(false)
  const { toast } = useToast()

  // Load Prompt Logic
  useEffect(() => {
    const loadPrompt = async () => {
      if (!sessionId) {
        setIsLoadingPrompt(false)
        return
      }

      setIsLoadingPrompt(true)

      try {
        if (session?.final_prompt) {
          setFinalPrompt(session.final_prompt)
        } else {
          const response = await apiClient.getFinalPrompt(sessionId)
          setFinalPrompt(response.final_prompt)
        }
      } catch (error) {
        console.error("Failed to load prompt:", error)
        try {
          const sessionData = await apiClient.getSession(sessionId)
          if (sessionData.final_prompt) {
            setFinalPrompt(sessionData.final_prompt)
          }
        } catch (err) {
          console.error("All methods failed:", err)
        }
      } finally {
        setIsLoadingPrompt(false)
      }
    }

    loadPrompt()
  }, [sessionId, session?.final_prompt])

  const wordCount = finalPrompt ? finalPrompt.split(/\s+/).filter(Boolean).length : 0

  const handleCopy = async () => {
    try {
      const success = await copyToClipboard(finalPrompt)
      if (success) {
        setIsCopied(true)
        setTimeout(() => setIsCopied(false), 2000)
        toast({ title: "Copied! ✓", description: "Prompt copied to clipboard" })
      } else {
        throw new Error("Copy failed")
      }
    } catch (error) {
      toast({ title: "Copy Failed", description: "Failed to copy prompt", variant: "destructive" })
    }
  }

  const handleDownload = () => {
    const blob = new Blob([finalPrompt], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `ai-prompt-${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast({ title: "Downloaded! ✓", description: "Prompt saved as text file" })
  }

  const handleRefine = async () => {
    if (!refinementInput.trim()) {
      toast({ title: "Empty Input", description: "Please describe what you want to change", variant: "destructive" })
      return
    }

    setIsRefining(true)
    try {
      const refined = await refinePrompt(refinementInput)
      setFinalPrompt(refined)
      setRefinementInput("")
      toast({ title: "Prompt Refined! ✨", description: "Your prompt has been updated" })
    } catch (error) {
      toast({ title: "Refinement Failed", description: "Failed to refine prompt.", variant: "destructive" })
    } finally {
      setIsRefining(false)
    }
  }

  // Loading state
  if (isLoadingPrompt) {
    return (
      <div className="flex items-center justify-center py-24 bg-white rounded-2xl border border-gray-100 shadow-sm max-w-3xl mx-auto">
        <div className="text-center space-y-3">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-500 text-sm font-medium">Finalizing your prompt...</p>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-3xl mx-auto space-y-6 pb-12"
    >

      {/* --- PROMPT CARD --- */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        {/* Top Accent Line */}
        <div className="h-1 w-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />

        <div className="p-6 space-y-5">

          {/* Header Row */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 shadow-sm border border-blue-100">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900 tracking-tight">Your AI Prompt</h1>
                <p className="text-xs text-gray-500 font-medium">Ready for generation</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 self-start md:self-center">
              <Button
                onClick={handleCopy}
                variant="outline"
                className="bg-white hover:bg-gray-50 text-gray-700 border-gray-200 h-8 px-4 text-xs font-semibold shadow-sm transition-all"
              >
                {isCopied ? <Check className="w-3.5 h-3.5 mr-1.5 text-green-600" /> : <Copy className="w-3.5 h-3.5 mr-1.5" />}
                {isCopied ? "Copied" : "Copy"}
              </Button>
              <Button
                onClick={handleDownload}
                variant="outline"
                className="bg-white hover:bg-gray-50 text-gray-700 border-gray-200 h-8 px-4 text-xs font-semibold shadow-sm transition-all"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" />
                Save
              </Button>
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-100 uppercase tracking-wide">
              {session?.selected_category || "Image"}
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-100 uppercase tracking-wide">
              {session?.selected_llm || "Claude"}
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-600 border border-gray-200 uppercase tracking-wide">
              <FileText className="w-3 h-3" />
              {wordCount} words
            </span>
          </div>

          {/* Prompt Text Box */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-100 to-purple-100 rounded-xl opacity-30 blur-sm group-hover:opacity-60 transition duration-500"></div>
            <div className="relative bg-white border border-gray-200 rounded-xl p-5">
              <p className="text-gray-900 text-base leading-relaxed font-medium whitespace-pre-wrap selection:bg-blue-100">
                {finalPrompt || "Generating your prompt..."}
              </p>
            </div>
          </div>

        </div>
      </div>

      {/* --- REFINE CARD --- */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-1">
            <Wand2 className="w-4 h-4 text-gray-900" />
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide">Refine Result</h3>
          </div>

          {/* Input & Button Layout */}
          <div className="flex flex-col gap-3">
            <Textarea
              value={refinementInput}
              onChange={(e) => setRefinementInput(e.target.value)}
              placeholder="E.g. Make lighting warmer, remove background..."
              disabled={isRefining}
              className="w-full min-h-[60px] bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500 text-sm py-3 px-4 rounded-xl resize-none transition-all text-gray-900"
            />

            {/* Buttons Aligned to Right */}
            <div className="flex flex-col sm:flex-row gap-2 justify-end items-center">
              {onStartNew && (
                <Button
                  onClick={onStartNew}
                  variant="ghost"
                  className="text-gray-500 hover:text-blue-600 hover:bg-blue-50 text-xs font-medium px-4 h-9"
                >
                  <Plus className="w-3.5 h-3.5 mr-1.5" />
                  Start Over
                </Button>
              )}

              <Button
                onClick={handleRefine}
                disabled={isRefining || !refinementInput.trim()}
                className="bg-black hover:bg-gray-800 text-white h-9 px-6 rounded-lg text-xs font-bold shadow-md transition-transform active:scale-95 w-full sm:w-auto"
              >
                {isRefining ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> : <RefreshCw className="w-3.5 h-3.5 mr-1.5" />}
                Refine Prompt
              </Button>
            </div>
          </div>
        </div>
      </div>

    </motion.div>
  )
}