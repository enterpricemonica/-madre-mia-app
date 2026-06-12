"""Atrapador de webhooks SOLO para probar el mock: guarda lo que reciba en un log."""
import json
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/catch")
async def catch(req: Request):
    data = await req.json()
    with open("/tmp/madremia-webhooks.log", "a") as f:
        f.write(json.dumps(data) + "\n")
    return {"ok": True}
