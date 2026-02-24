"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { LandingPage } from "@/components/landing-page"
import { CategorySelector } from "@/components/ui/category-selector"
import { GeneratePanel } from "@/components/generate-panel"
import { ChatInterface } from "@/components/ui/chat-interface"
import { ImageGallery } from "@/components/image-gallery"
import { Sidebar } from "@/components/sidebar"
import { PromptDisplay } from "@/components/ui/prompt-display"
import { HistorySidebar } from "@/components/history-sidebar" // ✅ ADD THIS
import { Button } from "@/components/ui/button"
import { ArrowLeft, Loader2 } from "lucide-react"
import { useSession } from "@/contexts/session-context"
import { apiClient } from "@/lib/api-client"

type Step = "landing" | "category" | "generate" | "chat" | "final"

export default function Home() {
  const { session, sessionId, initializeSession, selectCategory, isLoading } = useSession()
  const [currentStep, setCurrentStep] = useState<Step>("landing")
  const [isInitializing, setIsInitializing] = useState(false)

  const handleCategorySelect = async (categoryName: string) => {
    console.log("🎯 Category selected from landing:", categoryName)
    setIsInitializing(true)

    try {
      if (!sessionId) {
        console.log("📝 Creating new session...")
        await initializeSession()
        await new Promise(resolve => setTimeout(resolve, 500))
      }

      console.log("📁 Saving category:", categoryName)
      const placeholderIdea = `Create a ${categoryName.toLowerCase()} style image`
      await selectCategory(categoryName, placeholderIdea)

      console.log("✅ Category saved, moving to generate")
      setCurrentStep("generate")
    } catch (error) {
      console.error("❌ Failed to select category:", error)
    } finally {
      setIsInitializing(false)
    }
  }

  const handleCategoryComplete = () => {
    console.log("✅ Category complete")
    setCurrentStep("generate")
  }

  const handlePromptGenerated = (prompt: string) => {
    console.log("✅ Prompt generated")
    setCurrentStep("final")
  }

  const handleAdvancedMode = () => {
    console.log("💬 Advanced mode")
    setCurrentStep("chat")
  }

  const handleChatComplete = () => {
    console.log("✅ Chat complete")
    setCurrentStep("final")
  }

  const handleStartNew = async () => {
    console.log("🔄 Starting new")

    if (sessionId) {
      try {
        await apiClient.saveVisualSettings(sessionId, {
          aspect_ratio: undefined,
          color_palette: undefined,
          camera_settings: undefined,
          image_purpose: undefined,
        })
        console.log("✅ Visual settings cleared")
      } catch (error) {
        console.error("Failed to clear settings:", error)
      }
    }

    setCurrentStep("landing")
  }

  // Landing Page
  if (currentStep === "landing") {
    return (
      <div className="flex h-screen flex-col bg-gray-50">
        {/* Header removed to avoid duplication with LandingPage nav */}
        {isInitializing ? (
          <div className="flex flex-1 items-center justify-center bg-gray-50">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              <p className="text-sm text-gray-600">Setting up your workspace...</p>
            </div>
          </div>
        ) : (
          <LandingPage onCategorySelect={handleCategorySelect} />
        )}
      </div>
    )
  }

  // Main App
  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* ✅ HISTORY SIDEBAR - Shows on final step */}
        {currentStep === "final" && (
          <div className="flex-shrink-0">
            <HistorySidebar />
          </div>
        )}

        <main className="flex flex-1 flex-col overflow-hidden">
          <div className="flex flex-1 overflow-hidden bg-gray-50">
            <div className="flex-1 overflow-y-auto">
              <div className="p-8">
                <div className="w-full max-w-7xl mx-auto">
                  {/* Step 1: Category Selection */}
                  {currentStep === "category" && (
                    <CategorySelector onComplete={handleCategoryComplete} />
                  )}

                  {/* Step 2: Generate Mode */}
                  {currentStep === "generate" && (
                    <div className="space-y-6">
                      <ImageGallery />
                      <GeneratePanel
                        onPromptGenerated={handlePromptGenerated}
                        onAdvancedMode={handleAdvancedMode}
                      />
                    </div>
                  )}

                  {/* Step 2b: Advanced Chat Mode */}
                  {currentStep === "chat" && (
                    <div className="h-[calc(100vh-12rem)]">
                      <ChatInterface onComplete={handleChatComplete} />
                    </div>
                  )}

                  {/* Step 3: Final Prompt Display */}
                  {currentStep === "final" && (
                    <div className="space-y-6">
                      {session?.final_prompt ? (
                        <>
                          <PromptDisplay onStartNew={handleStartNew} />
                          <ImageGallery />
                        </>
                      ) : (
                        <div className="flex items-center justify-center h-96">
                          <div className="text-center space-y-4">
                            <p className="text-gray-600">No prompt generated yet</p>
                            <Button
                              onClick={() => setCurrentStep("generate")}
                              className="bg-black hover:bg-gray-800 text-white"
                            >
                              Go Back to Generate
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
