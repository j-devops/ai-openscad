"""Security validation utilities"""

import re
from typing import Tuple, List


class SecurityValidator:
    """Validate and sanitize user inputs"""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove dangerous characters from filenames

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        return re.sub(r'[^a-zA-Z0-9_\-\.]', '', filename)

    @staticmethod
    def validate_scad_code(code: str) -> Tuple[bool, List[str]]:
        """Basic security validation of OpenSCAD code

        Args:
            code: OpenSCAD code to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check for suspicious patterns
        dangerous_patterns = [
            (r'import\s*<.*\.\./.*>', 'Path traversal in import statement'),
            (r'use\s*<.*\.\./.*>', 'Path traversal in use statement'),
        ]

        for pattern, error_msg in dangerous_patterns:
            if re.search(pattern, code):
                errors.append(error_msg)

        # Size limit
        from app.config import settings
        if len(code) > settings.MAX_CODE_SIZE:
            errors.append(f"Code exceeds size limit ({settings.MAX_CODE_SIZE} bytes)")

        # Must not be empty
        if not code.strip():
            errors.append("Code cannot be empty")

        return len(errors) == 0, errors

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate OpenAI API key format

        Args:
            api_key: API key to validate

        Returns:
            True if valid format
        """
        # OpenAI keys start with sk- and have specific length
        return bool(re.match(r'^sk-[a-zA-Z0-9]{32,}$', api_key))
