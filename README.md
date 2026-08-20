# ArtifactQA

Evidence-bound inspection receipts for generated media and other binary
artifacts.

ArtifactQA does not certify safety, copyright clearance, legal compliance or
overall visual quality. It makes one narrower guarantee: an inspection verdict
is attached to the SHA-256 of the exact file that was inspected. An unavailable
inspector produces unknown, never pass.

## Install

~~~bash
pip install artifactqa
~~~

## Example

~~~python
from artifactqa import Inspection, inspect

receipt = inspect(
    "render.mp4",
    inspector=lambda path: Inspection(verdict="pass", summary="no visible defect"),
    inspector_name="local-policy-check",
    policy_version="2026-08",
)

assert receipt.matches("render.mp4")
~~~

## Integration guidance

Treat unknown as a blocking state for automated downstream actions. Store the
receipt with the artifact and create a new receipt after each binary change.
Use Approval Ledger or another human-review system for the decision to release
an artifact.

## Development

~~~bash
PYTHONPATH=src python -m unittest discover -s tests -v
uv build
~~~

## License

MIT. See [LICENSE](LICENSE).
