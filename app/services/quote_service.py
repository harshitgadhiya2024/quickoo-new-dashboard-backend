from typing import Any

from app.db.mongodb import get_database
from app.schemas.quote import (
    Location,
    PriceBreakdownLine,
    QuoteRequest,
    QuoteResponse,
    VehicleQuoteItem,
)
from app.utils.geo import haversine_miles

_VAT_RATE = 0.20


def _round_money(value: float) -> float:
    return round(value, 2)


def _mileage_price(
    distance_miles: float,
    base_price: float,
    base_price_per_default_miles: int,
    extra_price_per_miles: float,
) -> float:
    if distance_miles <= base_price_per_default_miles:
        return float(base_price)
    extra_miles = distance_miles - base_price_per_default_miles
    return float(base_price) + extra_miles * float(extra_price_per_miles)


def _pickup_surcharge_key(doc: dict) -> str:
    pt = doc.get("pickup_type", "")
    apt = doc.get("additional_pricing_type", "")
    return f"{pt}_{apt}".strip("_") or "pickup_surcharge"


async def _fetch_airport_pickup_surcharges() -> list[dict[str, Any]]:
    db = get_database()
    cursor = db.extra_pickup_types.find({"is_active": True})
    docs = await cursor.to_list(length=None)
    return [
        d
        for d in docs
        if (d.get("pickup_type") or "").strip().lower() == "airport"
    ]


async def _fetch_active_vehicle_classes() -> list[dict]:
    db = get_database()
    cursor = db.vehicle_classes.find({"is_active": True}).sort("created_at", -1)
    return await cursor.to_list(length=None)


def _distance_between(from_loc: Location, to_loc: Location) -> float:
    return haversine_miles(
        from_loc.latitude,
        from_loc.longitude,
        to_loc.latitude,
        to_loc.longitude,
    )


async def generate_quotes(payload: QuoteRequest) -> QuoteResponse:
    distance_miles = _round_money(
        _distance_between(payload.from_, payload.to)
    )

    quotes_break_down_price_list: list[dict[str, Any]] = []
    surcharge_docs: list[dict] = []

    pt = (payload.pickup_type or "").strip().lower()
    if pt == "airport":
        surcharge_docs = await _fetch_airport_pickup_surcharges()
        for doc in surcharge_docs:
            key = _pickup_surcharge_key(doc)
            amount = int(doc.get("base_price", 0))
            quotes_break_down_price_list.append({key: amount})

    surcharges_total = sum(int(doc.get("base_price", 0)) for doc in surcharge_docs)

    vehicles = await _fetch_active_vehicle_classes()
    vehicle_quotes: list[VehicleQuoteItem] = []

    for vc in vehicles:
        mileage = _mileage_price(
            distance_miles,
            vc["base_price"],
            vc["base_price_per_default_miles"],
            vc["extra_price_per_miles"],
        )
        mileage = _round_money(mileage)

        breakdown: list[tuple[str, float]] = []

        for doc in surcharge_docs:
            label = (
                f"Pickup surcharge ({doc.get('pickup_type', '')} / "
                f"{doc.get('additional_pricing_type', '')})"
            ).strip()
            amt = float(int(doc.get("base_price", 0)))
            breakdown.append((label, amt))

        breakdown.append(
            (
                f"Distance pricing ({distance_miles} mi, "
                f"first {vc['base_price_per_default_miles']} mi base, "
                f"then {vc['extra_price_per_miles']} per mi)",
                mileage,
            )
        )

        subtotal_before_vat = _round_money(surcharges_total + mileage)
        vat_amount = _round_money(subtotal_before_vat * _VAT_RATE)
        breakdown.append(("VAT (20%)", vat_amount))

        total_price = _round_money(subtotal_before_vat + vat_amount)

        vehicle_quotes.append(
            VehicleQuoteItem(
                vehicle_class_id=vc["vehicle_class_id"],
                vehicle_class_image=vc["vehicle_class_image"],
                class_name=vc["class_name"],
                allow_passengers=vc["allow_passengers"],
                allow_luggage=vc["allow_luggage"],
                base_price=float(vc["base_price"]),
                base_price_per_default_miles=int(vc["base_price_per_default_miles"]),
                extra_price_per_miles=float(vc["extra_price_per_miles"]),
                is_active=bool(vc["is_active"]),
                price_breakdown=[
                    PriceBreakdownLine(description=d, amount=a) for d, a in breakdown
                ],
                total_price=total_price,
            )
        )

    return QuoteResponse(
        distance_miles=distance_miles,
        quotes_break_down_price_list=quotes_break_down_price_list,
        vehicle_quotes=vehicle_quotes,
    )
