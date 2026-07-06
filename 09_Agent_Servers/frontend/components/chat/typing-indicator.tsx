"use client";

import { Loader2 } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-message-in">
      <div className="flex size-11 items-center justify-center rounded-2xl border border-border/70 bg-card shadow-sm">
        <Loader2 className="size-4 animate-spin text-primary" />
      </div>
      <div className="flex items-center gap-2 rounded-2xl border border-border/70 bg-card px-4 py-3 text-sm text-muted-foreground shadow-sm">
        <span className="inline-flex items-center gap-1.5">
          <span className="size-2 rounded-full bg-primary/70 animate-typing-dot-1" />
          <span className="size-2 rounded-full bg-primary/70 animate-typing-dot-2" />
          <span className="size-2 rounded-full bg-primary/70 animate-typing-dot-3" />
        </span>
        Thinking about the best answer…
      </div>
    </div>
  );
}
