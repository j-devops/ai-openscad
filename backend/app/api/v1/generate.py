"""Code generation endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.core.ai_generator import AIGenerator
from app.utils.security import SecurityValidator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI generator
ai_generator = AIGenerator()


class GenerateRequest(BaseModel):
    """Code generation request model"""
    prompt: str
    style: str = "functional"
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


class GenerateResponse(BaseModel):
    """Code generation response model"""
    code: str
    generated_at: str


@router.post("/", response_model=GenerateResponse)
async def generate_code(request: GenerateRequest):
    """Generate OpenSCAD code from natural language prompt"""
    try:
        logger.info(f"Generating code for prompt: {request.prompt[:50]}...")

        # Generate code using AI
        code = await ai_generator.generate_scad_code(
            request.prompt,
            request.style,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Validate generated code
        is_valid, errors = SecurityValidator.validate_scad_code(code)
        if not is_valid:
            logger.warning(f"Generated code failed validation: {errors}")
            raise HTTPException(
                status_code=400,
                detail=f"Generated code failed security validation: {', '.join(errors)}"
            )

        from datetime import datetime
        return GenerateResponse(
            code=code,
            generated_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")
