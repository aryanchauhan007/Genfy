"use client"

import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  ImageIcon, 
  Sparkles, 
  Wand2, 
  Type, 
  ChevronRight,
  Settings2,
  ChevronDown,
  ChevronUp
} from "lucide-react"
import { useState, useEffect } from "react"
import { useSession } from "@/contexts/session-context"
import { VisualSettings } from "@/lib/api-client"

export function Sidebar() {
  const { saveVisualSettings, session } = useSession()
  const [settings, setSettings] = useState<VisualSettings>({
    aspectratio: "1:1",
    colorpalette: undefined,
    camerasettings: undefined,
    imagepurpose: undefined,
  })
  const [variations, setVariations] = useState([1])
  
  // Advanced options state
  const [contentType, setContentType] = useState("Photo")
  const [style, setStyle] = useState("None")
  const [visualIntensity, setVisualIntensity] = useState([50])
  const [colorAndTone, setColorAndTone] = useState("Auto")
  const [lighting, setLighting] = useState("Auto")
  const [composition, setComposition] = useState("Auto")
  const [advancedMode, setAdvancedMode] = useState(false)

  // Load session settings when available (FIXED WITH UNDERSCORES)
  useEffect(() => {
    if (session) {
      const sessionSettings: VisualSettings = {
        aspectratio: session.selected_aspect_ratio || "1:1",
        colorpalette: session.selected_color_palette,
        camerasettings: session.selected_camera_settings,
        imagepurpose: session.selected_image_purpose,
      }
      setSettings(sessionSettings)
    }
  }, [session])

  const handleAspectRatioChange = async (ratio: string) => {
    const newSettings = { ...settings, aspectratio: ratio }
    setSettings(newSettings)
    try {
      await saveVisualSettings(newSettings)
    } catch (error) {
      console.error('Failed to save aspect ratio:', error)
    }
  }

  const handleSaveAdvancedSettings = async () => {
    // Save all advanced settings to backend
    const advancedSettings = {
      ...settings,
      contenttype: contentType,
      style: style,
      visualintensity: visualIntensity[0],
      colorandtone: colorAndTone,
      lighting: lighting,
      composition: composition,
    }
    try {
      await saveVisualSettings(advancedSettings as any)
    } catch (error) {
      console.error('Failed to save advanced settings:', error)
    }
  }

  // Aspect Ratios
  const aspectRatios = [
    { value: "1:1", label: "1:1" },
    { value: "16:9", label: "16:9" },
    { value: "9:16", label: "9:16" },
    { value: "4:3", label: "4:3" },
  ]

  // Content Types
  const contentTypes = [
    "Photo", "Art", "Graphic", "Illustration", "Digital Art"
  ]

  // Styles
  const styles = [
    "None", "Vibrant", "Cinematic", "Vintage", "Minimalist",
    "Dramatic", "Soft Dreamy", "Bold Graphic", "Noir", "Pastel"
  ]

  // Color & Tone options
  const colorToneOptions = [
    "Auto", "Warm", "Cool", "Muted", "Vibrant", "Monochrome", "Black & White"
  ]

  // Lighting options
  const lightingOptions = [
    "Auto", "Golden Hour", "Studio", "Natural", "Dramatic", "Backlit", "Low Key", "High Key"
  ]

  // Composition options
  const compositionOptions = [
    "Auto", "Close-up", "Portrait", "Wide Shot", "Macro", "Aerial", "Eye Level"
  ]

  return (
    <aside className="w-80 border-l border-border bg-sidebar shadow-xl flex flex-col">
      <ScrollArea className="flex-1">
        <div className="space-y-6 p-6">
          {/* GENERATE Section */}
          <div className="space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              GENERATE
            </h3>
            <div className="space-y-1">
              <Button
                variant="secondary"
                className="w-full justify-between gap-2 bg-gradient-to-r from-primary/15 to-accent/15 text-primary shadow-sm shadow-primary/20 transition-all hover:scale-[1.02] hover:from-primary/20 hover:to-accent/20"
              >
                <span className="flex items-center gap-2">
                  <ImageIcon className="h-4 w-4" />
                  Text to Image
                </span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-between gap-2 text-muted-foreground hover:bg-accent hover:text-foreground"
              >
                <span className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Generative Fill
                </span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-between gap-2 text-muted-foreground hover:bg-accent hover:text-foreground"
              >
                <span className="flex items-center gap-2">
                  <Wand2 className="h-4 w-4" />
                  Generative Expand
                </span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-between gap-2 text-muted-foreground hover:bg-accent hover:text-foreground"
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

          {/* Aspect Ratio */}
          <div>
            <div className="text-sm font-medium mb-3">Aspect Ratio</div>
            <div className="grid grid-cols-4 gap-2">
              {aspectRatios.map((ratio) => (
                <Button
                  key={ratio.value}
                  variant="outline"
                  size="sm"
                  onClick={() => handleAspectRatioChange(ratio.value)}
                  className={`h-10 transition-all ${
                    settings.aspectratio === ratio.value
                      ? "bg-primary text-primary-foreground shadow-md border-primary"
                      : "hover:border-primary/50"
                  }`}
                >
                  {ratio.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Content Type */}
          <div>
            <div className="text-sm font-medium mb-3">Content Type</div>
            <Select value={contentType} onValueChange={(val) => {
              setContentType(val)
              handleSaveAdvancedSettings()
            }}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {contentTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Style */}
          <div>
            <div className="text-sm font-medium mb-3">Style</div>
            <Select value={style} onValueChange={(val) => {
              setStyle(val)
              handleSaveAdvancedSettings()
            }}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {styles.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Variations */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm font-medium">Variations</div>
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

          {/* Advanced Options Toggle */}
          <Button
            variant="outline"
            onClick={() => setAdvancedMode(!advancedMode)}
            className="w-full justify-between"
          >
            <div className="flex items-center gap-2">
              <Settings2 className="h-4 w-4" />
              <span className="text-sm font-medium">Advanced Options</span>
            </div>
            {advancedMode ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>

          {/* Advanced Options (Conditional) */}
          {advancedMode && (
            <div className="space-y-5 p-4 rounded-lg border border-primary/20 bg-primary/5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-primary">
                Advanced Settings
              </h4>

              {/* Visual Intensity */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="text-sm font-medium">Visual Intensity</div>
                  <span className="text-sm text-muted-foreground">{visualIntensity[0]}%</span>
                </div>
                <Slider
                  value={visualIntensity}
                  onValueChange={setVisualIntensity}
                  max={100}
                  min={0}
                  step={5}
                  className="w-full"
                />
              </div>

              {/* Color & Tone */}
              <div>
                <div className="text-sm font-medium mb-3">Color & Tone</div>
                <Select value={colorAndTone} onValueChange={setColorAndTone}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {colorToneOptions.map((option) => (
                      <SelectItem key={option} value={option}>
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Lighting */}
              <div>
                <div className="text-sm font-medium mb-3">Lighting</div>
                <Select value={lighting} onValueChange={setLighting}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {lightingOptions.map((option) => (
                      <SelectItem key={option} value={option}>
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Composition */}
              <div>
                <div className="text-sm font-medium mb-3">Composition</div>
                <Select value={composition} onValueChange={setComposition}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {compositionOptions.map((option) => (
                      <SelectItem key={option} value={option}>
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          <Separator className="bg-border" />

          {/* Session Info - FIXED WITH UNDERSCORES */}
          {session && (
            <div className="rounded-lg border border-border bg-card/50 p-3">
              <div className="mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Session Info
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Step:</span>
                  <span className="font-medium text-foreground">{session.current_step}</span>
                </div>
                {session.selected_category && (
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Category:</span>
                    <span className="font-medium text-foreground truncate ml-2">
                      {session.selected_category}
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">LLM:</span>
                  <span className="font-medium text-foreground">{session.selected_llm}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
    </aside>
  )
}
