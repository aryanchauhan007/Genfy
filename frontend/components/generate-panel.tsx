"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select"
import {
  ImageIcon,
  Loader2,
  MessageSquare,
  Zap,
  AlertCircle,
  Wand2,
  Layers,
  Sparkles,
  FolderOpen,
  X
} from "lucide-react"
import { useSession } from "@/contexts/session-context"
import { useToast } from "@/hooks/use-toast"
import { motion, AnimatePresence } from "framer-motion"
import { apiClient } from "@/lib/api-client"
import { VisualSettingsModal } from "@/components/ui/visual-settings-modal"

// ----------------------------------------------------------------------
// 📷 YOUR CUSTOM IMAGES
// ----------------------------------------------------------------------
const HERO_IMAGES = [
  {
    id: 1,
    src: "/Sinchan.png",
    color: ""
  },
  {
    id: 2,
    src: "/Stitch.png",
    color: ""
  },
  {
    id: 3,
    src: "/Mountains.png",
    color: ""
  },
  {
    id: 4,
    src: "/Boy.png",
    color: ""
  },
]
// ----------------------------------------------------------------------

// --- POP-IN & ROTATE ANIMATION ---
function HeroImagePopRotate() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % HERO_IMAGES.length)
    }, 3000)
    return () => clearInterval(timer)
  }, [])

  const currentImage = HERO_IMAGES[index]

  return (
    <div className="relative w-20 h-20 mb-3"> {/* Slightly smaller container */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentImage.id}
          initial={{ opacity: 0, scale: 0.5, rotate: -20 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          exit={{ opacity: 0, scale: 0.5, rotate: 20 }}
          transition={{ duration: 0.5, type: "spring", stiffness: 260, damping: 20 }}
          className="absolute inset-0 rounded-2xl overflow-hidden shadow-lg border-[3px] border-white bg-white"
        >
          <div className={`absolute inset-0 opacity-10 ${currentImage.color}`} />

          {/* ✅ Image Fix: object-contain + padding */}
          <img
            src={currentImage.src}
            alt="Creative Preview"
            className="w-full h-full object-contain p-1"
          />
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

interface GeneratePanelProps {
  onPromptGenerated?: (prompt: string) => void
  onAdvancedMode?: () => void
}

export function GeneratePanel({ onPromptGenerated, onAdvancedMode }: GeneratePanelProps) {
  const [prompt, setPrompt] = useState("")
  const [mode, setMode] = useState<'quick' | 'advanced'>('quick')
  const [isFocused, setIsFocused] = useState(false)

  // Settings state
  const [aspectRatio, setAspectRatio] = useState(" Instagram Square (1:1)")
  const [colorPalette, setColorPalette] = useState(" Natural Sunlight/Golden Hour")
  const [cameraSettings, setCameraSettings] = useState(" Standard (50mm)")
  const [imagePurpose, setImagePurpose] = useState(" Social Media Post")
  const [model, setModel] = useState("Claude")
  const [hasAppliedSettings, setHasAppliedSettings] = useState(false)
  const [availableModels, setAvailableModels] = useState<string[]>([])

  //  FILE UPLOAD STATE
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string, url: string }>>([])
  const [isUploading, setIsUploading] = useState(false)

  const {
    generateQuickPrompt,
    isLoading,
    error,
    clearError,
    initializeSession,
    sessionId,
    session,
    selectCategory,
    startChat,
    activeProject,
    clearProject,
  } = useSession()
  const { toast } = useToast()

  useEffect(() => {
    if (!sessionId) initializeSession()
  }, [sessionId, initializeSession])

  useEffect(() => {
    const loadLLMs = async () => {
      try {
        const response = await apiClient.getAvailableLLMs()
        setAvailableModels(response.llms || ["Claude", "Mistral"])
      } catch (error) {
        setAvailableModels(["Claude", "Mistral"])
      }
    }
    loadLLMs()
  }, [])

  useEffect(() => {
    if (session) {
      if (session.selected_llm) setModel(session.selected_llm)

      if (session.selected_aspect_ratio ||
        session.selected_color_palette ||
        session.selected_camera_settings ||
        session.selected_image_purpose) {
        setHasAppliedSettings(true)
        if (session.selected_aspect_ratio) setAspectRatio(session.selected_aspect_ratio)
        if (session.selected_color_palette) setColorPalette(session.selected_color_palette)
        if (session.selected_camera_settings) setCameraSettings(session.selected_camera_settings)
        if (session.selected_image_purpose) setImagePurpose(session.selected_image_purpose)
      }

      // Load existing files if any
      if (session.uploaded_files) {
        setUploadedFiles(session.uploaded_files.map((f: any) => ({ name: f.name, url: f.url })))
      }
    }
  }, [session])

  useEffect(() => {
    if (error) {
      toast({ title: "Error", description: error, variant: "destructive" })
      clearError()
    }
  }, [error, toast, clearError])

  const handleAspectRatioChange = (value: string) => setAspectRatio(value)
  const handleColorPaletteChange = (value: string) => setColorPalette(value)
  const handleCameraSettingsChange = (value: string) => setCameraSettings(value)
  const handleImagePurposeChange = (value: string) => setImagePurpose(value)

  const handleApplySettings = async () => {
    try {
      if (sessionId) {
        await apiClient.saveVisualSettings(sessionId, {
          aspect_ratio: aspectRatio,
          color_palette: colorPalette,
          camera_settings: cameraSettings,
          image_purpose: imagePurpose,
        })
        setHasAppliedSettings(true)
        toast({ title: "Settings Applied ✓", description: "Visual settings will be used in generation" })
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to apply settings", variant: "destructive" })
    }
  }

  const handleClearSettings = async () => {
    try {
      if (sessionId) {
        await apiClient.saveVisualSettings(sessionId, {
          aspect_ratio: undefined,
          color_palette: undefined,
          camera_settings: undefined,
          image_purpose: undefined,
        })
        setHasAppliedSettings(false)
        setAspectRatio(" Instagram Square (1:1)")
        setColorPalette(" Natural Sunlight/Golden Hour")
        setCameraSettings(" Standard (50mm)")
        setImagePurpose(" Social Media Post")
        toast({ title: "Settings Cleared", description: "Visual settings removed" })
      }
    } catch (error) {
      console.error('Failed to clear settings:', error)
    }
  }

  const handleModelChange = async (value: string) => {
    setModel(value)
    if (sessionId) {
      await apiClient.setLLM(sessionId, value)
      toast({ title: "Model Updated", description: `Switched to ${value}` })
    }
  }

  //  NEW: Handle clearing project context
  const handleClearProject = async () => {
    try {
      if (sessionId) {
        // await apiClient.deactivateProjectContext(sessionId) // Only if this method exists
      }
      clearProject()
      toast({
        title: "Project Cleared",
        description: "Brand context removed from generation"
      })
    } catch (error) {
      console.error("Failed to clear project:", error)
      toast({
        title: "Error",
        description: "Failed to clear project context",
        variant: "destructive"
      })
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !sessionId) return

    setIsUploading(true)
    try {
      const data = await apiClient.uploadFile(sessionId, file)

      if (data.success) {
        setUploadedFiles(prev => [...prev, { name: file.name, url: data.url }])
        toast({
          title: "File Uploaded ✓",
          description: data.vision_analysis ? "Image analyzed for context" : `${file.name} uploaded`,
        })
      }
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: "Failed to upload file",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
      e.target.value = ""
    }
  }

  const handleRemoveFile = async (index: number) => {
    if (!sessionId) return
    try {
      await apiClient.deleteSessionFile(sessionId, index)
      setUploadedFiles(prev => prev.filter((_, i) => i !== index))
      toast({
        title: "File Removed",
        description: "Reference file removed from generation"
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to remove file",
        variant: "destructive"
      })
    }
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast({ title: "Empty Input", description: "Please describe what you want to create", variant: "destructive" })
      return
    }
    if (!session?.selected_category) {
      toast({ title: "No Category Selected", description: "Please select a category first", variant: "destructive" })
      return
    }

    try {
      await selectCategory(session.selected_category, prompt)

      if (sessionId) {
        if (hasAppliedSettings) {
          await apiClient.saveVisualSettings(sessionId, {
            aspect_ratio: aspectRatio,
            color_palette: colorPalette,
            camera_settings: cameraSettings,
            image_purpose: imagePurpose,
          })
        } else {
          await apiClient.saveVisualSettings(sessionId, {
            aspect_ratio: undefined,
            color_palette: undefined,
            camera_settings: undefined,
            image_purpose: undefined,
          })
        }
      }

      if (mode === 'quick') {
        const finalPrompt = await generateQuickPrompt()
        toast({
          title: "Prompt Generated! ✨",
          description: hasAppliedSettings ? "Generated with visual settings applied" : "Generated with AI defaults"
        })
        if (onPromptGenerated) onPromptGenerated(finalPrompt)
      } else {
        if (sessionId && session?.selected_category) {
          await startChat(
            session.selected_category,
            prompt,
            hasAppliedSettings ? {
              aspect_ratio: aspectRatio,
              color_palette: colorPalette,
              camera_settings: cameraSettings,
              image_purpose: imagePurpose,
            } : undefined
          )
          toast({ title: "Chat Started! 💬", description: "Let's build your prompt together" })
        }
        if (onAdvancedMode) onAdvancedMode()
      }
    } catch (err) {
      toast({ title: "Generation Failed", description: err instanceof Error ? err.message : "Failed to generate prompt.", variant: "destructive" })
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleGenerate()
    }
  }

  // Options arrays (Shortened for cleaner code)
  const aspectRatioOptions = [{ value: " Instagram Square (1:1)", label: "Square (1:1)" }, { value: " Instagram Feed (4:5)", label: "Portrait (4:5)" }, { value: " YouTube Thumbnail (16:9)", label: "Landscape (16:9)" }]
  const colorPaletteOptions = [{ value: " Natural Sunlight/Golden Hour", label: "Golden Hour" }, { value: " Bright Studio Lighting", label: "Studio Light" }, { value: " Neon/Vibrant Colors", label: "Neon" }]
  const cameraSettingsOptions = [{ value: " Standard (50mm)", label: "Standard" }, { value: " Wide Angle (24mm)", label: "Wide Angle" }, { value: " Cinematic (35mm)", label: "Cinematic" }]
  const imagePurposeOptions = [{ value: " Social Media Post", label: "Social Media" }, { value: " Website Hero Image", label: "Website" }, { value: " Product Photography", label: "Product" }]

  return (
    // ✅ ALIGNMENT FIX: Changed max-w-6xl to max-w-3xl for a compact look
    <div className="flex flex-col items-center w-full max-w-3xl mx-auto space-y-6 px-4 py-8">

      {/* ============================================================================ */}
      {/*  PROJECT CONTEXT BADGE */}
      {/* ============================================================================ */}
      <AnimatePresence>
        {activeProject && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="w-full bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl p-4 flex justify-between items-start shadow-lg"
          >
            <div className="flex items-start gap-3 flex-1 min-w-0">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-2.5 flex-shrink-0 shadow-md">
                <FolderOpen className="h-5 w-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-blue-900 mb-1 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-blue-600" />
                  Using Project: {activeProject.name}
                </div>
                {activeProject.instructions && (
                  <p className="text-sm text-blue-700 line-clamp-2 mb-2">
                    {activeProject.instructions}
                  </p>
                )}
                <div className="flex items-center gap-3 text-xs text-blue-600">
                  <span className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                    {activeProject.files?.length || 0} reference file(s)
                  </span>
                  <span className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                    Brand guidelines active
                  </span>
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearProject}
              className="hover:bg-blue-100 flex-shrink-0 ml-2 text-blue-600 hover:text-blue-800"
              title="Clear project context"
            >
              <X className="h-4 w-4" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
      {/* ============================================================================ */}
      {/* END OF PROJECT CONTEXT BADGE */}
      {/* ============================================================================ */}

      {/* Hero Icon & Title */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-2 flex flex-col items-center"
      >
        <HeroImagePopRotate />

        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 leading-tight">
          Start creating with Genfy
        </h1>

        <p className="text-gray-500 text-sm max-w-md mx-auto">
          Describe what you want to see and we'll generate it for you
        </p>
      </motion.div>

      {/* Mode Toggle */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="bg-white p-1 rounded-full inline-flex relative border border-gray-200 shadow-sm"
      >
        <motion.div
          layout
          className="absolute inset-y-1 bg-gray-900 rounded-full shadow-md"
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          style={{
            left: mode === 'quick' ? '4px' : '50%',
            right: mode === 'quick' ? '50%' : '4px'
          }}
        />

        <button onClick={() => setMode('quick')} className={`relative z-10 px-5 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-2 ${mode === 'quick' ? 'text-white' : 'text-gray-500 hover:text-gray-900'}`} disabled={isLoading}>
          <Zap className="w-3.5 h-3.5" /> Quick Generate
        </button>
        <button onClick={() => setMode('advanced')} className={`relative z-10 px-5 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-2 ${mode === 'advanced' ? 'text-white' : 'text-gray-500 hover:text-gray-900'}`} disabled={isLoading}>
          <MessageSquare className="w-3.5 h-3.5" /> Advanced Q&A
        </button>
      </motion.div>

      {/* Main Input Box - "SHORT BAR" STYLE */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="w-full relative group"
      >
        <div className={`absolute -inset-[1px] bg-gradient-to-r from-blue-300 via-purple-300 to-pink-300 rounded-3xl transition-all duration-500 ${isFocused ? 'opacity-100 blur-sm' : 'opacity-30 blur group-hover:opacity-60'}`}></div>

        <div className={`relative bg-white rounded-3xl border transition-all duration-300 ${isFocused ? 'border-blue-200 shadow-xl shadow-blue-100' : 'border-gray-200 shadow-lg'}`}>

          {/* ✅ SHORT BAR: Reduced height from h-32 to h-14, padding reduced */}
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={isLoading}
            placeholder={session?.selected_category
              ? `Describe your ${session.selected_category}...`
              : "Describe what you want to create... (e.g., A futuristic cityscape at sunset)"
            }
            className="w-full bg-transparent border-none text-gray-900 placeholder:text-gray-400 px-5 py-4 text-base resize-none outline-none h-16 scrollbar-hide selection:bg-blue-100 selection:text-blue-900"
          />

          {/* ✅ COMPACT TOOLBAR: Reduced padding and spacing */}
          <div className="bg-gray-50/80 border-t border-gray-100 rounded-b-3xl px-4 py-2">

            <div className="flex flex-wrap items-center gap-3 mb-2 pt-1">
              <input
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                id="reference-upload"
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.svg"
                disabled={isUploading}
              />
              <label htmlFor="reference-upload" className="cursor-pointer">
                <div className={`flex items-center justify-center h-8 px-3 bg-white border border-gray-200 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-50 transition-colors shadow-sm ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`} title="Upload">
                  {isUploading ? <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" /> : <ImageIcon className="w-3.5 h-3.5 mr-2" />}
                  <span className="text-xs">{isUploading ? 'Uploading...' : 'Upload'}</span>
                </div>
              </label>

              {/* Show uploaded files */}
              {uploadedFiles.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {uploadedFiles.map((file, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-1.5 bg-blue-50 border border-blue-200 rounded-lg px-2 py-1 group hover:bg-blue-100 transition-colors"
                    >
                      <ImageIcon className="w-3 h-3 text-blue-600" />
                      <span className="text-xs text-blue-700 max-w-[100px] truncate">
                        {file.name}
                      </span>
                      <button
                        onClick={() => handleRemoveFile(idx)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-3 h-3 text-blue-600 hover:text-blue-800" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <Select value={model} onValueChange={handleModelChange}>
                <SelectTrigger className="w-[120px] h-8 bg-white border-gray-200 hover:bg-gray-50 text-gray-700 hover:text-gray-900 text-xs shadow-sm">
                  <div className="flex items-center gap-2">
                    <Layers className="w-3.5 h-3.5 text-gray-400 group-hover:text-gray-600" />
                    <span>{model}</span>
                  </div>
                </SelectTrigger>
                <SelectContent className="bg-white border-gray-200">
                  {availableModels.map((llm) => <SelectItem key={llm} value={llm} className="text-xs text-gray-700 hover:text-black hover:bg-gray-50 cursor-pointer">{llm}</SelectItem>)}
                </SelectContent>
              </Select>

              <VisualSettingsModal
                aspectRatio={aspectRatio} colorPalette={colorPalette} cameraSettings={cameraSettings} imagePurpose={imagePurpose}
                onAspectRatioChange={handleAspectRatioChange} onColorPaletteChange={handleColorPaletteChange} onCameraSettingsChange={handleCameraSettingsChange} onImagePurposeChange={handleImagePurposeChange}
                onApply={handleApplySettings} onClear={handleClearSettings} hasSettings={hasAppliedSettings}
                aspectRatioOptions={aspectRatioOptions} colorPaletteOptions={colorPaletteOptions} cameraSettingsOptions={cameraSettingsOptions} imagePurposeOptions={imagePurposeOptions}
              />
            </div>

            <div className="flex items-center justify-between pt-1 pb-1 border-t border-gray-200/50 mt-1">
              <span className={`text-[10px] font-mono transition-colors ${prompt.length > 900 ? "text-red-500 font-bold" : "text-gray-400"}`}>
                {prompt.length} / 1000
              </span>

              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={handleGenerate}
                  disabled={isLoading || !prompt.trim() || !session?.selected_category}
                  className="bg-black hover:bg-gray-800 text-white rounded-lg px-6 h-8 font-semibold shadow-sm disabled:opacity-50 transition-all flex items-center gap-2 text-xs"
                >
                  {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                  {isLoading ? "Generating..." : mode === 'quick' ? "Generate" : "Start"}
                </Button>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.div>

      <AnimatePresence>
        {!session?.selected_category && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="flex items-center gap-2 text-amber-600 bg-amber-50 px-3 py-1 rounded-full border border-amber-200 text-[10px] font-medium"
          >
            <AlertCircle className="w-3 h-3" />
            Please select a category above
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}