from __future__ import annotations

import time

from datapizza.tools import tool

from goa_travel_agent.config.settings import settings
from goa_travel_agent.src.utils.logger import get_logger

log = get_logger(__name__)

MAX_RETRIES = 2


@tool
def verify_hotel(hotel_name: str, locality: str = "Goa") -> str:
    """Verify if a hotel is currently operational by searching the web.

    Args:
        hotel_name: Name of the hotel to verify
        locality: Locality or area of the hotel
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        return f"Tavily not installed. Cannot verify '{hotel_name}'."

    if not settings.TAVILY_API_KEY:
        return f"Tavily API key not configured. Cannot verify '{hotel_name}'."

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    query = f"Hotel {hotel_name} {locality} Goa India reviews status 2025"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = client.search(query=query, max_results=3, search_depth="basic")
            results = result.get("results", [])
            if not results:
                return f"No online information found for '{hotel_name}' in {locality}."

            summaries = []
            for r in results:
                title = r.get("title", "")
                snippet = r.get("content", "")[:200]
                url = r.get("url", "")
                summaries.append(f"  - {title}: {snippet} ({url})")

            return (
                f"Verification results for '{hotel_name}' ({locality}):\n"
                + "\n".join(summaries)
            )

        except Exception as exc:
            log.warning("Tavily attempt %d failed: %s", attempt, exc)
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
            else:
                return f"Could not verify '{hotel_name}': {exc}"

    return f"Verification failed for '{hotel_name}'."


@tool
def search_place_info(query: str, location: str = "Goa India") -> str:
    """Search the web for current information about tourist places, attractions, or activities.

    Args:
        query: What to search for (e.g. 'best time to visit Anjuna Beach', 'Dudhsagar waterfall entry fees 2025')
        location: Geographic context for the search
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        return "Tavily not installed. Cannot perform web search."

    if not settings.TAVILY_API_KEY:
        return "Tavily API key not configured. Cannot perform web search."

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    full_query = f"{query} {location}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = client.search(
                query=full_query,
                max_results=4,
                search_depth="basic",
                include_answer=True,
            )

            # Get the AI-generated answer if available
            answer = result.get("answer", "")
            results = result.get("results", [])

            if not answer and not results:
                return f"No web information found for: {query}"

            output_lines = []

            if answer:
                output_lines.append(f"Current information: {answer}\n")

            if results:
                output_lines.append("Sources:")
                for r in results[:3]:
                    title = r.get("title", "")
                    snippet = r.get("content", "")[:180]
                    url = r.get("url", "")
                    output_lines.append(f"  - {title}: {snippet}... ({url})")

            return "\n".join(output_lines)

        except Exception as exc:
            log.warning("Tavily search attempt %d failed: %s", attempt, exc)
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
            else:
                return f"Web search failed: {exc}"

    return f"Web search failed after {MAX_RETRIES} attempts."
