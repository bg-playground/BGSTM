from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.crud.quality_digest import next_delivery
from app.models.quality_digest_subscription import DigestCadence
from app.schemas.quality_digest import DigestSubscriptionUpdate


def test_next_delivery_daily_weekly_and_off() -> None:
    now = datetime(2026, 9, 9, 12, 0, 0)

    assert next_delivery(DigestCadence.daily, now) == now + timedelta(days=1)
    assert next_delivery(DigestCadence.weekly, now) == now + timedelta(days=7)
    assert next_delivery(DigestCadence.off, now) is None


@pytest.mark.parametrize("window", [7, 30, 90])
def test_subscription_accepts_supported_windows(window: int) -> None:
    payload = DigestSubscriptionUpdate(cadence=DigestCadence.daily, window_days=window)
    assert payload.window_days == window


def test_subscription_rejects_unsupported_window() -> None:
    with pytest.raises(ValidationError):
        DigestSubscriptionUpdate(cadence=DigestCadence.daily, window_days=14)
