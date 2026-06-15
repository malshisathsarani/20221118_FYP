import 'package:flutter/material.dart';
import 'dart:math' as math;

class BreathingBubbleScreen extends StatefulWidget {
  const BreathingBubbleScreen({super.key});

  @override
  State<BreathingBubbleScreen> createState() => _BreathingBubbleScreenState();
}

class _BreathingBubbleScreenState extends State<BreathingBubbleScreen>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late AnimationController _glowController;
  late AnimationController _particleController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _glowAnimation;
  int _breathCount = 0;
  String _breathPhase = 'Tap to start';
  String _breathInstruction = 'Breathe with the bubble';
  bool _isPlaying = false;

  @override
  void initState() {
    super.initState();

    // Main breathing animation
    _controller = AnimationController(
      duration: const Duration(milliseconds: 12000), // 12 seconds per cycle
      vsync: this,
    );

    // Glow pulse animation
    _glowController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat(reverse: true);

    // Particle animation
    _particleController = AnimationController(
      duration: const Duration(milliseconds: 3000),
      vsync: this,
    )..repeat();

    // Breathing cycle: 4s inhale -> 2s hold -> 4s exhale -> 2s hold
    _scaleAnimation = TweenSequence<double>([
      // Inhale (4 seconds)
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.5, end: 1.0)
            .chain(CurveTween(curve: Curves.easeInOut)),
        weight: 33.3, // 4/12
      ),
      // Hold (2 seconds)
      TweenSequenceItem(
        tween: ConstantTween<double>(1.0),
        weight: 16.7, // 2/12
      ),
      // Exhale (4 seconds)
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.0, end: 0.5)
            .chain(CurveTween(curve: Curves.easeInOut)),
        weight: 33.3, // 4/12
      ),
      // Hold (2 seconds)
      TweenSequenceItem(
        tween: ConstantTween<double>(0.5),
        weight: 16.7, // 2/12
      ),
    ]).animate(_controller);

    _glowAnimation = Tween<double>(begin: 0.3, end: 0.7).animate(
      CurvedAnimation(parent: _glowController, curve: Curves.easeInOut),
    );

    _controller.addListener(() {
      final value = _controller.value;
      setState(() {
        if (value < 0.333) {
          _breathPhase = 'Breathe In';
          _breathInstruction = 'Inhale slowly through your nose';
        } else if (value < 0.5) {
          _breathPhase = 'Hold';
          _breathInstruction = 'Hold your breath gently';
        } else if (value < 0.833) {
          _breathPhase = 'Breathe Out';
          _breathInstruction = 'Exhale slowly through your mouth';
        } else {
          _breathPhase = 'Hold';
          _breathInstruction = 'Pause and relax';
        }
      });
    });

    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        setState(() {
          _breathCount++;
        });
        if (_isPlaying) {
          _controller.forward(from: 0);
        }
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _glowController.dispose();
    _particleController.dispose();
    super.dispose();
  }

  void _togglePlayPause() {
    setState(() {
      if (_isPlaying) {
        _controller.stop();
        _isPlaying = false;
      } else {
        _isPlaying = true;
        if (_controller.value == 0 || _controller.value == 1) {
          _breathCount = 0;
          _controller.forward(from: 0);
        } else {
          _controller.forward();
        }
      }
    });
  }

  void _reset() {
    setState(() {
      _controller.reset();
      _breathCount = 0;
      _isPlaying = false;
      _breathPhase = 'Tap to start';
      _breathInstruction = 'Breathe with the bubble';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF667EEA),
              Color(0xFF764BA2),
              Color(0xFF8B5CF6),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white, size: 28),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                    const Text(
                      'Breathing Exercise',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.refresh, color: Colors.white, size: 28),
                      onPressed: _reset,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Breath count
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha:0.2),
                  borderRadius: BorderRadius.circular(30),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.favorite, color: Colors.white, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Cycles: $_breathCount',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 40),

              // Breathing bubble with particles
              Expanded(
                child: Center(
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Animated particles
                      ...List.generate(8, (index) {
                        return AnimatedBuilder(
                          animation: _particleController,
                          builder: (context, child) {
                            final angle = (index * math.pi * 2 / 8) +
                                (_particleController.value * math.pi * 2);
                            final distance = 180 + (math.sin(_particleController.value * math.pi * 2) * 30);
                            final x = math.cos(angle) * distance;
                            final y = math.sin(angle) * distance;
                            final opacity = 0.3 + (math.sin(_particleController.value * math.pi * 2) * 0.2);

                            return Transform.translate(
                              offset: Offset(x, y),
                              child: Container(
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Colors.white.withValues(alpha:opacity),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.white.withValues(alpha:0.5),
                                      blurRadius: 10,
                                      spreadRadius: 2,
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        );
                      }),

                      // Main breathing bubble
                      AnimatedBuilder(
                        animation: Listenable.merge([_scaleAnimation, _glowAnimation]),
                        builder: (context, child) {
                          return Transform.scale(
                            scale: _scaleAnimation.value,
                            child: Container(
                              width: 280,
                              height: 280,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: RadialGradient(
                                  colors: [
                                    Colors.white.withValues(alpha:0.9),
                                    const Color(0xFFA78BFA).withValues(alpha:0.8),
                                    const Color(0xFF8B5CF6).withValues(alpha:0.6),
                                  ],
                                  stops: const [0.2, 0.6, 1.0],
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.white.withValues(alpha:_glowAnimation.value),
                                    blurRadius: 60,
                                    spreadRadius: 20,
                                  ),
                                  BoxShadow(
                                    color: const Color(0xFF8B5CF6).withValues(alpha:0.4),
                                    blurRadius: 40,
                                    spreadRadius: 10,
                                  ),
                                ],
                              ),
                              child: Center(
                                child: Text(
                                  _breathPhase,
                                  style: TextStyle(
                                    fontSize: 28,
                                    fontWeight: FontWeight.w600,
                                    color: const Color(0xFF667EEA),
                                    letterSpacing: 1,
                                    shadows: [
                                      Shadow(
                                        color: Colors.white.withValues(alpha:0.5),
                                        blurRadius: 10,
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),

              // Instructions and controls
              Container(
                padding: const EdgeInsets.all(32.0),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha:0.2),
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(30)),
                ),
                child: Column(
                  children: [
                    Text(
                      _breathInstruction,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 18,
                        color: Colors.white,
                        fontWeight: FontWeight.w500,
                        height: 1.5,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Play/Pause button
                    GestureDetector(
                      onTap: _togglePlayPause,
                      child: Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha:0.3),
                              blurRadius: 20,
                              spreadRadius: 5,
                            ),
                          ],
                        ),
                        child: Icon(
                          _isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                          size: 40,
                          color: const Color(0xFF8B5CF6),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Tips
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha:0.1),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.lightbulb_outline,
                            color: Colors.amber,
                            size: 24
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Find a quiet space and focus on the bubble\'s rhythm',
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.white.withValues(alpha:0.9),
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
