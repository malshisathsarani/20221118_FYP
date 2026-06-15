import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:math' as math;
import 'dart:ui' as ui;

class CalmPuzzleScreen extends StatefulWidget {
  const CalmPuzzleScreen({super.key});

  @override
  State<CalmPuzzleScreen> createState() => _CalmPuzzleScreenState();
}

class _CalmPuzzleScreenState extends State<CalmPuzzleScreen>
    with TickerProviderStateMixin {
  List<PuzzlePiece> pieces = [];
  int? selectedIndex;
  int moveCount = 0;
  bool isCompleted = false;
  late AnimationController _celebrationController;
  late AnimationController _breatheController;
  late AnimationController _shimmerController;
  late AnimationController _bubbleController;
  String selectedDifficulty = 'Easy'; // Easy (2x2), Medium (3x3), Hard (4x4)
  int gridSize = 2;
  final List<Bubble> _bubbles = [];

  // Calming nature images
  final List<PuzzleImage> images = [
    PuzzleImage(
      name: 'Ocean Waves',
      colors: [Color(0xFF84D2F6), Color(0xFF5AB0D9), Color(0xFF3F97C4), Color(0xFF2E7CA6)],
      icon: Icons.waves,
    ),
    PuzzleImage(
      name: 'Forest Peace',
      colors: [Color(0xFF8FD99F), Color(0xFF5DBF73), Color(0xFF3FA660), Color(0xFF2D8B4E)],
      icon: Icons.forest,
    ),
    PuzzleImage(
      name: 'Sunset Sky',
      colors: [Color(0xFFFFB6A3), Color(0xFFFF8F7F), Color(0xFFFF6B5C), Color(0xFFE84A3C)],
      icon: Icons.wb_sunny,
    ),
    PuzzleImage(
      name: 'Lavender Fields',
      colors: [Color(0xFFD4B5E8), Color(0xFFB890D9), Color(0xFF9D6FCC), Color(0xFF8454BF)],
      icon: Icons.local_florist,
    ),
    PuzzleImage(
      name: 'Cherry Blossom',
      colors: [Color(0xFFFFD1E0), Color(0xFFFFADC9), Color(0xFFFF8BB3), Color(0xFFFF6B9D)],
      icon: Icons.yard,
    ),
    PuzzleImage(
      name: 'Mountain Mist',
      colors: [Color(0xFFB8C9D9), Color(0xFF94AABF), Color(0xFF6F8CA6), Color(0xFF4D6D8C)],
      icon: Icons.terrain,
    ),
  ];

  int selectedImageIndex = 0;

  @override
  void initState() {
    super.initState();
    _celebrationController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _breatheController = AnimationController(
      duration: const Duration(seconds: 4),
      vsync: this,
    )..repeat(reverse: true);
    _shimmerController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();
    _bubbleController = AnimationController(
      duration: const Duration(seconds: 60),
      vsync: this,
    )..repeat();

    // Initialize bubbles
    final random = math.Random();
    for (int i = 0; i < 15; i++) {
      _bubbles.add(Bubble(
        x: random.nextDouble(),
        y: random.nextDouble(),
        size: 20 + random.nextDouble() * 60,
        speed: 0.3 + random.nextDouble() * 0.7,
        opacity: 0.1 + random.nextDouble() * 0.2,
      ));
    }

    _initializePuzzle();
  }

  @override
  void dispose() {
    _celebrationController.dispose();
    _breatheController.dispose();
    _shimmerController.dispose();
    _bubbleController.dispose();
    super.dispose();
  }

  void _initializePuzzle() {
    pieces.clear();
    final selectedImage = images[selectedImageIndex];
    final totalPieces = gridSize * gridSize;

    // Create gradient pieces based on grid size
    for (int i = 0; i < totalPieces; i++) {
      final colorIndex = (i * selectedImage.colors.length / totalPieces).floor().clamp(0, selectedImage.colors.length - 1);
      pieces.add(PuzzlePiece(
        color: selectedImage.colors[colorIndex],
        number: i + 1,
        correctIndex: i,
      ));
    }

    _shufflePuzzle();
    moveCount = 0;
    isCompleted = false;
  }

  bool _isPuzzleComplete() {
    for (int i = 0; i < pieces.length; i++) {
      if (pieces[i].correctIndex != i) {
        return false;
      }
    }
    return true;
  }

  void _showSuccessDialog() {
    _celebrationController.forward();
    HapticFeedback.heavyImpact();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => PopScope(
        canPop: false,
        child: Center(
          child: ScaleTransition(
            scale: Tween<double>(begin: 0.0, end: 1.0).animate(
              CurvedAnimation(parent: _celebrationController, curve: Curves.elasticOut),
            ),
            child: Dialog(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(32),
              ),
              backgroundColor: Colors.transparent,
              elevation: 0,
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.white,
                      Colors.purple.shade50,
                    ],
                  ),
                  borderRadius: BorderRadius.circular(32),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.purple.withOpacity(0.3),
                      blurRadius: 30,
                      spreadRadius: 10,
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(40),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Animated confetti icon
                    RotationTransition(
                      turns: Tween<double>(begin: 0.0, end: 0.1).animate(
                        CurvedAnimation(parent: _celebrationController, curve: Curves.elasticOut),
                      ),
                      child: const Icon(
                        Icons.celebration,
                        size: 80,
                        color: Color(0xFFFFD700),
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Beautiful Work!',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.w700,
                        color: Colors.black87,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Completed in $moveCount ${moveCount == 1 ? 'move' : 'moves'}',
                      style: TextStyle(
                        fontSize: 18,
                        color: Colors.grey[700],
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'You stayed calm and focused.\nTake a moment to appreciate your patience.',
                      style: TextStyle(
                        fontSize: 15,
                        color: Colors.grey[600],
                        fontStyle: FontStyle.italic,
                        height: 1.5,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () {
                              Navigator.pop(context);
                              _resetPuzzle();
                            },
                            icon: const Icon(Icons.refresh, size: 20),
                            label: const Text(
                              'New Puzzle',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF8B5CF6),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 24,
                                vertical: 16,
                              ),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                              elevation: 0,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              _celebrationController.reset();
                              Navigator.pop(context);
                              Navigator.pop(context);
                            },
                            icon: const Icon(Icons.close, size: 20),
                            label: const Text(
                              'Finish',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.black87,
                              side: BorderSide(
                                color: Colors.grey.shade300,
                                width: 2,
                              ),
                              padding: const EdgeInsets.symmetric(
                                horizontal: 24,
                                vertical: 16,
                              ),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _shufflePuzzle() {
    setState(() {
      pieces.shuffle(math.Random());
    });
  }

  void _onPieceTap(int index) {
    if (isCompleted) return;

    HapticFeedback.lightImpact();

    setState(() {
      if (selectedIndex == null) {
        selectedIndex = index;
      } else {
        if (selectedIndex == index) {
          // Deselect if tapping the same piece
          selectedIndex = null;
        } else {
          // Swap pieces
          final temp = pieces[selectedIndex!];
          pieces[selectedIndex!] = pieces[index];
          pieces[index] = temp;
          selectedIndex = null;
          moveCount++;

          // Check for completion
          if (_isPuzzleComplete()) {
            isCompleted = true;
            Future.delayed(const Duration(milliseconds: 500), () {
              _showSuccessDialog();
            });
          }
        }
      }
    });
  }

  void _resetPuzzle() {
    _celebrationController.reset();
    _initializePuzzle();
  }

  void _changeDifficulty(String difficulty) {
    setState(() {
      selectedDifficulty = difficulty;
      if (difficulty == 'Easy') {
        gridSize = 2;
      } else if (difficulty == 'Medium') {
        gridSize = 3;
      } else {
        gridSize = 4;
      }
      _initializePuzzle();
    });
  }

  void _showImagePicker() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        builder: (context, scrollController) => Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.white,
                Colors.purple.shade50,
              ],
            ),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
          ),
          child: SingleChildScrollView(
            controller: scrollController,
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'Choose a Peaceful Scene',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 20),
                  GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.3,
                    ),
                    itemCount: images.length,
                    itemBuilder: (context, index) {
                      final image = images[index];
                      final isSelected = selectedImageIndex == index;
                      return GestureDetector(
                        onTap: () {
                          Navigator.pop(context);
                          Future.delayed(const Duration(milliseconds: 100), () {
                            setState(() {
                              selectedImageIndex = index;
                              _initializePuzzle();
                            });
                          });
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: image.colors,
                            ),
                            borderRadius: BorderRadius.circular(16),
                            border: isSelected
                                ? Border.all(color: Colors.white, width: 3)
                                : null,
                            boxShadow: isSelected
                                ? [
                                    BoxShadow(
                                      color: image.colors[0].withOpacity(0.5),
                                      blurRadius: 15,
                                      spreadRadius: 2,
                                    ),
                                  ]
                                : [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.1),
                                      blurRadius: 8,
                                      spreadRadius: 1,
                                    ),
                                  ],
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                image.icon,
                                size: 32,
                                color: Colors.white,
                              ),
                              const SizedBox(height: 6),
                              Text(
                                image.name,
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Gradient background
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Colors.purple.shade50,
                  Colors.blue.shade50,
                  Colors.pink.shade50,
                ],
              ),
            ),
          ),

          // Animated floating bubbles
          AnimatedBuilder(
            animation: _bubbleController,
            builder: (context, child) {
              return CustomPaint(
                painter: BubblePainter(
                  bubbles: _bubbles,
                  animationValue: _bubbleController.value,
                ),
                child: Container(),
              );
            },
          ),

          // Main content
          SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.black87, size: 28),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                    const Spacer(),
                    // Breathing indicator
                    AnimatedBuilder(
                      animation: _breatheController,
                      builder: (context, child) {
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.9),
                            borderRadius: BorderRadius.circular(20),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.purple.withOpacity(0.2 + _breatheController.value * 0.2),
                                blurRadius: 10 + _breatheController.value * 10,
                                spreadRadius: 1,
                              ),
                            ],
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.self_improvement,
                                size: 16 + _breatheController.value * 4,
                                color: Color.lerp(
                                  Colors.purple.shade300,
                                  Colors.purple.shade600,
                                  _breatheController.value,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Breathe',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.purple.shade700,
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.refresh, color: Colors.black87, size: 28),
                      onPressed: _resetPuzzle,
                    ),
                  ],
                ),
              ),

              // Title and moves
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Column(
                  children: [
                    const Text(
                      'Peaceful Puzzle',
                      style: TextStyle(
                        fontSize: 36,
                        fontWeight: FontWeight.w800,
                        color: Colors.black87,
                        letterSpacing: -1,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.purple.shade100,
                            Colors.blue.shade100,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.purple.withOpacity(0.2),
                            blurRadius: 10,
                            spreadRadius: 1,
                          ),
                        ],
                      ),
                      child: Text(
                        'Moves: $moveCount',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Colors.purple.shade700,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Difficulty and Image selector
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.9),
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10,
                              spreadRadius: 1,
                            ),
                          ],
                        ),
                        child: Row(
                          children: ['Easy', 'Medium', 'Hard'].map((difficulty) {
                            final isSelected = selectedDifficulty == difficulty;
                            return Expanded(
                              child: GestureDetector(
                                onTap: () => _changeDifficulty(difficulty),
                                child: AnimatedContainer(
                                  duration: const Duration(milliseconds: 200),
                                  padding: const EdgeInsets.symmetric(vertical: 10),
                                  decoration: BoxDecoration(
                                    gradient: isSelected
                                        ? LinearGradient(
                                            colors: [
                                              Colors.purple.shade400,
                                              Colors.purple.shade600,
                                            ],
                                          )
                                        : null,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    difficulty,
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w600,
                                      color: isSelected ? Colors.white : Colors.grey[600],
                                    ),
                                  ),
                                ),
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    GestureDetector(
                      onTap: _showImagePicker,
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: images[selectedImageIndex].colors.take(2).toList(),
                          ),
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: images[selectedImageIndex].colors[0].withOpacity(0.4),
                              blurRadius: 10,
                              spreadRadius: 1,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.palette,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Puzzle grid
              Expanded(
                child: Center(
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final availableSize = math.min(constraints.maxWidth, constraints.maxHeight);
                      final puzzleSize = availableSize - 16;

                      return SingleChildScrollView(
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Container(
                            width: puzzleSize,
                            height: puzzleSize,
                            margin: const EdgeInsets.all(8),
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.9),
                              borderRadius: BorderRadius.circular(32),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.purple.withOpacity(0.2),
                                  blurRadius: 30,
                                  spreadRadius: 5,
                                ),
                              ],
                            ),
                            child: GridView.builder(
                              physics: const NeverScrollableScrollPhysics(),
                              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: gridSize,
                                crossAxisSpacing: gridSize == 2 ? 16 : gridSize == 3 ? 12 : 8,
                                mainAxisSpacing: gridSize == 2 ? 16 : gridSize == 3 ? 12 : 8,
                              ),
                              itemCount: pieces.length,
                              itemBuilder: (context, index) {
                                final piece = pieces[index];
                                final isSelected = selectedIndex == index;
                                final isCorrect = piece.correctIndex == index;

                                return GestureDetector(
                                  onTap: () => _onPieceTap(index),
                                  child: AnimatedContainer(
                                    duration: const Duration(milliseconds: 300),
                                    curve: Curves.easeOutCubic,
                                    decoration: BoxDecoration(
                                      gradient: LinearGradient(
                                        begin: Alignment.topLeft,
                                        end: Alignment.bottomRight,
                                        colors: [
                                          piece.color,
                                          piece.color.withOpacity(0.8),
                                        ],
                                      ),
                                      borderRadius: BorderRadius.circular(gridSize == 2 ? 20 : gridSize == 3 ? 16 : 12),
                                      border: isSelected
                                          ? Border.all(color: Colors.white, width: gridSize == 2 ? 4 : 3)
                                          : isCorrect && !isCompleted
                                              ? Border.all(color: Colors.green.withOpacity(0.5), width: 2)
                                              : null,
                                      boxShadow: isSelected
                                          ? [
                                              BoxShadow(
                                                color: piece.color.withOpacity(0.6),
                                                blurRadius: 20,
                                                spreadRadius: 3,
                                              ),
                                            ]
                                          : [
                                              BoxShadow(
                                                color: Colors.black.withOpacity(0.1),
                                                blurRadius: 8,
                                                spreadRadius: 1,
                                              ),
                                            ],
                                    ),
                                    transform: Matrix4.identity()
                                      ..scale(isSelected ? 0.95 : 1.0),
                                    child: LayoutBuilder(
                                      builder: (context, constraints) {
                                        final tileSize = constraints.maxWidth;
                                        final circleSize = tileSize * 0.65;
                                        final fontSize = tileSize * 0.28;

                                        return Center(
                                          child: Container(
                                            width: circleSize,
                                            height: circleSize,
                                            decoration: BoxDecoration(
                                              color: Colors.white.withOpacity(0.6),
                                              shape: BoxShape.circle,
                                              border: Border.all(
                                                color: Colors.white.withOpacity(0.9),
                                                width: gridSize == 4 ? 2 : 3,
                                              ),
                                            ),
                                            alignment: Alignment.center,
                                            child: FittedBox(
                                              fit: BoxFit.scaleDown,
                                              child: Padding(
                                                padding: const EdgeInsets.all(4.0),
                                                child: Text(
                                                  '${piece.number}',
                                                  textAlign: TextAlign.center,
                                                  style: TextStyle(
                                                    fontSize: fontSize,
                                                    fontWeight: FontWeight.w900,
                                                    color: Colors.white,
                                                    height: 1.0,
                                                    shadows: [
                                                      Shadow(
                                                        color: Colors.black.withOpacity(0.7),
                                                        blurRadius: 10,
                                                        offset: const Offset(2, 2),
                                                      ),
                                                      Shadow(
                                                        color: Colors.black.withOpacity(0.5),
                                                        blurRadius: 6,
                                                        offset: const Offset(1, 1),
                                                      ),
                                                    ],
                                                  ),
                                                ),
                                              ),
                                            ),
                                          ),
                                        );
                                      },
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),

              // Calming message
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
                child: AnimatedBuilder(
                  animation: _shimmerController,
                  builder: (context, child) {
                    return ShaderMask(
                      shaderCallback: (bounds) {
                        return LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            Colors.purple.shade300,
                            Colors.blue.shade300,
                            Colors.pink.shade300,
                          ],
                          stops: [
                            _shimmerController.value - 0.3,
                            _shimmerController.value,
                            _shimmerController.value + 0.3,
                          ],
                        ).createShader(bounds);
                      },
                      child: const Text(
                        "Take your time • Breathe • Just peace",
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                          height: 1.2,
                          letterSpacing: 0.5,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
        ],
      ),
    );
  }
}

class Bubble {
  final double x;
  final double y;
  final double size;
  final double speed;
  final double opacity;

  Bubble({
    required this.x,
    required this.y,
    required this.size,
    required this.speed,
    required this.opacity,
  });
}

class BubblePainter extends CustomPainter {
  final List<Bubble> bubbles;
  final double animationValue;

  BubblePainter({
    required this.bubbles,
    required this.animationValue,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (final bubble in bubbles) {
      // Calculate bubble position with slow upward movement
      final yOffset = (animationValue * bubble.speed) % 1.0;
      final x = bubble.x * size.width;
      final y = ((bubble.y + yOffset) % 1.2) * size.height;

      // Create gradient for bubble
      final paint = Paint()
        ..shader = RadialGradient(
          colors: [
            Colors.white.withOpacity(bubble.opacity),
            Colors.white.withOpacity(bubble.opacity * 0.3),
            Colors.transparent,
          ],
          stops: const [0.0, 0.7, 1.0],
        ).createShader(Rect.fromCircle(
          center: Offset(x, y),
          radius: bubble.size / 2,
        ))
        ..style = PaintingStyle.fill;

      // Draw bubble
      canvas.drawCircle(Offset(x, y), bubble.size / 2, paint);

      // Draw bubble highlight
      final highlightPaint = Paint()
        ..color = Colors.white.withOpacity(bubble.opacity * 0.6)
        ..style = PaintingStyle.fill;

      canvas.drawCircle(
        Offset(x - bubble.size * 0.2, y - bubble.size * 0.2),
        bubble.size * 0.15,
        highlightPaint,
      );
    }
  }

  @override
  bool shouldRepaint(BubblePainter oldDelegate) => true;
}

class PuzzlePiece {
  final Color color;
  final int number;
  final int correctIndex;

  PuzzlePiece({
    required this.color,
    required this.number,
    required this.correctIndex,
  });
}

class PuzzleImage {
  final String name;
  final List<Color> colors;
  final IconData icon;

  PuzzleImage({
    required this.name,
    required this.colors,
    required this.icon,
  });
}
