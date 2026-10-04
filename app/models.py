from enum import Enum
from pydantic import BaseModel

class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    complete = "complete"
    failed = "failed"

class GenerationMode(str, Enum):
    character = "character"
    object = "object"
    print3d = "3d-print"

class JobResponse(BaseModel):
    id: str
    status: JobStatus
    mode: GenerationMode
    source_image: str
    output_dir: str
    message: str | None = None
