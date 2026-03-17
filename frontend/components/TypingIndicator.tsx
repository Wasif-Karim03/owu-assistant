"use client";

import { GraduationCap } from "lucide-react";

export default function TypingIndicator() {
  return (
    <div className="flex items-end gap-2.5 justify-start animate-message-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-owu-red flex items-center justify-center mb-1">
        <GraduationCap className="w-4 h-4 text-white" />
      </div>

      <div className="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-bl-md px-5 py-4">
        <div className="flex items-center gap-1.5">
          <span className="typing-dot w-2 h-2 rounded-full bg-owu-text-muted inline-block" />
          <span className="typing-dot w-2 h-2 rounded-full bg-owu-text-muted inline-block" />
          <span className="typing-dot w-2 h-2 rounded-full bg-owu-text-muted inline-block" />
        </div>
      </div>
    </div>
  );
}
