"""Analytics service for suggestion metrics and trends"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus


class SuggestionAnalytics:
    """Service class providing analytics over LinkSuggestion data"""

    @staticmethod
    async def get_acceptance_rates(
        db: AsyncSession,
        time_period: str | None = None,
    ) -> dict[str, Any]:
        """
        Calculate suggestion acceptance, rejection, and pending rates.

        Args:
            db: Async database session
            time_period: Optional ISO-8601 date string; only include suggestions created on or after this date

        Returns:
            dict with total, accepted, rejected, pending counts and rates
        """
        query = select(LinkSuggestion)
        if time_period is not None:
            cutoff = datetime.fromisoformat(time_period)
            query = query.where(LinkSuggestion.created_at >= cutoff)

        result = await db.execute(query)
        suggestions = result.scalars().all()

        total = len(suggestions)
        accepted = sum(1 for s in suggestions if s.status == SuggestionStatus.ACCEPTED)
        rejected = sum(1 for s in suggestions if s.status == SuggestionStatus.REJECTED)
        pending = sum(1 for s in suggestions if s.status == SuggestionStatus.PENDING)

        return {
            "total": total,
            "accepted": accepted,
            "rejected": rejected,
            "pending": pending,
            "acceptance_rate": round(accepted / total * 100, 2) if total > 0 else 0.0,
            "rejection_rate": round(rejected / total * 100, 2) if total > 0 else 0.0,
            "pending_rate": round(pending / total * 100, 2) if total > 0 else 0.0,
        }

    @staticmethod
    async def get_confidence_distribution(
        db: AsyncSession,
        algorithm: str | None = None,
    ) -> dict[str, Any]:
        """
        Get distribution of similarity scores, optionally filtered by algorithm.

        Scores are bucketed into 10 bands: [0.0–0.1), [0.1–0.2), …, [0.9–1.0].

        Args:
            db: Async database session
            algorithm: Optional suggestion_method value to filter by (e.g. "keyword_match")

        Returns:
            dict with buckets list and summary statistics
        """
        query = select(LinkSuggestion)
        if algorithm is not None:
            query = query.where(LinkSuggestion.suggestion_method == algorithm)

        result = await db.execute(query)
        suggestions = result.scalars().all()

        # Build 10 equal-width buckets over [0, 1]
        buckets: list[dict[str, Any]] = []
        for i in range(10):
            lower = round(i * 0.1, 1)
            upper = round((i + 1) * 0.1, 1)
            label = f"{lower:.1f}-{upper:.1f}"
            count = sum(
                1
                for s in suggestions
                if ((lower <= s.similarity_score < upper) if i < 9 else (lower <= s.similarity_score <= upper))
            )
            buckets.append({"range": label, "count": count})

        scores = [s.similarity_score for s in suggestions]
        total = len(scores)

        return {
            "buckets": buckets,
            "total": total,
            "average": round(sum(scores) / total, 4) if total > 0 else 0.0,
            "min": round(min(scores), 4) if total > 0 else 0.0,
            "max": round(max(scores), 4) if total > 0 else 0.0,
        }

    @staticmethod
    async def get_generation_trends(
        db: AsyncSession,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Get suggestion generation trends over the specified number of days.

        Returns one entry per day with a count of suggestions created that day.

        Args:
            db: Async database session
            days: Number of days to look back (default 30)

        Returns:
            dict with a daily list and the total count over the period
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = select(LinkSuggestion).where(LinkSuggestion.created_at >= cutoff)
        result = await db.execute(query)
        suggestions = result.scalars().all()

        # Build a day-by-day count map
        day_counts: dict[str, int] = {}
        for s in suggestions:
            day = s.created_at.strftime("%Y-%m-%d")
            day_counts[day] = day_counts.get(day, 0) + 1

        # Build ordered list of days in range
        daily: list[dict[str, Any]] = []
        for i in range(days):
            day = (datetime.utcnow() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            daily.append({"date": day, "count": day_counts.get(day, 0)})

        return {"days": days, "daily": daily, "total": len(suggestions)}

    @staticmethod
    async def get_review_velocity(
        db: AsyncSession,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Calculate how quickly suggestions are being reviewed.

        Measures the time in hours from creation to review for suggestions
        reviewed within the specified window.

        Args:
            db: Async database session
            days: Number of days to look back (default 30)

        Returns:
            dict with average/min/max review time in hours and reviewed count
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = select(LinkSuggestion).where(
            LinkSuggestion.reviewed_at.is_not(None),
            LinkSuggestion.reviewed_at >= cutoff,
        )
        result = await db.execute(query)
        reviewed = result.scalars().all()

        durations_hours: list[float] = []
        for s in reviewed:
            delta = s.reviewed_at - s.created_at
            durations_hours.append(delta.total_seconds() / 3600)

        total = len(durations_hours)

        return {
            "days": days,
            "reviewed_count": total,
            "average_hours": round(sum(durations_hours) / total, 2) if total > 0 else 0.0,
            "min_hours": round(min(durations_hours), 2) if total > 0 else 0.0,
            "max_hours": round(max(durations_hours), 2) if total > 0 else 0.0,
        }

    @staticmethod
    async def get_algorithm_comparison(db: AsyncSession) -> dict[str, Any]:
        """
        Compare performance across different suggestion algorithms.

        Args:
            db: Async database session

        Returns:
            dict with a list of per-algorithm stats and overall totals
        """
        algorithms: list[dict[str, Any]] = []

        for method in SuggestionMethod:
            result = await db.execute(
                select(LinkSuggestion).where(LinkSuggestion.suggestion_method == method)
            )
            suggestions = result.scalars().all()

            total = len(suggestions)
            accepted = sum(1 for s in suggestions if s.status == SuggestionStatus.ACCEPTED)
            rejected = sum(1 for s in suggestions if s.status == SuggestionStatus.REJECTED)
            pending = sum(1 for s in suggestions if s.status == SuggestionStatus.PENDING)
            scores = [s.similarity_score for s in suggestions]

            algorithms.append(
                {
                    "algorithm": method.value,
                    "total": total,
                    "accepted": accepted,
                    "rejected": rejected,
                    "pending": pending,
                    "acceptance_rate": round(accepted / total * 100, 2) if total > 0 else 0.0,
                    "average_score": round(sum(scores) / total, 4) if total > 0 else 0.0,
                }
            )

        return {"algorithms": algorithms}
