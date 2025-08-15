from fastapi import FastAPI


def test_ping():
    from fastapi.testclient import TestClient
    from .server import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    assert client.get("/ping").json()["message"] == "pong"
