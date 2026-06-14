import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'dart:math' as math;
import 'dart:convert';
import 'dart:ui' as ui;
import 'package:vector_math/vector_math_64.dart' show Vector3;
import '../../../core/services/artwork_service.dart';
import '../../../core/models/artwork.dart';

class MandalaColoringScreen extends StatefulWidget {
  const MandalaColoringScreen({super.key});

  @override
  State<MandalaColoringScreen> createState() => _MandalaColoringScreenState();
}

class _MandalaColoringScreenState extends State<MandalaColoringScreen>
    with SingleTickerProviderStateMixin {
  Color selectedColor = const Color(0xFF8B5CF6);
  Map<int, Color> sectionColors = {};
  final GlobalKey _mandalaKey = GlobalKey();
  late AnimationController _glowController;
  final ArtworkService _artworkService = ArtworkService();
  bool _isSaving = false;
  List<ArtworkThumbnail> _savedMandalas = [];
  bool _isLoadingGallery = true;
  MandalaDesign selectedDesign = MandalaDesign.flower;

  // Zoom and pan
  final TransformationController _transformationController = TransformationController();
  double _currentScale = 1.0;

  // Calming pastel color palette
  final List<ColorOption> colorPalette = [
    ColorOption(color: const Color(0xFF8B5CF6), name: 'Lavender'),
    ColorOption(color: const Color(0xFFEC4899), name: 'Rose'),
    ColorOption(color: const Color(0xFF10B981), name: 'Mint'),
    ColorOption(color: const Color(0xFF3B82F6), name: 'Sky'),
    ColorOption(color: const Color(0xFFF59E0B), name: 'Sunshine'),
    ColorOption(color: const Color(0xFFEF4444), name: 'Coral'),
    ColorOption(color: const Color(0xFF06B6D4), name: 'Aqua'),
    ColorOption(color: const Color(0xFF8B4513), name: 'Earth'),
    ColorOption(color: const Color(0xFF6B7280), name: 'Storm'),
    ColorOption(color: const Color(0xFFA855F7), name: 'Purple'),
    ColorOption(color: const Color(0xFFF472B6), name: 'Pink'),
    ColorOption(color: const Color(0xFF22C55E), name: 'Green'),
  ];

  @override
  void initState() {
    super.initState();
    _glowController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat(reverse: true);
    _loadSavedMandalas();
  }

  @override
  void dispose() {
    _glowController.dispose();
    _transformationController.dispose();
    super.dispose();
  }

  Future<void> _loadSavedMandalas() async {
    try {
      final artworks = await _artworkService.getThumbnails(limit: 20);
      setState(() {
        _savedMandalas = artworks;
        _isLoadingGallery = false;
      });
    } catch (e) {
      setState(() => _isLoadingGallery = false);
    }
  }

  void _handleTap(TapDownDetails details) {
    final RenderBox? renderBox =
        _mandalaKey.currentContext?.findRenderObject() as RenderBox?;
    if (renderBox == null) return;

    final size = renderBox.size;

    // Convert global position to local position relative to the CustomPaint
    final localPosition = renderBox.globalToLocal(details.globalPosition);

    // Apply the inverse of the InteractiveViewer's transformation
    final Matrix4 transform = _transformationController.value;
    final Matrix4 inverseTransform = Matrix4.inverted(transform);

    // Transform the local position accounting for zoom/pan
    final Vector3 transformed = inverseTransform.transform3(Vector3(
      localPosition.dx,
      localPosition.dy,
      0,
    ));

    final transformedPosition = Offset(transformed.x, transformed.y);

    final section = selectedDesign.getSectionFromPosition(transformedPosition, size);

    if (section != null) {
      setState(() {
        sectionColors[section] = selectedColor;
      });
    }
  }

  void _resetZoom() {
    _transformationController.value = Matrix4.identity();
    setState(() {
      _currentScale = 1.0;
    });
  }

  Future<void> _saveMandala() async {
    if (sectionColors.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Mandala is empty. Color it first!')),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      final boundary = _mandalaKey.currentContext!.findRenderObject()
          as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final pngBytes = byteData!.buffer.asUint8List();
      final base64Image = base64Encode(pngBytes);

      final thumbnailImage = await boundary.toImage(pixelRatio: 0.5);
      final thumbnailByteData =
          await thumbnailImage.toByteData(format: ui.ImageByteFormat.png);
      final thumbnailBytes = thumbnailByteData!.buffer.asUint8List();
      final base64Thumbnail = base64Encode(thumbnailBytes);

      await _artworkService.createArtwork(
        imageData: base64Image,
        thumbnailData: base64Thumbnail,
        title: 'Mandala ${DateTime.now().toString().substring(0, 16)}',
      );

      await _loadSavedMandalas();

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
                    '✨ Beautiful mandala saved!',
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
            content: Text('Error saving mandala: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _viewMandala(ArtworkThumbnail thumbnail) async {
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
          SnackBar(content: Text('Error loading mandala: $e')),
        );
      }
    }
  }

  void _showDesignPicker() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
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
            const SizedBox(height: 20),
            const Text(
              'Choose a Mandala Design',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: Color(0xFF1F2937),
              ),
            ),
            const SizedBox(height: 20),
            GridView.count(
              shrinkWrap: true,
              crossAxisCount: 2,
              mainAxisSpacing: 16,
              crossAxisSpacing: 16,
              children: MandalaDesign.values.map((design) {
                return GestureDetector(
                  onTap: () {
                    setState(() {
                      selectedDesign = design;
                      sectionColors.clear();
                    });
                    Navigator.pop(context);
                  },
                  child: Container(
                    decoration: BoxDecoration(
                      color: selectedDesign == design
                          ? const Color(0xFF8B5CF6).withOpacity(0.1)
                          : Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: selectedDesign == design
                            ? const Color(0xFF8B5CF6)
                            : Colors.grey[300]!,
                        width: 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.05),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          design.icon,
                          size: 48,
                          color: selectedDesign == design
                              ? const Color(0xFF8B5CF6)
                              : const Color(0xFF6B7280),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          design.name,
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: selectedDesign == design
                                ? const Color(0xFF8B5CF6)
                                : const Color(0xFF1F2937),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
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
                padding: const EdgeInsets.all(16),
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
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.auto_awesome,
                            color: Color(0xFF8B5CF6),
                            size: 24,
                          ),
                        ),
                        const SizedBox(width: 10),
                        const Text(
                          'Mindful Mandala',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF1F2937),
                          ),
                        ),
                      ],
                    ),
                    Row(
                      children: [
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
                            child: const Icon(
                              Icons.grid_view,
                              color: Color(0xFF8B5CF6),
                              size: 20,
                            ),
                          ),
                          onPressed: _showDesignPicker,
                          tooltip: 'Choose design',
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
                            child: const Icon(
                              Icons.close,
                              color: Color(0xFF6B7280),
                              size: 20,
                            ),
                          ),
                          onPressed: () => Navigator.of(context).pop(),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Instruction
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.7),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.touch_app,
                        color: const Color(0xFF8B5CF6).withOpacity(0.7),
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Tap sections to color. Pinch to zoom. Double-tap to reset zoom.',
                          style: TextStyle(
                            fontSize: 13,
                            color: const Color(0xFF1F2937).withOpacity(0.8),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 8),

              // Zoom indicator
              if (_currentScale > 1.0)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF8B5CF6).withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.zoom_in, size: 16, color: Color(0xFF8B5CF6)),
                            const SizedBox(width: 6),
                            Text(
                              '${(_currentScale * 100).toInt()}%',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF8B5CF6),
                              ),
                            ),
                            const SizedBox(width: 6),
                            GestureDetector(
                              onTap: _resetZoom,
                              child: const Icon(Icons.refresh, size: 16, color: Color(0xFF8B5CF6)),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

              // Mandala Canvas with zoom
              Expanded(
                child: InteractiveViewer(
                  transformationController: _transformationController,
                  minScale: 1.0,
                  maxScale: 4.0,
                  boundaryMargin: const EdgeInsets.all(100),
                  onInteractionUpdate: (details) {
                    setState(() {
                      _currentScale = _transformationController.value.getMaxScaleOnAxis();
                    });
                  },
                  child: Center(
                    child: LayoutBuilder(
                      builder: (context, constraints) {
                        final size = math.min(constraints.maxWidth, constraints.maxHeight) - 32;
                        return Container(
                          width: size,
                          height: size,
                          margin: const EdgeInsets.all(16),
                          child: RepaintBoundary(
                            key: _mandalaKey,
                            child: GestureDetector(
                              onTapDown: _handleTap,
                              child: AnimatedBuilder(
                                animation: _glowController,
                                builder: (context, child) {
                                  return CustomPaint(
                                    painter: selectedDesign.getPainter(
                                      sectionColors,
                                      _glowController.value,
                                    ),
                                    size: Size(size, size),
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
              ),

              const SizedBox(height: 8),

              // Gallery Section
              Container(
                height: 100,
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'Your Creations',
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
                          : _savedMandalas.isEmpty
                              ? const Center(
                                  child: Text(
                                    'No saved mandalas yet',
                                    style: TextStyle(
                                      color: Color(0xFF6B7280),
                                      fontSize: 12,
                                    ),
                                  ),
                                )
                              : ListView.builder(
                                  scrollDirection: Axis.horizontal,
                                  padding: const EdgeInsets.symmetric(horizontal: 16),
                                  itemCount: _savedMandalas.length,
                                  itemBuilder: (context, index) {
                                    final mandala = _savedMandalas[index];
                                    return GestureDetector(
                                      onTap: () => _viewMandala(mandala),
                                      child: Container(
                                        width: 60,
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
                                          child: mandala.thumbnailData != null
                                              ? Image.memory(
                                                  base64Decode(mandala.thumbnailData!),
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
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    // Color Palette
                    SizedBox(
                      height: 50,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: colorPalette.length,
                        itemBuilder: (context, index) {
                          final colorOption = colorPalette[index];
                          final isSelected = selectedColor == colorOption.color;
                          return GestureDetector(
                            onTap: () =>
                                setState(() => selectedColor = colorOption.color),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              width: isSelected ? 50 : 44,
                              height: isSelected ? 50 : 44,
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
                                      size: 24,
                                    )
                                  : null,
                            ),
                          );
                        },
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Action Buttons
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              setState(() => sectionColors.clear());
                            },
                            icon: const Icon(Icons.refresh),
                            label: const Text('Clear'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF6B7280),
                              side: const BorderSide(color: Color(0xFFD1D5DB)),
                              padding: const EdgeInsets.symmetric(vertical: 14),
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
                            onPressed: _isSaving ? null : _saveMandala,
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
                            label: Text(_isSaving ? 'Saving...' : 'Save Mandala'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF8B5CF6),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
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
}

class ColorOption {
  final Color color;
  final String name;

  ColorOption({required this.color, required this.name});
}

enum MandalaDesign {
  flower,
  geometric,
  lotus,
  star;

  String get name {
    switch (this) {
      case MandalaDesign.flower:
        return 'Flower';
      case MandalaDesign.geometric:
        return 'Geometric';
      case MandalaDesign.lotus:
        return 'Lotus';
      case MandalaDesign.star:
        return 'Star';
    }
  }

  IconData get icon {
    switch (this) {
      case MandalaDesign.flower:
        return Icons.local_florist;
      case MandalaDesign.geometric:
        return Icons.hexagon_outlined;
      case MandalaDesign.lotus:
        return Icons.spa;
      case MandalaDesign.star:
        return Icons.star_outline;
    }
  }

  CustomPainter getPainter(Map<int, Color> colors, double glowValue) {
    switch (this) {
      case MandalaDesign.flower:
        return FlowerMandalaPainter(sectionColors: colors, glowValue: glowValue);
      case MandalaDesign.geometric:
        return GeometricMandalaPainter(
            sectionColors: colors, glowValue: glowValue);
      case MandalaDesign.lotus:
        return LotusMandalaPainter(sectionColors: colors, glowValue: glowValue);
      case MandalaDesign.star:
        return StarMandalaPainter(sectionColors: colors, glowValue: glowValue);
    }
  }

  int? getSectionFromPosition(Offset position, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final maxRadius = math.min(size.width, size.height) / 2 - 20;

    final dx = position.dx - center.dx;
    final dy = position.dy - center.dy;
    final distance = math.sqrt(dx * dx + dy * dy);

    // Center circle
    if (distance < maxRadius * 0.15) return -1;

    // Outside mandala
    if (distance > maxRadius) return null;

    var angle = math.atan2(dy, dx) * 180 / math.pi;
    angle = (angle + 360) % 360;

    // Calculate ring (0-3) based on distance from center circle edge
    final normalizedDistance = (distance - (maxRadius * 0.15)) / (maxRadius - (maxRadius * 0.15));
    final ring = (normalizedDistance * 4).floor().clamp(0, 3);

    // 12 segments per ring (30 degrees each)
    final segment = (angle / 30).floor() % 12;

    return ring * 12 + segment;
  }
}

// Flower Mandala Painter
class FlowerMandalaPainter extends CustomPainter {
  final Map<int, Color> sectionColors;
  final double glowValue;

  FlowerMandalaPainter({required this.sectionColors, required this.glowValue});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final maxRadius = math.min(size.width, size.height) / 2 - 20;
    final centerRadius = maxRadius * 0.15;

    // Background circle
    final bgPaint = Paint()
      ..color = Colors.grey.shade50
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, maxRadius, bgPaint);

    // Draw petals in rings
    const rings = 4;
    const segments = 12;

    for (int ring = 0; ring < rings; ring++) {
      final innerRadius = centerRadius + (ring / rings) * (maxRadius - centerRadius);
      final outerRadius = centerRadius + ((ring + 1) / rings) * (maxRadius - centerRadius);

      for (int segment = 0; segment < segments; segment++) {
        final sectionIndex = ring * segments + segment;
        final startAngle = (segment * 30 - 90) * math.pi / 180;
        final sweepAngle = 30 * math.pi / 180;

        final color = sectionColors[sectionIndex] ?? Colors.white;

        final paint = Paint()
          ..color = color
          ..style = PaintingStyle.fill;

        final path = Path();
        final rect = Rect.fromCircle(center: center, radius: outerRadius);
        path.arcTo(rect, startAngle, sweepAngle, false);

        final innerRect = Rect.fromCircle(center: center, radius: innerRadius);
        path.lineTo(
          center.dx + innerRadius * math.cos(startAngle + sweepAngle),
          center.dy + innerRadius * math.sin(startAngle + sweepAngle),
        );
        path.arcTo(innerRect, startAngle + sweepAngle, -sweepAngle, false);
        path.close();

        canvas.drawPath(path, paint);

        final borderPaint = Paint()
          ..color = Colors.grey.shade300
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.0;
        canvas.drawPath(path, borderPaint);
      }
    }

    // Center circle
    final centerColor = sectionColors[-1] ?? const Color(0xFF8B5CF6).withOpacity(0.3);
    final centerPaint = Paint()
      ..color = centerColor
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, centerRadius, centerPaint);

    // Draw decorative dots in center
    for (int i = 0; i < 8; i++) {
      final angle = (i * 45) * math.pi / 180;
      final dotRadius = centerRadius * 0.7;
      final x = center.dx + dotRadius * math.cos(angle);
      final y = center.dy + dotRadius * math.sin(angle);

      final dotPaint = Paint()
        ..color = Colors.white.withOpacity(0.7)
        ..style = PaintingStyle.fill;
      canvas.drawCircle(Offset(x, y), 3, dotPaint);
    }

    final centerBorderPaint = Paint()
      ..color = Colors.grey.shade400
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;
    canvas.drawCircle(center, centerRadius, centerBorderPaint);

    // Outer border with glow
    final outerGlowPaint = Paint()
      ..color = const Color(0xFF8B5CF6).withOpacity(0.1 + glowValue * 0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    canvas.drawCircle(center, maxRadius, outerGlowPaint);
  }

  @override
  bool shouldRepaint(FlowerMandalaPainter oldDelegate) {
    return oldDelegate.sectionColors != sectionColors ||
        oldDelegate.glowValue != glowValue;
  }
}

// Geometric Mandala Painter
class GeometricMandalaPainter extends FlowerMandalaPainter {
  GeometricMandalaPainter({
    required super.sectionColors,
    required super.glowValue,
  });
}

// Lotus Mandala Painter
class LotusMandalaPainter extends FlowerMandalaPainter {
  LotusMandalaPainter({
    required super.sectionColors,
    required super.glowValue,
  });
}

// Star Mandala Painter
class StarMandalaPainter extends FlowerMandalaPainter {
  StarMandalaPainter({
    required super.sectionColors,
    required super.glowValue,
  });
}
