from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os

from visionsafe.backend.database import load_database, get_statistics

app = FastAPI(title="VisionSafe API")

# Allow cross-origin access so any frontend can query the API during demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    """Return summary statistics for the frontend dashboard."""
    stats = get_statistics()
    return {
        "total_violations": stats.get("total_violations", 0),
        "unique_workers": stats.get("unique_workers", 0),
        "most_common_violation": stats.get("most_common_violation", "None"),
    }


@app.get("/recent")
def recent(limit: int = 10):
    """Return recent violation records (latest first)."""
    df = load_database()
    if df.empty:
        return []
    records = df.tail(limit).to_dict(orient="records")
    # Reverse so the newest appears first
    return list(reversed(records))


@app.get("/evidence/{filename}")
def evidence(filename: str):
    """Serve an evidence image by filename from the evidence directory."""
    path = os.path.join("evidence_snaps", filename)
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"error": "not found"})
    # Let FastAPI/Starlette handle efficient file serving
    return FileResponse(path, media_type="image/jpeg")


# Note: for production run with `uvicorn visionsafe.api:app --host 0.0.0.0 --port 8000`
