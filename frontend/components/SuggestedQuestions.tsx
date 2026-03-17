"use client";

import { Lightbulb } from "lucide-react";

const SUGGESTIONS = [
  "What events are happening today?",
  "How do I contact Student Accounts?",
  "Where do I go for career help?",
  "How do I register for classes?",
  "What's in the OWU Daily?",
  "Where is the IOCP office?",
];

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

export default function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="flex flex-col items-center justify-center flex-1 px-4 py-12">
      <div className="w-16 h-16 rounded-full bg-owu-red-muted flex items-center justify-center mb-6">
        <Lightbulb className="w-7 h-7 text-owu-red" />
      </div>

      <h2 className="font-heading text-2xl font-semibold text-owu-text mb-2">
        How can I help?
      </h2>
      <p className="text-owu-text-muted text-sm mb-8 text-center max-w-md">
        I can answer questions about campus resources, events, offices, deadlines, and more.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-lg">
        {SUGGESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="text-left px-4 py-3 rounded-xl border border-gray-200 bg-white
                       hover:border-owu-red/30 hover:bg-owu-red-muted/50
                       text-sm text-owu-text transition-all
                       shadow-sm hover:shadow"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
