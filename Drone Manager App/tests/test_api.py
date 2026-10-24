from fastapi.testclient import TestClient
from backend.app.main import app
import backend.app.routes.resources as resource_routes
import backend.app.routes.analytics as analytics_routes

class FakeStore:
    def __init__(self):
        self.data = {name: [] for name in ("drones", "batteries", "missions", "flights", "maintenance", "battery_history")}
        self.ready = True
        self.error = None
    def list(self, collection):
        return list(self.data.setdefault(collection, []))
    def create(self, collection, payload):
        item = dict(payload, id=f"{collection}-{len(self.data.setdefault(collection, []))+1}", created_at="2026-01-01T00:00:00Z")
        self.data[collection].append(item)
        return item
    def get(self, collection, item_id):
        return next((x for x in self.data.setdefault(collection, []) if x["id"] == item_id), None)
    def update(self, collection, item_id, payload):
        item = self.get(collection, item_id)
        if item is None:
            return None
        item.update(payload)
        return item
    def delete(self, collection, item_id):
        item = self.get(collection, item_id)
        if item is None:
            return False
        self.data[collection].remove(item)
        return True

def setup_fake_store(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(resource_routes, "get_store", lambda: fake)
    monkeypatch.setattr(analytics_routes, "get_store", lambda: fake)
    return fake

def test_frontend_and_static_assets():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert "Drone Manager" in client.get("/").text
    assert client.get("/assets/app.js").status_code == 200
    assert client.get("/assets/style.css").status_code == 200

def test_health_and_config(monkeypatch):
    setup_fake_store(monkeypatch)
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/config").json()["api_base_url"] == "/api/v1"
    assert client.get("/docs").status_code == 200

def test_drone_crud_and_analytics(monkeypatch):
    setup_fake_store(monkeypatch)
    client = TestClient(app)
    payload = {
        "name": "Test Drone", "manufacturer": "Test Maker", "model": "X1",
        "serial_number": "TEST-001", "drone_type": "Survey"
    }
    created = client.post("/api/v1/drones", json=payload)
    assert created.status_code == 201, created.text
    item_id = created.json()["id"]
    assert client.get("/api/v1/drones").json()["count"] == 1
    assert client.put(f"/api/v1/drones/{item_id}", json={"status": "INACTIVE"}).status_code == 200
    assert client.get("/api/v1/analytics/dashboard").json()["total_drones"] == 1
    assert client.delete(f"/api/v1/drones/{item_id}").status_code == 200

def test_unknown_api_route_is_404(monkeypatch):
    setup_fake_store(monkeypatch)
    client = TestClient(app)
    assert client.get("/api/v1/does-not-exist").status_code == 404
