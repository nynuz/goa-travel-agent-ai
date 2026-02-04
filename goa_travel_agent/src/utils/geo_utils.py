from __future__ import annotations

import math

# Hardcoded coordinates for ~30 Goa localities (lat, lon)
GOA_COORDS: dict[str, tuple[float, float]] = {
    "agonda": (14.9888, 74.0023),
    "anjuna": (15.5739, 73.7413),
    "arambol": (15.6868, 73.7042),
    "assagao": (15.5935, 73.7631),
    "baga": (15.5551, 73.7514),
    "bardez": (15.5600, 73.7800),
    "benaulim": (15.2640, 73.9295),
    "calangute": (15.5439, 73.7555),
    "canacona": (15.0100, 74.0500),
    "candolim": (15.5176, 73.7620),
    "chapora": (15.6044, 73.7351),
    "colva": (15.2798, 73.9221),
    "divar island": (15.5100, 73.8800),
    "dona paula": (15.3955, 73.8079),
    "margao": (15.2832, 73.9862),
    "marmagao": (15.3989, 73.7929),
    "mapusa": (15.5923, 73.8080),
    "mobor": (15.2108, 73.9275),
    "morjim": (15.6308, 73.7273),
    "nuvem": (15.3100, 73.9400),
    "old goa": (15.5009, 73.9116),
    "palolem": (15.0100, 74.0230),
    "panjim": (15.4909, 73.8278),
    "porvorim": (15.5200, 73.8200),
    "quepem": (15.2131, 74.0780),
    "saligao": (15.5654, 73.7840),
    "sangolda": (15.5500, 73.7900),
    "sanguem": (15.2300, 74.1500),
    "sanquelim": (15.5600, 74.0100),
    "vagator": (15.5979, 73.7353),
    "varca": (15.2340, 73.9310),
    "vasco da gama": (15.3982, 73.8113),
    "velsao": (15.3700, 73.8600),
    "verna": (15.3600, 73.9400),
}

TRAFFIC_FACTOR = 1.5  # Goa roads multiplier
AVG_SPEED_KMH = 30  # average speed in Goa (accounting for traffic)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_between(loc1: str, loc2: str) -> float | None:
    """Return approximate distance in km between two Goa localities."""
    c1 = GOA_COORDS.get(loc1.lower())
    c2 = GOA_COORDS.get(loc2.lower())
    if c1 is None or c2 is None:
        return None
    return haversine(c1[0], c1[1], c2[0], c2[1])


def estimate_travel_time(loc1: str, loc2: str) -> float | None:
    """Estimate travel time in minutes between two localities (with traffic factor)."""
    dist = distance_between(loc1, loc2)
    if dist is None:
        return None
    return (dist / AVG_SPEED_KMH) * 60 * TRAFFIC_FACTOR


def cluster_by_proximity(
    places: list[dict], num_days: int
) -> list[list[dict]]:
    """Group places into clusters (one per day) by geographic proximity.

    Uses a simple greedy nearest-neighbor clustering.
    Each place dict should have a 'city' or 'locality' key.
    """
    if not places or num_days <= 0:
        return []

    def _get_loc(p: dict) -> str:
        return (p.get("locality") or p.get("city") or "").lower()

    def _get_coords(p: dict) -> tuple[float, float] | None:
        loc = _get_loc(p)
        return GOA_COORDS.get(loc)

    # Assign coordinates
    items = []
    for p in places:
        coords = _get_coords(p)
        if coords:
            items.append((p, coords))
        else:
            items.append((p, (15.4, 73.9)))  # fallback: central Goa

    if len(items) <= num_days:
        return [[item[0]] for item in items]

    # Greedy clustering: pick a seed, grab nearest neighbors
    remaining = list(range(len(items)))
    clusters: list[list[dict]] = []
    per_day = max(1, len(items) // num_days)

    for _ in range(num_days):
        if not remaining:
            break
        seed_idx = remaining[0]
        cluster_indices = [seed_idx]
        remaining.remove(seed_idx)

        while len(cluster_indices) < per_day and remaining:
            last_coords = items[cluster_indices[-1]][1]
            best_idx = min(
                remaining,
                key=lambda i: haversine(last_coords[0], last_coords[1], items[i][1][0], items[i][1][1]),
            )
            cluster_indices.append(best_idx)
            remaining.remove(best_idx)

        clusters.append([items[i][0] for i in cluster_indices])

    # Distribute remaining
    for i, idx in enumerate(remaining):
        clusters[i % len(clusters)].append(items[idx][0])

    return clusters
