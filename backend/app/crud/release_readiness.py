from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.notification import create_notification_for_all_users
from app.models.link import RequirementTestCaseLink
from app.models.notification import NotificationType
from app.models.release_signoff import ReleaseSignoff, ReleaseSignoffRole
from app.models.requirement import Requirement
from app.models.suggestion import LinkSuggestion, SuggestionStatus
from app.models.test_case import TestCase
from app.models.user import User
from app.schemas.release_readiness import ReadinessCriterion, ReadinessSnapshot, ReadinessSummary, RoleSignoff

_READINESS_ROLES: tuple[ReleaseSignoffRole, ...] = (
    ReleaseSignoffRole.qa_lead,
    ReleaseSignoffRole.product,
    ReleaseSignoffRole.eng_lead,
)


def _to_role(value: str | ReleaseSignoffRole) -> ReleaseSignoffRole:
    if isinstance(value, ReleaseSignoffRole):
        return value
    if value.startswith("ReleaseSignoffRole."):
        value = value.split(".", 1)[1]
    return ReleaseSignoffRole(value)


def _format_ratio(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "data not available"
    percentage = numerator / denominator * 100
    return f"{percentage:.1f}% ({numerator}/{denominator})"


def _score_ratio(
    *,
    criterion_id: str,
    label: str,
    category: str,
    numerator: int,
    denominator: int,
    pass_threshold: float,
    warn_threshold: float,
    threshold: str,
) -> ReadinessCriterion:
    if denominator == 0:
        return ReadinessCriterion(
            id=criterion_id,
            label=label,
            status="na",
            value="data not available",
            threshold=threshold,
            category=category,
        )

    percentage = numerator / denominator * 100
    if percentage >= pass_threshold:
        status = "pass"
    elif percentage >= warn_threshold:
        status = "warn"
    else:
        status = "fail"

    return ReadinessCriterion(
        id=criterion_id,
        label=label,
        status=status,
        value=_format_ratio(numerator, denominator),
        threshold=threshold,
        category=category,
    )


async def _active_signoff_by_role(db: AsyncSession) -> dict[ReleaseSignoffRole, ReleaseSignoff]:
    result = await db.execute(
        select(ReleaseSignoff)
        .where(ReleaseSignoff.revoked_at.is_(None))  # type: ignore[attr-defined]
        .order_by(ReleaseSignoff.created_at.desc())
    )

    signoffs: dict[ReleaseSignoffRole, ReleaseSignoff] = {}
    for signoff in result.scalars().all():
        role_raw = signoff.role.value if isinstance(signoff.role, ReleaseSignoffRole) else str(signoff.role)
        role_key = _to_role(role_raw)
        if role_key not in signoffs:
            signoffs[role_key] = signoff
    return signoffs


async def create_signoff(
    db: AsyncSession,
    role: str | ReleaseSignoffRole,
    user_id: UUID,
    note: str | None = None,
) -> ReleaseSignoff:
    role_enum = _to_role(role)

    existing = await db.execute(
        select(ReleaseSignoff).where(
            ReleaseSignoff.role == role_enum,
            ReleaseSignoff.revoked_at.is_(None),  # type: ignore[attr-defined]
        )
    )
    current = existing.scalar_one_or_none()
    if current is not None:
        current.revoked_at = datetime.utcnow()

    signoff = ReleaseSignoff(
        role=role_enum,
        signed_off_by_user_id=user_id,
        signed_off_at=datetime.utcnow(),
        note=note,
    )
    db.add(signoff)
    await db.commit()
    await db.refresh(signoff)
    return signoff


async def revoke_signoff(db: AsyncSession, role: str | ReleaseSignoffRole, user_id: UUID) -> ReleaseSignoff | None:
    role_enum = _to_role(role)

    result = await db.execute(
        select(ReleaseSignoff).where(
            ReleaseSignoff.role == role_enum,
            ReleaseSignoff.revoked_at.is_(None),  # type: ignore[attr-defined]
        )
    )
    signoff = result.scalar_one_or_none()
    if signoff is None:
        return None

    signoff.revoked_at = datetime.utcnow()
    signoff.note = signoff.note or f"Revoked by user {user_id}"
    await db.commit()
    await db.refresh(signoff)
    return signoff


async def request_signoff(
    db: AsyncSession,
    role: str | ReleaseSignoffRole,
    requester: User,
    note: str | None = None,
) -> None:
    role_enum = _to_role(role)
    await create_notification_for_all_users(
        db,
        type=NotificationType.COVERAGE_DROP,
        title=f"Release sign-off requested: {role_enum.value}",
        message=(
            f"{requester.full_name or requester.email} requested {role_enum.value} sign-off"
            f" for release readiness.{f' Note: {note}' if note else ''}"
        ),
        metadata={"role": role_enum.value, "requested_by": str(requester.id)},
        exclude_user_id=requester.id,
    )


async def get_readiness_snapshot(db: AsyncSession) -> ReadinessSnapshot:
    total_requirements = (await db.execute(select(func.count()).select_from(Requirement))).scalar() or 0
    total_test_cases = (await db.execute(select(func.count()).select_from(TestCase))).scalar() or 0

    req_with_links = (
        await db.execute(
            select(func.count(func.distinct(RequirementTestCaseLink.requirement_id))).select_from(
                RequirementTestCaseLink
            )
        )
    ).scalar() or 0
    tc_with_links = (
        await db.execute(
            select(func.count(func.distinct(RequirementTestCaseLink.test_case_id))).select_from(RequirementTestCaseLink)
        )
    ).scalar() or 0

    total_suggestions = (await db.execute(select(func.count()).select_from(LinkSuggestion))).scalar() or 0
    pending_suggestions = (
        await db.execute(
            select(func.count()).select_from(LinkSuggestion).where(LinkSuggestion.status == SuggestionStatus.PENDING)
        )
    ).scalar() or 0

    criteria: list[ReadinessCriterion] = [
        _score_ratio(
            criterion_id="requirements_linked",
            label="Requirements with at least one linked test case",
            category="Coverage",
            numerator=req_with_links,
            denominator=total_requirements,
            pass_threshold=95,
            warn_threshold=80,
            threshold=">=95% pass, 80-94% warn, <80% fail",
        ),
        _score_ratio(
            criterion_id="test_cases_linked",
            label="Test cases with at least one linked requirement",
            category="Coverage",
            numerator=tc_with_links,
            denominator=total_test_cases,
            pass_threshold=90,
            warn_threshold=70,
            threshold=">=90% pass, 70-89% warn, <70% fail",
        ),
    ]

    if total_suggestions == 0:
        criteria.append(
            ReadinessCriterion(
                id="pending_link_suggestions",
                label="Pending link suggestions awaiting review",
                status="na",
                value="data not available",
                threshold="0 pass, 1-10 warn, >10 fail",
                category="Quality",
            )
        )
    else:
        if pending_suggestions == 0:
            pending_status = "pass"
        elif pending_suggestions <= 10:
            pending_status = "warn"
        else:
            pending_status = "fail"
        criteria.append(
            ReadinessCriterion(
                id="pending_link_suggestions",
                label="Pending link suggestions awaiting review",
                status=pending_status,
                value=f"{pending_suggestions}",
                threshold="0 pass, 1-10 warn, >10 fail",
                category="Quality",
            )
        )

    if hasattr(TestCase, "last_run_status"):
        never_executed_count = (
            await db.execute(
                select(func.count()).select_from(TestCase).where(getattr(TestCase, "last_run_status").is_(None))
            )
        ).scalar() or 0
        failed_count = (
            await db.execute(
                select(func.count()).select_from(TestCase).where(getattr(TestCase, "last_run_status") == "failed")
            )
        ).scalar() or 0

        if total_test_cases == 0:
            never_status = "na"
            never_value = "data not available"
        else:
            never_pct = never_executed_count / total_test_cases * 100
            if never_pct <= 5:
                never_status = "pass"
            elif never_pct <= 20:
                never_status = "warn"
            else:
                never_status = "fail"
            never_value = f"{never_pct:.1f}% ({never_executed_count}/{total_test_cases})"

        criteria.append(
            ReadinessCriterion(
                id="never_executed_test_cases",
                label="Test cases with no last_run_status (never executed)",
                status=never_status,
                value=never_value,
                threshold="<=5% pass, 6-20% warn, >20% fail",
                category="Quality",
            )
        )
        if total_test_cases == 0:
            failed_status = "na"
            failed_value = "data not available"
        elif failed_count == 0:
            failed_status = "pass"
            failed_value = "0"
        elif failed_count <= 3:
            failed_status = "warn"
            failed_value = str(failed_count)
        else:
            failed_status = "fail"
            failed_value = str(failed_count)

        criteria.append(
            ReadinessCriterion(
                id="failed_last_run_test_cases",
                label="Test cases with last_run_status == 'failed'",
                status=failed_status,
                value=failed_value,
                threshold="0 pass, 1-3 warn, >3 fail",
                category="Quality",
            )
        )
    else:
        criteria.extend(
            [
                ReadinessCriterion(
                    id="never_executed_test_cases",
                    label="Test cases with no last_run_status (never executed)",
                    status="na",
                    value="data not available",
                    threshold="<=5% pass, 6-20% warn, >20% fail",
                    category="Quality",
                ),
                ReadinessCriterion(
                    id="failed_last_run_test_cases",
                    label="Test cases with last_run_status == 'failed'",
                    status="na",
                    value="data not available",
                    threshold="0 pass, 1-3 warn, >3 fail",
                    category="Quality",
                ),
            ]
        )

    signoffs_by_role = await _active_signoff_by_role(db)
    user_ids = [str(s.signed_off_by_user_id) for s in signoffs_by_role.values()]
    users_by_id: dict[str, User] = {}
    if user_ids:
        users = (
            (
                await db.execute(select(User).where(User.id.in_(user_ids)))  # type: ignore[arg-type]
            )
            .scalars()
            .all()
        )
        users_by_id = {str(user.id): user for user in users}

    signoffs: list[RoleSignoff] = []
    for role in _READINESS_ROLES:
        signoff = signoffs_by_role.get(role)
        if signoff is None:
            signoffs.append(
                RoleSignoff(role=role.value, signed_off=False, signed_off_by=None, signed_off_at=None, note=None)
            )
            continue

        user = users_by_id.get(str(signoff.signed_off_by_user_id))
        signed_off_by = None
        if user is not None:
            signed_off_by = user.full_name or user.email

        signoffs.append(
            RoleSignoff(
                role=role.value,
                signed_off=True,
                signed_off_by=signed_off_by,
                signed_off_at=signoff.signed_off_at,
                note=signoff.note,
            )
        )

    all_roles_signed = all(signoff.signed_off for signoff in signoffs)
    criteria.append(
        ReadinessCriterion(
            id="all_roles_signed_off",
            label="All three roles signed off",
            status="pass" if all_roles_signed else "warn",
            value="yes" if all_roles_signed else "no",
            threshold="all roles required",
            category="Process",
        )
    )

    failed_count = sum(1 for c in criteria if c.status == "fail")
    warning_count = sum(1 for c in criteria if c.status == "warn")
    non_process_fail = any(c.status == "fail" and c.id != "all_roles_signed_off" for c in criteria)
    unsigned_roles = any(not signoff.signed_off for signoff in signoffs)

    if total_requirements == 0 or total_test_cases == 0:
        overall_status = "no_go"
    elif non_process_fail:
        overall_status = "no_go"
    elif warning_count > 0 or unsigned_roles:
        overall_status = "caution"
    else:
        overall_status = "go"

    summary = ReadinessSummary(
        total=len(criteria),
        passed=sum(1 for c in criteria if c.status == "pass"),
        failed=failed_count,
        warning=warning_count,
    )

    return ReadinessSnapshot(
        overall_status=overall_status,
        generated_at=datetime.now(timezone.utc),
        criteria=criteria,
        signoffs=signoffs,
        summary=summary,
    )
