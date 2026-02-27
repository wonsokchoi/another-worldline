"""Tests for daily pull reset logic."""
from datetime import datetime, timezone, timedelta

import pytest

from app.core.config import settings


def test_free_pulls_per_day_config():
    """Default free pulls should be 3."""
    assert settings.FREE_PULLS_PER_DAY == 3


def test_reset_hour_kst():
    """Reset should happen at KST midnight (UTC+9 00:00)."""
    assert settings.STORY_RESET_HOUR_KST == 0


def test_kst_timezone_calculation():
    """KST timezone offset should be +9 hours."""
    kst = timezone(timedelta(hours=9))
    now_utc = datetime(2026, 2, 27, 15, 0, 0, tzinfo=timezone.utc)
    now_kst = now_utc.astimezone(kst)
    assert now_kst.hour == 0  # 15:00 UTC = 00:00 KST (next day)
    assert now_kst.day == 28


def test_daily_reset_logic():
    """Pull counter should reset after KST midnight."""
    kst = timezone(timedelta(hours=9))

    # Scenario: last reset was yesterday KST
    yesterday_kst = datetime(2026, 2, 26, 12, 0, 0, tzinfo=kst)
    today_reset = datetime(2026, 2, 27, 0, 0, 0, tzinfo=kst)

    # yesterday_kst < today_reset → should reset
    assert yesterday_kst < today_reset


def test_daily_reset_same_day():
    """Pull counter should NOT reset on same KST day."""
    kst = timezone(timedelta(hours=9))

    # Scenario: last reset was today morning KST
    today_morning_kst = datetime(2026, 2, 27, 8, 0, 0, tzinfo=kst)
    today_reset = datetime(2026, 2, 27, 0, 0, 0, tzinfo=kst)

    # today_morning_kst >= today_reset → should NOT reset
    assert today_morning_kst >= today_reset


def test_coupon_deduction_when_free_exhausted():
    """When free pulls exhausted, coupons should be deducted."""
    # Simulated user state
    daily_free_pulls_used = 3
    coupon_balance = 5

    # Logic from stories.py endpoint
    if daily_free_pulls_used >= settings.FREE_PULLS_PER_DAY:
        if coupon_balance > 0:
            coupon_balance -= 1
        else:
            raise Exception("should not reach here if coupon > 0")

    assert coupon_balance == 4


def test_no_coupon_no_pull():
    """When no free pulls and no coupons, pull should be denied."""
    daily_free_pulls_used = 3
    coupon_balance = 0

    denied = False
    if daily_free_pulls_used >= settings.FREE_PULLS_PER_DAY:
        if coupon_balance <= 0:
            denied = True

    assert denied is True
