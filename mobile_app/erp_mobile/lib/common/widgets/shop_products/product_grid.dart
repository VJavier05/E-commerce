import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/sizes.dart';

class JProductGrid extends StatelessWidget {
  final int itemCount;
  final bool shrinkWrap;
  final ScrollPhysics? physics;
  final Widget? Function(BuildContext, int) itemBuilder;

  const JProductGrid({
    super.key,
    required this.itemCount,
    this.shrinkWrap = true,
    this.physics = const NeverScrollableScrollPhysics(),
    required this.itemBuilder,
  });

  @override
  Widget build(BuildContext context) {
    final double screenWidth = MediaQuery.of(context).size.width;
    final int crossAxisCount =
        (screenWidth ~/ 180).clamp(2, 4); // Adjusts column count
    final double itemHeight =
        screenWidth / crossAxisCount * 1.4; // Dynamic height

    return GridView.builder(
      itemCount: itemCount,
      shrinkWrap: shrinkWrap,
      physics: physics,
      padding: const EdgeInsets.all(JSizes.gridViewSpacing),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: JSizes.gridViewSpacing,
        crossAxisSpacing: JSizes.gridViewSpacing,
        mainAxisExtent: itemHeight,
      ),
      itemBuilder: itemBuilder,
    );
  }
}
