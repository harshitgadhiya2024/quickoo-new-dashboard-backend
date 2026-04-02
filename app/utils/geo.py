import math

_EARTH_RADIUS_MILES = 3958.8


def haversine_miles(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Great-circle distance between two WGS84 points in miles."""
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.asin(min(1.0, math.sqrt(a)))
    return _EARTH_RADIUS_MILES * c
