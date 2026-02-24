"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Copy, Download, Clock, FileText } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { ScrollArea } from "@/components/ui/scroll-area"
import { copyToClipboard } from "@/lib/utils"

interface PromptDetailModalProps {
  isOpen: boolean
  onClose: () => void
  prompt: {
    id: string
    prompt_text: string
    category: string
    created_at: string
    model_used?: string
    word_count?: number
  } | null
}

export function PromptDetailModal({ isOpen, onClose, prompt }: PromptDetailModalProps) {
  const { toast } = useToast()

  if (!prompt) return null

  const handleCopy = async () => {
    try {
      const success = await copyToClipboard(prompt.prompt_text)
      if (success) {
        toast({
          title: "Copied!",
          description: "Prompt copied to clipboard",
        })
      } else {
        throw new Error("Copy failed")
      }
    } catch (error) {
      toast({
        title: "Failed",
        description: "Could not copy to clipboard",
        variant: "destructive",
      })
    }
  }

  const handleDownload = () => {
    const blob = new Blob([prompt.prompt_text], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `prompt-${prompt.category.replace(/\s+/g, '-')}-${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "Downloaded!",
      description: "Prompt saved as text file",
    })
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="max-w-4xl h-[85vh] p-0 gap-0 flex flex-col overflow-hidden"
        showCloseButton={true}
      >
        {/* Header - Fixed */}
        <div className="p-6 pb-4 border-b border-gray-200 flex-shrink-0">
          <DialogHeader>
            <div className="space-y-3 pr-8">
              <DialogTitle className="text-2xl font-bold text-gray-900">
                Prompt Details
              </DialogTitle>

              {/* Metadata Badges */}
              <div className="flex flex-wrap gap-2">
                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full">
                  <FileText className="w-3.5 h-3.5" />
                  {prompt.category}
                </span>
                {prompt.model_used && (
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-purple-600 bg-purple-50 px-3 py-1.5 rounded-full">
                    {prompt.model_used}
                  </span>
                )}
                <span className="inline-flex items-center gap-1.5 text-xs text-gray-600 bg-gray-100 px-3 py-1.5 rounded-full">
                  {prompt.word_count || 0} words
                </span>
                <span className="inline-flex items-center gap-1.5 text-xs text-gray-600 bg-gray-100 px-3 py-1.5 rounded-full">
                  <Clock className="w-3.5 h-3.5" />
                  {formatDate(prompt.created_at)}
                </span>
              </div>
            </div>
          </DialogHeader>
        </div>

        {/* Content - Scrollable with proper height */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-none">
            <p className="text-gray-900 text-[15px] leading-[1.8] whitespace-pre-wrap">
              {prompt.prompt_text}
            </p>
          </div>
        </div>

        {/* Footer - Fixed */}
        <div className="p-6 pt-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between flex-shrink-0">
          <Button
            onClick={onClose}
            variant="outline"
            className="border-gray-300 hover:bg-white"
          >
            Close
          </Button>
          <div className="flex gap-2">
            {/* ✅ UPDATED: Changed Copy button to blue color */}
            <Button
              onClick={handleCopy}
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy
            </Button>
            <Button
              onClick={handleDownload}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
