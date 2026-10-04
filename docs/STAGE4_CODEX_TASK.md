# Stage 4 — Reconstruction + Real 3D Viewer

## Objective
Connect Toomuch3D's existing reconstruction abstraction to a real mesh-generation backend and display the resulting mesh in the browser.

## Existing contract
Generation:
- POST /v1/generate
- GET /v1/jobs/{job_id}

Reconstruction:
- POST /v1/jobs/{job_id}/reconstruct
- GET /v1/jobs/{job_id}/mesh

Configuration:
- TOOMUCH3D_RECONSTRUCTION_COMMAND
- TOOMUCH3D_RECONSTRUCTION_TIMEOUT

## Work items
1. Evaluate Hi3DGen as the first reconstruction/geometry candidate.
2. Verify code and model/checkpoint licensing before vendoring or redistribution.
3. Prefer an external-engine adapter or subprocess boundary rather than merging the whole research repo into Toomuch3D.
4. Implement reliable reconstruction job state: queued, processing, complete, failed.
5. Return mesh metadata including format and download URL.
6. Add a browser 3D viewer for GLB output.
7. Add orbit, zoom, reset-camera, wireframe/background controls where practical.
8. Add download actions for supported formats.
9. Keep STL/3MF print preparation separate from visual GLB generation.
10. Add tests for API readiness and failure paths.

## Browser bug-fix requirements
- App must start even if Hi3D or reconstruction engines are absent.
- UI must clearly display which dependency/checkpoint is missing.
- Avoid infinite polling if a job fails.
- Reconstruction polling must stop and show an error when reconstruction fails.
- Disable actions that cannot currently succeed.

## Stage 4 acceptance criteria
- Fresh Python environment can start the FastAPI app without GPU dependencies.
- / renders successfully.
- /health returns 200.
- /v1/system returns explicit Hi3D and reconstruction readiness.
- With configured engines, image generation can reach a completed multi-view job.
- Reconstruction produces a real mesh file.
- Browser can load and rotate a GLB model.
- User can download the generated mesh.
- Missing GPU/model dependencies produce actionable messages rather than a blank page or server crash.

## Future Stage 5
3D-print preparation:
- target dimensions in mm
- flat base
- watertight repair
- normals repair
- decimation
- STL export
- 3MF export
- optional Bambu-oriented workflow
