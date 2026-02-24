"use client"

import { Header } from "@/components/header"
import { Button } from "@/components/ui/button"
import { BookOpen, ArrowRight } from "lucide-react"
import { useRouter } from "next/navigation"

export default function LearnPage() {
  const router = useRouter()

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <Header />

      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Learn</h1>
              <p className="text-gray-500 text-sm">Master the art of prompt engineering</p>
            </div>
          </div>

          <div className="text-center py-20">
            <p className="text-gray-600 mb-4">Learning resources coming soon!</p>
            <Button
              onClick={() => router.push('/')}
              className="bg-black hover:bg-gray-800 text-white flex items-center gap-2"
            >
              Start Creating
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
