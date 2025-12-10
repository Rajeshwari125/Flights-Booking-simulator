# pricing.py
from datetime import datetime, timezone
import math

def _parse_departure_iso(departure_iso):
    """
    Robust parsing for departure time strings.
    Accepts:
      - 'YYYY-MM-DDTHH:MM:SS'
      - 'YYYY-MM-DD HH:MM:SS'
      - 'YYYY-MM-DD'
    Returns a timezone-aware datetime if possible; otherwise uses naive datetime.
    """
    if not departure_iso:
        return None
    s = str(departure_iso).strip()
    # normalize space -> T for fromisoformat if needed
    s = s.replace(" ", "T")
    try:
        dt = datetime.fromisoformat(s)
        # if no tzinfo, keep naive (we'll calculate relative to now naive)
        return dt
    except Exception:
        # last-resort parsing (YYYY-MM-DD)
        try:
            return datetime.strptime(s.split("T")[0], "%Y-%m-%d")
        except Exception:
            return None

def compute_dynamic_price(base_fare,
                          seats_available,
                          seats_total,
                          departure_iso,
                          demand_index=1.0,
                          now_dt=None):
    """
    Compute a dynamic price based on base fare, seats remaining, time to departure, and demand.
    Returns rounded float price.

    Tunable parameters:
      - k_seat, p_seat control seat scarcity effect
      - time thresholds control time-to-departure effect
      - min/max multipliers limit extreme swings
    """

    # Basic validation and normalization
    try:
        base_fare = float(base_fare)
    except Exception:
        base_fare = 0.0

    try:
        seats_total = int(seats_total) if seats_total is not None else 1
    except Exception:
        seats_total = 1
    if seats_total <= 0:
        seats_total = 1

    try:
        seats_available = int(seats_available) if seats_available is not None else seats_total
    except Exception:
        seats_available = seats_total
    seats_available = max(0, min(seats_available, seats_total))

    try:
        demand_index = float(demand_index)
    except Exception:
        demand_index = 1.0
    # bound demand reasonable range
    demand_index = max(0.5, min(demand_index, 5.0))

    # compute seats percentage
    seats_pct = seats_available / seats_total  # 1.0 means all seats available

    # Seat scarcity factor: increases price when seats_pct is low
    # seat_factor added multiplicatively as (1 + seat_factor)
    k_seat = 1.2   # maximum ~ +20% influenced by seats scarcity
    p_seat = 1.5   # exponent for non-linear effect
    seat_factor = k_seat * ((1 - seats_pct) ** p_seat)

    # Time-to-departure factor
    dep_dt = _parse_departure_iso(departure_iso)
    if now_dt is None:
        now_dt = datetime.now(dep_dt.tzinfo) if dep_dt and dep_dt.tzinfo else datetime.now()
    hours_to_dep = None
    if dep_dt:
        diff = dep_dt - now_dt
        hours_to_dep = diff.total_seconds() / 3600.0
        hours_to_dep = max(hours_to_dep, 0.0)
    else:
        # no departure info -> assume long time away
        hours_to_dep = 9999.0

    # Piecewise time factor (examples — tune for your use case)
    if hours_to_dep > 168:       # > 1 week
        time_factor = 0.00
    elif hours_to_dep > 72:      # 3-7 days
        time_factor = 0.05
    elif hours_to_dep > 24:      # 1-3 days
        time_factor = 0.15
    elif hours_to_dep > 6:       # 6-24 hours
        time_factor = 0.35
    else:                        # <6 hours
        time_factor = 0.60

    # Combine effects
    dynamic = base_fare * (1 + seat_factor) * (1 + time_factor) * demand_index

    # Safety bounds so price does not explode or drop too low
    min_price = base_fare * 0.6    # floor at 60% of base fare
    max_price = base_fare * 4.0    # ceiling at 400% (tunable)
    # If base_fare == 0, fallback to a small minimum
    if base_fare <= 0:
        min_price = 1.0
        max_price = max(1.0, max_price)

    dynamic = max(min_price, min(dynamic, max_price))

    # Round to 2 decimals
    return round(float(dynamic), 2)


# Small convenience wrapper for safe access when passing sqlite row/dict
def compute_dynamic_price_from_record(record):
    """
    record: mapping-like with keys:
      - base_fare or price
      - seats_available or seats
      - seats_total
      - departure_time or times
      - demand_index

    Example:
      compute_dynamic_price_from_record(dict(row))
    """
    base_fare = record.get('base_fare') or record.get('price') or 0.0
    seats_available = record.get('seats_available') or record.get('seats') or record.get('seats_total') or 0
    seats_total = record.get('seats_total') or record.get('seats') or seats_available or 1
    departure = record.get('departure_time') or record.get('times') or record.get('time')
    demand_index = record.get('demand_index') or 1.0

    return compute_dynamic_price(base_fare, seats_available, seats_total, departure, demand_index)
