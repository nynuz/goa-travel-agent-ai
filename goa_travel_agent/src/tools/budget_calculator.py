from __future__ import annotations

from datapizza.tools import tool

# Average costs in INR (2025 estimates)
HOTEL_COSTS = {
    3: (2500, 4000),
    4: (5000, 8000),
    5: (10000, 18000),
}

FOOD_COSTS = {
    "budget": {"breakfast": 200, "lunch": 400, "dinner": 600},
    "moderate": {"breakfast": 350, "lunch": 600, "dinner": 900},
    "luxury": {"breakfast": 500, "lunch": 800, "dinner": 1200},
}

TRANSPORT_COSTS = {
    "airport_taxi": (800, 1500),
    "scooter_per_day": (300, 500),
    "taxi_per_day": (500, 1000),
}

ACTIVITY_COSTS = {
    "water_sports": (500, 2000),
    "spa": (2000, 5000),
    "boat_cruise": (1000, 3000),
    "museum_entry": (50, 300),
}


@tool
def estimate_budget(num_days: int, hotel_stars: int = 3, travel_style: str = "moderate") -> str:
    """Estimate total trip budget for Goa.

    Args:
        num_days: Number of days/nights for the trip
        hotel_stars: Hotel star rating (3, 4, or 5)
        travel_style: One of 'budget', 'moderate', or 'luxury'
    """
    if num_days < 1:
        return "Please specify at least 1 day."

    style = travel_style.lower()
    if style not in FOOD_COSTS:
        style = "moderate"

    stars = max(3, min(5, hotel_stars))
    hotel_min, hotel_max = HOTEL_COSTS[stars]
    food = FOOD_COSTS[style]
    daily_food = food["breakfast"] + food["lunch"] + food["dinner"]

    transport_daily_min, transport_daily_max = TRANSPORT_COSTS["scooter_per_day"] if style == "budget" else TRANSPORT_COSTS["taxi_per_day"]
    airport_min, airport_max = TRANSPORT_COSTS["airport_taxi"]

    # Activities: assume 1 activity per day
    act_min, act_max = (300, 1000) if style == "budget" else (500, 2000) if style == "moderate" else (1000, 5000)

    total_min = (hotel_min + daily_food + transport_daily_min + act_min) * num_days + airport_min * 2
    total_max = (hotel_max + daily_food + transport_daily_max + act_max) * num_days + airport_max * 2

    daily_min = hotel_min + daily_food + transport_daily_min + act_min
    daily_max = hotel_max + daily_food + transport_daily_max + act_max

    lines = [
        f"Budget Estimate for {num_days}-day Goa Trip ({style.title()} style, {stars}-star hotel):",
        "",
        f"  Hotel ({stars}-star): Rs.{hotel_min:,}-{hotel_max:,}/night",
        f"  Food: Rs.{daily_food:,}/day",
        f"  Transport: Rs.{transport_daily_min:,}-{transport_daily_max:,}/day",
        f"  Activities: Rs.{act_min:,}-{act_max:,}/day",
        f"  Airport transfers: Rs.{airport_min:,}-{airport_max:,} (round trip)",
        "",
        f"  Daily total: Rs.{daily_min:,} - Rs.{daily_max:,}",
        f"  TRIP TOTAL: Rs.{total_min:,} - Rs.{total_max:,}",
        f"  (approx. ${total_min // 83:,} - ${total_max // 83:,} USD)",
        "",
        "Tips:",
    ]

    if style == "budget":
        lines.append("  - Rent a scooter to save on transport")
        lines.append("  - Eat at local shacks for authentic food at lower prices")
    elif style == "luxury":
        lines.append("  - Book spa packages for better deals")
        lines.append("  - Consider all-inclusive resort packages")
    else:
        lines.append("  - Mix beach shack meals with restaurant dinners")
        lines.append("  - Book activities through your hotel for group discounts")

    return "\n".join(lines)
