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


# Colombia está en UTC-5 (sin horario de verano). created_at se guarda en UTC,
# así que 00:00 en Colombia = 05:00 en UTC. Con esto el cuadre del día es correcto.
COLOMBIA_OFFSET = timedelta(hours=5)


def _parse_date(date_str):
    """El día pedido (YYYY-MM-DD); si no viene, HOY en hora de Colombia."""
    if date_str:
        return date_cls.fromisoformat(date_str)
    return (datetime.utcnow() - COLOMBIA_OFFSET).date()


def _sales_summary(db: Session, day):
    # 'day' es una fecha de Colombia; convertimos sus límites a UTC para comparar.
    start = datetime(day.year, day.month, day.day) + COLOMBIA_OFFSET
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
    total = 0   # total cobrado (incluye propina, = lo que realmente entró)
    tips = 0    # de ese total, cuánto fue propina (para repartir al equipo, Ley 1935/2018)
    for p in payments:
        key = p.method or "otro"
        by_method[key] = by_method.get(key, 0) + p.amount
        total += p.amount
        tips += (p.order.tip_amount or 0) if p.order else 0

    return {
        "date": day.isoformat(),
        "total": total,                 # cobrado (ventas + propina)
        "tips": tips,                   # propina (subconjunto del total)
        "net_sales": total - tips,      # ventas del negocio, sin propina
        "count": len(payments),
        "by_method": by_method,
    }


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
    writer.writerow(["Ventas netas (sin propina)", summary["net_sales"]])
    writer.writerow(["Propinas (a repartir)", summary["tips"]])
    writer.writerow(["TOTAL COBRADO", summary["total"]])
    writer.writerow(["Pedidos", summary["count"]])

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="ventas-{summary["date"]}.csv"'},
    )
