import os
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_generate_diagram_success(monkeypatch, tmp_path):
    """
    Tests the "happy path" of the API.
    We mock the agent to return a valid path to a temporary file.
    We expect a 200 OK response with an image.
    """
    fake_file_path = tmp_path / "test_diagram.png"
    fake_file_path.write_bytes(b"fake image data")

    async def mock_run_in_threadpool(func, prompt):
        return fake_file_path

    monkeypatch.setattr("src.api.run_in_threadpool", mock_run_in_threadpool)

    response = client.post("/diagrams/generate", json={"prompt": "create a test diagram"})

    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    assert response.content == b"fake image data"

    assert not os.path.exists(fake_file_path)


@pytest.mark.asyncio
async def test_generate_diagram_agent_failure(monkeypatch):
    """
    Tests the "sad path" of the API.
    We mock the agent to return an empty string, simulating a failure.
    We expect a 500 Internal Server Error.
    """
    async def mock_run_in_threadpool_fail(func, prompt):
        return ""

    monkeypatch.setattr("src.api.run_in_threadpool", mock_run_in_threadpool_fail)

    response = client.post("/diagrams/generate", json={"prompt": "this will fail"})

    assert response.status_code == 500
    assert "Agent failed to generate a valid diagram file" in response.json()["detail"]


def test_health_check():
    """Tests the simple health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
