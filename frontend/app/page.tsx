"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { LandingPage } from "@/components/landing-page"
import { useSession } from "@/contexts/session-context"
import { useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"

export default function Home() {
  const { initializeSession, selectCategory, sessionId } = useSession()
  const [isInitializing, setIsInitializing] = useState(false)
  const router = useRouter()

  const handleCategorySelect = async (categoryName: string) => {
    console.log("🎯 Category selected:", categoryName)
    setIsInitializing(true)

    try {
      // 1. Ensure we have a session
      let activeSessionId = sessionId
      if (!activeSessionId) {
        console.log("📝 Creating new session...")
        // We need a way to get the ID synchronously or wait for it.
        // Since initializeSession updates state asynchronously, we might duplicate the creation logic here 
        // OR rely on context to handle it.
        // Actually selectCategory in context handles creation if missing!
        // But we need the ID for routing.

        // Let's rely on selectCategory to do the heavy lifting, 
        // but we need the ID to redirect.
        // Providing a callback or returning ID from selectCategory would be ideal.
        // But strictly, selectCategory is void.

        // Let's manually initialize here to get the ID if needed.
        // But initializeSession is void too in context...
        // Wait, context implementation:
        // initializeSession calls apiClient.createSession -> response.session_id
        // But it *doesn't return* it.

        // Workaround: We'll modify selectCategory to return the ID or we'll trust state update?
        // State update is async.
        // Best approach: Use apiClient directly here for the critical path? No, keep logic in context.

        // Let's assume selectCategory sets the session ID in local storage or state.
        // But we need to await it.
      }

      const placeholderIdea = `Create a ${categoryName.toLowerCase()} style image`

      // We will perform the action. 
      // NOTE: Context's selectCategory automatically initializes session if missing and sets sessionId state.
      // However, we can't easily grab that ID "out" of the void function to redirect.
      // We should check localStorage or rely on the fact that selectCategory is async.

      await selectCategory(categoryName, placeholderIdea)

      // After selectCategory resolves, sessionId state *should* be updated, but might be stale in this closure?
      // Actually, we can get it from localStorage or wait.
      // Or better: Modify LandingPage to JUST redirect to /create? No, we want seamless.

      // Let's read from localStorage as a fallback since Context sets it.
      const id = localStorage.getItem('session_id')
      if (id) {
        router.push(`/generate/${id}`)
      } else {
        console.error("Session ID missing after creation")
      }

    } catch (error) {
      console.error("❌ Failed to select category:", error)
    } finally {
      setIsInitializing(false)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <div className="flex flex-1 overflow-hidden">
        <div className="flex flex-1 flex-col overflow-hidden">
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
      </div>
    </div>
  )
}
