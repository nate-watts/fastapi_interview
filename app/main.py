from __future__ import annotations
from fastapi import FastAPI
from .routers import assets, vulnerabilities

app = FastAPI(
    title="Security Assets + Vulnerabilities",
    version="0.1.0",
    description="FastAPI app for interview exercises.",
)

app.include_router(assets.router)
app.include_router(vulnerabilities.router)


@app.get("/health")
def health():
    return {"status": "ok"}
