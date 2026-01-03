"""Rendering endpoints"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import logging

from app.core.render_manager import RenderManager
from app.utils.security import SecurityValidator
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize render manager
render_manager = RenderManager()


class RenderRequest(BaseModel):
    """Render request model"""
    code: str
    format: str = "both"  # 'png', 'stl', or 'both'


class RenderResponse(BaseModel):
    """Render response model"""
    job_id: str
    status: str
    preview_url: str | None = None
    stl_url: str | None = None
    error: str | None = None


@router.post("/", response_model=RenderResponse)
async def submit_render_job(request: RenderRequest):
    """Submit a rendering job"""
    try:
        # Validate code
        is_valid, errors = SecurityValidator.validate_scad_code(request.code)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Code validation failed: {', '.join(errors)}"
            )

        # Submit job
        job_id = await render_manager.submit_render_job(request.code, request.format)

        logger.info(f"Render job submitted: {job_id}")

        return RenderResponse(
            job_id=job_id,
            status="queued"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit render job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit render job: {str(e)}")


@router.get("/{job_id}", response_model=RenderResponse)
async def get_render_status(job_id: str):
    """Get render job status"""
    try:
        status = await render_manager.get_job_status(job_id)
        return RenderResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get render status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/preview")
async def get_preview(job_id: str):
    """Get PNG preview image"""
    preview_path = Path(settings.DATA_PATH) / "renders" / f"{job_id}.png"

    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="Preview not found")

    return FileResponse(
        preview_path,
        media_type="image/png",
        filename=f"{job_id}.png"
    )


@router.get("/{job_id}/download")
async def download_stl(job_id: str):
    """Download STL file"""
    stl_path = Path(settings.DATA_PATH) / "exports" / f"{job_id}.stl"

    if not stl_path.exists():
        raise HTTPException(status_code=404, detail="STL file not found")

    return FileResponse(
        stl_path,
        media_type="application/sla",
        filename=f"model_{job_id}.stl",
        headers={"Content-Disposition": f"attachment; filename=model_{job_id}.stl"}
    )
