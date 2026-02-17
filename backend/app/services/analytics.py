"""Analytics service for suggestion metrics"""

from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus


class SuggestionAnalytics:
    """Service for computing suggestion analytics"""

    @staticmethod
    async def get_acceptance_rates(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """
        Get acceptance rates by algorithm

        Returns:
            {
                "overall": {"total": 100, "accepted": 75, "rejected": 20, "pending": 5, "rate": 0.75},
                "by_algorithm": {
                    "tfidf": {"total": 30, "accepted": 22, "rate": 0.73},
                    "llm": {"total": 40, "accepted": 35, "rate": 0.875},
                    ...
                }
            }
        """
        query = select(
            LinkSuggestion.suggestion_method, LinkSuggestion.status, func.count(LinkSuggestion.id).label("count")
        )

        if start_date:
            query = query.where(LinkSuggestion.created_at >= start_date)
        if end_date:
            query = query.where(LinkSuggestion.created_at <= end_date)

        query = query.group_by(LinkSuggestion.suggestion_method, LinkSuggestion.status)

        result = await db.execute(query)
        rows = result.all()

        # Organize data
        by_algorithm = {}
        overall_totals = {"total": 0, "accepted": 0, "rejected": 0, "pending": 0}

        for method, status, count in rows:
            method_name = method.value if hasattr(method, "value") else str(method)

            if method_name not in by_algorithm:
                by_algorithm[method_name] = {"total": 0, "accepted": 0, "rejected": 0, "pending": 0}

            by_algorithm[method_name]["total"] += count
            overall_totals["total"] += count

            status_name = status.value if hasattr(status, "value") else str(status)
            if status_name in by_algorithm[method_name]:
                by_algorithm[method_name][status_name] += count
                overall_totals[status_name] += count

        # Calculate rates
        for method_data in by_algorithm.values():
            reviewed = method_data["accepted"] + method_data["rejected"]
            method_data["rate"] = method_data["accepted"] / reviewed if reviewed > 0 else 0.0

        overall_reviewed = overall_totals["accepted"] + overall_totals["rejected"]
        overall_totals["rate"] = overall_totals["accepted"] / overall_reviewed if overall_reviewed > 0 else 0.0

        return {"overall": overall_totals, "by_algorithm": by_algorithm}

    @staticmethod
    async def get_confidence_distribution(db: AsyncSession, algorithm: Optional[str] = None) -> dict[str, Any]:
        """
        Get distribution of confidence scores by algorithm and status

        Returns buckets: [0-0.3, 0.3-0.5, 0.5-0.7, 0.7-0.9, 0.9-1.0]
        """
        query = select(LinkSuggestion.suggestion_method, LinkSuggestion.status, LinkSuggestion.similarity_score)

        if algorithm:
            # Map algorithm name to enum
            # Note: 'tfidf' maps to SEMANTIC_SIMILARITY as TF-IDF is the implementation
            # used for semantic similarity in this system
            method_map = {
                "tfidf": SuggestionMethod.SEMANTIC_SIMILARITY,
                "keyword": SuggestionMethod.KEYWORD_MATCH,
                "hybrid": SuggestionMethod.HYBRID,
                "llm": SuggestionMethod.LLM_EMBEDDING,
            }
            if algorithm in method_map:
                query = query.where(LinkSuggestion.suggestion_method == method_map[algorithm])

        result = await db.execute(query)
        rows = result.all()

        # Define buckets
        buckets = {
            "0.0-0.3": {"accepted": 0, "rejected": 0, "pending": 0},
            "0.3-0.5": {"accepted": 0, "rejected": 0, "pending": 0},
            "0.5-0.7": {"accepted": 0, "rejected": 0, "pending": 0},
            "0.7-0.9": {"accepted": 0, "rejected": 0, "pending": 0},
            "0.9-1.0": {"accepted": 0, "rejected": 0, "pending": 0},
        }

        for method, status, score in rows:
            # Determine bucket
            if score < 0.3:
                bucket = "0.0-0.3"
            elif score < 0.5:
                bucket = "0.3-0.5"
            elif score < 0.7:
                bucket = "0.5-0.7"
            elif score < 0.9:
                bucket = "0.7-0.9"
            else:
                bucket = "0.9-1.0"

            status_name = status.value if hasattr(status, "value") else str(status)
            if status_name in buckets[bucket]:
                buckets[bucket][status_name] += 1

        return {"buckets": buckets}

    @staticmethod
    async def get_generation_trends(db: AsyncSession, days: int = 30) -> list[dict[str, Any]]:
        """
        Get daily suggestion generation trends

        Returns array of {date, total, by_algorithm: {tfidf: X, llm: Y, ...}}
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        query = (
            select(
                func.date(LinkSuggestion.created_at).label("date"),
                LinkSuggestion.suggestion_method,
                func.count(LinkSuggestion.id).label("count"),
            )
            .where(LinkSuggestion.created_at >= start_date)
            .group_by(func.date(LinkSuggestion.created_at), LinkSuggestion.suggestion_method)
            .order_by(func.date(LinkSuggestion.created_at))
        )

        result = await db.execute(query)
        rows = result.all()

        # Organize by date
        trends = {}
        for date, method, count in rows:
            date_str = date.isoformat() if hasattr(date, "isoformat") else str(date)
            method_name = method.value if hasattr(method, "value") else str(method)

            if date_str not in trends:
                trends[date_str] = {"date": date_str, "total": 0, "by_algorithm": {}}

            trends[date_str]["total"] += count
            trends[date_str]["by_algorithm"][method_name] = count

        return list(trends.values())

    @staticmethod
    async def get_review_velocity(db: AsyncSession, days: int = 30) -> dict[str, Any]:
        """
        Calculate review velocity metrics

        Returns:
            {
                "avg_time_to_review_hours": 24.5,
                "daily_review_rate": 15.3,
                "pending_backlog": 50
            }
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get reviewed suggestions
        query = select(LinkSuggestion.created_at, LinkSuggestion.reviewed_at).where(
            LinkSuggestion.reviewed_at.isnot(None), LinkSuggestion.created_at >= start_date
        )

        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return {"avg_time_to_review_hours": 0, "daily_review_rate": 0, "pending_backlog": 0}

        # Calculate average time to review
        total_hours = 0
        for created, reviewed in rows:
            delta = reviewed - created
            total_hours += delta.total_seconds() / 3600

        avg_time_to_review = total_hours / len(rows)
        daily_review_rate = len(rows) / days

        # Get pending count
        pending_query = select(func.count(LinkSuggestion.id)).where(LinkSuggestion.status == SuggestionStatus.PENDING)
        pending_result = await db.execute(pending_query)
        pending_backlog = pending_result.scalar() or 0

        return {
            "avg_time_to_review_hours": round(avg_time_to_review, 2),
            "daily_review_rate": round(daily_review_rate, 2),
            "pending_backlog": pending_backlog,
        }

    @staticmethod
    async def get_algorithm_comparison(db: AsyncSession) -> list[dict[str, Any]]:
        """
        Compare algorithms across multiple metrics

        Returns array of algorithm stats with recommendations
        """
        acceptance_data = await SuggestionAnalytics.get_acceptance_rates(db)

        # Get average confidence scores by algorithm
        query = select(
            LinkSuggestion.suggestion_method,
            func.avg(LinkSuggestion.similarity_score).label("avg_score"),
            func.count(LinkSuggestion.id).label("total"),
        ).group_by(LinkSuggestion.suggestion_method)

        result = await db.execute(query)
        rows = result.all()

        comparison = []
        for method, avg_score, total in rows:
            method_name = method.value if hasattr(method, "value") else str(method)
            algo_data = acceptance_data["by_algorithm"].get(method_name, {})

            comparison.append(
                {
                    "algorithm": method_name,
                    "total_suggestions": total,
                    "acceptance_rate": algo_data.get("rate", 0.0),
                    "avg_confidence": round(float(avg_score), 3) if avg_score else 0.0,
                    "accepted": algo_data.get("accepted", 0),
                    "rejected": algo_data.get("rejected", 0),
                    "pending": algo_data.get("pending", 0),
                }
            )

        # Sort by acceptance rate descending
        comparison.sort(key=lambda x: x["acceptance_rate"], reverse=True)

        return comparison
