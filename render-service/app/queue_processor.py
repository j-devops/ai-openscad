"""Redis queue processor for rendering jobs"""

import json
import time
from pathlib import Path
import logging
from redis import Redis
from app.renderer import OpenSCADRenderer

logger = logging.getLogger(__name__)


class RenderQueueProcessor:
    """Process rendering jobs from Redis queue"""

    def __init__(self, redis_url: str, data_path: Path):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.data_path = Path(data_path)
        self.renderer = OpenSCADRenderer()

    def run(self):
        """Continuously process render queue"""
        logger.info("Queue processor started")

        while True:
            try:
                # Blocking pop from queue (timeout 5 seconds)
                job_raw = self.redis.brpop('render_queue', timeout=5)

                if job_raw:
                    _, job_json = job_raw
                    job = json.loads(job_json)
                    self.process_job(job)
                else:
                    # No jobs, just wait
                    time.sleep(0.1)

            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                time.sleep(1)

    def process_job(self, job: dict):
        """Process single render job

        Args:
            job: Job dictionary with job_id, scad_path, format
        """
        job_id = job['job_id']
        scad_path = Path(job['scad_path'])

        logger.info(f"Processing job: {job_id}")

        # Update status to processing
        job['status'] = 'processing'
        self.redis.setex(f'job:{job_id}', 3600, json.dumps(job))

        try:
            errors = []

            # Render PNG preview
            preview_path = self.data_path / "renders" / f"{job_id}.png"
            preview_success, preview_error = self.renderer.render_png(scad_path, preview_path)

            if preview_success:
                job['preview_url'] = f"/api/v1/render/{job_id}/preview"
                logger.info(f"Preview ready: {job_id}")
            elif preview_error:
                errors.append(f"Preview: {preview_error}")

            # Render STL if requested
            if job['format'] in ['stl', 'both']:
                stl_path = self.data_path / "exports" / f"{job_id}.stl"
                stl_success, stl_error = self.renderer.render_stl(scad_path, stl_path)

                if stl_success:
                    job['stl_url'] = f"/api/v1/render/{job_id}/download"
                    logger.info(f"STL ready: {job_id}")
                elif stl_error:
                    errors.append(f"STL: {stl_error}")

            # Set final status
            if errors:
                job['status'] = 'failed'
                job['error'] = '; '.join(errors)
                logger.error(f"Job failed: {job_id} - {job['error']}")
            else:
                job['status'] = 'completed'
                logger.info(f"Job completed: {job_id}")

        except Exception as e:
            job['status'] = 'failed'
            job['error'] = str(e)
            logger.error(f"Job failed: {job_id} - {str(e)}")

        # Update final status
        self.redis.setex(f'job:{job_id}', 3600, json.dumps(job))
