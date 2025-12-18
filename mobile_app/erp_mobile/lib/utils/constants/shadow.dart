import 'package:flutter/cupertino.dart';

class JShadowStyle {
  static final verticalProductShadow = BoxShadow(
    color: const Color.fromRGBO(60, 64, 67, 0.3), // rgba(60, 64, 67, 0.3)
    blurRadius: 2, // Similar to the first shadow's blur effect
    spreadRadius: 0, // No extra spread
    offset: const Offset(0, 1), // (0px 1px)
  );

  static final horizontalProductShadow = BoxShadow(
    color: const Color.fromRGBO(60, 64, 67, 0.15), // rgba(60, 64, 67, 0.15)
    blurRadius: 3, // A bit larger blur
    spreadRadius: 1, // Small spread effect
    offset: const Offset(0, 1), // (0px 1px)
  );
}
