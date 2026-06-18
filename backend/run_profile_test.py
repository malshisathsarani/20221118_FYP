"""
Minimal server to test profile endpoints without heavy ML dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.routes import auth, profile

# Import models
from app.models import user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mental Health Chatbot API - Profile Test",
    version="1.0.0",
    description="Lightweight server for testing profile endpoints"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include only auth and profile routers (no ML dependencies)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "app": "Mental Health Chatbot API - Profile Test",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "note": "This is a lightweight server for testing profile endpoints only"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
