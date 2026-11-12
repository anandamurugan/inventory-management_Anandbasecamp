"""Tests for the restocking recommendation and order endpoints."""


def test_recommendations_zero_budget_is_empty(client):
    data = client.get("/api/restocking/recommendations?budget=0").json()
    assert data["items"] == []
    assert data["total_cost"] == 0


def test_recommendations_never_exceed_budget(client):
    for budget in (500, 5000, 20000, 100000):
        data = client.get(f"/api/restocking/recommendations?budget={budget}").json()
        assert data["total_cost"] <= budget
        assert data["remaining"] == round(budget - data["total_cost"], 2)


def test_recommendations_only_growing_demand(client):
    data = client.get("/api/restocking/recommendations?budget=100000").json()
    assert data["items"]
    assert all(i["demand_gap"] > 0 and i["quantity"] <= i["demand_gap"] for i in data["items"])
    gaps = [i["demand_gap"] for i in data["items"]]
    assert gaps == sorted(gaps, reverse=True)


def test_place_order_and_list(client):
    rec = client.get("/api/restocking/recommendations?budget=20000").json()
    items = [{"sku": i["sku"], "quantity": i["quantity"]} for i in rec["items"]]
    resp = client.post("/api/restocking-orders", json={"budget": 20000, "items": items})
    assert resp.status_code == 201
    order = resp.json()
    assert order["total_cost"] == rec["total_cost"]
    assert order["lead_time_days"] == max(i["lead_time_days"] for i in rec["items"])
    assert order["id"] in [o["id"] for o in client.get("/api/restocking-orders").json()]


def test_place_order_rejects_bad_input(client):
    assert client.post("/api/restocking-orders", json={"budget": 100, "items": []}).status_code == 400
    assert client.post("/api/restocking-orders", json={"budget": 100, "items": [{"sku": "NOPE", "quantity": 1}]}).status_code == 400
    assert client.post("/api/restocking-orders", json={"budget": 1, "items": [{"sku": "WDG-001", "quantity": 10}]}).status_code == 400
