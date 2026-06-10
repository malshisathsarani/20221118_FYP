from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import cloudinary
import cloudinary.uploader
from ...core.config import settings
from ..dependencies import get_current_user_id

router = APIRouter()

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """
    Upload audio file to Cloudinary

    Accepts: .wav, .mp3, .m4a, .ogg
    Max size: 10MB
    Returns: Cloudinary URL for the audio file
    """

    # Validate file type
    allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/x-m4a", "audio/ogg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: WAV, MP3, M4A, OGG"
        )

    # Validate file size (10MB max)
    contents = await file.read()
    file_size = len(contents)
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size: 10MB"
        )

    # Reset file pointer
    await file.seek(0)

    try:
        # Upload to Cloudinary using unsigned preset (bypasses API restrictions)
        result = cloudinary.uploader.unsigned_upload(
            file.file,
            settings.CLOUDINARY_UPLOAD_PRESET,  # Use preset from config
            resource_type="video",  # 'video' type handles audio files
            folder=f"mental-health-chatbot/audio/user_{user_id}"
        )

        return {
            "audio_path": result['secure_url'],
            "audio_id": result['public_id'],
            "format": result['format'],
            "size": result['bytes'],
            "duration": result.get('duration'),
            "message": "Audio uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.delete("/delete/{audio_id:path}")
async def delete_audio(
    audio_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete audio file from Cloudinary

    audio_id: The public_id returned from upload
    """

    # Verify user owns this file
    if f"user_{user_id}" not in audio_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this file"
        )

    try:
        result = cloudinary.uploader.destroy(
            audio_id,
            resource_type="video"
        )

        if result['result'] == 'ok':
            return {"message": "Audio deleted successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail="Audio not found"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )
