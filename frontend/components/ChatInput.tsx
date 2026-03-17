"use client";

import { useRef, useState, useCallback, type KeyboardEvent, type ChangeEvent } from "react";
import { SendHorizonal } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const MAX_CHARS = 2000;

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const autoResize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    const maxH = 4 * 24 + 16; // ~4 lines
    el.style.height = `${Math.min(el.scrollHeight, maxH)}px`;
  }, []);

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    if (e.target.value.length <= MAX_CHARS) {
      setValue(e.target.value);
    }
    autoResize();
  };

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
      <div className="mx-auto max-w-3xl">
        <div className="flex items-end gap-3 rounded-xl border border-gray-200 bg-owu-grey px-4 py-2.5 focus-within:border-owu-red/40 focus-within:ring-2 focus-within:ring-owu-red/10 transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Ask anything about OWU — events, offices, deadlines, resources..."
            className="flex-1 resize-none bg-transparent text-owu-text placeholder:text-owu-text-muted text-[0.935rem] leading-6 outline-none disabled:opacity-50"
          />

          <div className="flex items-center gap-2 pb-0.5">
            <span
              className={`text-xs tabular-nums ${
                value.length > MAX_CHARS * 0.9
                  ? "text-red-500"
                  : "text-owu-text-muted"
              }`}
            >
              {value.length}/{MAX_CHARS}
            </span>

            <button
              type="button"
              onClick={submit}
              disabled={disabled || !value.trim()}
              className="flex items-center justify-center w-9 h-9 rounded-lg
                         bg-owu-red text-white hover:bg-owu-red-light
                         disabled:opacity-40 disabled:cursor-not-allowed
                         transition-colors"
              aria-label="Send message"
            >
              <SendHorizonal className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/** Imperative helper: lets parent set + submit a message. */
export function useAutoSubmit(onSend: (message: string) => void) {
  return useCallback(
    (message: string) => {
      onSend(message);
    },
    [onSend]
  );
}
