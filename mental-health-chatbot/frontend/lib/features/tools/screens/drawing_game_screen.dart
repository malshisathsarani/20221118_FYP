import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'dart:ui' as ui;
import 'dart:math' as math;
import 'dart:convert';
import 'dart:typed_data';
import '../../../core/services/artwork_service.dart';
import '../../../core/models/artwork.dart';

class DrawingGameScreen extends StatefulWidget {
  const DrawingGameScreen({super.key});

  @override
  State<DrawingGameScreen> createState() => _DrawingGameScreenState();
}

class _DrawingGameScreenState extends State<DrawingGameScreen>
    with SingleTickerProviderStateMixin {
  final List<DrawingPoint> points = [];
  Color selectedColor = const Color(0xFF8B5CF6);
  double strokeWidth = 4.0;
  DrawingMode drawingMode = DrawingMode.normal;
  late AnimationController _sparkleController;
  final ArtworkService _artworkService = ArtworkService();
  final GlobalKey _canvasKey = GlobalKey();
  bool _isSaving = false;
  List<ArtworkThumbnail> _previousArtworks = [];
  bool _isLoadingGallery = true;

  // Soft, calming pastel colors
  final List<ColorOption> availableColors = [
    ColorOption(color: const Color(0xFF8B5CF6), name: 'Lavender'),
    ColorOption(color: const Color(0xFFEC4899), name: 'Pink'),
    ColorOption(color: const Color(0xFF10B981), name: 'Mint'),
    ColorOption(color: const Color(0xFF3B82F6), name: 'Sky Blue'),
    ColorOption(color: const Color(0xFFF59E0B), name: 'Sunshine'),
    ColorOption(color: const Color(0xFFEF4444), name: 'Coral'),
    ColorOption(color: const Color(0xFF06B6D4), name: 'Aqua'),
    ColorOption(color: const Color(0xFF8B4513), name: 'Earth'),
    ColorOption(color: const Color(0xFF6B7280), name: 'Storm'),
  ];

  @override
  void initState() {
    super.initState();
    _sparkleController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
    _loadPreviousArtworks();
  }

  @override
  void dispose() {
    _sparkleController.dispose();
    super.dispose();
  }

  Future<void> _loadPreviousArtworks() async {
    try {
      final artworks = await _artworkService.getThumbnails(limit: 20);
      setState(() {
        _previousArtworks = artworks;
        _isLoadingGallery = false;
      });
    } catch (e) {
      setState(() => _isLoadingGallery = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not load gallery: $e')),
        );
      }
    }
  }

  void _addPoint(Offset offset) {
    setState(() {
      Paint paint = Paint()
        ..color = selectedColor
        ..isAntiAlias = true
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round;

      if (drawingMode == DrawingMode.glow) {
        paint.maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);
      }

      points.add(DrawingPoint(
        offset: offset,
        paint: paint,
        mode: drawingMode,
      ));
    });
  }

  void _clearCanvas() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Clear Canvas?'),
        content: const Text('This will erase all your artwork'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() => points.clear());
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
            ),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  Future<void> _saveDrawing() async {
    if (points.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Canvas is empty. Draw something first!')),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      // Capture the canvas as an image
      final boundary = _canvasKey.currentContext!.findRenderObject()
          as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final pngBytes = byteData!.buffer.asUint8List();
      final base64Image = base64Encode(pngBytes);

      // Create thumbnail (smaller version)
      final thumbnailImage = await boundary.toImage(pixelRatio: 0.5);
      final thumbnailByteData =
          await thumbnailImage.toByteData(format: ui.ImageByteFormat.png);
      final thumbnailBytes = thumbnailByteData!.buffer.asUint8List();
      final base64Thumbnail = base64Encode(thumbnailBytes);

      // Save to database
      await _artworkService.createArtwork(
        imageData: base64Image,
        thumbnailData: base64Thumbnail,
        title: 'Drawing ${DateTime.now().toString().substring(0, 16)}',
      );

      // Reload gallery
      await _loadPreviousArtworks();

      setState(() => _isSaving = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    '✨ Beautiful artwork saved!',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
            backgroundColor: const Color(0xFF10B981),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    } catch (e) {
      setState(() => _isSaving = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving artwork: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _viewArtwork(ArtworkThumbnail thumbnail) async {
    try {
      final artwork = await _artworkService.getArtwork(thumbnail.id);
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => Dialog(
            backgroundColor: Colors.transparent,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  constraints: const BoxConstraints(maxHeight: 500),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Header
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                artwork.title ?? 'Untitled',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.close),
                              onPressed: () => Navigator.pop(context),
                            ),
                          ],
                        ),
                      ),
                      // Image
                      Flexible(
                        child: ClipRRect(
                          borderRadius: const BorderRadius.vertical(
                            bottom: Radius.circular(20),
                          ),
                          child: Image.memory(
                            base64Decode(artwork.imageData),
                            fit: BoxFit.contain,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading artwork: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFFF5F3FF),
              Color(0xFFEDE9FE),
              Color(0xFFDDD6FE),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.1),
                                blurRadius: 10,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: const Icon(Icons.palette,
                              color: Color(0xFF8B5CF6), size: 24),
                        ),
                        const SizedBox(width: 10),
                        const Text(
                          'Mindful Drawing',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF1F2937),
                          ),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: const Icon(Icons.close,
                            color: Color(0xFF6B7280), size: 20),
                      ),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
              ),

              // Drawing Mode Selector
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4),
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: _buildModeButton(
                          'Normal',
                          Icons.brush,
                          DrawingMode.normal,
                        ),
                      ),
                      Expanded(
                        child: _buildModeButton(
                          'Glow',
                          Icons.auto_awesome,
                          DrawingMode.glow,
                        ),
                      ),
                      Expanded(
                        child: _buildModeButton(
                          'Rainbow',
                          Icons.gradient,
                          DrawingMode.rainbow,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 8),

              // Drawing Canvas
              Expanded(
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 20,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(24),
                    child: GestureDetector(
                      onPanDown: (details) => _addPoint(details.localPosition),
                      onPanUpdate: (details) => _addPoint(details.localPosition),
                      onPanEnd: (details) {
                        setState(() {
                          points.add(DrawingPoint(
                            offset: Offset.zero,
                            paint: Paint(),
                            mode: drawingMode,
                          ));
                        });
                      },
                      child: RepaintBoundary(
                        key: _canvasKey,
                        child: Stack(
                          children: [
                            CustomPaint(
                              painter: GridPainter(),
                              size: Size.infinite,
                            ),
                            CustomPaint(
                              painter: DrawingPainter(points),
                              size: Size.infinite,
                            ),
                            AnimatedBuilder(
                              animation: _sparkleController,
                              builder: (context, child) {
                                return CustomPaint(
                                  painter: SparklePainter(
                                    _sparkleController.value,
                                    points.isNotEmpty
                                        ? points.last.offset
                                        : Offset.zero,
                                  ),
                                  size: Size.infinite,
                                );
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 8),

              // Gallery Section
              Container(
                height: 110,
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'Your Gallery',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1F2937),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: _isLoadingGallery
                          ? const Center(child: CircularProgressIndicator())
                          : _previousArtworks.isEmpty
                              ? const Center(
                                  child: Text(
                                    'No saved artworks yet',
                                    style: TextStyle(
                                      color: Color(0xFF6B7280),
                                      fontSize: 12,
                                    ),
                                  ),
                                )
                              : ListView.builder(
                                  scrollDirection: Axis.horizontal,
                                  padding: const EdgeInsets.symmetric(horizontal: 16),
                                  itemCount: _previousArtworks.length,
                                  itemBuilder: (context, index) {
                                    final artwork = _previousArtworks[index];
                                    return GestureDetector(
                                      onTap: () => _viewArtwork(artwork),
                                      child: Container(
                                        width: 70,
                                        margin: const EdgeInsets.only(right: 12),
                                        decoration: BoxDecoration(
                                          color: Colors.white,
                                          borderRadius: BorderRadius.circular(12),
                                          boxShadow: [
                                            BoxShadow(
                                              color: Colors.black.withOpacity(0.1),
                                              blurRadius: 8,
                                              offset: const Offset(0, 2),
                                            ),
                                          ],
                                        ),
                                        child: ClipRRect(
                                          borderRadius: BorderRadius.circular(12),
                                          child: artwork.thumbnailData != null
                                              ? Image.memory(
                                                  base64Decode(artwork.thumbnailData!),
                                                  fit: BoxFit.cover,
                                                )
                                              : const Center(
                                                  child: Icon(
                                                    Icons.image,
                                                    color: Color(0xFF6B7280),
                                                  ),
                                                ),
                                        ),
                                      ),
                                    );
                                  },
                                ),
                    ),
                  ],
                ),
              ),

              // Controls
              Container(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                child: Column(
                  children: [
                    // Brush Size
                    Row(
                      children: [
                        const Icon(Icons.line_weight,
                            size: 18, color: Color(0xFF6B7280)),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Slider(
                            value: strokeWidth,
                            min: 2,
                            max: 20,
                            divisions: 18,
                            activeColor: const Color(0xFF8B5CF6),
                            onChanged: (value) =>
                                setState(() => strokeWidth = value),
                          ),
                        ),
                        Container(
                          width: 30,
                          height: 30,
                          decoration: BoxDecoration(
                            color: selectedColor,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: Colors.white,
                              width: 2,
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 8),

                    // Color Palette
                    SizedBox(
                      height: 44,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: availableColors.length,
                        itemBuilder: (context, index) {
                          final colorOption = availableColors[index];
                          final isSelected = selectedColor == colorOption.color;
                          return GestureDetector(
                            onTap: () =>
                                setState(() => selectedColor = colorOption.color),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              width: isSelected ? 44 : 38,
                              height: isSelected ? 44 : 38,
                              margin: const EdgeInsets.only(right: 12),
                              decoration: BoxDecoration(
                                color: colorOption.color,
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: isSelected
                                      ? Colors.white
                                      : Colors.transparent,
                                  width: 3,
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: colorOption.color.withOpacity(0.4),
                                    blurRadius: isSelected ? 12 : 6,
                                    spreadRadius: isSelected ? 2 : 0,
                                  ),
                                ],
                              ),
                              child: isSelected
                                  ? const Icon(
                                      Icons.check,
                                      color: Colors.white,
                                      size: 20,
                                    )
                                  : null,
                            ),
                          );
                        },
                      ),
                    ),

                    const SizedBox(height: 12),

                    // Action Buttons
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _clearCanvas,
                            icon: const Icon(Icons.delete_outline),
                            label: const Text('Clear'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFFEF4444),
                              side: const BorderSide(color: Color(0xFFEF4444)),
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          flex: 2,
                          child: ElevatedButton.icon(
                            onPressed: _isSaving ? null : _saveDrawing,
                            icon: _isSaving
                                ? const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                          Colors.white),
                                    ),
                                  )
                                : const Icon(Icons.save_alt),
                            label: Text(_isSaving ? 'Saving...' : 'Save Drawing'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF8B5CF6),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                      ],
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

  Widget _buildModeButton(String label, IconData icon, DrawingMode mode) {
    final isSelected = drawingMode == mode;
    return GestureDetector(
      onTap: () => setState(() => drawingMode = mode),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF8B5CF6) : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : const Color(0xFF6B7280),
              size: 18,
            ),
            const SizedBox(height: 3),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                color: isSelected ? Colors.white : const Color(0xFF6B7280),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

enum DrawingMode { normal, glow, rainbow }

class ColorOption {
  final Color color;
  final String name;

  ColorOption({required this.color, required this.name});
}

class DrawingPoint {
  final Offset offset;
  final Paint paint;
  final DrawingMode mode;

  DrawingPoint({
    required this.offset,
    required this.paint,
    required this.mode,
  });
}

class DrawingPainter extends CustomPainter {
  final List<DrawingPoint> points;

  DrawingPainter(this.points);

  @override
  void paint(Canvas canvas, Size size) {
    for (int i = 0; i < points.length - 1; i++) {
      if (points[i].offset != Offset.zero &&
          points[i + 1].offset != Offset.zero) {
        Paint paint = points[i].paint;

        // Rainbow mode
        if (points[i].mode == DrawingMode.rainbow) {
          final hue = (i / points.length * 360) % 360;
          paint = Paint()
            ..color = HSVColor.fromAHSV(1.0, hue, 0.8, 0.9).toColor()
            ..strokeWidth = points[i].paint.strokeWidth
            ..strokeCap = StrokeCap.round
            ..isAntiAlias = true;
        }

        canvas.drawLine(points[i].offset, points[i + 1].offset, paint);
      } else if (points[i].offset != Offset.zero) {
        canvas.drawCircle(points[i].offset, points[i].paint.strokeWidth / 2,
            points[i].paint);
      }
    }
  }

  @override
  bool shouldRepaint(DrawingPainter oldDelegate) => true;
}

class GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.grey[300]!
      ..strokeWidth = 1;

    const spacing = 30.0;
    for (double i = 0; i < size.width; i += spacing) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
    }
    for (double i = 0; i < size.height; i += spacing) {
      canvas.drawLine(Offset(0, i), Offset(size.width, i), paint);
    }
  }

  @override
  bool shouldRepaint(GridPainter oldDelegate) => false;
}

class SparklePainter extends CustomPainter {
  final double progress;
  final Offset position;

  SparklePainter(this.progress, this.position);

  @override
  void paint(Canvas canvas, Size size) {
    if (position == Offset.zero) return;

    final paint = Paint()
      ..color = Colors.amber.withOpacity((1 - progress) * 0.6)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < 4; i++) {
      final angle = (i * math.pi / 2) + (progress * math.pi * 2);
      final distance = 20 * progress;
      final sparklePos = Offset(
        position.dx + math.cos(angle) * distance,
        position.dy + math.sin(angle) * distance,
      );
      canvas.drawCircle(sparklePos, 2 * (1 - progress), paint);
    }
  }

  @override
  bool shouldRepaint(SparklePainter oldDelegate) => true;
}
