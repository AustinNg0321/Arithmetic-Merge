"""test_rate_limiter.py — rate-limit enforcement for all API endpoints.

Limits under test
-----------------
/api/verify    : 1 per 10 seconds  (route-level @limiter.limit)
/api/restart   : 1 per 10 seconds  (route-level @limiter.limit)
/api/statistics: 2 per second      (default_limits on Limiter instance)

Tests marked @pytest.mark.slow exercise the real time windows and add
~10 s or ~1 s to the suite run.  Skip them with:  pytest -m "not slow"
"""
import time
import pytest
from extensions import limiter

VERIFY_URL = "/api/verify"
RESTART_URL = "/api/restart"
STATS_URL = "/api/statistics"

# Minimal valid POST body — passes parse_seed_and_moves without 400
_BODY = {"seed": "test-seed", "moves": []}


# ---------------------------------------------------------------------------
# Autouse reset — guarantee a clean counter state before every test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_limiter(limiter_client):
    limiter.reset()
    yield


# ===========================================================================
# /api/verify — 1 per 10 seconds
# ===========================================================================

def test_verify_first_call_succeeds(limiter_client):
    res = limiter_client.post(VERIFY_URL, json=_BODY)
    assert res.status_code == 200


def test_verify_second_call_within_window_returns_429(limiter_client):
    limiter_client.post(VERIFY_URL, json=_BODY)
    res = limiter_client.post(VERIFY_URL, json=_BODY)
    assert res.status_code == 429


def test_verify_after_reset_returns_200(limiter_client):
    limiter_client.post(VERIFY_URL, json=_BODY)
    limiter.reset()
    res = limiter_client.post(VERIFY_URL, json=_BODY)
    assert res.status_code == 200


@pytest.mark.slow
def test_verify_after_time_interval_returns_200(limiter_client):
    limiter_client.post(VERIFY_URL, json=_BODY)
    time.sleep(10.1)
    res = limiter_client.post(VERIFY_URL, json=_BODY)
    assert res.status_code == 200


# ===========================================================================
# /api/restart — 1 per 10 seconds
# ===========================================================================

def test_restart_first_call_succeeds(limiter_client):
    res = limiter_client.post(RESTART_URL, json=_BODY)
    assert res.status_code == 200


def test_restart_second_call_within_window_returns_429(limiter_client):
    limiter_client.post(RESTART_URL, json=_BODY)
    res = limiter_client.post(RESTART_URL, json=_BODY)
    assert res.status_code == 429


def test_restart_after_reset_returns_200(limiter_client):
    limiter_client.post(RESTART_URL, json=_BODY)
    limiter.reset()
    res = limiter_client.post(RESTART_URL, json=_BODY)
    assert res.status_code == 200


@pytest.mark.slow
def test_restart_after_time_interval_returns_200(limiter_client):
    limiter_client.post(RESTART_URL, json=_BODY)
    time.sleep(10.1)
    res = limiter_client.post(RESTART_URL, json=_BODY)
    assert res.status_code == 200


# ===========================================================================
# /api/statistics — 2 per second (default limit)
# ===========================================================================

def test_statistics_allows_two_calls(limiter_client):
    res1 = limiter_client.get(STATS_URL)
    res2 = limiter_client.get(STATS_URL)
    assert res1.status_code == 200
    assert res2.status_code == 200


def test_statistics_third_call_returns_429(limiter_client):
    limiter_client.get(STATS_URL)
    limiter_client.get(STATS_URL)
    res = limiter_client.get(STATS_URL)
    assert res.status_code == 429


@pytest.mark.slow
def test_statistics_resets_after_one_second(limiter_client):
    limiter_client.get(STATS_URL)
    limiter_client.get(STATS_URL)
    time.sleep(1.1)
    res = limiter_client.get(STATS_URL)
    assert res.status_code == 200


# ===========================================================================
# Isolation — each endpoint's quota is independent
# ===========================================================================

def test_all_endpoints_have_independent_rate_limits(limiter_client):
    """Exhausting /api/verify's quota must not block /api/restart or /api/statistics."""
    limiter_client.post(VERIFY_URL, json=_BODY)
    rate_limited = limiter_client.post(VERIFY_URL, json=_BODY)
    assert rate_limited.status_code == 429

    res_restart = limiter_client.post(RESTART_URL, json=_BODY)
    assert res_restart.status_code == 200

    res_stats = limiter_client.get(STATS_URL)
    assert res_stats.status_code == 200
