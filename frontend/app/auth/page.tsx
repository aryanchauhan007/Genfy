"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Loader2, ArrowLeft, Sparkles } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useToast } from "@/components/ui/use-toast"
import Link from "next/link"
import { useSession } from "@/contexts/session-context"

export default function AuthPage() {
    const [isLoading, setIsLoading] = useState(false)
    const [isSignUp, setIsSignUp] = useState(false)
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const router = useRouter()
    const { toast } = useToast()
    const { login, signup } = useSession()

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)
        console.log("handleAuth started", { isSignUp, email })

        try {
            if (isSignUp) {
                console.log("Calling signup")
                await signup(email, password)
                console.log("SignUp successful, auto-logging in")

                await login(email, password)
                console.log("Auto-login successful")

                toast({
                    title: "Account created!",
                    description: "Welcome! You have been logged in.",
                })
                router.push("/")
                router.refresh()
            } else {
                console.log("Calling login")
                await login(email, password)
                console.log("SignIn successful")
                router.push("/")
                router.refresh()
            }
        } catch (error: any) {
            console.error("Auth error caught:", error)

            // ✅ UX IMPROVEMENT: If user exists, try to log in automatically
            if (isSignUp && error.message === "User already exists") {
                console.log("User exists, attempting auto-login...")
                toast({
                    title: "Account exists",
                    description: "Logging you in...",
                })
                try {
                    await login(email, password)
                    console.log("Fallback login successful")
                    router.push("/")
                    router.refresh()
                    return
                } catch (loginError) {
                    // If login also fails (e.g. wrong password), show appropriate error
                    console.error("Fallback login failed:", loginError)
                    toast({
                        variant: "destructive",
                        title: "Login failed",
                        description: "Account exists, but password was incorrect.",
                    })
                    return
                }
            }

            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "Authentication failed",
            })
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-white text-gray-900 font-sans flex flex-col relative overflow-hidden">

            {/* Background Gradients */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-pink-100 via-white to-white opacity-60 z-0"></div>

            {/* Header */}
            <header className="relative z-10 p-6 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-black transition-colors font-medium">
                    <ArrowLeft className="w-4 h-4" /> Back to Home
                </Link>
            </header>

            <main className="flex-1 flex items-center justify-center relative z-10 px-4">
                <div className="w-full max-w-md">

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="bg-white/80 backdrop-blur-xl border border-white/20 rounded-[32px] p-8 shadow-2xl relative overflow-hidden"
                    >
                        {/* Decorative Sparkle */}
                        <div className="absolute -top-10 -right-10 w-32 h-32 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full blur-3xl opacity-50 pointer-events-none"></div>

                        <div className="text-center mb-8 relative">
                            <div className="flex justify-center mb-4">
                                <div className="w-12 h-12 bg-black rounded-2xl flex items-center justify-center">
                                    <Sparkles className="w-6 h-6 text-white" />
                                </div>
                            </div>
                            <h1 className="text-3xl font-bold tracking-tight mb-2">
                                {isSignUp ? "Create your account" : "Welcome back"}
                            </h1>
                            <p className="text-gray-500 text-sm">
                                {isSignUp ? "Start creating stunning AI visuals today" : "Sign in to continue creating"}
                            </p>
                        </div>

                        <form onSubmit={handleAuth} className="space-y-4">
                            <div className="space-y-2">
                                <Input
                                    type="email"
                                    placeholder="Email address"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="rounded-xl border-gray-200 bg-gray-50/50 h-12 text-base focus-visible:ring-1 focus-visible:ring-black"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Input
                                    type="password"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="rounded-xl border-gray-200 bg-gray-50/50 h-12 text-base focus-visible:ring-1 focus-visible:ring-black"
                                    required
                                />
                            </div>

                            <Button
                                type="submit"
                                className="w-full h-12 rounded-xl bg-black text-white hover:bg-gray-800 font-semibold text-[15px] transition-all hover:scale-[1.02] active:scale-[0.98]"
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                ) : (
                                    isSignUp ? "Sign Up" : "Sign In"
                                )}
                            </Button>
                        </form>

                        <div className="mt-8 text-center">
                            <p className="text-sm text-gray-500">
                                {isSignUp ? "Already have an account?" : "Don't have an account?"}
                                <button
                                    onClick={() => setIsSignUp(!isSignUp)}
                                    className="ml-2 font-semibold text-black hover:underline"
                                >
                                    {isSignUp ? "Sign in" : "Sign up"}
                                </button>
                            </p>
                        </div>

                    </motion.div>
                </div>
            </main>

            <footer className="relative z-10 p-6 text-center text-sm text-gray-400">
                &copy; {new Date().getFullYear()} Genfy. All rights reserved.
            </footer>
        </div>
    )
}
