"""Tests for external_results Pydantic schemas (BGSTM#299)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import pytest

from app.schemas.external_results import (
    ArtifactCreate,
    ArtifactKind,
    ArtifactResponse,
    CaseOutcome,
    CaseResultCreate,
    CaseResultResponse,
    CaseResultUpdate,
    ErrorResponse,
    RunStatus,
    SessionCreate,
    SessionFinish,
    SessionResponse,
)

# ---------------------------------------------------------------------------
# Enum value tests
# ---------------------------------------------------------------------------


class TestRunStatus:
    def test_all_values(self):
        assert set(RunStatus) == {
            RunStatus.started,
            RunStatus.passed,
            RunStatus.failed,
            RunStatus.skipped,
            RunStatus.aborted,
        }

    def test_string_values(self):
        assert RunStatus.started.value == "started"
        assert RunStatus.passed.value == "passed"
        assert RunStatus.failed.value == "failed"
        assert RunStatus.skipped.value == "skipped"
        assert RunStatus.aborted.value == "aborted"


class TestCaseOutcome:
    def test_all_values(self):
        assert set(CaseOutcome) == {
            CaseOutcome.passed,
            CaseOutcome.failed,
            CaseOutcome.skipped,
            CaseOutcome.flaky,
        }

    def test_string_values(self):
        assert CaseOutcome.passed.value == "passed"
        assert CaseOutcome.failed.value == "failed"
        assert CaseOutcome.skipped.value == "skipped"
        assert CaseOutcome.flaky.value == "flaky"


class TestArtifactKind:
    def test_all_values(self):
        assert set(ArtifactKind) == {
            ArtifactKind.screenshot,
            ArtifactKind.trace,
            ArtifactKind.video,
            ArtifactKind.log,
            ArtifactKind.other,
        }

    def test_string_values(self):
        assert ArtifactKind.screenshot.value == "screenshot"
        assert ArtifactKind.trace.value == "trace"
        assert ArtifactKind.video.value == "video"
        assert ArtifactKind.log.value == "log"
        assert ArtifactKind.other.value == "other"


# ---------------------------------------------------------------------------
# SessionFinish validator
# ---------------------------------------------------------------------------


class TestSessionFinish:
    def test_passed_is_allowed(self):
        sf = SessionFinish(status=RunStatus.passed, summary={})
        assert sf.status == RunStatus.passed

    def test_failed_is_allowed(self):
        sf = SessionFinish(status=RunStatus.failed, summary={"total": 5, "failed": 3})
        assert sf.status == RunStatus.failed

    def test_aborted_is_allowed(self):
        sf = SessionFinish(status=RunStatus.aborted, summary={})
        assert sf.status == RunStatus.aborted

    def test_started_is_rejected(self):
        with pytest.raises(ValueError, match="started"):
            SessionFinish(status=RunStatus.started, summary={})

    def test_skipped_is_rejected(self):
        with pytest.raises(ValueError):
            SessionFinish(status=RunStatus.skipped, summary={})

    def test_summary_defaults_to_empty_dict(self):
        sf = SessionFinish(status=RunStatus.passed)
        assert sf.summary == {}


# ---------------------------------------------------------------------------
# CaseResultCreate validator
# ---------------------------------------------------------------------------


class TestCaseResultCreate:
    def _base(self, **kwargs):
        base = dict(
            session_id=uuid.uuid4(),
            title="Login test",
            outcome=CaseOutcome.passed,
            duration_ms=100,
        )
        base.update(kwargs)
        return base

    def test_rejects_neither_id(self):
        with pytest.raises(ValueError, match="At least one of"):
            CaseResultCreate(**self._base())

    def test_accepts_only_external_id(self):
        obj = CaseResultCreate(**self._base(external_id="spec::login"))
        assert obj.external_id == "spec::login"
        assert obj.test_case_id is None

    def test_accepts_only_test_case_id(self):
        tc_id = uuid.uuid4()
        obj = CaseResultCreate(**self._base(test_case_id=tc_id))
        assert obj.test_case_id == tc_id
        assert obj.external_id is None

    def test_accepts_both_ids(self):
        tc_id = uuid.uuid4()
        obj = CaseResultCreate(**self._base(test_case_id=tc_id, external_id="spec::login"))
        assert obj.test_case_id == tc_id
        assert obj.external_id == "spec::login"

    def test_duration_ms_rejects_negative(self):
        with pytest.raises(ValueError):
            CaseResultCreate(**self._base(external_id="x", duration_ms=-1))

    def test_duration_ms_accepts_zero(self):
        obj = CaseResultCreate(**self._base(external_id="x", duration_ms=0))
        assert obj.duration_ms == 0

    def test_requirement_ids_defaults_to_empty(self):
        obj = CaseResultCreate(**self._base(external_id="x"))
        assert obj.requirement_ids == []


# ---------------------------------------------------------------------------
# Round-trip tests: model_dump_json -> model_validate_json
# ---------------------------------------------------------------------------


class TestRoundTrip:
    _now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    _session_id = uuid.uuid4()
    _project_id = uuid.uuid4()
    _case_id = uuid.uuid4()
    _artifact_id = uuid.uuid4()

    def test_session_create_roundtrip(self):
        obj = SessionCreate(
            runner="@bgstm/playwright-core@0.1.0",
            project_id=self._project_id,
            git_sha="abc123",
            git_branch="main",
            ci_url="https://ci.example.com/run/42",  # type: ignore[arg-type]
            metadata={"os": "linux"},
        )
        restored = SessionCreate.model_validate_json(obj.model_dump_json())
        assert restored.runner == obj.runner
        assert restored.project_id == obj.project_id
        assert restored.git_sha == obj.git_sha
        assert str(restored.ci_url) == str(obj.ci_url)

    def test_session_response_roundtrip(self):
        obj = SessionResponse(
            id=self._session_id,
            status=RunStatus.started,
            started_at=self._now,
            runner="pytest-bgstm@1.0",
            project_id=self._project_id,
        )
        restored = SessionResponse.model_validate_json(obj.model_dump_json())
        assert restored.id == obj.id
        assert restored.status == RunStatus.started
        assert restored.finished_at is None

    def test_case_result_create_roundtrip(self):
        req_id = uuid.uuid4()
        obj = CaseResultCreate(
            session_id=self._session_id,
            external_id="suite::test_login",
            title="Login test",
            outcome=CaseOutcome.passed,
            duration_ms=250,
            requirement_ids=[req_id],
        )
        restored = CaseResultCreate.model_validate_json(obj.model_dump_json())
        assert restored.external_id == obj.external_id
        assert restored.outcome == CaseOutcome.passed
        assert restored.requirement_ids == [req_id]

    def test_case_result_response_roundtrip(self):
        obj = CaseResultResponse(
            id=self._case_id,
            session_id=self._session_id,
            external_id="suite::test_login",
            title="Login test",
            outcome=CaseOutcome.failed,
            duration_ms=500,
            created_at=self._now,
            auto_registered=True,
        )
        restored = CaseResultResponse.model_validate_json(obj.model_dump_json())
        assert restored.id == obj.id
        assert restored.auto_registered is True

    def test_case_result_update_roundtrip(self):
        obj = CaseResultUpdate(outcome=CaseOutcome.flaky, duration_ms=300)
        restored = CaseResultUpdate.model_validate_json(obj.model_dump_json())
        assert restored.outcome == CaseOutcome.flaky
        assert restored.duration_ms == 300

    def test_artifact_create_roundtrip(self):
        obj = ArtifactCreate(
            case_result_id=self._case_id,
            kind=ArtifactKind.screenshot,
            filename="failure.png",
            content_type="image/png",
            size_bytes=20480,
        )
        restored = ArtifactCreate.model_validate_json(obj.model_dump_json())
        assert restored.kind == ArtifactKind.screenshot
        assert restored.size_bytes == 20480

    def test_artifact_response_roundtrip(self):
        obj = ArtifactResponse(
            id=self._artifact_id,
            case_result_id=self._case_id,
            kind=ArtifactKind.trace,
            filename="trace.zip",
            content_type="application/zip",
            size_bytes=1024,
            url="https://storage.example.com/artifacts/trace.zip",  # type: ignore[arg-type]
            uploaded_at=self._now,
        )
        restored = ArtifactResponse.model_validate_json(obj.model_dump_json())
        assert restored.id == obj.id
        assert str(restored.url) == str(obj.url)

    def test_error_response_roundtrip(self):
        obj = ErrorResponse(
            code="runner_token.invalid",
            message="The provided runner token is invalid or has been revoked.",
            details={"token_prefix": "bgstm_runner_"},
        )
        raw = json.loads(obj.model_dump_json())
        restored = ErrorResponse.model_validate(raw)
        assert restored.code == obj.code
        assert restored.details == obj.details
