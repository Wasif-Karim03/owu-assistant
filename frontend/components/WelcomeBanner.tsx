"use client";

import { GraduationCap, BookOpen, Lock } from "lucide-react";

export default function WelcomeBanner() {
  return (
    <div className="text-center px-4 pt-10 pb-2">
      <div className="mx-auto max-w-md">
        {/* shield / crest placeholder */}
        <div className="mx-auto w-16 h-16 rounded-2xl bg-owu-red flex items-center justify-center mb-5 shadow-md">
          <GraduationCap className="w-8 h-8 text-white" />
        </div>

        <h2 className="font-heading text-2xl font-semibold text-owu-text mb-2">
          Hi! I&apos;m your OWU Campus Assistant
        </h2>
        <p className="text-sm text-owu-text-muted leading-relaxed mb-5">
          I can answer questions about events, offices, deadlines, financial
          aid, academic resources, and more. I&apos;ll let you know if I
          don&apos;t have an answer — and point you to the right place.
        </p>

        <div className="flex items-center justify-center gap-3">
          <span className="inline-flex items-center gap-1.5 text-xs text-owu-text-muted bg-white border border-gray-200 rounded-full px-3 py-1.5">
            <BookOpen className="w-3.5 h-3.5 text-owu-red" />
            Powered by OWU content
          </span>
          <span className="inline-flex items-center gap-1.5 text-xs text-owu-text-muted bg-white border border-gray-200 rounded-full px-3 py-1.5">
            <Lock className="w-3.5 h-3.5 text-owu-red" />
            Private to your session
          </span>
        </div>
      </div>
    </div>
  );
}
