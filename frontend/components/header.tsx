"use client"

import { Button } from "@/components/ui/button"
import { Sparkles, Bell, User as UserIcon, Search, LogOut } from "lucide-react"
import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import { useSession } from "@/contexts/session-context"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function Header() {
  const router = useRouter()
  const pathname = usePathname()
  const { user, signOut } = useSession()

  // Check if we're on the home page or have a step parameter
  const isGeneratePage = pathname === '/' || pathname.includes('?step=')
  const isProjectsPage = pathname === '/projects'
  const isLearnPage = pathname === '/learn'

  return (
    <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3 shadow-sm">
      <div className="flex items-center gap-8">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 cursor-pointer">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 shadow-md transition-transform hover:scale-110">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-semibold text-gray-900">
            Genfy
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1">
          {/* Generate */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/')}
            className={`relative font-medium transition-all hover:scale-105 hover:bg-gray-100 ${isGeneratePage
                ? 'text-gray-900 after:absolute after:bottom-0 after:left-1/2 after:h-0.5 after:w-3/4 after:-translate-x-1/2 after:bg-gray-900'
                : 'text-gray-600 hover:text-gray-900'
              }`}
          >
            Generate
          </Button>

          {/* My Projects */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/projects')}
            className={`relative font-medium transition-all hover:scale-105 hover:bg-gray-100 ${isProjectsPage
                ? 'text-gray-900 after:absolute after:bottom-0 after:left-1/2 after:h-0.5 after:w-3/4 after:-translate-x-1/2 after:bg-gray-900'
                : 'text-gray-600 hover:text-gray-900'
              }`}
          >
            My Projects
          </Button>

          {/* Learn */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/learn')}
            className={`relative font-medium transition-all hover:scale-105 hover:bg-gray-100 ${isLearnPage
                ? 'text-gray-900 after:absolute after:bottom-0 after:left-1/2 after:h-0.5 after:w-3/4 after:-translate-x-1/2 after:bg-gray-900'
                : 'text-gray-600 hover:text-gray-900'
              }`}
          >
            Learn
          </Button>
        </nav>
      </div>

      {/* Right Side Icons */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="text-gray-600 transition-all hover:scale-110 hover:bg-gray-100 hover:text-gray-900"
        >
          <Search className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="text-gray-600 transition-all hover:scale-110 hover:bg-gray-100 hover:text-gray-900"
        >
          <Bell className="h-5 w-5" />
        </Button>

        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full text-gray-600 transition-all hover:scale-110 hover:bg-gray-100 hover:text-gray-900"
              >
                <UserIcon className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuLabel className="font-normal text-xs text-gray-500">
                {user.email}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={signOut} className="text-red-600 cursor-pointer">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Link href="/auth">
            <Button
              variant="default"
              size="sm"
              className="bg-black hover:bg-gray-800 text-white rounded-full px-4"
            >
              Sign In
            </Button>
          </Link>
        )}
      </div>
    </header>
  )
}
