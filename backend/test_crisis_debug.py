"""
Debug Crisis Detection
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.crisis_detection.model import get_crisis_detection_model

def test_crisis_model():
    print("="*70)
    print("Testing Crisis Detection Model Directly")
    print("="*70)

    model = get_crisis_detection_model()

    test_messages = [
        "I'm so happy today!",
        "I feel sad and lonely",
        "I feel hopeless and worthless. I can't go on anymore.",
        "I want to kill myself",
        "Everything is great!"
    ]

    for msg in test_messages:
        print(f"\nMessage: '{msg}'")
        result = model.predict_crisis_from_text(msg)
        print(f"  Is Crisis: {result['is_crisis']}")
        print(f"  Confidence: {result['confidence']:.2%}")

        # Also test predict_risk
        text_emotion = {
            'original_text': msg,
            'primary_emotion': 'sadness',
            'primary_score': 0.9
        }
        risk_result = model.predict_risk(text_emotion)
        print(f"  Risk Level: {risk_result['risk_level']}")
        print(f"  Risk Score: {risk_result['risk_score']:.2%}")
        print(f"  Risk Factors: {risk_result['risk_factors']}")

if __name__ == "__main__":
    test_crisis_model()
