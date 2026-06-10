from fastapi import APIRouter
from .routes import auth, chat, crisis

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(crisis.router, prefix="/crisis", tags=["Crisis"])

__all__ = ["api_router"]
