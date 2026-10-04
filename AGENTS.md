# Toomuch3D — Codex Project Instructions

## Goal
Build Toomuch3D into a production-oriented image-to-3D web application.

Pipeline:
1. Browser image upload
2. Hi3D Stage 1 multi-view generation
3. Hi3D Stage 2 high-resolution refinement
4. Mesh reconstruction backend
5. Interactive browser 3D preview
6. Export GLB/OBJ/STL and later 3MF
7. 3D-print cleanup: physical dimensions, flat base, watertight repair, polygon reduction

## Current architecture
- FastAPI backend: app/main.py
- Settings: app/config.py
- Hi3D adapter: app/services/hi3d.py
- Reconstruction adapter: app/services/reconstruction.py
- Browser UI: app/static/
- Data: data/uploads and data/jobs
- Upstream Hi3D is external and configured with environment variables.

## Rules
- Do not remove Hi3D attribution or licenses/Hi3D-MIT.txt.
- Do not commit model checkpoints, uploaded images, generated meshes, secrets, or .env files.
- Never claim reconstruction/export functionality works unless it is exercised or clearly marked untested.
- Preserve Windows compatibility where practical, but GPU inference may run in Linux/Docker/cloud.
- Keep GPU workloads outside request handlers; API calls should queue/background long-running work.
- Return useful API errors to the browser instead of generic failures.
- Validate file types and paths.
- Prefer modular engine adapters so Hi3D/reconstruction engines can be replaced.
- Avoid copying third-party source into this repo unless its license and attribution requirements are reviewed.
- Before adding a model/checkpoint, verify its license separately from the source-code license.

## Development commands
Install:
    python -m venv .venv
    pip install -r requirements.txt

Run:
    uvicorn app.main:app --reload

Browser:
    http://127.0.0.1:8000/

API docs:
    http://127.0.0.1:8000/docs

Readiness:
    GET /health
    GET /v1/system

## Definition of done for code changes
- App imports without crashing when optional GPU engines are not installed.
- Browser root loads.
- /health returns successfully.
- /v1/system explains missing dependencies.
- New functionality has a focused test or reproducible verification step.
- README/.env.example updated when configuration changes.
