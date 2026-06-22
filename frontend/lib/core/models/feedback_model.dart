enum FeedbackType {
  emotionAccuracy('emotion_accuracy'),
  responseQuality('response_quality'),
  crisisDetection('crisis_detection');

  final String value;
  const FeedbackType(this.value);

  static FeedbackType fromString(String value) {
    return FeedbackType.values.firstWhere(
      (type) => type.value == value,
      orElse: () => FeedbackType.responseQuality,
    );
  }
}

class FeedbackResponse {
  final int id;
  final int userId;
  final int chatId;
  final int rating;
  final String feedbackType;
  final String? comment;
  final bool isProcessed;
  final DateTime createdAt;

  FeedbackResponse({
    required this.id,
    required this.userId,
    required this.chatId,
    required this.rating,
    required this.feedbackType,
    this.comment,
    required this.isProcessed,
    required this.createdAt,
  });

  factory FeedbackResponse.fromJson(Map<String, dynamic> json) {
    return FeedbackResponse(
      id: json['id'],
      userId: json['user_id'],
      chatId: json['chat_id'],
      rating: json['rating'],
      feedbackType: json['feedback_type'],
      comment: json['comment'],
      isProcessed: json['is_processed'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'chat_id': chatId,
      'rating': rating,
      'feedback_type': feedbackType,
      'comment': comment,
      'is_processed': isProcessed,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class BiasPattern {
  final String patternType;
  final int occurrenceCount;
  final String severity;
  final List<String> exampleComments;
  final String recommendation;

  BiasPattern({
    required this.patternType,
    required this.occurrenceCount,
    required this.severity,
    required this.exampleComments,
    required this.recommendation,
  });

  factory BiasPattern.fromJson(Map<String, dynamic> json) {
    return BiasPattern(
      patternType: json['pattern_type'],
      occurrenceCount: json['occurrence_count'],
      severity: json['severity'],
      exampleComments: List<String>.from(json['example_comments'] ?? []),
      recommendation: json['recommendation'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'pattern_type': patternType,
      'occurrence_count': occurrenceCount,
      'severity': severity,
      'example_comments': exampleComments,
      'recommendation': recommendation,
    };
  }
}

class BiasAnalysisResult {
  final int totalFeedbacks;
  final int negativeCount;
  final double negativePercentage;
  final double emotionAccuracyScore;
  final double responseQualityScore;
  final double crisisDetectionScore;
  final List<BiasPattern> biasPatterns;
  final List<String> recommendations;
  final DateTime analysisDate;
  final bool needsModelReview;

  BiasAnalysisResult({
    required this.totalFeedbacks,
    required this.negativeCount,
    required this.negativePercentage,
    required this.emotionAccuracyScore,
    required this.responseQualityScore,
    required this.crisisDetectionScore,
    required this.biasPatterns,
    required this.recommendations,
    required this.analysisDate,
    required this.needsModelReview,
  });

  factory BiasAnalysisResult.fromJson(Map<String, dynamic> json) {
    return BiasAnalysisResult(
      totalFeedbacks: json['total_feedbacks'],
      negativeCount: json['negative_count'],
      negativePercentage: (json['negative_percentage'] as num).toDouble(),
      emotionAccuracyScore: (json['emotion_accuracy_score'] as num).toDouble(),
      responseQualityScore: (json['response_quality_score'] as num).toDouble(),
      crisisDetectionScore: (json['crisis_detection_score'] as num).toDouble(),
      biasPatterns: (json['bias_patterns'] as List)
          .map((pattern) => BiasPattern.fromJson(pattern))
          .toList(),
      recommendations: List<String>.from(json['recommendations'] ?? []),
      analysisDate: DateTime.parse(json['analysis_date']),
      needsModelReview: json['needs_model_review'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_feedbacks': totalFeedbacks,
      'negative_count': negativeCount,
      'negative_percentage': negativePercentage,
      'emotion_accuracy_score': emotionAccuracyScore,
      'response_quality_score': responseQualityScore,
      'crisis_detection_score': crisisDetectionScore,
      'bias_patterns': biasPatterns.map((p) => p.toJson()).toList(),
      'recommendations': recommendations,
      'analysis_date': analysisDate.toIso8601String(),
      'needs_model_review': needsModelReview,
    };
  }
}

class FeedbackStats {
  final int totalFeedbacks;
  final double averageRating;
  final Map<int, int> ratingsDistribution;
  final Map<String, int> feedbackByType;
  final List<FeedbackResponse> recentFeedbacks;

  FeedbackStats({
    required this.totalFeedbacks,
    required this.averageRating,
    required this.ratingsDistribution,
    required this.feedbackByType,
    required this.recentFeedbacks,
  });

  factory FeedbackStats.fromJson(Map<String, dynamic> json) {
    return FeedbackStats(
      totalFeedbacks: json['total_feedbacks'],
      averageRating: (json['average_rating'] as num).toDouble(),
      ratingsDistribution: Map<int, int>.from(
        json['ratings_distribution'].map(
          (k, v) => MapEntry(int.parse(k.toString()), v as int),
        ),
      ),
      feedbackByType: Map<String, int>.from(json['feedback_by_type']),
      recentFeedbacks: (json['recent_feedbacks'] as List)
          .map((feedback) => FeedbackResponse.fromJson(feedback))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_feedbacks': totalFeedbacks,
      'average_rating': averageRating,
      'ratings_distribution': ratingsDistribution,
      'feedback_by_type': feedbackByType,
      'recent_feedbacks': recentFeedbacks.map((f) => f.toJson()).toList(),
    };
  }
}
