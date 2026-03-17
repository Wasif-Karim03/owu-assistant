"use client";

import { useCallback, useEffect, useState } from "react";
import {
  GraduationCap,
  Globe,
  Mail,
  BarChart3,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Stats {
  total_documents: number;
  total_chunks: number;
  document_sources: { source_type: string; count: number }[];
}

type FeedbackState = null | { type: "success" | "error"; message: string };

export default function AdminPage() {
  const [url, setUrl] = useState("");
  const [emailContent, setEmailContent] = useState("");
  const [emailDate, setEmailDate] = useState("");
  const [stats, setStats] = useState<Stats | null>(null);

  const [urlLoading, setUrlLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [urlFeedback, setUrlFeedback] = useState<FeedbackState>(null);
  const [emailFeedback, setEmailFeedback] = useState<FeedbackState>(null);

  const loadStats = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/stats`);
      if (res.ok) setStats(await res.json());
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const handleIngestUrl = async () => {
    if (!url.trim()) return;
    setUrlLoading(true);
    setUrlFeedback(null);
    try {
      const res = await fetch(`${API_URL}/api/admin/ingest/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json();
      if (res.ok) {
        setUrlFeedback({
          type: "success",
          message: `Ingested "${data.title}" — ${data.chunks} chunks created.`,
        });
        setUrl("");
        loadStats();
      } else {
        setUrlFeedback({ type: "error", message: data.detail || "Ingestion failed" });
      }
    } catch {
      setUrlFeedback({ type: "error", message: "Network error" });
    } finally {
      setUrlLoading(false);
    }
  };

  const handleIngestEmail = async () => {
    if (!emailContent.trim() || !emailDate) return;
    setEmailLoading(true);
    setEmailFeedback(null);
    try {
      const res = await fetch(`${API_URL}/api/admin/ingest/email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: emailContent, date: emailDate }),
      });
      const data = await res.json();
      if (res.ok) {
        setEmailFeedback({
          type: "success",
          message: `Ingested "${data.title}" — ${data.chunks} chunks created.`,
        });
        setEmailContent("");
        setEmailDate("");
        loadStats();
      } else {
        setEmailFeedback({ type: "error", message: data.detail || "Ingestion failed" });
      }
    } catch {
      setEmailFeedback({ type: "error", message: "Network error" });
    } finally {
      setEmailLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-owu-grey">
      {/* header */}
      <header className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-3xl flex items-center gap-3 px-6 py-4">
          <div className="w-9 h-9 rounded-lg bg-owu-red flex items-center justify-center">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-heading text-lg font-semibold text-owu-text">
              OWU Assistant Admin
            </h1>
            <p className="text-xs text-owu-text-muted">
              Manage data sources and view system stats
            </p>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-3xl px-6 py-8 space-y-8">
        {/* ── stats ─────────────────────────────────── */}
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-owu-red" />
            <h2 className="font-heading text-base font-semibold text-owu-text">
              System Stats
            </h2>
          </div>
          {stats ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <StatCard label="Documents" value={stats.total_documents} />
              <StatCard label="Chunks" value={stats.total_chunks} />
              {stats.document_sources.map((s) => (
                <StatCard
                  key={s.source_type}
                  label={s.source_type}
                  value={s.count}
                />
              ))}
            </div>
          ) : (
            <p className="text-sm text-owu-text-muted">Loading stats…</p>
          )}
        </section>

        {/* ── ingest URL ────────────────────────────── */}
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-5 h-5 text-owu-red" />
            <h2 className="font-heading text-base font-semibold text-owu-text">
              Ingest a URL
            </h2>
          </div>
          <div className="flex gap-3">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.owu.edu/..."
              className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-2
                         focus:outline-none focus:border-owu-red/40 focus:ring-2 focus:ring-owu-red/10"
            />
            <button
              onClick={handleIngestUrl}
              disabled={urlLoading || !url.trim()}
              className="flex items-center gap-2 text-sm font-medium text-white
                         bg-owu-red hover:bg-owu-red-light rounded-lg px-4 py-2
                         disabled:opacity-40 transition-colors"
            >
              {urlLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              Ingest
            </button>
          </div>
          <Feedback state={urlFeedback} />
        </section>

        {/* ── ingest email ──────────────────────────── */}
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Mail className="w-5 h-5 text-owu-red" />
            <h2 className="font-heading text-base font-semibold text-owu-text">
              Add OWU Daily Email
            </h2>
          </div>
          <div className="space-y-3">
            <input
              type="date"
              value={emailDate}
              onChange={(e) => setEmailDate(e.target.value)}
              className="text-sm border border-gray-200 rounded-lg px-3 py-2
                         focus:outline-none focus:border-owu-red/40 focus:ring-2 focus:ring-owu-red/10"
            />
            <textarea
              rows={6}
              value={emailContent}
              onChange={(e) => setEmailContent(e.target.value)}
              placeholder="Paste the full email content here…"
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 resize-y
                         focus:outline-none focus:border-owu-red/40 focus:ring-2 focus:ring-owu-red/10"
            />
            <button
              onClick={handleIngestEmail}
              disabled={emailLoading || !emailContent.trim() || !emailDate}
              className="flex items-center gap-2 text-sm font-medium text-white
                         bg-owu-red hover:bg-owu-red-light rounded-lg px-4 py-2
                         disabled:opacity-40 transition-colors"
            >
              {emailLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              Ingest Email
            </button>
          </div>
          <Feedback state={emailFeedback} />
        </section>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-owu-grey px-4 py-3">
      <p className="text-2xl font-semibold text-owu-text">{value}</p>
      <p className="text-xs text-owu-text-muted capitalize">{label}</p>
    </div>
  );
}

function Feedback({ state }: { state: FeedbackState }) {
  if (!state) return null;
  const isOk = state.type === "success";
  return (
    <div
      className={`mt-3 flex items-start gap-2 text-sm rounded-lg px-3 py-2 ${
        isOk
          ? "bg-green-50 text-green-700"
          : "bg-red-50 text-red-700"
      }`}
    >
      {isOk ? (
        <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
      ) : (
        <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
      )}
      <p>{state.message}</p>
    </div>
  );
}
