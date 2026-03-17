"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Trash2, GraduationCap, Plus, X } from "lucide-react";
import ChatMessage from "@/components/ChatMessage";
import TypingIndicator from "@/components/TypingIndicator";
import ChatInput from "@/components/ChatInput";
import SuggestedQuestions from "@/components/SuggestedQuestions";
import WelcomeBanner from "@/components/WelcomeBanner";
import {
  sendMessage,
  getHistory,
  clearHistory,
  isApiError,
  type Message,
} from "@/lib/api";
import { getOrCreateSessionId, resetSessionId } from "@/lib/session";

const STORAGE_KEY = "owu-assistant-messages";

function loadCachedMessages(): Message[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveCachedMessages(msgs: Message[]) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(msgs));
  } catch { /* quota exceeded — ignore */ }
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const errorTimer = useRef<ReturnType<typeof setTimeout>>();

  // auto-dismiss error after 5s
  useEffect(() => {
    if (!error) return;
    errorTimer.current = setTimeout(() => setError(null), 5000);
    return () => clearTimeout(errorTimer.current);
  }, [error]);

  // persist messages to sessionStorage
  useEffect(() => {
    if (messages.length > 0) saveCachedMessages(messages);
  }, [messages]);

  // scroll to bottom on new messages
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  // init session & load history
  useEffect(() => {
    const sid = getOrCreateSessionId();
    setSessionId(sid);

    const cached = loadCachedMessages();
    if (cached.length > 0) {
      setMessages(cached);
    } else {
      getHistory(sid).then((history) => {
        if (history.length > 0) setMessages(history);
      });
    }
  }, []);

  const handleSend = useCallback(
    async (text: string) => {
      if (!sessionId) return;
      setError(null);

      const userMsg: Message = { role: "user", content: text };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);

      try {
        const res = await sendMessage(sessionId, text);

        if (res.session_id !== sessionId) {
          setSessionId(res.session_id);
        }

        const assistantMsg: Message = {
          role: "assistant",
          content: res.response,
          sources: res.sources,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        if (isApiError(err)) {
          setError(err.error);
        } else {
          setError(
            "Sorry, something went wrong. Please try again in a moment."
          );
        }
        const fallback: Message = {
          role: "assistant",
          content:
            "I wasn't able to get a response. Please try again in a moment.",
        };
        setMessages((prev) => [...prev, fallback]);
      } finally {
        setLoading(false);
      }
    },
    [sessionId],
  );

  const handleClear = useCallback(async () => {
    if (!sessionId) return;
    await clearHistory(sessionId).catch(() => {});
    setMessages([]);
    sessionStorage.removeItem(STORAGE_KEY);
    const newSid = resetSessionId();
    setSessionId(newSid);
  }, [sessionId]);

  const handleNewConversation = useCallback(async () => {
    if (sessionId) {
      await clearHistory(sessionId).catch(() => {});
    }
    setMessages([]);
    setError(null);
    sessionStorage.removeItem(STORAGE_KEY);
    const newSid = resetSessionId();
    setSessionId(newSid);
  }, [sessionId]);

  return (
    <div className="flex flex-col h-screen bg-owu-grey">
      {/* ── header ─────────────────────────────────── */}
      <header className="flex-shrink-0 bg-white border-b border-gray-200">
        <div className="mx-auto max-w-3xl flex items-center justify-between px-4 sm:px-6 py-3.5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-owu-red flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-heading text-lg font-semibold text-owu-text leading-tight">
                OWU Assistant
              </h1>
              <p className="text-xs text-owu-text-muted hidden sm:block">
                Your campus questions, answered.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            {messages.length > 0 && (
              <>
                <button
                  onClick={handleNewConversation}
                  className="flex items-center gap-1.5 text-xs text-owu-text-muted
                             hover:text-owu-red transition-colors px-2 py-1.5 rounded-md
                             hover:bg-owu-red-muted"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">New conversation</span>
                </button>
                <button
                  onClick={handleClear}
                  className="flex items-center gap-1.5 text-xs text-owu-text-muted
                             hover:text-owu-red transition-colors px-2 py-1.5 rounded-md
                             hover:bg-owu-red-muted"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Clear</span>
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ── messages area ──────────────────────────── */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {messages.length === 0 && !loading ? (
          <div>
            <WelcomeBanner />
            <SuggestedQuestions onSelect={handleSend} />
          </div>
        ) : (
          <div className="mx-auto max-w-3xl px-4 sm:px-6 py-6 space-y-5">
            {messages.map((msg, i) => (
              <ChatMessage
                key={i}
                role={msg.role}
                content={msg.content}
                sources={msg.sources}
              />
            ))}
            {loading && <TypingIndicator />}
          </div>
        )}
      </div>

      {/* ── error banner ───────────────────────────── */}
      {error && (
        <div className="border-t border-red-200 bg-red-50 px-4 py-2.5 sm:px-6">
          <div className="mx-auto max-w-3xl flex items-center justify-between">
            <p className="text-sm text-red-700">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ── input ──────────────────────────────────── */}
      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
}
