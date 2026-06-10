"""
Test script for ML models
Run with: python test_ml.py
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.text_emotion.inference import analyze_text_emotion


def test_text_emotion():
    """Test text emotion analysis"""
    print("=" * 60)
    print("Testing Text Emotion Analysis")
    print("=" * 60)

    test_cases = [
        "I feel so happy and excited today!",
        "I'm really sad and don't know what to do.",
        "This makes me so angry!",
        "I'm scared and anxious about everything.",
        "I love spending time with my family.",
        "Wow, that's surprising!",
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{text}\"")
        print("-" * 60)

        try:
            result = analyze_text_emotion(text)

            print(f"Primary Emotion: {result['primary_emotion']} "
                  f"(score: {result['primary_score']})")
            print(f"Sentiment: {result['sentiment']}")
            print("\nAll emotions:")

            for emotion in result['all_emotions'][:3]:  # Show top 3
                print(f"  - {emotion['emotion']}: {emotion['score']:.4f}")

        except Exception as e:
            print(f"ERROR: {str(e)}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\nMental Health Chatbot - ML Model Test\n")

    print("This will download the pre-trained model on first run.")
    print("It may take a few minutes...\n")

    input("Press Enter to start testing...")

    test_text_emotion()
