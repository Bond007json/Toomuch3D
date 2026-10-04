import shutil
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models import GenerationMode, JobResponse, JobStatus
from app.services.hi3d import Hi3DEngine, Hi3DError

app = FastAPI(title="Toomuch3D API", version="0.3.0")
engine = Hi3DEngine()
jobs: dict[str, JobResponse] = {}

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", include_in_schema=False)
def index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Toomuch3D</h1><p>UI files are missing. Reinstall or update the repository.</p>", status_code=503)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Toomuch3D"}

@app.get("/v1/system")
def system_status() -> dict:
    root = settings.hi3d_root.resolve()
    checks = {
        "hi3d_root": root.exists(),
        "stage1_script": (root / "pipeline_i2v_eval_v01.py").exists(),
        "stage2_script": (root / "pipeline_i2v_eval_v02.py").exists(),
        "stage1_checkpoint": settings.first_stage_checkpoint.exists(),
        "stage2_checkpoint": settings.second_stage_checkpoint.exists(),
    }
    return {"ready": all(checks.values()), "checks": checks}

def run_generation(job_id: str, source: Path, job_dir: Path) -> None:
    job = jobs[job_id]
    job.status = JobStatus.processing
    job.message = "Generating high-resolution multi-view images..."
    try:
        engine.generate_multiviews(source, job_dir / "multiview")
        job.status = JobStatus.complete
        job.message = "Multi-view generation complete. Ready for reconstruction."
    except Exception as exc:
        job.status = JobStatus.failed
        job.message = str(exc)[:4000]

@app.post("/v1/generate", response_model=JobResponse)
def generate(background_tasks: BackgroundTasks,image: UploadFile = File(...),mode: GenerationMode = Form(GenerationMode.object)) -> JobResponse:
    suffix = Path(image.filename or "input.png").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(400, "Upload PNG, JPG, JPEG, or WebP.")
    status = system_status()
    if not status["ready"]:
        missing = ", ".join(k for k, ok in status["checks"].items() if not ok)
        raise HTTPException(503, f"Hi3D is not configured. Missing: {missing}")
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
