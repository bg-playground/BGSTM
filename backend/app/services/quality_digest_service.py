"""Build and dispatch scheduled Quality KPI digests."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import quality_digest as digest_crud
from app.crud import quality_metrics as quality_crud
from app.crud.notification import create_notification
from app.crud.quality_recovery import get_recovery_trend
from app.models.notification import NotificationType
from app.models.quality_digest_subscription import QualityDigestSubscription


@dataclass(frozen=True)
class QualityDigest:
    window_days: int
    title: str
    body: str
    dashboard_path: str


async def build_digest(db: AsyncSession, window_days: int) -> QualityDigest:
    pass_rate = await quality_crud.get_pass_rate_trend(db, window_days)
    defects = await quality_crud.get_defect_trend(db, window_days)
    modules = await quality_crud.get_defects_by_module(db, window_days, 3)
    automation = await quality_crud.get_automation_coverage(db)
    summary = await quality_crud.get_summary_stats(db)
    recovery = await get_recovery_trend(db, window_days, "overall")

    executions = sum(point.total_executed for point in pass_rate.points)
    passed = sum(round(point.total_executed * point.pass_rate_pct / 100) for point in pass_rate.points)
    failed = sum(point.total for point in defects.points)

    lines = [f"Quality KPI digest — last {window_days} days"]
    if executions:
        lines.append(f"Execution pass rate: {passed}/{executions} ({passed / executions * 100:.2f}%).")
    else:
        lines.append(f"Execution pass rate: {pass_rate.reason or 'No executions are available.'}")
    lines.append(f"Failed executions: {failed}.")
    lines.append(f"Open critical failures (current): {summary.open_critical_defects}.")
    if automation.reason:
        lines.append(f"Automation coverage (current): {automation.reason}")
    else:
        lines.append(
            f"Automation coverage (current): {automation.percent_automated:.2f}% "
            f"({automation.automated}/{automation.total})."
        )
    if recovery.mean_recovery_hours is None:
        recovery_text = recovery.reason or "No resolved recovery episodes are available."
    else:
        recovery_text = f"{recovery.mean_recovery_hours:.2f} hours"
    lines.append(
        "Execution Mean Time to Recovery (time-to-green): "
        f"{recovery_text}; {recovery.resolved_episodes} resolved, {recovery.open_episodes} open. "
        "This is execution recovery, not defect lifecycle Mean Time To Repair."
    )
    if modules.modules:
        lines.append("Top failing modules: " + ", ".join(f"{item.module} ({item.count})" for item in modules.modules) + ".")
    else:
        lines.append(f"Top failing modules: {modules.reason or 'No failed executions in this window.'}")

    dashboard_path = f"/quality-dashboard?window={window_days}"
    lines.append(f"Dashboard: {dashboard_path}")
    return QualityDigest(
        window_days=window_days,
        title=f"Quality KPI Digest — {window_days} days",
        body="\n".join(lines),
        dashboard_path=dashboard_path,
    )


async def deliver_in_app(
    db: AsyncSession,
    subscription: QualityDigestSubscription,
    digest: QualityDigest,
) -> None:
    await create_notification(
        db,
        user_id=subscription.user_id,
        type=NotificationType.QUALITY_DIGEST,
        title=digest.title,
        message=digest.body,
        metadata={"window_days": digest.window_days, "dashboard_path": digest.dashboard_path},
    )


async def dispatch_due_digests(db: AsyncSession, now: datetime | None = None) -> int:
    now = now or datetime.utcnow()
    due = await digest_crud.get_due_subscriptions(db, now)
    delivered = 0
    for subscription in due:
        digest = await build_digest(db, subscription.window_days)
        await deliver_in_app(db, subscription, digest)
        await digest_crud.mark_delivered(db, subscription, now)
        delivered += 1
    return delivered
