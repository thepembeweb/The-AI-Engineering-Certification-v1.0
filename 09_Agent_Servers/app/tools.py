from __future__ import annotations

from typing import Annotated
from typing import List

import arxiv
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

from app.rag import retrieve_information


@tool
def arxiv_search(
    query: Annotated[str, "arXiv search query"],
    max_results: Annotated[int, "maximum number of papers to return"] = 5,
) -> str:
    """Search arXiv papers and return concise results."""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    # arxiv>=4 removed Search.results(); use Client.results(search).
    if hasattr(search, "results"):
        results = list(search.results())
    else:
        results = list(arxiv.Client().results(search))

    if not results:
        return "No arXiv papers found."

    lines = []
    for i, paper in enumerate(results, start=1):
        published = getattr(paper, "published", None)
        year = published.year if published else "n/a"
        summary = " ".join((paper.summary or "").split())
        lines.append(
            f"{i}. {paper.title} ({year})\n"
            f"URL: {paper.entry_id}\n"
            f"Summary: {summary[:300]}"
        )
    return "\n\n".join(lines)


def get_tool_belt() -> List:
    tavily_tool = TavilySearch(max_results=5)
    return [tavily_tool, arxiv_search, retrieve_information]
