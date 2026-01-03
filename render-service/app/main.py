"""Render service main entry point"""

import os
import logging
from pathlib import Path
from app.queue_processor import RenderQueueProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for render service"""
    logger.info("Starting OpenSCAD Render Service")

    # Get configuration from environment
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    data_path = Path(os.getenv('DATA_PATH', './data'))

    # Create data directories
    (data_path / "scad_files").mkdir(parents=True, exist_ok=True)
    (data_path / "renders").mkdir(parents=True, exist_ok=True)
    (data_path / "exports").mkdir(parents=True, exist_ok=True)

    logger.info(f"Data path: {data_path}")
    logger.info(f"Redis URL: {redis_url}")

    # Start queue processor
    processor = RenderQueueProcessor(redis_url, data_path)
    processor.run()


if __name__ == "__main__":
    main()
