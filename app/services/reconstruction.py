from pathlib import Path

class ReconstructionNotConfigured(RuntimeError):
    pass

class ReconstructionEngine:
    """Interface for the next milestone's multi-view -> mesh backend."""

    def reconstruct(self, views_dir: Path, output_dir: Path) -> Path:
        raise ReconstructionNotConfigured(
            "3D reconstruction backend is not configured yet. "
            "Hi3D currently supplies the multi-view generation stage."
        )
