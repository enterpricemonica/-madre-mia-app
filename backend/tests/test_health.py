"""The endpoint the uptime monitor watches.

It must fail when the database is unreachable, not just when the process dies —
a health check that only proves Python is running would have reported this app
as healthy through an outage where no customer could see the menu.
"""


def test_health_ok_when_database_answers(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_reports_503_when_database_fails(client, monkeypatch):
    import main
    from fastapi import HTTPException

    def broken(*args, **kwargs):
        raise RuntimeError("connection refused")

    # Replace the session's execute so the endpoint hits a real failure.
    from sqlalchemy.orm import Session
    monkeypatch.setattr(Session, "execute", broken)

    r = client.get("/health")
    assert r.status_code == 503
    assert "database" in r.json()["detail"]
