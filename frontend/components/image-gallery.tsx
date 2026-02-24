"use client"

import { Download, Heart, Sparkles, Maximize2, Share2, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react"
import { apiClient, PromptHistory } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { copyToClipboard } from "@/lib/utils"

export function ImageGallery() {
  const [favorites, setFavorites] = useState<number[]>([])
  const [history, setHistory] = useState<PromptHistory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  // Load history on mount
  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setIsLoading(true)
    try {
      const response = await apiClient.getHistory(4) // Get 4 most recent
      if (response.success) {
        // Filter only items with generated images
        const withImages = response.history.filter(item => item.generated_image_url)
        setHistory(withImages)
      }
    } catch (error) {
      console.error('Failed to load history:', error)
      toast({
        title: "Error",
        description: "Failed to load image history",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const toggleFavorite = (id: number) => {
    setFavorites((prev) => (prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]))
  }

  const handleDownload = async (imageUrl: string, id: number) => {
    try {
      const response = await fetch(imageUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Genfy-image-${id}.jpg`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      toast({
        title: "Downloaded",
        description: "Image saved successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download image",
        variant: "destructive",
      })
    }
  }

  const handleShare = async (prompt: string) => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: 'Genfy Generated Image',
          text: prompt,
        })
      } else {
        const success = await copyToClipboard(prompt)
        if (success) {
          toast({
            title: "Copied",
            description: "Prompt copied to clipboard",
          })
        } else {
          toast({
            title: "Copy Failed",
            description: "Failed to copy prompt",
            variant: "destructive",
          })
        }
      }
    } catch (error) {
      console.error('Share failed:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center overflow-auto">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading your creations...</p>
        </div>
      </div>
    )
  }

  // ✅ Only show gallery if there are images, otherwise return null (nothing)
  if (history.length === 0) {
    return null
  }

  return (
    <div className="flex flex-1 items-center justify-center overflow-auto">
      <div className="grid grid-cols-2 gap-6 p-6">
        {history.map((item) => (
          <div
            key={item.id}
            className="group relative overflow-hidden rounded-2xl border border-border bg-card shadow-lg transition-all duration-300 hover:scale-[1.02] hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/20"
          >
            <img
              src={item.generated_image_url || "/placeholder.svg"}
              alt={item.user_idea}
              className="aspect-square w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <div className="absolute inset-0 flex items-center justify-center gap-3 bg-gradient-to-t from-background/95 via-background/80 to-background/50 opacity-0 backdrop-blur-md transition-all duration-300 group-hover:opacity-100">
              <Button
                size="icon"
                variant="secondary"
                onClick={() => item.generated_image_url && handleDownload(item.generated_image_url, item.id)}
                className="h-11 w-11 rounded-full bg-card/80 text-foreground shadow-lg backdrop-blur-sm transition-all hover:scale-110 hover:bg-card"
              >
                <Download className="h-5 w-5" />
              </Button>
              <Button
                size="icon"
                variant="secondary"
                onClick={() => toggleFavorite(item.id)}
                className={`h-11 w-11 rounded-full shadow-lg backdrop-blur-sm transition-all hover:scale-110 ${favorites.includes(item.id)
                  ? "bg-destructive text-white hover:bg-destructive/90"
                  : "bg-card/80 text-foreground hover:bg-card"
                  }`}
              >
                <Heart className={`h-5 w-5 ${favorites.includes(item.id) ? "fill-current" : ""}`} />
              </Button>
              <Button
                size="icon"
                variant="secondary"
                onClick={() => handleShare(item.final_prompt)}
                className="h-11 w-11 rounded-full bg-card/80 text-foreground shadow-lg backdrop-blur-sm transition-all hover:scale-110 hover:bg-card"
              >
                <Share2 className="h-5 w-5" />
              </Button>
              <Button
                size="icon"
                variant="secondary"
                className="h-11 w-11 rounded-full bg-card/80 text-foreground shadow-lg backdrop-blur-sm transition-all hover:scale-110 hover:bg-card"
              >
                <Maximize2 className="h-5 w-5" />
              </Button>
            </div>
            <div className="absolute left-3 top-3 rounded-full bg-background/80 px-3 py-1 text-xs font-medium text-foreground backdrop-blur-sm">
              {item.category}
            </div>
            <div className="absolute bottom-3 left-3 right-3 rounded-lg bg-background/80 p-2 text-xs text-foreground backdrop-blur-sm opacity-0 transition-opacity group-hover:opacity-100">
              <p className="truncate">{item.user_idea}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
