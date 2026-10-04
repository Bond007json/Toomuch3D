# Toomuch3D

Toomuch3D is an image-to-3D application foundation built around a modular generation pipeline.

## MVP pipeline

1. Upload a PNG/JPG/WebP image.
2. Preprocess the image.
3. Run Hi3D Stage 1 for multi-view generation.
4. Run Hi3D Stage 2 for high-resolution refinement.
5. Pass generated views to a reconstruction backend.
6. Preview and export the finished asset as GLB/OBJ/STL/3MF.

The current milestone implements the application/API layer and a Hi3D command adapter. Reconstruction and production mesh export are explicit extension points until a reconstruction backend is integrated.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Hi3D integration

Clone the upstream Hi3D project separately, download its required checkpoints, and configure the paths in `.env`. Keeping the research engine separate makes it easier to update or replace without coupling it to the web application.

## Attribution

The Hi3D integration is based on:

> Hi3D: Pursuing High-Resolution Image-to-3D Generation with Video Diffusion Models, Haibo Yang et al., ACM MM 2024.

Hi3D-Official is MIT licensed. See `THIRD_PARTY_NOTICES.md` and `licenses/Hi3D-MIT.txt`.

## Status

Milestone 2: browser upload workspace + asynchronous Hi3D generation flow.

### Browser UI

Run the API and open `http://127.0.0.1:8000/` to use the Toomuch3D workspace. It includes drag-and-drop upload, Object/Character/3D Print modes, live job polling, pipeline progress, and a Stage 3 reconstruction/viewer placeholder.
