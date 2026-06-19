class ChatMessage {
  final int id;
  final String sessionId;
  final String message;
  final String response;
  final EmotionAnalysis? emotionAnalysis;
  final String? audioEmotion;
  final String? audioUrl;
  final CrisisDetection? crisisDetection;
  final DateTime createdAt;

  ChatMessage({
    required this.id,
    required this.sessionId,
    required this.message,
    required this.response,
    this.emotionAnalysis,
    this.audioEmotion,
    this.audioUrl,
    this.crisisDetection,
    required this.createdAt,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      sessionId: json['session_id'],
      message: json['message'],
      response: json['response'],
      emotionAnalysis: json['emotion_analysis'] != null
          ? EmotionAnalysis.fromJson(json['emotion_analysis'])
          : null,
      audioEmotion: json['audio_emotion'],
      audioUrl: json['audio_url'] ?? json['audio_data'],
      crisisDetection: json['crisis_detection'] != null
          ? CrisisDetection.fromJson(json['crisis_detection'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class EmotionAnalysis {
  final String emotion;
  final double confidence;
  final Map<String, double> allScores;

  EmotionAnalysis({
    required this.emotion,
    required this.confidence,
    required this.allScores,
  });

  factory EmotionAnalysis.fromJson(Map<String, dynamic> json) {
    return EmotionAnalysis(
      emotion: json['emotion'],
      confidence: (json['confidence'] as num).toDouble(),
      allScores: Map<String, double>.from(
        json['all_scores'].map((key, value) => MapEntry(key, (value as num).toDouble())),
      ),
    );
  }
}

class CrisisDetection {
  final bool isCrisis;
  final String? severity;
  final double crisisScore;
  final List<String>? indicators;

  CrisisDetection({
    required this.isCrisis,
    this.severity,
    required this.crisisScore,
    this.indicators,
  });

  factory CrisisDetection.fromJson(Map<String, dynamic> json) {
    return CrisisDetection(
      isCrisis: json['is_crisis'],
      severity: json['severity'],
      crisisScore: (json['crisis_score'] as num).toDouble(),
      indicators: json['indicators'] != null
          ? List<String>.from(json['indicators'])
          : null,
    );
  }
}
