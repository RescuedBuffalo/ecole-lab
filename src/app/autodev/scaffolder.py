from __future__ import annotations

from pathlib import Path


FEATURE_DIR = Path(__file__).parent / "generated"


def validate_spec(spec: dict) -> None:
    required = {"id", "goal", "user_story", "constraints", "acceptance_tests"}
    missing = required - spec.keys()
    if missing:
        raise ValueError(f"missing keys: {missing}")


def scaffold(spec: dict) -> Path:
    validate_spec(spec)
    out = FEATURE_DIR / f"feature_{spec['id']}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "__init__.py").write_text("", encoding="utf-8")
    server = (
        "from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get('/ping')\n"
        "def ping():\n    return {'message': 'pong'}\n"
    )
    (out / "server.py").write_text(server, encoding="utf-8")
    test = (
        "from fastapi import FastAPI\n"
        "def test_ping():\n    from fastapi.testclient import TestClient\n"
        "    from .server import router\n    app = FastAPI()\n    app.include_router(router)\n    client = TestClient(app)\n    assert client.get('/ping').json()['message'] == 'pong'\n"
    )
    (out / "tests.py").write_text(test, encoding="utf-8")
    (out / "README.md").write_text(
        f"Generated feature {spec['id']}\n", encoding="utf-8"
    )
    return out
