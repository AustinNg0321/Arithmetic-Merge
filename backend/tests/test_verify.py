"""test_verify.py — 100% path coverage for POST /api/verify"""
import pytest
from unittest.mock import patch

from tests.conftest import WON_GAME_2, LOST_GAME_1, ABANDONED_GAME_1

VERIFY_URL = "/api/verify"

# ---------------------------------------------------------------------------
# A short in-progress replay derived from ABANDONED_GAME_1's first 5 moves.
# The conftest `in_progress_replay` fixture also provides this, but defining
# it here keeps each test's dependency explicit.
# ---------------------------------------------------------------------------
_IN_PROGRESS = {
    "seed": ABANDONED_GAME_1["seed"],
    "moves": ABANDONED_GAME_1["moves"][:5],
}


# ===========================================================================
# Terminal success: Won games
# ===========================================================================

def test_verify_won_game_returns_200(client):
    res = client.post(VERIFY_URL, json=WON_GAME_2)
    assert res.status_code == 200


def test_verify_won_game_increments_wins(client):
    res = client.post(VERIFY_URL, json=WON_GAME_2)
    assert res.get_json()["wins"] == 1


def test_verify_won_game_response_shape(client):
    """Success response must contain the four stat keys and must NOT include 'verified'."""
    res = client.post(VERIFY_URL, json=WON_GAME_2)
    data = res.get_json()
    for key in ("user_id", "wins", "losses", "abandoned"):
        assert key in data, f"Expected key '{key}' missing from success response"
    assert "verified" not in data, "Success response must not include 'verified'"


# ===========================================================================
# Terminal success: Lost games
# ===========================================================================

def test_verify_lost_game_returns_200(client):
    res = client.post(VERIFY_URL, json=LOST_GAME_1)
    assert res.status_code == 200


def test_verify_lost_game_increments_losses(client):
    res = client.post(VERIFY_URL, json=LOST_GAME_1)
    assert res.get_json()["losses"] == 1


# ===========================================================================
# In-progress & verification failures
# ===========================================================================

def test_verify_in_progress_returns_200(client, in_progress_replay):
    res = client.post(VERIFY_URL, json=in_progress_replay)
    assert res.status_code == 200


def test_verify_in_progress_returns_verified_false(client, in_progress_replay):
    res = client.post(VERIFY_URL, json=in_progress_replay)
    assert res.get_json()["verified"] is False


def test_verify_in_progress_increments_abandoned(client, in_progress_replay):
    res = client.post(VERIFY_URL, json=in_progress_replay)
    assert res.get_json()["abandoned"] == 1


def test_verify_empty_moves_is_verification_failure(client):
    """Zero moves → game still In Progress → verification_failed_response path."""
    res = client.post(VERIFY_URL, json={"seed": "test-seed", "moves": []})
    data = res.get_json()
    assert data["verified"] is False
    assert data["abandoned"] == 1


def test_verify_tampered_moves_returns_verified_false(client):
    """Appending a move after the game is Won makes simulate_game return (False, None)."""
    tampered = {
        "seed": WON_GAME_2["seed"],
        "moves": WON_GAME_2["moves"] + ["left"],
    }
    res = client.post(VERIFY_URL, json=tampered)
    assert res.get_json()["verified"] is False


def test_verify_tampered_moves_increments_abandoned(client):
    """simulate_game's (False, None) path routes through verification_failed_response,
    so abandoned must be incremented.

    TODO: If the simulate_game tampering path is ever short-circuited before
    verification_failed_response, abandoned would not increment — revisit this test.
    """
    tampered = {
        "seed": WON_GAME_2["seed"],
        "moves": WON_GAME_2["moves"] + ["left"],
    }
    res = client.post(VERIFY_URL, json=tampered)
    assert res.get_json()["abandoned"] == 1


# ===========================================================================
# Input validation & security (HTTP 400 / 404)
# ===========================================================================

def test_verify_missing_seed_returns_400(client):
    res = client.post(VERIFY_URL, json={"moves": ["left"]})
    assert res.status_code == 400


def test_verify_missing_moves_returns_400(client):
    res = client.post(VERIFY_URL, json={"seed": "abc"})
    assert res.status_code == 400


def test_verify_moves_not_a_list_returns_400(client):
    res = client.post(VERIFY_URL, json={"seed": "abc", "moves": "left"})
    assert res.status_code == 400


def test_verify_invalid_direction_in_moves_returns_400(client):
    res = client.post(VERIFY_URL, json={"seed": "abc", "moves": ["up", "sideways"]})
    assert res.status_code == 400


def test_verify_json_array_body_returns_400(client):
    """A top-level JSON array instead of an object must be rejected."""
    res = client.post(VERIFY_URL, json=[])
    assert res.status_code == 400


def test_verify_no_body_returns_400(client):
    """No body → get_request_json() returns {} → seed is None → 400."""
    res = client.post(VERIFY_URL)
    assert res.status_code == 400


def test_verify_user_not_found(client):
    """Patch get_user to return None to exercise the 404 abort in verify_game.

    The before_request hook will call the patched get_user (→ None) and then
    call create_new_session to mint a fresh User.  The route handler then calls
    get_user again (→ None) and aborts 404, which is the path under test.
    """
    with patch("routes.solo.get_user", return_value=None):
        res = client.post(VERIFY_URL, json={"seed": "abc", "moves": []})
    assert res.status_code == 404


# ===========================================================================
# State logic
# ===========================================================================

def test_verify_same_won_game_twice_double_counts(client):
    """The server performs no deduplication; submitting the same win twice → wins == 2."""
    client.post(VERIFY_URL, json=WON_GAME_2)
    res = client.post(VERIFY_URL, json=WON_GAME_2)
    assert res.get_json()["wins"] == 2
