from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_roles_endpoint_lists_roles():
    response = client.get("/roles")
    assert response.status_code == 200
    assert any(r["role"] == "Backend Developer" for r in response.json())


def test_analyse_returns_score_and_path():
    response = client.post("/analyse", json={
        "role": "Backend Developer", "skills": {"python": 3, "sql": 2}})
    body = response.json()
    assert response.status_code == 200
    assert 0 <= body["readiness"] <= 100
    assert len(body["learning_path"]) > 0


def test_unknown_role_returns_404():
    response = client.post("/analyse", json={"role": "Wizard", "skills": {}})
    assert response.status_code == 404

def test_invalid_skill_level_returns_422():
    response = client.post("/analyse", json={
        "role": "Backend Developer", "skills": {"python": 9}})
    assert response.status_code == 422