"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

import { cn } from "@/lib/utils";

const components: Components = {
  a: ({ className, ...props }) => (
    <a
      className={cn(
        "font-medium underline decoration-primary/50 underline-offset-4 hover:text-primary",
        className,
      )}
      target="_blank"
      rel="noreferrer"
      {...props}
    />
  ),
  code: ({ className, children, ...props }) => {
    const inline = !className;
    return (
      <code
        className={cn(
          inline
            ? "rounded-md bg-muted px-1.5 py-0.5 text-[0.92em] font-medium"
            : "block overflow-x-auto rounded-xl bg-background/80 p-4 text-sm leading-6",
          className,
        )}
        {...props}
      >
        {children}
      </code>
    );
  },
  h1: ({ className, children, ...props }) => (
    <h1
      className={cn(
        "mb-2 mt-6 text-2xl font-semibold tracking-tight",
        className,
      )}
      {...props}
    >
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }) => (
    <h2
      className={cn(
        "mb-2 mt-5 text-xl font-semibold tracking-tight",
        className,
      )}
      {...props}
    >
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }) => (
    <h3
      className={cn("mb-1.5 mt-4 text-lg font-semibold", className)}
      {...props}
    >
      {children}
    </h3>
  ),
  li: ({ className, ...props }) => (
    <li className={cn("ml-5 list-disc py-0.5", className)} {...props} />
  ),
  p: ({ className, ...props }) => (
    <p
      className={cn("leading-7 [&:not(:first-child)]:mt-3", className)}
      {...props}
    />
  ),
  pre: ({ className, ...props }) => (
    <pre
      className={cn(
        "overflow-x-auto rounded-2xl border border-border/70 bg-background/80 p-4 text-sm leading-6 shadow-sm",
        className,
      )}
      {...props}
    />
  ),
  ul: ({ className, ...props }) => (
    <ul className={cn("space-y-1.5", className)} {...props} />
  ),
};

export function Markdown({ content }: Readonly<{ content: string }>) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {content}
    </ReactMarkdown>
  );
}
