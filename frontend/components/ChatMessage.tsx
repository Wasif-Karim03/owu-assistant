"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ExternalLink, GraduationCap, ChevronDown, ChevronUp } from "lucide-react";
import type { Source } from "@/lib/api";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  sources?: Source[] | null;
}

export default function ChatMessage({ role, content, sources }: ChatMessageProps) {
  const isUser = role === "user";
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const hasSources = !isUser && sources && sources.length > 0;

  return (
    <div
      className={`flex items-end gap-2.5 animate-message-in ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-owu-red flex items-center justify-center mb-1">
          <GraduationCap className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? "order-first" : ""}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-[0.935rem] leading-relaxed ${
            isUser
              ? "bg-owu-red text-white rounded-br-md"
              : "bg-white text-owu-text border border-gray-100 shadow-sm rounded-bl-md"
          }`}
        >
          <div className={isUser ? "" : "chat-markdown"}>
            {isUser ? (
              <p className="whitespace-pre-wrap">{content}</p>
            ) : (
              <ReactMarkdown>{content}</ReactMarkdown>
            )}
          </div>
        </div>

        {hasSources && (
          <div className="mt-1.5 ml-1">
            <button
              onClick={() => setSourcesOpen((o) => !o)}
              className="inline-flex items-center gap-1 text-xs text-owu-text-muted
                         hover:text-owu-red transition-colors"
            >
              {sourcesOpen ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
              {sources!.length} {sources!.length === 1 ? "source" : "sources"} used
            </button>

            {sourcesOpen && (
              <div className="flex flex-wrap gap-1.5 mt-1.5 animate-message-in">
                {sources!.map((source, idx) => (
                  <a
                    key={idx}
                    href={source.url || "#"}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-owu-text-muted
                               bg-owu-grey hover:bg-owu-red-muted px-2.5 py-1 rounded-full
                               transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span className="truncate max-w-[200px]">{source.title}</span>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
