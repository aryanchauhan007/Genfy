"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Header } from "@/components/header"
import { PromptDisplay } from "@/components/ui/prompt-display"
import { ImageGallery } from "@/components/image-gallery"
import { HistorySidebar } from "@/components/history-sidebar"
import { useSession } from "@/contexts/session-context"
import { Loader2, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function ResultPage() {
    const params = useParams()
    const router = useRouter()
    const { sessionId, joinSession, session, isLoading } = useSession()
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

    const handleStartNew = async () => {
        // Clear visual settings if needed, or just go home
        router.push('/')
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
                {/* History Sidebar */}
                <div className="flex-shrink-0 border-r border-gray-200 bg-white">
                    <HistorySidebar />
                </div>

                <main className="flex flex-1 flex-col overflow-hidden">
                    <div className="flex flex-1 overflow-hidden bg-gray-50">
                        <div className="flex-1 overflow-y-auto">
                            <div className="p-8">
                                <div className="w-full max-w-7xl mx-auto space-y-6">
                                    {/* Back Button */}
                                    <Button
                                        variant="ghost"
                                        onClick={() => router.push('/')}
                                        className="mb-4"
                                    >
                                        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
                                    </Button>

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
                                                    onClick={() => router.push(`/generate/${sessionId}`)}
                                                    className="bg-black hover:bg-gray-800 text-white"
                                                >
                                                    Go to Generate
                                                </Button>
                                            </div>
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
