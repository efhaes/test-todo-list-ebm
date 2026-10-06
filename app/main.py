from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import todos
from app.core.database import engine

app = FastAPI(
    title="Todo List API",
    description=(
        "REST API Todo List dengan filtering, sorting, pagination, "
        "dan insert data random. Dibuat dengan FastAPI + SQLAlchemy + MySQL."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(todos.router)


@app.get("/health", tags=["Health"], summary="Cek aplikasi & koneksi database")
def health():
    """Dipakai untuk memastikan app hidup dan bisa konek ke MySQL."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database tidak bisa dihubungi")
    return {"status": "ok", "database": "up"}