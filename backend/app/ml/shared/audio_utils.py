"""
Audio Utilities for downloading and processing audio files
"""
import os
import tempfile
import requests
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def download_audio_from_url(audio_url: str) -> Optional[str]:
    """
    Download audio file from URL (Cloudinary) to temporary directory

    Args:
        audio_url: URL of the audio file (from Cloudinary)

    Returns:
        Path to downloaded audio file, or None if download failed
    """
    try:
        logger.info(f"Downloading audio from: {audio_url}")

        # Create temp directory if it doesn't exist
        temp_dir = Path(tempfile.gettempdir()) / "mental_health_audio"
        temp_dir.mkdir(exist_ok=True)

        # Download audio file
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()

        # Determine file extension from URL or content type
        file_extension = _get_audio_extension(audio_url, response.headers.get('content-type'))

        # Save to temporary file
        temp_file_path = temp_dir / f"audio_{os.getpid()}_{hash(audio_url)}{file_extension}"

        with open(temp_file_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Audio downloaded successfully to: {temp_file_path}")
        return str(temp_file_path)

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download audio from {audio_url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        return None


def _get_audio_extension(url: str, content_type: Optional[str]) -> str:
    """
    Determine audio file extension from URL or content type

    Args:
        url: Audio file URL
        content_type: Content-Type header value

    Returns:
        File extension with dot (e.g., '.wav', '.mp3')
    """
    # Try to get extension from URL
    if '.' in url.split('/')[-1]:
        parts = url.split('.')
        ext = parts[-1].lower().split('?')[0]  # Remove query params
        if ext in ['wav', 'mp3', 'm4a', 'ogg', 'flac']:
            return f'.{ext}'

    # Fall back to content type
    if content_type:
        content_type_map = {
            'audio/wav': '.wav',
            'audio/wave': '.wav',
            'audio/x-wav': '.wav',
            'audio/mpeg': '.mp3',
            'audio/mp3': '.mp3',
            'audio/x-m4a': '.m4a',
            'audio/ogg': '.ogg',
            'audio/flac': '.flac',
        }
        return content_type_map.get(content_type.lower(), '.wav')

    # Default to WAV
    return '.wav'


def cleanup_temp_audio(file_path: str) -> None:
    """
    Delete temporary audio file

    Args:
        file_path: Path to temporary audio file
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary audio file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup audio file {file_path}: {e}")
