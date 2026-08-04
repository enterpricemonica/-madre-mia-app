"""Nothing that looks like a real credential may be committed.

This repository is PUBLIC. `.env.example` is tracked on purpose — it documents
which variables exist — and that is exactly why real values slipped into it:
the file looks harmless. Four live Wompi sandbox keys sat in it publicly until
2026-08-03.

Deleting a secret in a later commit does not remove it from history, so the fix
for a leak is always rotation, never deletion. This test exists to stop the next
one happening.
"""
import re
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent

# Prefixes real providers use. A placeholder never carries one of these followed
# by a long random-looking tail.
SUSPICIOUS = [
    (re.compile(r"prv_(test|prod)_[A-Za-z0-9]{20,}"), "Wompi private key"),
    (re.compile(r"pub_(test|prod)_[A-Za-z0-9]{20,}"), "Wompi public key"),
    (re.compile(r"sk_(test|live)_[A-Za-z0-9]{20,}"), "Stripe secret key"),
    (re.compile(r"postgres(?:ql)?://[^:\s]+:(?!CONTRASENA|PASSWORD|xxx)[^@\s]{6,}@"), "database password"),
]


def test_env_example_holds_no_real_credentials():
    text = (BACKEND / ".env.example").read_text(encoding="utf-8")
    found = [name for pattern, name in SUSPICIOUS if pattern.search(text)]
    assert not found, (
        f".env.example appears to contain real credentials: {found}. "
        "Replace them with placeholders AND rotate the exposed keys — the file "
        "is public, and git history keeps them even after they are removed."
    )


def test_real_env_is_not_tracked_by_git():
    """`.env` itself must stay out of version control."""
    gitignore = (BACKEND.parent / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore, ".gitignore no longer excludes .env"
