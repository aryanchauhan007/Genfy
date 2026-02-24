"use client"

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient, Session, VisualSettings } from '@/lib/api-client';
import { supabase } from '@/lib/supabase';
import { User } from '@supabase/supabase-js';
import { useRouter } from 'next/navigation';

interface SessionContextType {
  sessionId: string | null;
  session: Session | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;

  // Auth actions
  signOut: () => Promise<void>;

  // Session actions
  initializeSession: (llmProvider?: string) => Promise<void>;
  refreshSession: () => Promise<void>;

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

    // Check for existing auth
    const checkAuth = async () => {
      const { data: { session: authSession } } = await supabase.auth.getSession();
      setUser(authSession?.user ?? null);
    };
    checkAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (!session?.user) {
        // Clear app session on logout if desired, or keep it.
        // For now, we allow the session to persist but unlink it? 
        // User asked for "create only when signed in".
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
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

  const initializeSession = useCallback(async (llmProvider: string = 'Claude') => {
    setIsLoading(true);
    setError(null);

    try {
      // Pass user_id if logged in (Requires backend update to accept it)
      const response = await apiClient.createSession(llmProvider, user?.id);

      // Update session with user_id if we have one? 
      // Ideally backend createSession should take user_id.
      // We'll address this in backend update.

      setSessionId(response.session_id);
      localStorage.setItem('session_id', response.session_id);
      await refreshSession(response.session_id);
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [handleError, user]);

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

  const selectCategory = useCallback(async (category: string, userIdea: string) => {
    // If no user, we should probably block here, but LandingPage will handle the block.
    // If not logged in, we can start a session but we can't "create" (save/generate).
    // The user said "create only when I am ... signed in". 
    // So selectCategory (which starts generation flow) should require auth or be allowed?
    // LandingPage "Start Creating" will check auth. 

    if (!sessionId) {
      await initializeSession();
      // We might need to wait for session init
    }

    // Safety check just in case
    // if (!sessionId) return; // initializeSession is async, so sessionId might not be set immediately if we don't wait? 
    // Wait, initializeSession is async. 
    // But we need the ID.

    // Better pattern: ensure session exists
    let activeSessionId = sessionId;
    if (!activeSessionId) {
      // Reuse initialize logic to get ID
      try {
        const response = await apiClient.createSession('Claude', user?.id);
        activeSessionId = response.session_id;
        setSessionId(activeSessionId);
        localStorage.setItem('session_id', activeSessionId!);
      } catch (e) {
        handleError(e);
        return;
      }
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
  }, [sessionId, initializeSession, refreshSession, handleError, user]);

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
    signOut,
    initializeSession,
    refreshSession,
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
    // refreshHistory, 
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
