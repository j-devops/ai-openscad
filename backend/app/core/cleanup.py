"""Background task for cleaning up old files"""

import os
import time
import logging
from pathlib import Path
from typing import List

from app.config import settings

logger = logging.getLogger(__name__)


class FileCleanup:
    """Manages cleanup of old generated files"""

    def __init__(self, max_age_hours: int = 24):
        """
        Initialize file cleanup

        Args:
            max_age_hours: Maximum age of files in hours before deletion (default: 24)
        """
        self.max_age_hours = max_age_hours
        self.max_age_seconds = max_age_hours * 3600
        self.data_path = Path(settings.DATA_PATH)

    def cleanup_old_files(self) -> dict:
        """
        Remove files older than max_age_hours

        Returns:
            dict with cleanup statistics
        """
        if not self.data_path.exists():
            logger.warning(f"Data path does not exist: {self.data_path}")
            return {"deleted": 0, "errors": 0, "freed_bytes": 0}

        deleted_count = 0
        error_count = 0
        freed_bytes = 0
        cutoff_time = time.time() - self.max_age_seconds

        # Directories to clean
        directories_to_clean = [
            self.data_path / "scad_files",
            self.data_path / "renders",
            self.data_path / "logs"
        ]

        for directory in directories_to_clean:
            if not directory.exists():
                continue

            try:
                for file_path in directory.iterdir():
                    if not file_path.is_file():
                        continue

                    try:
                        # Check file modification time
                        file_mtime = file_path.stat().st_mtime
                        if file_mtime < cutoff_time:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_count += 1
                            freed_bytes += file_size
                            logger.debug(f"Deleted old file: {file_path.name}")

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error deleting file {file_path}: {str(e)}")

            except Exception as e:
                logger.error(f"Error scanning directory {directory}: {str(e)}")
                error_count += 1

        if deleted_count > 0:
            freed_mb = freed_bytes / (1024 * 1024)
            logger.info(
                f"Cleanup complete: deleted {deleted_count} files, "
                f"freed {freed_mb:.2f}MB, {error_count} errors"
            )
        else:
            logger.debug("Cleanup complete: no old files to delete")

        return {
            "deleted": deleted_count,
            "errors": error_count,
            "freed_bytes": freed_bytes
        }

    def get_disk_usage(self) -> dict:
        """
        Get current disk usage statistics

        Returns:
            dict with file counts and sizes by type
        """
        if not self.data_path.exists():
            return {}

        stats = {
            "scad_files": {"count": 0, "bytes": 0},
            "stl_files": {"count": 0, "bytes": 0},
            "png_files": {"count": 0, "bytes": 0},
            "log_files": {"count": 0, "bytes": 0},
            "total_bytes": 0
        }

        try:
            for root, dirs, files in os.walk(self.data_path):
                for filename in files:
                    file_path = Path(root) / filename
                    try:
                        file_size = file_path.stat().st_size

                        if filename.endswith('.scad'):
                            stats["scad_files"]["count"] += 1
                            stats["scad_files"]["bytes"] += file_size
                        elif filename.endswith('.stl'):
                            stats["stl_files"]["count"] += 1
                            stats["stl_files"]["bytes"] += file_size
                        elif filename.endswith('.png'):
                            stats["png_files"]["count"] += 1
                            stats["png_files"]["bytes"] += file_size
                        elif filename.endswith('.log'):
                            stats["log_files"]["count"] += 1
                            stats["log_files"]["bytes"] += file_size

                        stats["total_bytes"] += file_size

                    except Exception as e:
                        logger.error(f"Error stat'ing file {file_path}: {str(e)}")

        except Exception as e:
            logger.error(f"Error walking data directory: {str(e)}")

        return stats
