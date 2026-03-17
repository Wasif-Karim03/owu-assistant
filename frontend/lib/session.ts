import { v4 as uuidv4 } from "uuid";

const SESSION_KEY = "owu-assistant-session-id";

export function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return uuidv4();

  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = uuidv4();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export function resetSessionId(): string {
  const id = uuidv4();
  if (typeof window !== "undefined") {
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}
