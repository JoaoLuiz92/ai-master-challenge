"""Integration tests for T27: same input, same queue, no network (LEAD-30, LEAD-32)."""

import socket

from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import get_settings

QUEUE_PARAMS = {"view": "mine", "agent": "Anna Snelling"}


def _queue_bytes() -> bytes:
    with TestClient(create_app()) as client:
        response = client.get("/api/queue", params=QUEUE_PARAMS)
        assert response.status_code == 200
        assert response.json()["items"]
        return response.content


def test_lead_30_identical_input_yields_byte_identical_queue() -> None:
    assert _queue_bytes() == _queue_bytes()


def test_lead_30_queue_runs_offline_and_deals_stay_in_memory(monkeypatch) -> None:
    local = {"127.0.0.1", "localhost", "::1"}
    original_connect = socket.socket.connect
    original_create = socket.create_connection

    def host_of(address: object) -> str:
        if isinstance(address, tuple):
            return str(address[0])
        return str(address)

    def guarded_connect(self: socket.socket, address: object) -> None:
        host = host_of(address)
        if host not in local:
            raise AssertionError(f"critical path opened a network connection to {host}")
        original_connect(self, address)

    def guarded_create(address: object, *args: object, **kwargs: object) -> socket.socket:
        host = host_of(address)
        if host not in local:
            raise AssertionError(f"critical path opened a network connection to {host}")
        return original_create(address, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket, "create_connection", guarded_create)

    data_dir = get_settings().data_dir
    before = {path.name: path.stat().st_mtime_ns for path in data_dir.iterdir() if path.is_file()}

    with TestClient(create_app()) as client:
        response = client.get("/api/queue", params=QUEUE_PARAMS)
        assert response.status_code == 200
        assert response.json()["items"]
        assert client.app.state.deals
        assert client.app.state.raw_dataset is not None

    after = {path.name: path.stat().st_mtime_ns for path in data_dir.iterdir() if path.is_file()}
    assert after == before
