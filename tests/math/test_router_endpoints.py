import asyncio
from typing import Dict, Any

from httpx import AsyncClient
from sqlalchemy import select

from src.app.db import async_session_maker
from src.app.models import Participant, Session, Item, Attempt


async def test_create_participant(app):
    """Test participant creation endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/math/participants",
            json={"age_band": "7-9", "interests": ["Sports", "Music"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "participant_id" in data

        # Verify participant was created in database
        async with async_session_maker() as session:
            participant = await session.get(Participant, data["participant_id"])
            assert participant is not None
            assert participant.age_band == "7-9"
            assert participant.interests == ["Sports", "Music"]


async def test_create_session_default_params(app):
    """Test session creation with default parameters."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create participant first
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "10-12", "interests": []}
        )
        participant_id = participant_resp.json()["participant_id"]

        # Create session with minimal payload
        response = await client.post(
            "/math/sessions", json={"participant_id": participant_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        session_id = data["session_id"]

        # Verify session was created with defaults
        async with async_session_maker() as session:
            session_obj = await session.get(Session, session_id)
            assert session_obj is not None
            assert session_obj.participant_id == participant_id
            assert session_obj.skill == "pythagorean.find_c"  # default

            # Check that items were created (default 5 pairs = 10 items)
            result = await session.execute(
                select(Item).where(Item.session_id == session_id)
            )
            items = result.scalars().all()
            assert len(items) == 10  # 5 pairs * 2 items per pair


async def test_create_session_custom_params(app):
    """Test session creation with custom parameters."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create participant
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "13-15", "interests": ["Games"]}
        )
        participant_id = participant_resp.json()["participant_id"]

        # Create session with custom parameters
        response = await client.post(
            "/math/sessions",
            json={
                "participant_id": participant_id,
                "skill": "pythagorean.find_leg",
                "n_pairs": 3,
                "motif": "Sports",
                "difficulty_mix": [4, 4, 4],
            },
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]

        # Verify session and items
        async with async_session_maker() as session:
            session_obj = await session.get(Session, session_id)
            assert session_obj.skill == "pythagorean.find_leg"

            result = await session.execute(
                select(Item).where(Item.session_id == session_id)
            )
            items = result.scalars().all()
            assert len(items) == 6  # 3 pairs * 2 items per pair
            assert all(item.motif == "Sports" for item in items)


async def test_get_next_item(app):
    """Test getting next item from a session."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup: create participant and session
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "7-9", "interests": []}
        )
        participant_id = participant_resp.json()["participant_id"]

        session_resp = await client.post(
            "/math/sessions", json={"participant_id": participant_id, "n_pairs": 2}
        )
        session_id = session_resp.json()["session_id"]

        # Get first item
        response = await client.get(f"/math/sessions/{session_id}/next")
        assert response.status_code == 200

        item_data = response.json()
        assert "item_id" in item_data
        assert "stem" in item_data
        assert "question" in item_data
        assert "context_id" in item_data

        # Get second item (should be different)
        response2 = await client.get(f"/math/sessions/{session_id}/next")
        assert response2.status_code == 200
        item_data2 = response2.json()
        assert item_data2["item_id"] != item_data["item_id"]


async def test_get_next_item_nonexistent_session(app):
    """Test getting next item from nonexistent session."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/math/sessions/nonexistent/next")
        assert response.status_code == 200
        assert response.json() == {"item": None}


async def test_log_attempt_success(app):
    """Test logging a correct attempt."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup session and get item
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "7-9", "interests": []}
        )
        participant_id = participant_resp.json()["participant_id"]

        session_resp = await client.post(
            "/math/sessions", json={"participant_id": participant_id, "n_pairs": 1}
        )
        session_id = session_resp.json()["session_id"]

        item_resp = await client.get(f"/math/sessions/{session_id}/next")
        item_data = item_resp.json()
        item_id = item_data["item_id"]

        # Get correct answer from problem spec
        async with async_session_maker() as session:
            item = await session.get(Item, item_id)
            correct_answer = float(item.problem_spec["solution"]["answer"])

        # Submit correct answer
        response = await client.post(
            "/math/attempts",
            json={
                "item_id": item_id,
                "answer_submitted": correct_answer,
                "hints_used": 0,
                "retries": 0,
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["correct"] is True
        assert "next_item" in result


async def test_log_attempt_incorrect(app):
    """Test logging an incorrect attempt."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup session and get item
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "7-9", "interests": []}
        )
        participant_id = participant_resp.json()["participant_id"]

        session_resp = await client.post(
            "/math/sessions", json={"participant_id": participant_id, "n_pairs": 1}
        )
        session_id = session_resp.json()["session_id"]

        item_resp = await client.get(f"/math/sessions/{session_id}/next")
        item_id = item_resp.json()["item_id"]

        # Submit incorrect answer
        response = await client.post(
            "/math/attempts",
            json={
                "item_id": item_id,
                "answer_submitted": 999.0,  # Obviously wrong
                "hints_used": 2,
                "retries": 1,
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["correct"] is False


async def test_log_attempt_nonexistent_item(app):
    """Test logging attempt for nonexistent item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/math/attempts",
            json={
                "item_id": "nonexistent",
                "answer_submitted": 5.0,
                "hints_used": 0,
                "retries": 0,
            },
        )
        assert response.status_code == 404


async def test_post_quiz(app):
    """Test post-quiz endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup session
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "7-9", "interests": []}
        )
        participant_id = participant_resp.json()["participant_id"]

        session_resp = await client.post(
            "/math/sessions", json={"participant_id": participant_id, "n_pairs": 1}
        )
        session_id = session_resp.json()["session_id"]

        # Post quiz data
        quiz_data = {"score": 85, "feedback": "Great job!"}
        response = await client.post(
            f"/math/sessions/{session_id}/post_quiz", json=quiz_data
        )
        assert response.status_code == 200
        assert response.json() == {"status": "stored"}

        # Verify data was stored
        async with async_session_maker() as session:
            session_obj = await session.get(Session, session_id)
            assert session_obj.post_quiz == quiz_data


async def test_post_quiz_nonexistent_session(app):
    """Test post-quiz with nonexistent session."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/math/sessions/nonexistent/post_quiz", json={})
        assert response.status_code == 404


async def test_log_attempt_duplicate_submission(app):
    """Test submitting attempt twice for the same item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup session and get item
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "7-9", "interests": []}
        )
        participant_id = participant_resp.json()["participant_id"]

        session_resp = await client.post(
            "/math/sessions", json={"participant_id": participant_id, "n_pairs": 1}
        )
        session_id = session_resp.json()["session_id"]

        item_resp = await client.get(f"/math/sessions/{session_id}/next")
        item_id = item_resp.json()["item_id"]

        # Submit first attempt
        response1 = await client.post(
            "/math/attempts",
            json={
                "item_id": item_id,
                "answer_submitted": 5.0,
                "hints_used": 0,
                "retries": 0,
            },
        )
        assert response1.status_code == 200
        first_result = response1.json()

        # Submit second attempt for same item
        response2 = await client.post(
            "/math/attempts",
            json={
                "item_id": item_id,
                "answer_submitted": 6.0,
                "hints_used": 1,
                "retries": 1,
            },
        )
        assert response2.status_code == 200
        second_result = response2.json()

        # Should return the original attempt result
        assert second_result["correct"] == first_result["correct"]


async def test_session_completion_flow(app):
    """Test processing multiple items in a session."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup session with 1 pair (2 items)
        participant_resp = await client.post(
            "/math/participants", json={"age_band": "7-9", "interests": []}
        )
        participant_id = participant_resp.json()["participant_id"]

        session_resp = await client.post(
            "/math/sessions", json={"participant_id": participant_id, "n_pairs": 1}
        )
        session_id = session_resp.json()["session_id"]

        # Process items in the session
        item_ids = []
        for i in range(2):  # Process 2 items (1 pair)
            item_resp = await client.get(f"/math/sessions/{session_id}/next")
            item_data = item_resp.json()

            # Should get a valid item
            assert "item_id" in item_data
            item_ids.append(item_data["item_id"])

            # Submit attempt
            await client.post(
                "/math/attempts",
                json={
                    "item_id": item_data["item_id"],
                    "answer_submitted": 5.0,
                    "hints_used": 0,
                    "retries": 0,
                },
            )

        # Verify we processed 2 different items
        assert len(set(item_ids)) == 2

        # Verify attempts were recorded
        async with async_session_maker() as session:
            result = await session.execute(
                select(Attempt).join(Item).where(Item.session_id == session_id)
            )
            attempts = result.scalars().all()
            assert len(attempts) == 2


# Test functions that need to be called with asyncio.run()
def test_create_participant_sync(app):
    asyncio.run(test_create_participant(app))


def test_create_session_default_params_sync(app):
    asyncio.run(test_create_session_default_params(app))


def test_create_session_custom_params_sync(app):
    asyncio.run(test_create_session_custom_params(app))


def test_get_next_item_sync(app):
    asyncio.run(test_get_next_item(app))


def test_get_next_item_nonexistent_session_sync(app):
    asyncio.run(test_get_next_item_nonexistent_session(app))


def test_log_attempt_success_sync(app):
    asyncio.run(test_log_attempt_success(app))


def test_log_attempt_incorrect_sync(app):
    asyncio.run(test_log_attempt_incorrect(app))


def test_log_attempt_nonexistent_item_sync(app):
    asyncio.run(test_log_attempt_nonexistent_item(app))


def test_post_quiz_sync(app):
    asyncio.run(test_post_quiz(app))


def test_post_quiz_nonexistent_session_sync(app):
    asyncio.run(test_post_quiz_nonexistent_session(app))


def test_log_attempt_duplicate_submission_sync(app):
    asyncio.run(test_log_attempt_duplicate_submission(app))


def test_session_completion_flow_sync(app):
    asyncio.run(test_session_completion_flow(app))
