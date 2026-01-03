"""Chat-based code modification endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.core.ai_generator import AIGenerator
from app.utils.security import SecurityValidator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI generator
ai_generator = AIGenerator()


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    current_code: str
    conversation_history: List[ChatMessage] = []
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    modified_code: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat_about_code(request: ChatRequest):
    """
    Chat with AI about the current code.
    Can ask questions, request modifications, or get explanations.
    """
    try:
        logger.info(f"Chat message: {request.message[:50]}...")

        # Build conversation context
        system_prompt = """You are an expert OpenSCAD assistant helping users modify and understand 3D models.

You can:
1. Explain what the current code does
2. Make modifications to the code based on user requests
3. Answer questions about OpenSCAD syntax and best practices
4. Suggest improvements

CRITICAL: You are a FORMATTING EXPERT. When modifying code, you MUST preserve the exact formatting style, indentation, comment alignment, and variable alignment of the original code. Treat formatting as sacred.

RESPONSE FORMAT:
You MUST determine if the user is asking for a code modification or just asking a question.

If MODIFYING CODE:
- Start with a brief explanation (1-2 sentences) of what you changed and why
- Then use this EXACT format for the code:

---MODIFIED-CODE-START---
```openscad
[complete modified code here]
```
---MODIFIED-CODE-END---

Example:
"I've doubled the size by changing each dimension from 10mm to 20mm.

---MODIFIED-CODE-START---
```openscad
cube([20,20,20], center=true);
```
---MODIFIED-CODE-END---"

If JUST ANSWERING (no code changes):
- Provide a helpful text response only
- Do NOT use the ---MODIFIED-CODE-START--- markers
- You can include code examples in regular markdown blocks for reference

MODIFICATION RULES:
1. When modifying code, output the ENTIRE modified code, not just the changes
2. PRESERVE the exact formatting style of the original code:
   - Keep comment alignment and spacing
   - Maintain variable assignment alignment (e.g., column-aligned = signs)
   - Preserve indentation patterns (spaces/tabs)
   - Keep comment style (inline //, block /* */, section headers)
   - Maintain blank line spacing between sections
3. Always use center=true for primitives (unless original doesn't)
4. Use $fn value from original code (or 100 if missing)
5. NEVER mix 2D primitives (circle, square) with 3D operations
6. Measurements in millimeters
7. When adding new variables, align them with existing variable declarations
8. Keep module definitions and function calls formatted consistently with the original

CURRENT CODE:
```openscad
{current_code}
```
"""

        # Build message history
        messages = [
            {"role": "system", "content": system_prompt.format(current_code=request.current_code)}
        ]

        # Add conversation history
        for msg in request.conversation_history[-6:]:  # Keep last 6 messages for context
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })

        # Call AI
        response = await ai_generator.client.chat.completions.create(
            model=request.model or "gpt-4-turbo-preview",
            messages=messages,
            temperature=request.temperature if request.temperature is not None else 0.4,
            max_tokens=request.max_tokens or 2000
        )

        assistant_response = response.choices[0].message.content

        # Check if response includes modified code
        modified_code = None
        response_text = assistant_response

        # Look for the modified code markers
        if "---MODIFIED-CODE-START---" in assistant_response and "---MODIFIED-CODE-END---" in assistant_response:
            # Split response into explanation and code
            parts = assistant_response.split("---MODIFIED-CODE-START---")
            response_text = parts[0].strip()

            # If explanation is empty, provide a default message
            if not response_text:
                response_text = "I've modified the code as requested."

            code_section = parts[1].split("---MODIFIED-CODE-END---")[0].strip()

            # Extract code from markdown block
            if "```openscad" in code_section:
                modified_code = code_section.split("```openscad")[1].split("```")[0].strip()
            elif "```" in code_section:
                modified_code = code_section.split("```")[1].split("```")[0].strip()
            else:
                # Try to extract code without markers
                modified_code = code_section.strip()

            # Validate modified code
            if modified_code:
                is_valid, errors = SecurityValidator.validate_scad_code(modified_code)
                if not is_valid:
                    logger.warning(f"Modified code failed validation: {errors}")
                    modified_code = None
                    response_text += "\n\n⚠️ Note: The code modification didn't pass validation. The original code remains unchanged."
                else:
                    logger.info(f"Code successfully modified via chat ({len(modified_code)} chars)")
                    # Add a note to the response that code was updated
                    response_text += "\n\n✓ Code updated in editor"

        return ChatResponse(
            response=response_text,
            modified_code=modified_code
        )

    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
