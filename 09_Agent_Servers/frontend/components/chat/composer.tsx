"use client";

import { useEffect, useRef } from "react";
import { Loader2, Send, Square } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Composer({
  value,
  onChange,
  onSubmit,
  onStop,
  isLoading,
}: Readonly<{
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  isLoading: boolean;
}>) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [value]);

  return (
    <form
      className="mx-auto w-full max-w-5xl px-4 pb-4 pt-3 sm:px-6 lg:px-8"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div className="rounded-[1.75rem] border border-border/70 bg-card/95 p-3 shadow-[0_20px_80px_-32px_color-mix(in_oklch,var(--primary)_35%,transparent)] backdrop-blur-xl">
        <div className="flex items-end gap-3 rounded-[1.5rem] border border-border/70 bg-background/80 px-3 py-3 shadow-inner">
          <textarea
            ref={ref}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                onSubmit();
              }
            }}
            rows={1}
            placeholder="Ask about your cat’s symptoms, food, vaccines, or follow-up care…"
            disabled={isLoading}
            className={cn(
              "min-h-12 max-h-44 flex-1 resize-none bg-transparent px-1 py-2 text-sm leading-6 outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed",
            )}
          />

          <Button
            type="button"
            size="icon"
            variant={isLoading ? "destructive" : "default"}
            onClick={isLoading ? onStop : onSubmit}
            className="size-11 rounded-2xl"
            aria-label={isLoading ? "Stop generation" : "Send message"}
            disabled={!isLoading && value.trim().length === 0}
          >
            {isLoading ? (
              <Square className="size-4 fill-current" />
            ) : (
              <Send className="size-4" />
            )}
          </Button>
        </div>

        <div className="mt-2 flex items-center justify-between gap-3 px-2 text-[11px] text-muted-foreground">
          <span>Press Enter to send, Shift+Enter for a new line.</span>
          {isLoading ? (
            <span className="inline-flex items-center gap-1.5">
              <Loader2 className="size-3.5 animate-spin text-primary" />
              Generation in progress
            </span>
          ) : null}
        </div>
      </div>
    </form>
  );
}
