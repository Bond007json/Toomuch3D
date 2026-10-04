import os
import shlex
import subprocess
from pathlib import Path

from app.config import settings

class ReconstructionError(RuntimeError):
    pass

class ReconstructionEngine:
    """Runs a configured multi-view-to-mesh command and returns its mesh output."""

    supported_extensions = (".glb", ".obj", ".stl", ".ply")

    @property
    def configured(self) -> bool:
        return bool(settings.reconstruction_command)

    def reconstruct(self, views_dir: Path, output_dir: Path) -> Path:
        if not self.configured:
            raise ReconstructionError(
                "Reconstruction is not configured. Set TOOMUCH3D_RECONSTRUCTION_COMMAND."
            )
        output_dir.mkdir(parents=True, exist_ok=True)
        command = settings.reconstruction_command.format(
            views=str(views_dir.resolve()),
            output=str(output_dir.resolve()),
        )
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(settings.cuda_device)
        result = subprocess.run(
            shlex.split(command),
            env=env,
            capture_output=True,
            text=True,
            timeout=settings.reconstruction_timeout,
        )
        if result.returncode != 0:
            raise ReconstructionError(result.stderr[-4000:] or "Reconstruction failed")
        meshes = []
        for ext in self.supported_extensions:
            meshes.extend(output_dir.rglob(f"*{ext}"))
        if not meshes:
            raise ReconstructionError("Reconstruction completed but produced no supported mesh file.")
        return max(meshes, key=lambda p: p.stat().st_mtime)
