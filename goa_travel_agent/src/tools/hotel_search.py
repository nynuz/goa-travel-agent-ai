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
def hotel_search_tool(query: str, min_stars: float = 0, min_rating: float = 0, locality: str = "") -> str:
    """Search hotels in Goa by description, star rating, review rating and locality.

    Args:
        query: Natural language description of desired hotel (e.g. 'luxury resort with pool near beach')
        min_stars: Minimum star rating (1-5), 0 means no filter
        min_rating: Minimum review rating (0-5), 0 means no filter
        locality: Specific locality name (e.g. 'Candolim'), empty means all
    """
    searcher = _get_searcher()
    results = searcher.search_hotels(
        query=query,
        min_stars=min_stars,
        min_rating=min_rating,
        locality=locality or None,
        top_k=5,
    )

    if not results:
        return "No hotels found matching your criteria."

    lines = []
    for r in results:
        name = r.get("property_name", "N/A")
        stars = r.get("hotel_star_rating", "?")
        rating = r.get("site_review_rating", "?")
        loc = r.get("locality", "?")
        facilities = r.get("hotel_facilities", "N/A")
        reviews = r.get("site_review_count", 0)
        room = r.get("room_type", "N/A")
        lines.append(
            f"- {name} | Stars: {stars} | Rating: {rating}/5 ({reviews} reviews) | "
            f"Locality: {loc} | Room: {room} | Facilities: {facilities}"
        )

    return "Hotel results:\n\n" + "\n".join(lines)
