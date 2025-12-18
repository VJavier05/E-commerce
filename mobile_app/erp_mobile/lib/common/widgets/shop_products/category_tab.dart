import 'package:flutter/material.dart';
import 'package:shewear/common/widgets/product_cards/productCard_vertical.dart';
import 'package:shewear/common/widgets/text/section_header.dart';

import '../../../utils/constants/sizes.dart';
import 'product_grid.dart';

// GRID CONTENT ONLY
class JCategorytab extends StatelessWidget {
  const JCategorytab({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return ListView(
        shrinkWrap: true,
        physics: NeverScrollableScrollPhysics(),
        children: [
          Padding(
            padding: const EdgeInsets.all(JSizes.defaultSpace),
            child: Column(
              children: [
                JSectionHeading(title: title),
                const SizedBox(
                  height: JSizes.spaceBtwItems,
                ),
                JProductGrid(
                  itemCount: 4,
                  itemBuilder: (_, index) =>
                      SizedBox(child: const JProductCardVertical()),
                ),
                const SizedBox(
                  height: JSizes.spaceBtwSections,
                )
              ],
            ),
          ),
        ]);
  }
}
