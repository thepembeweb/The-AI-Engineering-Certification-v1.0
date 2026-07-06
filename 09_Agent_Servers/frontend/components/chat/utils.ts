export type ChatMessage = {
  id?: string;
  type: string;
  content?: unknown;
  name?: string;
  tool_calls?: Array<{ id?: string; name?: string; args?: unknown }>;
};

export function getMessageText(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((block) => {
        if (typeof block === "string") return block;
        if (block && typeof block === "object" && "text" in block) {
          return String((block as { text?: unknown }).text ?? "");
        }
        return "";
      })
      .join("");
  }
  return "";
}

export function isNearBottom(viewport: HTMLElement) {
  return (
    viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight < 120
  );
}
