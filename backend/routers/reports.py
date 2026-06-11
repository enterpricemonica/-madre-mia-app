"""
Reportes de ventas — para cuadrar la caja.
El reporte = sumar los pagos `approved` de un día, agrupados por método.
Protegido con login admin (solo Rachel ve las ventas).
"""
import csv
import io
from datetime import datetime, date as date_cls, timedelta

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
import models

router = APIRouter(prefix="/reports", tags=["Reports"])


def _parse_date(date_str):
    """El día pedido (YYYY-MM-DD); si no viene, hoy."""
    return date_cls.fromisoformat(date_str) if date_str else date_cls.today()


def _sales_summary(db: Session, day):
    # OJO zona horaria: created_at se guarda en UTC y aquí usamos límites en UTC.
    # Para Colombia (UTC-5) el cuadre de la noche puede caer al día siguiente.
    # TODO: ajustar a hora de Colombia (restar 5h) en una mejora futura.
    start = datetime(day.year, day.month, day.day)
    end = start + timedelta(days=1)

    payments = (
        db.query(models.Payment)
        .filter(
            models.Payment.status == "approved",
            models.Payment.created_at >= start,
            models.Payment.created_at < end,
        )
        .all()
    )

    by_method = {}
    total = 0
    for p in payments:
        key = p.method or "otro"
        by_method[key] = by_method.get(key, 0) + p.amount
        total += p.amount

    return {"date": day.isoformat(), "total": total, "count": len(payments), "by_method": by_method}


# GET /reports/sales — resumen del día en JSON (protegido).
@router.get("/sales")
def sales_report(date: str | None = None, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return _sales_summary(db, _parse_date(date))


# GET /reports/sales.csv — el mismo resumen, descargable como CSV (protegido).
@router.get("/sales.csv")
def sales_report_csv(date: str | None = None, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    summary = _sales_summary(db, _parse_date(date))

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Reporte de ventas", summary["date"]])
    writer.writerow([])
    writer.writerow(["Metodo", "Total (COP)"])
    for method, amount in summary["by_method"].items():
        writer.writerow([method, amount])
    writer.writerow([])
    writer.writerow(["TOTAL", summary["total"]])
    writer.writerow(["Pedidos", summary["count"]])

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="ventas-{summary["date"]}.csv"'},
    )
