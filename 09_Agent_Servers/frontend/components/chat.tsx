"use client";

import { useEffect, useRef, useState } from "react";
import { useStream } from "@langchain/react";
import { ArrowDown, RotateCcw } from "lucide-react";

import { Composer } from "@/components/chat/composer";
import { EmptyState } from "@/components/chat/empty-state";
import { MessageBubble } from "@/components/chat/message-bubble";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import { isNearBottom, type ChatMessage } from "@/components/chat/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getMessageText, toolLabel } from "@/lib/messages";

function resolveApiUrl() {
  const value = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!value) {
    if (typeof window !== "undefined") {
      return new URL("/api", window.location.origin).href;
    }

    return "/api";
  }

  if (value.startsWith("/")) {
    if (typeof window !== "undefined") {
      return new URL(value, window.location.origin).href;
    }

    return value;
  }

  try {
    const url = new URL(value);
    if (url.protocol === "http:" || url.protocol === "https:") {
      return value;
    }
  } catch {
    // Fall through to default for malformed URLs.
  }

  if (typeof window !== "undefined") {
    return new URL("/api", window.location.origin).href;
  }

  return "/api";
}

const API_URL = resolveApiUrl();

export function Chat({ assistantId }: Readonly<{ assistantId: string }>) {
  const stream = useStream({ apiUrl: API_URL, assistantId });
  const { messages, isLoading, error, stop } = stream;

  const [input, setInput] = useState("");
  const [lastPrompt, setLastPrompt] = useState("");
  const [stuckToBottom, setStuckToBottom] = useState(true);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const viewport = document.querySelector<HTMLDivElement>(
      '[data-slot="scroll-area-viewport"]',
    );

    if (!viewport) return;

    const onScroll = () => setStuckToBottom(isNearBottom(viewport));
    onScroll();
    viewport.addEventListener("scroll", onScroll, { passive: true });

    return () => viewport.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (stuckToBottom) {
      endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages, isLoading, stuckToBottom]);

  const threadMessages = messages as ChatMessage[];
  const visibleMessages = threadMessages.filter((message) => {
    const text = getMessageText(message.content).trim();
    const isAssistantMessage =
      message.type === "ai" || message.type === "assistant";
    return !(isAssistantMessage && (text === "Y" || text === "N"));
  });

  const send = (text: string) => {
    const content = text.trim();
    if (!content || isLoading) return;
    setLastPrompt(content);
    stream.submit({ messages: [{ type: "human", content }] });
    setInput("");
  };

  const retry = () => {
    if (lastPrompt) send(lastPrompt);
  };

  const lastAiMessage = [...visibleMessages]
    .reverse()
    .find((message) => message.type === "ai" || message.type === "assistant");
  const activeToolCalls = lastAiMessage?.tool_calls ?? [];

  return (
    <div className="relative flex min-h-0 flex-1 flex-col">
      <ScrollArea className="flex-1 min-h-0">
        <div className="mx-auto flex min-h-full w-full max-w-5xl flex-col gap-5 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          {visibleMessages.length === 0 ? (
            <EmptyState onPick={send} />
          ) : (
            visibleMessages.map((message, index) => (
              <MessageBubble key={message.id ?? index} message={message} />
            ))
          )}

          {activeToolCalls.length > 0 && isLoading ? (
            <Card className="border-border/70 bg-card/85 shadow-sm">
              <CardContent className="flex flex-wrap items-center gap-2 p-4">
                {activeToolCalls.map((toolCall, index) => (
                  <span
                    key={toolCall.id ?? index}
                    className="inline-flex items-center gap-2 rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-sm font-medium text-primary"
                  >
                    <span className="size-2 rounded-full bg-primary animate-pulse" />
                    {toolLabel(toolCall.name)}
                  </span>
                ))}
              </CardContent>
            </Card>
          ) : null}

          {isLoading ? <TypingIndicator /> : null}

          {error ? (
            <Card className="border-destructive/30 bg-destructive/5">
              <CardContent className="flex items-center justify-between gap-4 p-4 text-sm">
                <div className="space-y-1">
                  <p className="font-medium text-destructive">
                    Something went wrong.
                  </p>
                  <p className="text-muted-foreground">
                    {error instanceof Error
                      ? error.message
                      : "The assistant could not finish that response."}
                  </p>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={retry}
                  disabled={!lastPrompt}
                >
                  <RotateCcw className="size-4" />
                  Retry
                </Button>
              </CardContent>
            </Card>
          ) : null}

          <div ref={endRef} />
        </div>
      </ScrollArea>

      {!stuckToBottom && visibleMessages.length > 0 ? (
        <div className="pointer-events-none absolute inset-x-0 bottom-24 flex justify-center px-4">
          <Button
            className="pointer-events-auto rounded-full shadow-lg"
            size="sm"
            variant="secondary"
            onClick={() =>
              endRef.current?.scrollIntoView({
                behavior: "smooth",
                block: "end",
              })
            }
          >
            <ArrowDown className="size-4" />
            Latest
          </Button>
        </div>
      ) : null}

      <Composer
        value={input}
        onChange={setInput}
        onSubmit={() => send(input)}
        onStop={() => void stop()}
        isLoading={isLoading}
      />
    </div>
  );
}
