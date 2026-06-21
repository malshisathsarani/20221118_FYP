
# Speech Emotion Recognition Model

## Model Information
- **Architecture**: Deep Neural Network
- **Input**: Audio features (380-dimensional vector)
- **Output**: 8 emotion classes
- **Accuracy**: 75.71%
- **F1-Score**: 75.55%

## Emotion Classes
angry, disgust, fear, happy, neutral, ps, sad, surprised

## Datasets Used
- RAVDESS (Ryerson Audio-Visual Database of Emotional Speech and Song)
- CREMA-D (Crowd-sourced Emotional Multimodal Actors Dataset)
- TESS (Toronto Emotional Speech Set)
- SAVEE (Surrey Audio-Visual Expressed Emotion)

Total training samples: 42888

## Features Extracted
- MFCC (40 coefficients)
- Mel-Spectrogram (128 bands)
- Chroma (12 features)
- Spectral Contrast (7 features)
- Zero Crossing Rate (1 feature)
- Spectral Rolloff (1 feature)
- Spectral Centroid (1 feature)

Total: 380 features (mean + std of each feature group)

## Usage

```python
import numpy as np
import librosa
import tensorflow as tf
import pickle

# Load model
model = tf.keras.models.load_model('speech_emotion_model.h5')

# Load label encoder and normalization params
with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

mean = np.load('feature_mean.npy')
std = np.load('feature_std.npy')

# Extract features from audio (use the extract_features function)
features = extract_features('path/to/audio.wav')

# Normalize
features = (features - mean) / (std + 1e-8)

# Predict
prediction = model.predict(features.reshape(1, -1))
emotion = label_encoder.classes_[np.argmax(prediction)]
confidence = prediction[0][np.argmax(prediction)]

print(f"Emotion: {emotion}, Confidence: {confidence*100:.2f}%")
```

## Files Included
- `speech_emotion_model.h5` - Trained model (Keras format)
- `speech_emotion_model/` - TensorFlow SavedModel format
- `label_encoder.pkl` - Label encoder for emotion classes
- `feature_mean.npy` - Feature normalization mean
- `feature_std.npy` - Feature normalization std
- `training_metrics.json` - Training metrics and configuration
- `confusion_matrix.png` - Confusion matrix visualization
- `training_history.png` - Training history plots

## Training Details
- Epochs: 100
- Batch Size: 32
- Optimizer: Adam
- Learning Rate: 0.001

## Performance Metrics
- Accuracy: 75.71%
- Precision: 82.23%
- Recall: 68.64%
- F1-Score: 75.55%

## Citation
If you use this model, please cite the datasets:
- RAVDESS: Livingstone SR, Russo FA (2018) The Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS)
- CREMA-D: Cao H, Cooper DG, Keutmann MK, Gur RC, Nenkova A, Verma R (2014)
- TESS: Dupuis K, Pichora-Fuller MK (2010)
- SAVEE: Haq S, Jackson PJB (2011)
