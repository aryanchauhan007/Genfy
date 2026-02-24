"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Header } from "@/components/header"
import { GeneratePanel } from "@/components/generate-panel"
import { ImageGallery } from "@/components/image-gallery"
import { ChatInterface } from "@/components/ui/chat-interface"
import { useSession } from "@/contexts/session-context"
import { Loader2 } from "lucide-react"

export default function GeneratePage() {
    const params = useParams()
    const router = useRouter()
    const { sessionId, joinSession, session, isLoading } = useSession()
    const [isChatMode, setIsChatMode] = useState(false)
    const [initializing, setInitializing] = useState(true)

    useEffect(() => {
        const init = async () => {
            if (params.sessionId && typeof params.sessionId === 'string') {
                if (sessionId !== params.sessionId) {
                    await joinSession(params.sessionId)
                }
            }
            setInitializing(false)
        }
        init()
    }, [params.sessionId, joinSession, sessionId])

    useEffect(() => {
        // If session is complete (has final prompt), redirect to result?
        // Or allow editing here.
        if (session?.current_step === "final_prompt" && session?.final_prompt) {
            router.push(`/result/${session.session_id || params.sessionId}`)
        }
        if (session?.current_step === "chat") {
            setIsChatMode(true)
        }
    }, [session, router, params.sessionId])

    const handlePromptGenerated = () => {
        router.push(`/result/${sessionId}`)
    }

    const handleAdvancedMode = () => {
        setIsChatMode(true)
    }

    const handleChatComplete = () => {
        router.push(`/result/${sessionId}`)
    }

    if (initializing || (isLoading && !session)) {
        return (
            <div className="flex h-screen items-center justify-center bg-gray-50">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
        )
    }

    return (
        <div className="flex h-screen flex-col bg-gray-50">
            <Header />
            <div className="flex flex-1 overflow-hidden">
                <main className="flex flex-1 flex-col overflow-hidden">
                    <div className="flex flex-1 overflow-hidden bg-gray-50">
                        <div className="flex-1 overflow-y-auto">
                            <div className="p-8">
                                <div className="w-full max-w-7xl mx-auto">
                                    <div className="space-y-6">
                                        <ImageGallery />

                                        {isChatMode ? (
                                            <div className="h-[calc(100vh-12rem)]">
                                                <ChatInterface onComplete={handleChatComplete} />
                                            </div>
                                        ) : (
                                            <GeneratePanel
                                                onPromptGenerated={handlePromptGenerated}
                                                onAdvancedMode={handleAdvancedMode}
                                            />
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    )
}
