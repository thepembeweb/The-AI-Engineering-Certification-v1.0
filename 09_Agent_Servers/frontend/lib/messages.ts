export function getMessageText(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((block) => {
        if (typeof block === "string") return block;
        if (block && typeof block === "object" && "text" in block) {
          const text = (block as { text?: unknown }).text;
          return typeof text === "string" ? text : "";
        }
        return "";
      })
      .join("");
  }
  return "";
}

export function toolLabel(name?: string): string {
  switch (name) {
    case "retrieve_information":
      return "Knowledge base";
    case "tavily_search":
    case "tavily_search_results_json":
      return "Web search";
    case "arxiv":
    case "arxiv_search":
      return "arXiv research";
    default:
      return name ?? "tool";
  }
}
