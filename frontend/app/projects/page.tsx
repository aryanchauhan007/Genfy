"use client"

import { HistorySidebar } from "@/components/history-sidebar"
import { Header } from "@/components/header"
import { Button } from "@/components/ui/button"
import { FolderOpen, Plus } from "lucide-react"
import { useRouter } from "next/navigation"

export default function ProjectsPage() {
  const router = useRouter()

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        {/* History Sidebar */}
        <div className="flex-shrink-0">
          <HistorySidebar />
        </div>
        
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <FolderOpen className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">My Projects</h1>
                  <p className="text-gray-500 text-sm">All your generated prompts in one place</p>
                </div>
              </div>

              <Button
                onClick={() => router.push('/')}
                className="bg-black hover:bg-gray-800 text-white flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                New Project
              </Button>
            </div>

            {/* Projects Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Empty State */}
              <div className="col-span-full flex flex-col items-center justify-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-200">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <FolderOpen className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No projects yet
                </h3>
                <p className="text-gray-500 text-center max-w-md mb-6">
                  Start creating amazing prompts and they'll appear here
                </p>
                <Button
                  onClick={() => router.push('/')}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                >
                  Create Your First Project
                </Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
