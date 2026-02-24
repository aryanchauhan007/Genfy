"use client"

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient, Session, VisualSettings, User } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

interface SessionContextType {
  sessionId: string | null;
  session: Session | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;

  // Auth actions
  login: (email: string, pass: string) => Promise<void>;
  signup: (email: string, pass: string) => Promise<void>;
  signOut: () => Promise<void>;

  // Session actions
  initializeSession: (llmProvider?: string) => Promise<void>;
  refreshSession: () => Promise<void>;
  joinSession: (sessionId: string) => Promise<void>;

  // Category actions
  selectCategory: (category: string, userIdea: string) => Promise<void>;

  // Visual settings actions
  saveVisualSettings: (settings: VisualSettings) => Promise<void>;
  generateQuickPrompt: () => Promise<string>;

  // Chat actions
  startChat: (category: string, userIdea: string, visualSettings?: VisualSettings) => Promise<void>;
  submitAnswer: (answer: string) => Promise<any>;
  getCurrentQuestion: () => Promise<any>;

  // Suggestions
  getSuggestions: (refresh?: number) => Promise<string[]>;
  toggleSuggestion: (suggestion: string) => Promise<void>;
  selectedSuggestions: string[];

  // Prompt actions
  getFinalPrompt: () => Promise<any>;
  refinePrompt: (instruction: string) => Promise<string>;
  skipToGeneration: () => Promise<void>;

  // Clear error
  clearError: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSuggestions, setSelectedSuggestions] = useState<string[]>([]);
  const router = useRouter();

  // Initialize session and auth on mount
  useEffect(() => {
    // Check for existing session
    const storedSessionId = localStorage.getItem('session_id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
      refreshSession(storedSessionId);
    }

    // Check for existing auth (simple localStorage persistence for now)
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error("Failed to parse stored user", e);
      }
    }
  }, []);

  const login = useCallback(async (email: string, pass: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.login(email, pass);
      setUser(res.user);
      localStorage.setItem('user', JSON.stringify(res.user));

      // ✅ CRITICAL FIX: Clear any existing session ID on login
      // This prevents the new user from trying to access the previous user's (or guest's) session
      // which would result in a 403 Forbidden error.
      setSessionId(null);
      setSession(null);
      localStorage.removeItem('session_id');

    } catch (err: any) {
      setError(err.message || "Login failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signup = useCallback(async (email: string, pass: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.signup(email, pass);
      // Auto login on signup? Or just notify?
      // Let's verify via login
      // For now, assume success means we can direct user to login or auto-login
      // In this simple flow, we won't auto-login unless we call login next.
      // User asked for "signup", usually implies logging in after or immediately.
    } catch (err: any) {
      setError(err.message || "Signup failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signOut = useCallback(async () => {
    // await apiClient.logout(); // Optional backend call
    localStorage.removeItem('user');
    setUser(null);
    router.push('/');
    router.refresh();
  }, [router]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((err: any) => {
    const message = err.message || 'An unexpected error occurred';
    setError(message);
    console.error('Session error:', err);
  }, []);

  const refreshSession = useCallback(async (id?: string) => {
    const targetId = id || sessionId;
    if (!targetId) return;

    try {
      const sessionData = await apiClient.getSession(targetId);
      setSession(sessionData);

      if (sessionData.selected_chips) {
        setSelectedSuggestions(sessionData.selected_chips);
      }
    } catch (err) {
      handleError(err);
    }
  }, [sessionId, handleError]);

  const initializeSession = useCallback(async (llmProvider: string = 'Claude') => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.createSession(llmProvider, user?.id);

      setSessionId(response.session_id);
      localStorage.setItem('session_id', response.session_id);
      await refreshSession(response.session_id);
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [handleError, user, refreshSession]);

  const joinSession = useCallback(async (id: string) => {
    setSessionId(id);
    localStorage.setItem('session_id', id);
    await refreshSession(id);
  }, [refreshSession]);

  const selectCategory = useCallback(async (category: string, userIdea: string) => {
    // ⚠️ CRITICAL: Always prefer localStorage over state for the most up-to-date ID
    // State updates (setSessionId) are async and might be stale in this closure
    let activeSessionId = localStorage.getItem('session_id') || sessionId;

    // Double check: if we just logged in, we cleared localStorage, so this should be null
    if (!activeSessionId) {
      try {
        console.log("📝 Creating new session for category selection...");
        const response = await apiClient.createSession('Claude', user?.id);
        activeSessionId = response.session_id;
        setSessionId(activeSessionId);
        localStorage.setItem('session_id', activeSessionId!);
      } catch (e) {
        handleError(e);
        return;
      }
    } else {
      console.log("♻️  Using existing session:", activeSessionId);
    }

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.selectCategory(activeSessionId!, category, userIdea);
      await refreshSession(activeSessionId!);
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, refreshSession, handleError, user]);

  const saveVisualSettings = useCallback(async (settings: VisualSettings) => {
    if (!sessionId) throw new Error('No active session');

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.saveVisualSettings(sessionId, settings);
      await refreshSession();
    } catch (err) {
      handleError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, refreshSession, handleError]);

  const generateQuickPrompt = useCallback(async (): Promise<string> => {
    if (!sessionId) throw new Error('No active session');

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.generateQuickPrompt(sessionId);
      await refreshSession();
      return response.final_prompt;
    } catch (err) {
      handleError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, refreshSession, handleError]);

  const startChat = useCallback(async (
    category: string,
    userIdea: string,
    visualSettings?: VisualSettings
  ) => {
    if (!sessionId) throw new Error('No active session');

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.startChat(sessionId, category, userIdea, visualSettings);
      await refreshSession();
    } catch (err) {
      handleError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, refreshSession, handleError]);

  const submitAnswer = useCallback(async (answer: string) => {
    if (!sessionId) throw new Error('No active session');

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.submitAnswer(sessionId, answer);
      await refreshSession();
      return response;
    } catch (err) {
      handleError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, refreshSession, handleError]);

  const skipToGeneration = useCallback(async () => {
    if (!sessionId) throw new Error('No active session');

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.skipToGeneration(sessionId);
      await refreshSession();
    } catch (err) {
      handleError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, refreshSession, handleError]);

  const getCurrentQuestion = useCallback(async () => {
    if (!sessionId) throw new Error('No active session');

    try {
      return await apiClient.getCurrentQuestion(sessionId);
    } catch (err) {
      handleError(err);
      throw err;
    }
  }, [sessionId, handleError]);

  const getSuggestions = useCallback(async (refresh: number = 0): Promise<string[]> => {
    if (!sessionId) throw new Error('No active session');

    try {
      const response = await apiClient.getSuggestions(sessionId, refresh);
      return response.suggestions;
    } catch (err) {
      handleError(err);
      return [];
    }
  }, [sessionId, handleError]);

  const toggleSuggestion = useCallback(async (suggestion: string) => {
    if (!sessionId) throw new Error('No active session');

    try {
      const response = await apiClient.toggleSuggestion(sessionId, suggestion);
      setSelectedSuggestions(response.selected_suggestions);
    } catch (err) {
      handleError(err);
    }
  }, [sessionId, handleError]);

  const getFinalPrompt = useCallback(async () => {
    if (!sessionId) throw new Error('No active session');

    try {
      return await apiClient.getFinalPrompt(sessionId);
    } catch (err) {
      handleError(err);
      throw err;
    }
  }, [sessionId, handleError]);

  const refinePrompt = useCallback(async (instruction: string): Promise<string> => {
    if (!sessionId) throw new Error('No active session');

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.refinePrompt(sessionId, instruction);
      await refreshSession();
      return response.refined_prompt;
    } catch (err) {
      handleError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, refreshSession, handleError]);

  const value: SessionContextType = {
    sessionId,
    session,
    user,
    isLoading,
    error,
    login,
    signup,
    signOut,
    initializeSession,
    refreshSession,
    joinSession,
    selectCategory,
    saveVisualSettings,
    generateQuickPrompt,
    startChat,
    submitAnswer,
    getCurrentQuestion,
    getSuggestions,
    toggleSuggestion,
    selectedSuggestions,
    getFinalPrompt,
    refinePrompt,
    skipToGeneration,
    clearError,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}
