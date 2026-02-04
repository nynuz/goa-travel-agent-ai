from __future__ import annotations

import json

from datapizza.tools import tool

from goa_travel_agent.src.utils.geo_utils import (
    cluster_by_proximity,
    estimate_travel_time,
)


@tool
def optimize_itinerary(places_json: str, num_days: int) -> str:
    """Group places into day-clusters optimized by geographic proximity.

    Args:
        places_json: JSON array of places, each with at least 'place' and 'city' keys.
                     Example: [{"place": "Fort Aguada", "city": "candolim"}, ...]
        num_days: Number of days available for sightseeing
    """
    try:
        places = json.loads(places_json)
    except json.JSONDecodeError:
        return "Error: places_json must be a valid JSON array."

    if not places:
        return "No places provided."
    if num_days < 1:
        return "Please specify at least 1 day."

    clusters = cluster_by_proximity(places, num_days)

    lines = []
    for day_num, cluster in enumerate(clusters, start=1):
        lines.append(f"Day {day_num}:")
        for i, place in enumerate(cluster):
            name = place.get("place", place.get("property_name", "Unknown"))
            city = place.get("city", place.get("locality", ""))
            lines.append(f"  {i + 1}. {name} ({city})")

            # travel time to next place in cluster
            if i < len(cluster) - 1:
                next_place = cluster[i + 1]
                next_city = next_place.get("city", next_place.get("locality", ""))
                travel = estimate_travel_time(city, next_city)
                if travel is not None:
                    lines.append(f"     -> ~{travel:.0f} min to next stop")

        lines.append("")

    return "\n".join(lines)
