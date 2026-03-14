import pytest
import time
from tests.conftest import WON_GAME_1, WON_GAME_2, LOST_GAME_1, LOST_GAME_2, ABANDONED_GAME_1, ABANDONED_GAME_2


def test_statistics_returns_200(client):
    res = client.get("/api/statistics")
    assert res.status_code == 200


def test_statistics_response_shape(client):
    res = client.get("/api/statistics")
    data = res.get_json()
    assert set(data.keys()) == {"user_id", "wins", "losses", "abandoned"}


def test_statistics_fresh_user_baseline(client):
    res = client.get("/api/statistics")
    data = res.get_json()
    assert data["wins"] == 0
    assert data["losses"] == 0
    assert data["abandoned"] == 0


def test_statistics_user_id_matches_session(client):
    res = client.get("/api/statistics")
    user_id_from_body = res.get_json()["user_id"]

    with client.session_transaction() as sess:
        user_id_from_session = sess["user_id"]

    assert user_id_from_body == user_id_from_session


def test_statistics_wins_reflect_verify_call(client):
    client.get("/api/statistics")
    client.post("/api/verify", json=WON_GAME_1)

    res = client.get("/api/statistics")
    data = res.get_json()
    assert data["wins"] == 1
    assert data["losses"] == 0
    assert data["abandoned"] == 0


def test_statistics_losses_reflect_verify_call(client):
    client.get("/api/statistics")
    client.post("/api/verify", json=LOST_GAME_1)
    
    res = client.get("/api/statistics")
    data = res.get_json()
    assert data["losses"] == 1
    assert data["wins"] == 0
    assert data["abandoned"] == 0


def test_statistics_abandoned_reflects_restart_call(client):
    client.get("/api/statistics")
    client.post("/api/restart", json=ABANDONED_GAME_1)
    
    res = client.get("/api/statistics")
    data = res.get_json()

    assert data["abandoned"] == 1
    assert data["wins"] == 0
    assert data["losses"] == 0


def test_statistics_accumulates_across_multiple_games(limiter_client):
    from extensions import limiter

    limiter_client.get("/api/statistics")
    limiter_client.post("/api/verify", json=WON_GAME_1)
    limiter.reset()
    limiter_client.post("/api/verify", json=WON_GAME_2)
    limiter.reset()
    limiter_client.post("/api/verify", json=LOST_GAME_1)
    limiter.reset()
    limiter_client.post("/api/verify", json=LOST_GAME_2)

    limiter_client.post("/api/restart", json=ABANDONED_GAME_1)
    limiter.reset()
    limiter_client.post("/api/restart", json=ABANDONED_GAME_2)
    
    res = limiter_client.get("/api/statistics")
    data = res.get_json()

    assert data["wins"] == 2
    assert data["abandoned"] == 2
    assert data["losses"] == 2


def test_statistics_no_prior_session_creates_new_user(client):
    client.delete_cookie("session")

    res = client.get("/api/statistics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["wins"] == 0
    assert data["losses"] == 0
    assert data["abandoned"] == 0


def test_statistics_invalid_user_id_creates_new(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "not-a-valid-uuid"

    res = client.get("/api/statistics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["wins"] == 0
    assert data["losses"] == 0
    assert data["abandoned"] == 0
    assert data["user_id"] != "not-a-valid-uuid"
