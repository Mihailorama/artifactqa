"""Evidence-bound inspection receipts for binary artifacts."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Literal


Verdict = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class Inspection:
    verdict: Verdict
    summary: str = ""

    def __post_init__(self) -> None:
        if self.verdict not in {"pass", "fail", "unknown"}:
            raise ValueError("inspection verdict must be pass, fail, or unknown")


@dataclass(frozen=True)
class InspectionReceipt:
    artifact_sha256: str
    artifact_size: int
    verdict: Verdict
    summary: str
    reason: str | None
    inspector_name: str
    policy_version: str
    inspected_at: str

    def matches(self, path: str | Path) -> bool:
        target = Path(path)
        return target.is_file() and _digest(target) == self.artifact_sha256


Inspector = Callable[[Path], Inspection]


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def inspect(
    path: str | Path,
    *,
    inspector: Inspector,
    inspector_name: str,
    policy_version: str,
) -> InspectionReceipt:
    """Inspect one file and return an auditable receipt.

    An inspector error is represented as unknown, never as pass.
    """

    artifact = Path(path)
    if not artifact.is_file():
        raise FileNotFoundError(artifact)
    if not inspector_name.strip() or not policy_version.strip():
        raise ValueError("inspector_name and policy_version are required")
    artifact_sha256 = _digest(artifact)
    try:
        result = inspector(artifact)
    except Exception as exc:
        result = Inspection(verdict="unknown", summary="")
        reason = str(exc) or exc.__class__.__name__
    else:
        reason = None
    return InspectionReceipt(
        artifact_sha256=artifact_sha256,
        artifact_size=artifact.stat().st_size,
        verdict=result.verdict,
        summary=result.summary,
        reason=reason,
        inspector_name=inspector_name,
        policy_version=policy_version,
        inspected_at=datetime.now(UTC).isoformat(),
    )


__all__ = ["Inspection", "InspectionReceipt", "Inspector", "Verdict", "inspect"]
