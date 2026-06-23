
import numpy as np
import librosa
import tensorflow as tf
import pickle
import warnings
warnings.filterwarnings('ignore')

class SpeechEmotionRecognizer:
    def __init__(self, model_path, label_encoder_path, mean_path, std_path):
        """Initialize Speech Emotion Recognizer"""
        self.model = tf.keras.models.load_model(model_path)

        with open(label_encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)

        self.mean = np.load(mean_path)
        self.std = np.load(std_path)

    def extract_features(self, audio_path, duration=3.0, sr=22050):
        """Extract audio features (mean + std, 380-dim to match training)"""
        try:
            y, sr = librosa.load(audio_path, duration=duration, sr=sr)

            target_length = int(duration * sr)
            if len(y) < target_length:
                y = np.pad(y, (0, target_length - len(y)), mode='constant')
            else:
                y = y[:target_length]

            def stats(feat):
                return np.concatenate([np.mean(feat.T, axis=0), np.std(feat.T, axis=0)])

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

            features = np.hstack([
                mfcc_feat, mel_feat, chroma_feat,
                contrast_feat, zcr_feat, rolloff_feat, centroid_feat
            ])

            return features
        except Exception as e:
            return None

    def predict(self, audio_path):
        """Predict emotion from audio file"""
        features = self.extract_features(audio_path)
        if features is None:
            return None

        features = (features - self.mean) / (self.std + 1e-8)
        features = features.reshape(1, -1)

        prediction = self.model.predict(features, verbose=0)
        emotion_idx = np.argmax(prediction)
        emotion = self.label_encoder.classes_[emotion_idx]
        confidence = prediction[0][emotion_idx]

        all_probs = {
            self.label_encoder.classes_[i]: float(prediction[0][i])
            for i in range(len(self.label_encoder.classes_))
        }

        return {
            'emotion': emotion,
            'confidence': float(confidence),
            'all_probabilities': all_probs
        }

# Example usage
if __name__ == "__main__":
    recognizer = SpeechEmotionRecognizer(
        model_path='speech_emotion_model.h5',
        label_encoder_path='label_encoder.pkl',
        mean_path='feature_mean.npy',
        std_path='feature_std.npy'
    )

    result = recognizer.predict('path/to/audio.wav')
    if result:
        pass  # Example usage - see documentation for details
