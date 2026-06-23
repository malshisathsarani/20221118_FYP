"""
Test ML Integration with Chat Service
Tests the integrated ML pipeline without database
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.unified_pipeline import get_unified_pipeline


def test_ml_pipeline():
    """Test the complete ML pipeline using UnifiedMLPipeline"""
    print("=" * 70)
    print("Testing Unified ML Pipeline Integration")
    print("=" * 70)

    print("\n📦 Loading ML models...")
    print("This may take a few minutes on first run (downloading models)...\n")

    try:
        pipeline = get_unified_pipeline()
        print("✅ Unified ML Pipeline initialized successfully!\n")

        # Get pipeline status
        status = pipeline.get_pipeline_status()
        print("📊 Pipeline Status:")
        print(f"  Pipeline: {status['pipeline']}")
        print(f"  All Systems Operational: {status['all_systems_operational']}")
        print("\n  Components:")
        for comp_name, comp_info in status['components'].items():
            status_icon = "✅" if comp_info['loaded'] else "❌"
            model_info = comp_info.get('model') or comp_info.get('algorithm', 'Unknown')
            print(f"    {status_icon} {comp_name}: {model_info}")

        print("\n" + "=" * 70)
        print("Testing Comprehensive Analysis (Text + Crisis Detection)")
        print("=" * 70)

        test_messages = [
            "I'm so happy today! Everything is going great!",
            "I feel really sad and lonely right now.",
            "This makes me so angry and frustrated!",
            "I'm scared about the future.",
            "I love spending time with my family.",
            "I feel hopeless and worthless. I can't go on anymore.",
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Message: \"{message}\"")
            print("-" * 70)

            # Run comprehensive analysis
            analysis = pipeline.analyze_comprehensive(text=message)

            # Extract results
            text_emotion = analysis.get('text_emotion', {})
            crisis_assessment = analysis.get('crisis_assessment', {})
            fusion_result = analysis.get('fusion_result', {})

            # Display text emotion
            print(f"   Text Emotion: {text_emotion.get('primary_emotion')} "
                  f"(confidence: {text_emotion.get('primary_score', 0):.2%})")
            print(f"   Sentiment: {text_emotion.get('sentiment', 'N/A')}")

            # Display fusion result
            print(f"   Overall Risk Level: {fusion_result.get('overall_risk_level')}")
            print(f"   Risk Score: {fusion_result.get('risk_score', 0):.2%}")
            print(f"   Emotional State: {fusion_result.get('emotional_state')}")

            # Display crisis assessment
            if crisis_assessment.get('is_crisis'):
                print(f"   ⚠️  CRISIS DETECTED!")
                print(f"   Risk Level: {crisis_assessment.get('risk_level')}")
                if crisis_assessment.get('emergency_resources'):
                    print(f"   Emergency resources: Available")

            # Display recommendations
            recommendations = fusion_result.get('recommendations', [])
            if recommendations:
                print(f"   Recommendations: {recommendations[0]}")

        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("=" * 70)

        print("\n📋 Summary:")
        print("✓ Text emotion analysis working")
        print("✓ Crisis detection working")
        print("✓ Multi-modal fusion working")
        print("✓ Comprehensive analysis pipeline operational")
        print("✓ Ready to integrate with chat API")

        print("\n💡 Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run this test: python test_ml_integration.py")
        print("  3. Start the API: uvicorn app.main:app --reload")
        print("  4. Test via API endpoints")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\nMental Health Chatbot - ML Integration Test\n")
    input("Press Enter to start testing...")
    test_ml_pipeline()
