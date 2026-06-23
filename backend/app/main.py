from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .core.scheduler import start_scheduler, stop_scheduler
from .api.routes import auth, chat, crisis, audio, emergency_contact, artwork, game_tracking, emergency_alert, users, feedback as feedback_routes
import logging

logger = logging.getLogger(__name__)

# Import all models to ensure they're registered with SQLAlchemy
from .models import user, chat as chat_model, crisis as crisis_model, feedback, emergency_contact as emergency_contact_model, artwork as artwork_model, game_session

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Mental Health Chatbot API with Emotion Analysis and Crisis Detection"
)


# Startup event: Start background scheduler
@app.on_event("startup")
async def startup_event():
    """Start background tasks when application starts."""
    try:
        start_scheduler()
    except ImportError:
        logger.warning("APScheduler not installed - auto-refresh disabled. Install with: pip install APScheduler")
    except Exception as e:
        logger.warning(f"Scheduler failed to start: {e}")


# Shutdown event: Stop background scheduler
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up when application shuts down."""
    try:
        stop_scheduler()
    except:
        pass

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(crisis.router, prefix="/api/crisis", tags=["Crisis"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])
app.include_router(emergency_contact.router, prefix="/api/emergency-contacts", tags=["Emergency Contacts"])
app.include_router(emergency_alert.router, prefix="/api/emergency-alert", tags=["Emergency Alerts"])
app.include_router(artwork.router, tags=["Artworks"])
app.include_router(game_tracking.router, prefix="/api/games", tags=["Game Tracking"])
app.include_router(feedback_routes.router, prefix="/api/feedback", tags=["Feedback"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
