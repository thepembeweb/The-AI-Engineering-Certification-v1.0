"use client";

import { useState } from "react";
import { Check, Copy, FileText, Search, Wrench } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Markdown } from "@/components/markdown";
import { cn } from "@/lib/utils";
import { getMessageText, type ChatMessage } from "./utils";

function toolIcon(name?: string) {
  if (name === "retrieve_information") return <FileText className="size-3" />;
  if (name?.startsWith("tavily")) return <Search className="size-3" />;
  if (name?.startsWith("arxiv")) return <Wrench className="size-3" />;
  return <Wrench className="size-3" />;
}

function toolLabel(name?: string) {
  if (name === "retrieve_information") return "Knowledge base";
  if (name?.startsWith("tavily")) return "Web search";
  if (name?.startsWith("arxiv")) return "arXiv research";
  return name ?? "tool";
}

export function MessageBubble({ message }: Readonly<{ message: ChatMessage }>) {
  const isHuman = message.type === "human";
  const isTool = message.type === "tool";
  const text = getMessageText(message.content);
  const [copied, setCopied] = useState(false);

  if (isTool) {
    return (
      <Card className="animate-message-in border-border/70 bg-muted/35 shadow-none">
        <CardContent className="space-y-2 p-4 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            {toolIcon(message.name)}
            <span className="font-medium text-foreground">
              {toolLabel(message.name)}
            </span>
            <span className="text-xs">result</span>
          </div>
          <details className="group rounded-2xl border border-border/60 bg-background/70 p-3">
            <summary className="cursor-pointer list-none text-sm font-medium text-muted-foreground">
              View details
            </summary>
            <div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-foreground/90">
              {text}
            </div>
          </details>
        </CardContent>
      </Card>
    );
  }

  return (
    <div
      className={cn(
        "group flex w-full items-end gap-3 animate-message-in",
        isHuman && "flex-row-reverse",
      )}
    >
      <div
        className={cn(
          "relative max-w-[min(44rem,85%)] rounded-3xl border px-4 py-3 shadow-sm transition-shadow",
          isHuman
            ? "border-primary/15 bg-primary text-primary-foreground shadow-primary/10"
            : "border-border/70 bg-card text-card-foreground",
        )}
      >
        {!isHuman && (
          <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
            <span aria-hidden className="size-2 rounded-full bg-primary" /> Cat
            Health Agent
          </div>
        )}

        <div className="text-sm leading-7">
          {isHuman ? (
            <p className="whitespace-pre-wrap">{text}</p>
          ) : (
            <Markdown content={text} />
          )}
        </div>

        <div className="mt-3 flex items-center justify-between gap-3">
          <div className="flex flex-wrap gap-1.5">
            {(message.tool_calls ?? []).map((toolCall, index) => (
              <Badge
                key={toolCall.id ?? index}
                variant="secondary"
                className="gap-1.5 rounded-full"
              >
                {toolIcon(toolCall.name)}
                {toolLabel(toolCall.name)}
              </Badge>
            ))}
          </div>

          {!isHuman && text ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 gap-1.5 rounded-full opacity-0 transition-opacity group-hover:opacity-100"
              onClick={async () => {
                await navigator.clipboard.writeText(text);
                setCopied(true);
                globalThis.setTimeout(() => setCopied(false), 2000);
              }}
            >
              {copied ? (
                <Check className="size-3.5" />
              ) : (
                <Copy className="size-3.5" />
              )}
              {copied ? "Copied" : "Copy"}
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
