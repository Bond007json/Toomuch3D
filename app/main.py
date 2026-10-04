import shutil
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models import GenerationMode, JobResponse, JobStatus
from app.services.hi3d import Hi3DEngine, Hi3DError

app = FastAPI(title="Toomuch3D API", version="0.2.0")
engine = Hi3DEngine()
jobs: dict[str, JobResponse] = {}
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Toomuch3D"}

def run_generation(job_id: str, source: Path, job_dir: Path) -> None:
    job = jobs[job_id]
    job.status = JobStatus.processing
    job.message = "Generating high-resolution multi-view images..."
    try:
        engine.generate_multiviews(source, job_dir / "multiview")
        job.status = JobStatus.complete
        job.message = "Multi-view generation complete. Reconstruction is the next pipeline stage."
    except Hi3DError as exc:
        job.status = JobStatus.failed
        job.message = str(exc)

@app.post("/v1/generate", response_model=JobResponse)
def generate(
    background_tasks: BackgroundTasks,
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
    job = JobResponse(id=job_id,status=JobStatus.queued,mode=mode,source_image=str(source),output_dir=str(job_dir),message="Job queued.")
    jobs[job_id] = job
    background_tasks.add_task(run_generation, job_id, source, job_dir)
    return job

@app.get("/v1/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]
