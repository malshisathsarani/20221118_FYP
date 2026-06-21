"""
Speech Emotion Recognition Model
Uses CUSTOM TRAINED Deep Neural Network for audio emotion classification
Trained on RAVDESS, CREMA-D, TESS, and SAVEE datasets (42,888 samples)
"""
import os
import numpy as np
import librosa
import tensorflow as tf
import pickle
from typing import List, Dict, Optional
import logging
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class SpeechEmotionModel:
    """
    Custom trained Deep Neural Network for speech emotion recognition

    Model Details:
    - Architecture: Deep Neural Network (4 dense layers)
    - Training Samples: 42,888 audio files
    - Datasets: RAVDESS, CREMA-D, TESS, SAVEE
    - Accuracy: 75.71%
    - Emotions: angry, disgust, fear, happy, neutral, ps, sad, surprised
    """

    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize the custom trained speech emotion classifier

        Args:
            model_dir: Directory containing trained model files
        """
        try:
            # Default to trained_models directory
            if model_dir is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                model_dir = os.path.join(base_dir, "speech_emotion")

            logger.info(f"Loading custom trained speech emotion model from: {model_dir}")

            # Load trained model
            model_path = os.path.join(model_dir, "speech_emotion_model.h5")
            self.model = tf.keras.models.load_model(model_path)
            logger.info("✓ Model loaded successfully")

            # Load label encoder
            label_encoder_path = os.path.join(model_dir, "label_encoder.pkl")
            with open(label_encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            logger.info(f"✓ Label encoder loaded - Emotions: {self.label_encoder.classes_.tolist()}")

            # Load normalization parameters
            self.mean = np.load(os.path.join(model_dir, "feature_mean.npy"))
            self.std = np.load(os.path.join(model_dir, "feature_std.npy"))
            logger.info("✓ Normalization parameters loaded")

            logger.info("Custom trained speech emotion model loaded successfully!")

        except Exception as e:
            logger.error(f"Failed to load custom trained speech emotion model: {str(e)}")
            logger.warning("Speech emotion model will not be available. Install TensorFlow to enable.")
            self.model = None
            self.label_encoder = None
            self.mean = None
            self.std = None

    def extract_features(self, audio_path: str, duration: float = 3.0, sr: int = 22050) -> Optional[np.ndarray]:
        """
        Extract audio features matching the training configuration

        Features (380-dim total):
        - MFCC: 40 coefficients (mean + std = 80)
        - Mel-Spectrogram: 128 bands (mean + std = 256)
        - Chroma: 12 features (mean + std = 24)
        - Spectral Contrast: 7 features (mean + std = 14)
        - Zero Crossing Rate: 1 feature (mean + std = 2)
        - Spectral Rolloff: 1 feature (mean + std = 2)
        - Spectral Centroid: 1 feature (mean + std = 2)

        Args:
            audio_path: Path to audio file
            duration: Audio duration in seconds
            sr: Sample rate

        Returns:
            Feature vector (380-dim) or None if error
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, duration=duration, sr=sr)

            # Pad or trim to exact duration
            target_length = int(duration * sr)
            if len(y) < target_length:
                y = np.pad(y, (0, target_length - len(y)), mode='constant')
            else:
                y = y[:target_length]

            # Helper function to get mean + std
            def stats(feat):
                return np.concatenate([np.mean(feat.T, axis=0), np.std(feat.T, axis=0)])

            # Extract features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
            mfcc_feat = stats(mfcc)

            mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            mel_feat = stats(librosa.power_to_db(mel))

            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_feat = stats(chroma)

            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            contrast_feat = stats(contrast)

            zcr = librosa.feature.zero_crossing_rate(y)
            zcr_feat = stats(zcr)

            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            rolloff_feat = stats(rolloff)

            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            centroid_feat = stats(centroid)

            # Combine all features
            features = np.hstack([
                mfcc_feat, mel_feat, chroma_feat,
                contrast_feat, zcr_feat, rolloff_feat, centroid_feat
            ])

            return features

        except Exception as e:
            logger.error(f"Error extracting features from {audio_path}: {str(e)}")
            return None

    def predict(self, audio_path: str) -> List[Dict[str, float]]:
        """
        Analyze emotions in audio file using custom trained model

        Args:
            audio_path: Path to audio file (wav, mp3, etc.)

        Returns:
            List of dicts with 'label' and 'score' for each emotion, sorted by score descending
            Example: [{'label': 'happy', 'score': 0.85}, {'label': 'neutral', 'score': 0.10}, ...]
        """
        if not audio_path:
            logger.warning("No audio path provided")
            return []

        # Check if model is loaded
        if self.model is None:
            logger.warning("Speech emotion model not available - TensorFlow not installed")
            return []

        try:
            # Extract features
            features = self.extract_features(audio_path)
            if features is None:
                logger.error("Failed to extract features")
                return []

            # Normalize features
            features = (features - self.mean) / (self.std + 1e-8)
            features = features.reshape(1, -1)

            # Predict
            prediction = self.model.predict(features, verbose=0)

            # Convert to list of dicts format
            results = []
            for i, emotion in enumerate(self.label_encoder.classes_):
                results.append({
                    'label': emotion,
                    'score': float(prediction[0][i])
                })

            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)

            logger.info(f"Predicted emotion: {results[0]['label']} ({results[0]['score']*100:.2f}%)")

            return results

        except Exception as e:
            logger.error(f"Error analyzing speech emotion: {str(e)}")
            return []


# Singleton instance
_model_instance = None


def get_speech_emotion_model() -> SpeechEmotionModel:
    """
    Get or create the singleton speech emotion model instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = SpeechEmotionModel()
    return _model_instance
