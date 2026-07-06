"use client";

import { Cat, Droplets, Pill, Sparkles, Syringe } from "lucide-react";

import { Button } from "@/components/ui/button";

const suggestions = [
  {
    icon: Pill,
    title: "Deworming",
    prompt: "How often should I deworm my cat?",
  },
  {
    icon: Syringe,
    title: "Kitten vaccines",
    prompt: "What vaccinations do kittens need?",
  },
  {
    icon: Droplets,
    title: "Dehydration signs",
    prompt: "What are signs of feline dehydration?",
  },
];

export function EmptyState({
  onPick,
}: Readonly<{ onPick: (text: string) => void }>) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-8 px-4 py-8 text-center">
      <div className="relative animate-message-in">
        <div className="absolute inset-0 -z-10 rounded-full bg-primary/15 blur-3xl" />
        <div className="flex size-20 items-center justify-center rounded-[2rem] bg-linear-to-br from-primary via-primary/90 to-chart-2 text-primary-foreground shadow-2xl shadow-primary/20">
          <Cat className="size-9" />
        </div>
      </div>

      <div className="max-w-2xl space-y-3 animate-message-in [animation-delay:80ms]">
        <div className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur">
          <Sparkles className="size-3.5 text-primary" />
          Friendly guidance for everyday cat care
        </div>
        <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl lg:text-5xl">
          Meow! How can I help your cat today?
        </h2>
        <p className="mx-auto max-w-xl text-balance text-sm leading-7 text-muted-foreground sm:text-base">
          Ask about symptoms, vaccines, nutrition, behavior, or practical next
          steps. The assistant will stream a thoughtful answer and call tools
          when needed.
        </p>
      </div>

      <div className="grid w-full max-w-3xl gap-3 sm:grid-cols-3">
        {suggestions.map(({ icon: Icon, title, prompt }, index) => (
          <Button
            key={prompt}
            variant="outline"
            className="h-auto flex-col items-start gap-2 rounded-2xl border-border/80 bg-card px-4 py-4 text-left shadow-sm transition-all duration-200 animate-message-in hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md"
            onClick={() => onPick(prompt)}
            style={{ animationDelay: `${160 + index * 90}ms` }}
          >
            <span className="flex size-8 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Icon className="size-4" />
            </span>
            <span className="text-sm font-semibold">{title}</span>
            <span className="whitespace-normal text-xs leading-5 text-muted-foreground">
              {prompt}
            </span>
          </Button>
        ))}
      </div>
    </div>
  );
}
