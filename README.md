# ecole-lab

Prototype "3-AI" system that allocates, writes and ships text content.
Everything runs locally with deterministic mocks.

## Quickstart

```bash
cp .env.example .env
docker compose up --build
```

Then seed plays:

```bash
docker compose exec api python -m src.app.seeds.seed_plays
```

Run a task:

```bash
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"topic":"Active recall for exam week","audience":"college students","objective":"subs","tone":"friendly, practical"}'
```

Outbox files appear under `/outbox/<attempt_id>/`.

AutoDev example:

```bash
curl -X POST http://localhost:8000/autodev/scaffold \
  -H 'Content-Type: application/json' \
  -d '{"id":"demo","goal":"ping","user_story":"as user","constraints":{},"acceptance_tests":[{}]}'
```

## Testing

```
poetry install
poetry run pytest
```
