"""test_restart.py — 100% path coverage for POST /api/restart"""
import pytest
from unittest.mock import patch

from tests.conftest import (
    WON_GAME_2,
    LOST_GAME_1,
    ABANDONED_GAME_1,
    ABANDONED_GAME_2,
    INVAILD_GAME_1,
)

RESTART_URL = "/api/restart"


# ===========================================================================
# Valid Restarts
# ===========================================================================

def test_restart_in_progress_returns_200(client):
    res = client.post(RESTART_URL, json=ABANDONED_GAME_1)
    assert res.status_code == 200


def test_restart_in_progress_increments_abandoned(client):
    res = client.post(RESTART_URL, json=ABANDONED_GAME_1)
    assert res.get_json()["abandoned"] == 1


def test_restart_in_progress_response_shape(client):
    """Success response must contain the four stat keys and must NOT include 'verified'."""
    res = client.post(RESTART_URL, json=ABANDONED_GAME_1)
    data = res.get_json()
    for key in ("user_id", "wins", "losses", "abandoned"):
        assert key in data, f"Expected key '{key}' missing from restart response"
    assert "verified" not in data, "Restart response must not include 'verified'"


def test_restart_does_not_increment_wins_or_losses(client):
    res = client.post(RESTART_URL, json=ABANDONED_GAME_1)
    data = res.get_json()
    assert data["wins"] == 0
    assert data["losses"] == 0


def test_restart_empty_moves_increments_abandoned(client):
    """Zero moves → game still In Progress → abandoned incremented."""
    res = client.post(RESTART_URL, json={"seed": "test-seed", "moves": []})
    data = res.get_json()
    assert res.status_code == 200
    assert data["abandoned"] == 1


# ===========================================================================
# Rejection of Terminal States (HTTP 400)
# ===========================================================================

def test_restart_won_game_returns_400(client):
    """A completed win must be rejected; use /api/verify for terminal games."""
    res = client.post(RESTART_URL, json=WON_GAME_2)
    assert res.status_code == 400


def test_restart_lost_game_returns_400(client):
    """A completed loss must be rejected; restart only accepts in-progress games."""
    res = client.post(RESTART_URL, json=LOST_GAME_1)
    assert res.status_code == 400


# ===========================================================================
# Validation & Error Handling
# ===========================================================================

def test_restart_tampered_moves_returns_verified_false(client):
    """If simulate_game returns (False, None), the response includes verified=False
    and abandoned is incremented (routes through verification_failed_response).

    INVAILD_GAME_1 contains all valid direction strings but the sequence becomes
    illegal mid-replay (a move not present in game.get_valid_moves()), causing
    simulate_game to short-circuit with (False, None).
    """
    res = client.post(RESTART_URL, json=INVAILD_GAME_1)
    data = res.get_json()
    assert data["verified"] is False
    assert data["abandoned"] == 1


def test_restart_missing_seed_returns_400(client):
    res = client.post(RESTART_URL, json={"moves": ["left"]})
    assert res.status_code == 400


def test_restart_missing_moves_returns_400(client):
    res = client.post(RESTART_URL, json={"seed": "abc"})
    assert res.status_code == 400


def test_restart_moves_not_a_list_returns_400(client):
    res = client.post(RESTART_URL, json={"seed": "abc", "moves": "left"})
    assert res.status_code == 400


def test_restart_invalid_direction_returns_400(client):
    """A move string not in {up, down, left, right} must be rejected with 400."""
    res = client.post(RESTART_URL, json={"seed": "abc", "moves": ["up", "forward"]})
    assert res.status_code == 400


def test_restart_user_not_found(client):
    """Patch get_user to return None to exercise the 404 abort in restart_game.

    The before_request hook will call the patched get_user (→ None) and then
    call create_new_session to mint a fresh User.  The route handler then calls
    get_user again (→ None) and aborts 404, which is the path under test.
    """
    with patch("routes.solo.get_user", return_value=None):
        res = client.post(RESTART_URL, json={"seed": "abc", "moves": []})
    assert res.status_code == 404


# ===========================================================================
# Accumulation Logic
# ===========================================================================

def test_restart_abandoned_count_accumulates(limiter_client):
    """Two successful in-progress restarts must bring abandoned to 2."""
    from extensions import limiter

    limiter_client.post(RESTART_URL, json=ABANDONED_GAME_1)
    limiter.reset()
    res = limiter_client.post(RESTART_URL, json=ABANDONED_GAME_2)
    assert res.get_json()["abandoned"] == 2
