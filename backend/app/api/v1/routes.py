"""API v1 routes aggregator"""

from fastapi import APIRouter
from app.api.v1 import generate, render, export_routes, chat

router = APIRouter()

# Include sub-routers
router.include_router(generate.router, prefix="/generate", tags=["generate"])
router.include_router(render.router, prefix="/render", tags=["render"])
router.include_router(export_routes.router, prefix="/export", tags=["export"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
