import os
import subprocess
import sys
from pathlib import Path

from app.config import settings

class Hi3DError(RuntimeError):
    pass

class Hi3DEngine:
    """Adapter around the upstream Hi3D Stage 1 and Stage 2 inference scripts."""

    def _run(self, script: str, checkpoint: Path, image_path: Path, output_dir: Path) -> None:
        root = settings.hi3d_root.resolve()
        script_path = root / script
        if not script_path.exists():
            raise Hi3DError(f"Hi3D script not found: {script_path}")
        if not checkpoint.exists():
            raise Hi3DError(f"Checkpoint not found: {checkpoint}")

        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(settings.cuda_device)
        cmd = [
            sys.executable,
            str(script_path),
            "--denoise_checkpoint", str(checkpoint.resolve()),
            "--image_path", str(image_path.resolve()),
            "--output_dir", str(output_dir.resolve()),
        ]
        result = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise Hi3DError(result.stderr[-4000:] or "Hi3D inference failed")

    def generate_multiviews(self, image_path: Path, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        self._run("pipeline_i2v_eval_v01.py", settings.first_stage_checkpoint, image_path, output_dir)
        self._run("pipeline_i2v_eval_v02.py", settings.second_stage_checkpoint, image_path, output_dir)
        return output_dir
