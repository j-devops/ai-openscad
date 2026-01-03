"""OpenSCAD CLI renderer"""

import subprocess
import os
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OpenSCADRenderer:
    """OpenSCAD command-line renderer"""

    def __init__(self, openscad_binary: str = "/usr/bin/openscad"):
        self.binary = openscad_binary
        self.timeout = int(os.getenv('RENDER_TIMEOUT', '120'))

    def render_png(
        self,
        scad_file: Path,
        output_file: Path,
        size: tuple = (800, 600)
    ) -> tuple[bool, str | None]:
        """Render PNG preview

        Args:
            scad_file: Path to .scad file
            output_file: Path to output PNG file
            size: Image size (width, height)

        Returns:
            Tuple of (success, error_message)
        """
        try:
            cmd = [
                self.binary,
                "-o", str(output_file),
                f"--imgsize={size[0]},{size[1]}",
                "--colorscheme=Tomorrow",
                "--camera=0,0,0,55,0,25,500",
                "--autocenter",
                "--viewall",
                str(scad_file)
            ]

            logger.info(f"Rendering PNG: {scad_file.name}")

            # Run with xvfb for headless rendering
            env = os.environ.copy()
            env['DISPLAY'] = ':99'

            # Start Xvfb in background
            xvfb = subprocess.Popen(
                ['Xvfb', ':99', '-screen', '0', '1024x768x24'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            try:
                # Give Xvfb time to start
                time.sleep(0.5)

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env=env
                )

                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else "OpenSCAD rendering failed"
                    logger.error(f"OpenSCAD error: {error_msg}")
                    return False, error_msg

                if not output_file.exists():
                    error_msg = "Preview image not created"
                    logger.error(f"Output file not created: {output_file}")
                    return False, error_msg

                logger.info(f"PNG rendered successfully: {output_file.name}")
                return True, None

            finally:
                xvfb.terminate()
                xvfb.wait()

        except subprocess.TimeoutExpired:
            error_msg = f"Rendering timeout ({self.timeout}s exceeded)"
            logger.error(f"Rendering timeout for {scad_file.name}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Rendering error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def render_stl(self, scad_file: Path, output_file: Path) -> tuple[bool, str | None]:
        """Render STL file

        Args:
            scad_file: Path to .scad file
            output_file: Path to output STL file

        Returns:
            Tuple of (success, error_message)
        """
        try:
            cmd = [
                self.binary,
                "-o", str(output_file),
                str(scad_file)
            ]

            logger.info(f"Rendering STL: {scad_file.name}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "STL generation failed"
                logger.error(f"STL generation error: {error_msg}")
                return False, error_msg

            if not output_file.exists():
                error_msg = "STL file not created"
                logger.error(f"STL file not created: {output_file}")
                return False, error_msg

            logger.info(f"STL rendered successfully: {output_file.name}")
            return True, None

        except subprocess.TimeoutExpired:
            error_msg = f"STL rendering timeout ({self.timeout}s exceeded)"
            logger.error(f"STL rendering timeout for {scad_file.name}")
            return False, error_msg
        except Exception as e:
            error_msg = f"STL rendering error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
