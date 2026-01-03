"""Render job management"""

import json
import uuid
from pathlib import Path
import logging
from redis import Redis

from app.config import settings

logger = logging.getLogger(__name__)


class RenderManager:
    """Manages rendering jobs and queue"""

    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.data_path = Path(settings.DATA_PATH)

    async def submit_render_job(self, code: str, format: str = 'both') -> str:
        """Submit rendering job to queue

        Args:
            code: OpenSCAD code to render
            format: Output format ('png', 'stl', or 'both')

        Returns:
            job_id: Unique job identifier
        """
        job_id = str(uuid.uuid4())

        # Save .scad file
        scad_path = self.data_path / "scad_files" / f"{job_id}.scad"
        scad_path.parent.mkdir(parents=True, exist_ok=True)
        scad_path.write_text(code)

        # Create job data
        job_data = {
            'job_id': job_id,
            'scad_path': str(scad_path),
            'format': format,
            'status': 'queued'
        }

        # Queue job (left push to list)
        self.redis.lpush('render_queue', json.dumps(job_data))

        # Store job status (with 1 hour TTL)
        self.redis.setex(f'job:{job_id}', 3600, json.dumps(job_data))

        logger.info(f"Queued render job: {job_id}")
        return job_id

    async def get_job_status(self, job_id: str) -> dict:
        """Get job status and results

        Args:
            job_id: Job identifier

        Returns:
            Job status dictionary

        Raises:
            ValueError: If job not found
        """
        job_data = self.redis.get(f'job:{job_id}')
        if not job_data:
            raise ValueError(f"Job not found: {job_id}")

        job = json.loads(job_data)

        # Build response
        response = {
            'job_id': job_id,
            'status': job.get('status', 'unknown')
        }

        if job.get('preview_url'):
            response['preview_url'] = job['preview_url']
        if job.get('stl_url'):
            response['stl_url'] = job['stl_url']
        if job.get('error'):
            response['error'] = job['error']

        return response

    async def update_job_status(self, job_id: str, updates: dict):
        """Update job status

        Args:
            job_id: Job identifier
            updates: Dictionary of fields to update
        """
        job_data = self.redis.get(f'job:{job_id}')
        if not job_data:
            raise ValueError(f"Job not found: {job_id}")

        job = json.loads(job_data)
        job.update(updates)

        # Update with extended TTL
        self.redis.setex(f'job:{job_id}', 3600, json.dumps(job))
        logger.info(f"Updated job {job_id}: {updates}")
