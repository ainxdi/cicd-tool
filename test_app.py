import pytest

from app import create_app


@pytest.fixture()
def client():
    return create_app().test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_version(client):
    assert "version" in client.get("/version").get_json()


def test_create_and_list_task(client):
    resp = client.post("/tasks", json={"title": "write pipeline"})
    assert resp.status_code == 201
    assert resp.get_json()["done"] is False
    assert len(client.get("/tasks").get_json()) == 1


def test_create_task_requires_title(client):
    assert client.post("/tasks", json={"title": "  "}).status_code == 400


def test_complete_and_delete_task(client):
    task_id = client.post("/tasks", json={"title": "x"}).get_json()["id"]
    assert client.patch(f"/tasks/{task_id}").get_json()["done"] is True
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.delete(f"/tasks/{task_id}").status_code == 404


def test_ui_page_is_served(client):
    resp = client.get("/")
    assert resp.status_code == 200
    page = resp.get_data(as_text=True)
    assert "<title>Tasks</title>" in page
    assert "static/app.js" in page


def test_ui_static_assets_are_served(client):
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_complete_unknown_task_returns_404(client):
    assert client.patch("/tasks/999").status_code == 404
