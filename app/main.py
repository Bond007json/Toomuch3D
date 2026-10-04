import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.config import settings
from app.models import GenerationMode, JobResponse, JobStatus
from app.services.hi3d import Hi3DEngine, Hi3DError

app = FastAPI(title="Toomuch3D API", version="0.1.0")
engine = Hi3DEngine()
jobs: dict[str, JobResponse] = {}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Toomuch3D"}

@app.post("/v1/generate", response_model=JobResponse)
def generate(
    image: UploadFile = File(...),
    mode: GenerationMode = Form(GenerationMode.object),
) -> JobResponse:
    suffix = Path(image.filename or "input.png").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(400, "Upload PNG, JPG, JPEG, or WebP.")

    job_id = uuid.uuid4().hex
    job_dir = settings.data_dir / "jobs" / job_id
    upload_dir = settings.data_dir / "uploads"
    job_dir.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)
    source = upload_dir / f"{job_id}{suffix}"

    with source.open("wb") as target:
        shutil.copyfileobj(image.file, target)

    job = JobResponse(
        id=job_id,
        status=JobStatus.processing,
        mode=mode,
        source_image=str(source),
        output_dir=str(job_dir),
    )
    jobs[job_id] = job

    try:
        engine.generate_multiviews(source, job_dir / "multiview")
        job.status = JobStatus.complete
        job.message = "Multi-view generation complete. Reconstruction is the next pipeline stage."
    except Hi3DError as exc:
        job.status = JobStatus.failed
        job.message = str(exc)
        raise HTTPException(500, detail=job.model_dump()) from exc

    return job

@app.get("/v1/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]
