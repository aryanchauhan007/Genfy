"use client"

import { useState, useEffect, useRef } from "react"
import { useSession } from "@/contexts/session-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2, Send, Sparkles, ArrowUp } from "lucide-react"
import { SuggestionChips } from "./suggestion-chips"
import { useToast } from "@/hooks/use-toast"
import { motion, AnimatePresence } from "framer-motion"

interface ChatInterfaceProps {
  onComplete: () => void
}

interface Message {
  role: "user" | "assistant"
  content: string
}

export function ChatInterface({ onComplete }: ChatInterfaceProps) {
  const {
    session,
    submitAnswer,
    getCurrentQuestion,
    getFinalPrompt,
    skipToGeneration,
  } = useSession()

  const [currentQuestion, setCurrentQuestion] = useState<any>(null)
  const [userInput, setUserInput] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [isComplete, setIsComplete] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  useEffect(() => {
    loadCurrentQuestion()
  }, [])

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTo({ top: scrollElement.scrollHeight, behavior: 'smooth' });
      }
    }
  }, [messages, isSubmitting])

  const loadCurrentQuestion = async () => {
    try {
      const questionData = await getCurrentQuestion()
      if (questionData.is_complete) {
        handleCompletion()
      } else {
        setCurrentQuestion(questionData.question)
        if (messages.length === 0) {
          setMessages([{
            role: "assistant",
            content: questionData.question.text,
          }])
        }
      }
    } catch (error) {
      console.error("Failed to load question:", error)
    }
  }

  const handleCompletion = async () => {
    setIsComplete(true)
    await getFinalPrompt()
    toast({ title: "Done! 🎉", description: "Generating your prompt..." })
    setTimeout(() => onComplete(), 1500)
  }

  const handleSubmit = async () => {
    if (!userInput.trim()) return

    setIsSubmitting(true)
    const currentInput = userInput
    setUserInput("")

    // Optimistic Update
    setMessages((prev) => [...prev, { role: "user", content: currentInput }])

    try {
      const response = await submitAnswer(currentInput)

      if (response.should_generate_prompt) {
        setMessages((prev) => [...prev, { role: "assistant", content: "Perfect! I have everything I need." }])
        handleCompletion()
      } else if (response.next_question) {
        setCurrentQuestion(response.next_question)
        setMessages((prev) => [...prev, {
          role: "assistant",
          content: response.next_question.text,
        }])
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to submit answer.", variant: "destructive" })
      setUserInput(currentInput)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  // --- FIX: Allow selecting multiple options ---
  const handleSuggestionSelect = (suggestion: string) => {
    setUserInput((prev) => {
      // Split current input by commas to check if item exists
      const parts = prev.split(',').map(s => s.trim()).filter(s => s !== "");

      if (parts.includes(suggestion)) {
        // If already selected, remove it (toggle off)
        return parts.filter(p => p !== suggestion).join(', ');
      } else {
        // If not selected, append it
        return parts.length > 0
          ? `${prev}, ${suggestion}`
          : suggestion;
      }
    })
  }

  // Render bold text helper
  const renderMessageContent = (text: string) => {
    return text.split(/(\*\*.*?\*\*)/g).map((part, index) =>
      part.startsWith('**') && part.endsWith('**')
        ? <strong key={index} className="font-bold text-gray-900">{part.slice(2, -2)}</strong>
        : <span key={index}>{part}</span>
    );
  };

  return (
    // Responsive Height: Fits on screen, max-height prevents it from getting too tall
    <div className="flex flex-col h-[80vh] max-h-[800px] min-h-[500px] w-full max-w-3xl mx-auto bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden font-sans relative">

      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-gray-900">Creative Assistant</h2>
            <p className="text-xs text-gray-500 font-medium">
              {isComplete ? "Session Complete" : "Refining your vision"}
            </p>
          </div>
        </div>

        {/* Skip Button */}
        {!isComplete && messages.length > 2 && (
          <Button
            onClick={async () => {
              setIsSubmitting(true)
              try {
                await skipToGeneration()
                handleCompletion()
              } catch (e) {
                toast({ title: "Error", description: "Failed to skip.", variant: "destructive" })
              } finally {
                setIsSubmitting(false)
              }
            }}
            variant="ghost"
            size="sm"
            className="text-xs text-gray-500 hover:text-blue-600 hover:bg-blue-50"
          >
            Skip to Gen ➤
          </Button>
        )}
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden bg-gray-50/50">
        <ScrollArea className="h-full px-4 md:px-8 py-6" ref={scrollRef}>
          <div className="flex flex-col gap-6 pb-4">
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {/* Message Bubble */}
                <div className={`max-w-[85%] rounded-2xl px-6 py-3.5 text-[15px] leading-relaxed shadow-sm ${msg.role === "user"
                    ? "bg-black text-white rounded-br-sm" // User = Black
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm" // AI = White
                  }`}>
                  {renderMessageContent(msg.content)}
                </div>
              </motion.div>
            ))}

            {isSubmitting && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="bg-white border border-gray-200 px-5 py-3 rounded-2xl rounded-bl-sm shadow-sm flex items-center gap-2">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}
            <div className="h-2" />
          </div>
        </ScrollArea>
      </div>

      {/* Input & Suggestions Footer */}
      {!isComplete && currentQuestion && (
        <div className="border-t border-gray-100 bg-white p-4 md:p-6 space-y-4 z-20">

          {/* Scrollable Suggestions - Prevents layout break */}
          <div className="max-h-[100px] overflow-y-auto custom-scrollbar -mx-2 px-2">
            <SuggestionChips
              currentQuestion={currentQuestion}
              onSelect={handleSuggestionSelect}
            />
          </div>

          {/* Modern Input Bar */}
          <div className="relative flex items-center bg-gray-50 border border-gray-200 rounded-full px-2 py-1.5 focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-300 transition-all shadow-sm">
            <Input
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isSubmitting}
              placeholder={currentQuestion.placeholder || "Type your answer here..."}
              className="flex-1 bg-transparent border-none text-base focus-visible:ring-0 focus-visible:ring-offset-0 px-4 h-10 shadow-none placeholder:text-gray-400 text-gray-900"
            />
            <Button
              onClick={handleSubmit}
              disabled={!userInput.trim() || isSubmitting}
              size="icon"
              className="h-9 w-9 rounded-full bg-blue-600 hover:bg-blue-700 text-white shrink-0 transition-transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100"
            >
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUp className="w-5 h-5" />}
            </Button>
          </div>

          <div className="text-center">
            <span className="text-[10px] text-gray-400 font-medium">Press Enter to send</span>
          </div>
        </div>
      )}
    </div>
  )
}