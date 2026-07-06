"use client";

import { useState } from "react";
import { Cat } from "lucide-react";

import { Chat } from "@/components/chat";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

const ASSISTANT_ID = process.env.NEXT_PUBLIC_ASSISTANT_ID ?? "simple_agent";

export default function Page() {
  const [chatKey, setChatKey] = useState(0);

  return (
    <main className="relative flex h-dvh flex-col overflow-hidden bg-[radial-gradient(circle_at_top_left,color-mix(in_oklch,var(--primary)_18%,transparent),transparent_40%),radial-gradient(circle_at_top_right,color-mix(in_oklch,var(--chart-2)_12%,transparent),transparent_35%),linear-gradient(180deg,var(--background),color-mix(in_oklch,var(--background)_92%,var(--secondary)))]">
      <header className="relative z-10 border-b border-border/70 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-2xl bg-linear-to-br from-primary via-primary/90 to-chart-2 text-primary-foreground shadow-lg shadow-primary/20">
              <Cat className="size-5" />
            </div>
            <div className="leading-tight">
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold tracking-tight sm:text-base">
                  Cat Health Agent
                </p>
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-300">
                  <span
                    aria-hidden
                    className="size-1.5 rounded-full bg-emerald-500"
                  />{" "}
                  online
                </span>
              </div>
              <p className="text-xs text-muted-foreground sm:text-sm">
                Warm, research-backed guidance for feline care
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setChatKey((v) => v + 1)}
            >
              New chat
            </Button>
          </div>
        </div>
      </header>

      <Chat key={chatKey} assistantId={ASSISTANT_ID} />
    </main>
  );
}
