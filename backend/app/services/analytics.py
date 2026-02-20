"""Analytics service for suggestion analytics"""

from collections import defaultdict
from datetime import timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus

_UNKNOWN_PERIOD = "unknown"


def _score_in_bin(score: float, low: float, high: float) -> bool:
    """Return True if score falls in [low, high] (inclusive on both ends for the last bin)."""
    return low <= score <= high


class SuggestionAnalytics:
    """Service for computing suggestion analytics"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _fetch_all_suggestions(self) -> list[LinkSuggestion]:
        """Fetch all suggestions from the database"""
        result = await self.db.execute(select(LinkSuggestion))
        return list(result.scalars().all())

    @staticmethod
    def _period_for(s: LinkSuggestion) -> str:
        """Return the YYYY-MM period string for a suggestion's created_at, or 'unknown'."""
        return s.created_at.strftime("%Y-%m") if s.created_at else _UNKNOWN_PERIOD

    async def get_acceptance_rates(self) -> list[dict[str, Any]]:
        """
        Calculate acceptance/rejection rates for link suggestions over time.

        Returns a list of monthly periods with counts of accepted, rejected,
        pending suggestions and the overall acceptance rate.
        """
        suggestions = await self._fetch_all_suggestions()

        # Group by year-month of created_at
        period_data: dict[str, dict[str, int]] = defaultdict(
            lambda: {"accepted": 0, "rejected": 0, "pending": 0, "total": 0}
        )

        for s in suggestions:
            period = self._period_for(s)
            period_data[period]["total"] += 1
            if s.status == SuggestionStatus.ACCEPTED:
                period_data[period]["accepted"] += 1
            elif s.status == SuggestionStatus.REJECTED:
                period_data[period]["rejected"] += 1
            else:
                period_data[period]["pending"] += 1

        results = []
        for period in sorted(period_data.keys()):
            data = period_data[period]
            total = data["total"]
            acceptance_rate = round(data["accepted"] / total * 100, 2) if total > 0 else 0.0
            results.append(
                {
                    "period": period,
                    "accepted": data["accepted"],
                    "rejected": data["rejected"],
                    "pending": data["pending"],
                    "total": total,
                    "acceptance_rate": acceptance_rate,
                }
            )

        return results

    async def get_confidence_distribution(self) -> list[dict[str, Any]]:
        """
        Distribution of confidence scores across suggestions.

        Returns counts and percentages for score ranges:
        0.0–0.2, 0.2–0.4, 0.4–0.6, 0.6–0.8, 0.8–1.0
        """
        suggestions = await self._fetch_all_suggestions()
        total = len(suggestions)

        bins = [
            ("0.0-0.2", 0.0, 0.2),
            ("0.2-0.4", 0.2, 0.4),
            ("0.4-0.6", 0.4, 0.6),
            ("0.6-0.8", 0.6, 0.8),
            ("0.8-1.0", 0.8, 1.0),
        ]

        results = []
        for i, (label, low, high) in enumerate(bins):
            is_last = i == len(bins) - 1
            count = sum(
                1
                for s in suggestions
                if s.similarity_score is not None and _score_in_bin(s.similarity_score, low, high)
                # For non-last bins exclude the upper boundary to avoid double-counting
                and (is_last or s.similarity_score < high)
            )
            percentage = round(count / total * 100, 2) if total > 0 else 0.0
            results.append({"range": label, "count": count, "percentage": percentage})

        return results

    async def get_generation_trends(self) -> list[dict[str, Any]]:
        """
        Trends in suggestion generation volume over time.

        Returns monthly counts of suggestions created.
        """
        suggestions = await self._fetch_all_suggestions()

        period_counts: dict[str, int] = defaultdict(int)
        for s in suggestions:
            period_counts[self._period_for(s)] += 1

        return [{"period": period, "count": count} for period, count in sorted(period_counts.items())]

    async def get_review_velocity(self) -> dict[str, Any]:
        """
        How quickly suggestions are being reviewed.

        Returns average and median review time (in hours) for reviewed suggestions.
        """
        suggestions = await self._fetch_all_suggestions()

        durations_hours: list[float] = []
        for s in suggestions:
            if s.reviewed_at is not None and s.created_at is not None:
                delta: timedelta = s.reviewed_at - s.created_at
                hours = delta.total_seconds() / 3600
                durations_hours.append(hours)

        total_reviewed = len(durations_hours)
        if total_reviewed == 0:
            return {
                "average_hours": 0.0,
                "median_hours": 0.0,
                "total_reviewed": 0,
            }

        average_hours = round(sum(durations_hours) / total_reviewed, 2)
        sorted_durations = sorted(durations_hours)
        mid = total_reviewed // 2
        if total_reviewed % 2 == 0:
            median_hours = round((sorted_durations[mid - 1] + sorted_durations[mid]) / 2, 2)
        else:
            median_hours = round(sorted_durations[mid], 2)

        return {
            "average_hours": average_hours,
            "median_hours": median_hours,
            "total_reviewed": total_reviewed,
        }

    async def get_algorithm_comparison(self) -> list[dict[str, Any]]:
        """
        Compare performance metrics across algorithms.

        Returns per-algorithm counts, acceptance rates, and average confidence scores.
        """
        suggestions = await self._fetch_all_suggestions()

        algo_data: dict[str, dict[str, Any]] = {
            method.value: {
                "total": 0,
                "accepted": 0,
                "rejected": 0,
                "pending": 0,
                "score_sum": 0.0,
                "score_count": 0,
            }
            for method in SuggestionMethod
        }

        for s in suggestions:
            key = s.suggestion_method.value if s.suggestion_method else None
            if key is None or key not in algo_data:
                continue
            algo_data[key]["total"] += 1
            if s.status == SuggestionStatus.ACCEPTED:
                algo_data[key]["accepted"] += 1
            elif s.status == SuggestionStatus.REJECTED:
                algo_data[key]["rejected"] += 1
            else:
                algo_data[key]["pending"] += 1
            if s.similarity_score is not None:
                algo_data[key]["score_sum"] += s.similarity_score
                algo_data[key]["score_count"] += 1

        results = []
        for algorithm, data in algo_data.items():
            total = data["total"]
            acceptance_rate = round(data["accepted"] / total * 100, 2) if total > 0 else 0.0
            avg_confidence = (
                round(data["score_sum"] / data["score_count"], 4) if data["score_count"] > 0 else 0.0
            )
            results.append(
                {
                    "algorithm": algorithm,
                    "total": total,
                    "accepted": data["accepted"],
                    "rejected": data["rejected"],
                    "pending": data["pending"],
                    "acceptance_rate": acceptance_rate,
                    "avg_confidence": avg_confidence,
                }
            )

        return results
