const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Source {
  title: string;
  url?: string | null;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  sources: Source[];
  has_clarifying_question: boolean;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[] | null;
  created_at?: string;
}

export interface ApiError {
  error: string;
  code: string;
}

async function fetchWithRetry(
  input: RequestInfo,
  init?: RequestInit,
  retries = 1,
): Promise<Response> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(input, init);
      if (res.ok || res.status === 429 || res.status === 400) return res;
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, 1000));
        continue;
      }
      return res;
    } catch (err) {
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, 1000));
        continue;
      }
      throw err;
    }
  }
  throw new Error("Request failed after retries");
}

export async function sendMessage(
  sessionId: string | null,
  message: string,
): Promise<ChatResponse> {
  const res = await fetchWithRetry(`${API_URL}/api/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (res.status === 429) {
    const err: ApiError = {
      error:
        "You've sent a lot of messages! Please wait a minute before trying again.",
      code: "rate_limit",
    };
    throw err;
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err: ApiError = {
      error: body.detail || "Failed to send message",
      code: "api_error",
    };
    throw err;
  }

  return res.json();
}

export async function getHistory(sessionId: string): Promise<Message[]> {
  const res = await fetchWithRetry(`${API_URL}/api/chat/history/${sessionId}`);
  if (!res.ok) return [];
  return res.json();
}

export async function clearHistory(sessionId: string): Promise<void> {
  await fetch(`${API_URL}/api/chat/history/${sessionId}`, {
    method: "DELETE",
  });
}

export function isApiError(err: unknown): err is ApiError {
  return (
    typeof err === "object" &&
    err !== null &&
    "code" in err &&
    "error" in err
  );
}
