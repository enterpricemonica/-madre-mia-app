"""Health check — what the uptime monitor watches.

Deliberately a router, not a bare route on `app`: the test suite builds its app
from routers, so anything declared directly on `app` in main.py is never
exercised. A health check nobody tests is exactly the thing that quietly stops
working.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """Is the app actually usable right now?

    Touches the database on purpose. A 200 from `/` only proves the Python
    process is alive — if Postgres is unreachable the customer's menu fails
    while `/` keeps answering cheerfully, which is the kind of outage that
    goes unnoticed for weeks.
    """
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database unreachable")
    return {"status": "ok"}
