"use client"

import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ImageIcon, Sparkles, Wand2, Type, ChevronRight } from "lucide-react"
import { useState, useEffect } from "react"
import { useSession } from "@/contexts/session-context"
import { VisualSettings } from "@/lib/api-client"

export function Sidebar() {
  const { saveVisualSettings, session } = useSession()
  const [settings, setSettings] = useState<VisualSettings>({
    aspect_ratio: "16:9",
    color_palette: undefined,
    camera_settings: undefined,
    image_purpose: undefined,
  })
  const [variations, setVariations] = useState([4])

  // Load session settings when available
  useEffect(() => {
    if (session) {
      // Settings would be in session.visual_settings if available
    }
  }, [session])

  const handleAspectRatioChange = async (ratio: string) => {
    const newSettings = { ...settings, aspect_ratio: ratio }
    setSettings(newSettings)
    try {
      await saveVisualSettings(newSettings)
    } catch (error) {
      console.error('Failed to save aspect ratio:', error)
    }
  }

  const handleContentTypeChange = async (value: string) => {
    const newSettings = { ...settings, image_purpose: value }
    setSettings(newSettings)
    try {
      await saveVisualSettings(newSettings)
    } catch (error) {
      console.error('Failed to save content type:', error)
    }
  }

  const handleStyleChange = async (value: string) => {
    const newSettings = { ...settings, color_palette: value }
    setSettings(newSettings)
    try {
      await saveVisualSettings(newSettings)
    } catch (error) {
      console.error('Failed to save style:', error)
    }
  }

  const aspectRatios = [
    { value: "1:1", label: "1:1" },
    { value: "16:9", label: "16:9" },
    { value: "9:16", label: "9:16" },
    { value: "4:3", label: "4:3" },
  ]

  return (
    <aside className="w-80 border-l border-border bg-sidebar shadow-xl">
      <ScrollArea className="h-full">
        <div className="space-y-6 p-6">
          <div className="space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Generate</h3>
            <div className="space-y-1">
              <Button
                variant="secondary"
                className="w-full justify-between gap-2 bg-gradient-to-r from-primary/15 to-accent/15 text-primary shadow-sm shadow-primary/20 transition-all hover:scale-[1.02] hover:from-primary/20 hover:to-accent/20 hover:shadow-md hover:shadow-primary/30"
              >
                <span className="flex items-center gap-2">
                  <ImageIcon className="h-4 w-4" />
                  Text to Image
                </span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-between gap-2 text-muted-foreground transition-all hover:scale-[1.02] hover:bg-accent hover:text-foreground"
              >
                <span className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Generative Fill
                </span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-between gap-2 text-muted-foreground transition-all hover:scale-[1.02] hover:bg-accent hover:text-foreground"
              >
                <span className="flex items-center gap-2">
                  <Wand2 className="h-4 w-4" />
                  Generative Expand
                </span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-between gap-2 text-muted-foreground transition-all hover:scale-[1.02] hover:bg-accent hover:text-foreground"
              >
                <span className="flex items-center gap-2">
                  <Type className="h-4 w-4" />
                  Text Effects
                </span>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <Separator className="bg-border" />

          <div className="space-y-4">
            <div>
              <label className="mb-3 block text-sm font-medium text-foreground">Aspect Ratio</label>
              <div className="grid grid-cols-4 gap-2">
                {aspectRatios.map((ratio) => (
                  <Button
                    key={ratio.value}
                    variant="outline"
                    size="sm"
                    onClick={() => handleAspectRatioChange(ratio.value)}
                    className={`h-10 transition-all hover:scale-105 hover:shadow-md ${
                      settings.aspect_ratio === ratio.value
                        ? "bg-primary text-primary-foreground shadow-md shadow-primary/30 hover:bg-primary/90 hover:shadow-lg hover:shadow-primary/40"
                        : "bg-input text-foreground hover:bg-accent"
                    }`}
                  >
                    {ratio.label}
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-3 block text-sm font-medium text-foreground">Content Type</label>
              <Select 
                defaultValue="photo" 
                onValueChange={handleContentTypeChange}
              >
                <SelectTrigger className="w-full bg-input transition-all hover:bg-accent">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="photo">Photo</SelectItem>
                  <SelectItem value="art">Art</SelectItem>
                  <SelectItem value="graphic">Graphic</SelectItem>
                  <SelectItem value="illustration">Illustration</SelectItem>
                  <SelectItem value="digital-art">Digital Art</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="mb-3 block text-sm font-medium text-foreground">Style</label>
              <Select 
                defaultValue="none"
                onValueChange={handleStyleChange}
              >
                <SelectTrigger className="w-full bg-input transition-all hover:bg-accent">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  <SelectItem value="vibrant">Vibrant</SelectItem>
                  <SelectItem value="cinematic">Cinematic</SelectItem>
                  <SelectItem value="vintage">Vintage</SelectItem>
                  <SelectItem value="minimalist">Minimalist</SelectItem>
                  <SelectItem value="dramatic">Dramatic</SelectItem>
                  <SelectItem value="soft">Soft & Dreamy</SelectItem>
                  <SelectItem value="bold">Bold & Graphic</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <div className="mb-3 flex items-center justify-between">
                <label className="text-sm font-medium text-foreground">Variations</label>
                <span className="rounded-full bg-primary/20 px-2.5 py-0.5 text-sm font-medium text-primary">
                  {variations[0]}
                </span>
              </div>
              <Slider 
                value={variations} 
                onValueChange={setVariations}
                max={4} 
                min={1} 
                step={1} 
                className="w-full" 
              />
            </div>

            {session && (
              <div className="rounded-lg border border-border bg-card/50 p-3">
                <div className="text-xs font-medium text-muted-foreground mb-1">Session Info</div>
                <div className="text-xs text-foreground space-y-1">
                  <div>Step: <span className="font-medium">{session.current_step}</span></div>
                  {session.selected_category && (
                    <div>Category: <span className="font-medium">{session.selected_category}</span></div>
                  )}
                  <div>LLM: <span className="font-medium">{session.selected_llm}</span></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </ScrollArea>
    </aside>
  )
}
