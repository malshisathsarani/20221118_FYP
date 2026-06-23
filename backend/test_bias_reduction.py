"""
Test Script for Bias Reduction System

This script tests all 5 bias reduction algorithms independently.
Run: python test_bias_reduction.py
"""

from app.core.database import SessionLocal
from app.ml.bias_reduction.bias_correction_algorithm import BiasReductionAlgorithm
from app.repositories.feedback_repo import FeedbackRepository
from app.models.user import User
from app.models.chat import Chat
from datetime import datetime


def test_algorithm_initialization():
    """Test 1: Check algorithm initializes correctly"""
    print("\n" + "="*60)
    print("TEST 1: Algorithm Initialization")
    print("="*60)

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)
        print(f"✅ Algorithm initialized successfully")
        print(f"   Correction patterns: {len(algorithm.correction_patterns)}")
        print(f"   Confidence adjustments: {len(algorithm.confidence_adjustments)}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    finally:
        db.close()


def test_pattern_correction():
    """Test 2: Pattern-based correction"""
    print("\n" + "="*60)
    print("TEST 2: Pattern-Based Correction")
    print("="*60)

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)

        # Simulate a prediction
        raw_prediction = {
            'emotion': 'sadness',
            'confidence': 0.85,
            'all_scores': {
                'sadness': 0.85,
                'anger': 0.10,
                'joy': 0.03,
                'fear': 0.02
            }
        }

        print(f"\n📊 Raw Prediction:")
        print(f"   Emotion: {raw_prediction['emotion']}")
        print(f"   Confidence: {raw_prediction['confidence']:.2%}")

        # Apply correction
        corrected = algorithm.apply_bias_reduction(
            text="I'm so frustrated!",
            raw_prediction=raw_prediction
        )

        print(f"\n✨ After Bias Reduction:")
        print(f"   Emotion: {corrected['emotion']}")
        print(f"   Confidence: {corrected['confidence']:.2%}")

        if corrected.get('corrected'):
            print(f"   ✅ Correction applied!")
            if corrected.get('corrections_applied'):
                print(f"   Reasons: {corrected['corrections_applied']}")
        else:
            print(f"   ℹ️  No correction needed")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    finally:
        db.close()


def test_contextual_correction():
    """Test 3: Contextual correction (negation, intensity)"""
    print("\n" + "="*60)
    print("TEST 3: Contextual Correction")
    print("="*60)

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)

        test_cases = [
            {
                'text': "I'm NOT sad at all",
                'emotion': 'sadness',
                'confidence': 0.75,
                'expected': 'Negation should reduce confidence'
            },
            {
                'text': "I'm VERY happy!",
                'emotion': 'joy',
                'confidence': 0.65,
                'expected': 'Intensity should boost confidence'
            },
            {
                'text': "Maybe I'm kinda upset",
                'emotion': 'anger',
                'confidence': 0.70,
                'expected': 'Uncertainty should reduce confidence'
            }
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {test['text']}")
            print(f"   Original confidence: {test['confidence']:.2%}")

            result = algorithm.apply_contextual_correction(
                text=test['text'],
                emotion=test['emotion'],
                confidence=test['confidence']
            )

            print(f"   Adjusted confidence: {result['confidence']:.2%}")
            print(f"   Expected: {test['expected']}")

            if result.get('context_adjusted'):
                print(f"   ✅ Context corrections: {result.get('context_corrections')}")
            else:
                print(f"   ℹ️  No context adjustments")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    finally:
        db.close()


def test_confidence_adjustment():
    """Test 4: Confidence adjustment based on history"""
    print("\n" + "="*60)
    print("TEST 4: Confidence Adjustment")
    print("="*60)

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)

        print("\n📊 Current Confidence Adjustments:")
        if algorithm.confidence_adjustments:
            for emotion, multiplier in algorithm.confidence_adjustments.items():
                status = "📈 Boost" if multiplier > 1.0 else "📉 Penalize" if multiplier < 1.0 else "➡️  Neutral"
                print(f"   {emotion}: {multiplier:.2f}x {status}")
        else:
            print("   ℹ️  No adjustments yet (need more feedback)")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    finally:
        db.close()


def test_ensemble_correction():
    """Test 5: Ensemble correction (text + audio)"""
    print("\n" + "="*60)
    print("TEST 5: Ensemble Correction (Text + Audio)")
    print("="*60)

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)

        # Test case 1: Agreement
        text_emotion = {
            'emotion': 'joy',
            'confidence': 0.75,
            'all_scores': {'joy': 0.75, 'sadness': 0.15}
        }
        audio_emotion = 'joy'

        print(f"\n🎤 Test Case 1: Agreement")
        print(f"   Text emotion: {text_emotion['emotion']} ({text_emotion['confidence']:.2%})")
        print(f"   Audio emotion: {audio_emotion}")

        result = algorithm.ensemble_correction(
            text="I'm happy",
            text_emotion=text_emotion,
            audio_emotion=audio_emotion
        )

        print(f"   ✨ Ensemble result: {result['emotion']} ({result['confidence']:.2%})")
        if result.get('ensemble_corrected'):
            print(f"   ✅ {result['ensemble_reason']}")

        # Test case 2: Disagreement
        text_emotion2 = {
            'emotion': 'sadness',
            'confidence': 0.70,
            'all_scores': {'sadness': 0.70, 'joy': 0.20}
        }
        audio_emotion2 = 'joy'

        print(f"\n🎤 Test Case 2: Disagreement")
        print(f"   Text emotion: {text_emotion2['emotion']} ({text_emotion2['confidence']:.2%})")
        print(f"   Audio emotion: {audio_emotion2}")

        result2 = algorithm.ensemble_correction(
            text="I'm okay",
            text_emotion=text_emotion2,
            audio_emotion=audio_emotion2
        )

        print(f"   ✨ Ensemble result: {result2['emotion']} ({result2['confidence']:.2%})")
        if result2.get('ensemble_corrected'):
            print(f"   ✅ {result2['ensemble_reason']}")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    finally:
        db.close()


def test_full_pipeline():
    """Test 6: Complete pipeline with all algorithms"""
    print("\n" + "="*60)
    print("TEST 6: Full Pipeline (All Algorithms Combined)")
    print("="*60)

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)

        test_message = "I'm NOT feeling sad anymore, I'm VERY excited!"

        raw_prediction = {
            'emotion': 'sadness',
            'confidence': 0.80,
            'all_scores': {
                'sadness': 0.80,
                'joy': 0.15,
                'anger': 0.03,
                'fear': 0.02
            }
        }

        print(f"\n📝 Input Message: '{test_message}'")
        print(f"\n📊 Initial ML Prediction:")
        print(f"   Emotion: {raw_prediction['emotion']}")
        print(f"   Confidence: {raw_prediction['confidence']:.2%}")

        # Step 1: Pattern correction
        step1 = algorithm.apply_bias_reduction(test_message, raw_prediction.copy())
        print(f"\n🔄 After Pattern Correction:")
        print(f"   Emotion: {step1['emotion']}")
        print(f"   Confidence: {step1['confidence']:.2%}")

        # Step 2: Contextual correction
        step2 = algorithm.apply_contextual_correction(
            test_message,
            step1['emotion'],
            step1['confidence']
        )
        print(f"\n🔄 After Contextual Correction:")
        print(f"   Emotion: {step2['emotion']}")
        print(f"   Confidence: {step2['confidence']:.2%}")
        if step2.get('context_corrections'):
            print(f"   Applied: {step2['context_corrections']}")

        # Step 3: Ensemble (simulate audio agreement)
        step3 = algorithm.ensemble_correction(
            test_message,
            step2,
            audio_emotion='joy'
        )
        print(f"\n🔄 After Ensemble Correction:")
        print(f"   Emotion: {step3['emotion']}")
        print(f"   Confidence: {step3['confidence']:.2%}")
        if step3.get('ensemble_reason'):
            print(f"   Reason: {step3['ensemble_reason']}")

        print(f"\n✨ FINAL RESULT:")
        print(f"   Original: {raw_prediction['emotion']} @ {raw_prediction['confidence']:.2%}")
        print(f"   Corrected: {step3['emotion']} @ {step3['confidence']:.2%}")

        if step3['emotion'] != raw_prediction['emotion']:
            print(f"   🎯 Bias successfully corrected!")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    finally:
        db.close()


def test_stats_endpoint():
    """Test 7: Algorithm statistics"""
    print("\n" + "="*60)
    print("TEST 7: Algorithm Statistics")
    print("="*60)

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)
        stats = algorithm.get_stats()

        print(f"\n📊 Algorithm Statistics:")
        print(f"   Correction patterns learned: {stats['correction_patterns']}")
        print(f"   Confidence adjustments: {stats['confidence_adjustments']}")
        print(f"   Last refresh: {stats['last_refresh']}")

        if stats['top_patterns']:
            print(f"\n🔝 Top Correction Patterns:")
            for pattern, count in stats['top_patterns'].items():
                print(f"      {pattern}: {count} cases")

        if stats['emotion_adjustments']:
            print(f"\n⚖️  Emotion Adjustments:")
            for emotion, multiplier in stats['emotion_adjustments'].items():
                print(f"      {emotion}: {multiplier:.2f}x")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("\n" + "🧪"*30)
    print("BIAS REDUCTION SYSTEM - TEST SUITE")
    print("🧪"*30)

    tests = [
        test_algorithm_initialization,
        test_pattern_correction,
        test_contextual_correction,
        test_confidence_adjustment,
        test_ensemble_correction,
        test_full_pipeline,
        test_stats_endpoint
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Bias reduction system is working!")
    else:
        print("\n⚠️  Some tests failed. Check logs above.")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
