from __future__ import annotations

from datapizza.tools import tool

from goa_travel_agent.src.vector_db.searcher import HybridSearcher

_searcher: HybridSearcher | None = None


def set_searcher(searcher: HybridSearcher) -> None:
    global _searcher
    _searcher = searcher


def _get_searcher() -> HybridSearcher:
    if _searcher is None:
        raise RuntimeError("Searcher not initialized. Call set_searcher() first.")
    return _searcher


@tool
def discover_places_tool(query: str, category: str = "") -> str:
    """Search tourist attractions and places to visit in Goa.

    Args:
        query: Natural language description of what you want to do or see (e.g. 'romantic sunset spot')
        category: Filter by category - one of: Beach, Nightlife, Culture, Adventure, Wellness, Food. Empty means all.
    """
    searcher = _get_searcher()
    results = searcher.search_places(
        query=query,
        category=category or None,
        top_k=5,
    )

    if not results:
        return "No places found matching your query."

    lines = []
    for r in results:
        place = r.get("place", r.get("full_text", "N/A"))
        city = r.get("city", "?")
        cat = r.get("category", "General")
        review = r.get("review", "")
        snippet = (review[:150] + "...") if len(str(review)) > 150 else review
        lines.append(f"- {place} ({city}) [{cat}]: {snippet}")

    return "Places found:\n\n" + "\n".join(lines)
