# test_pricing.py
from pricing import compute_dynamic_price
from datetime import datetime, timedelta

def test_normal_case():
    base = 100.0
    seats_total = 150
    seats_available = 150
    dep = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    price = compute_dynamic_price(base, seats_available, seats_total, dep, demand_index=1.0)
    assert price >= base * 0.6  # floor check
    assert price <= base * 4.0

def test_near_departure_scarce():
    base = 100.0
    seats_total = 150
    seats_available = 2
    dep = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    price = compute_dynamic_price(base, seats_available, seats_total, dep, demand_index=1.5)
    assert price > base  # should be higher than base fare

if __name__ == "__main__":
    test_normal_case()
    test_near_departure_scarce()
    print("pricing tests passed")
