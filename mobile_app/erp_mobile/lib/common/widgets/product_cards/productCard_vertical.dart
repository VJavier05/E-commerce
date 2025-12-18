import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:shewear/features/screens/home/user_home.dart';
import 'package:shewear/features/screens/product_detail/product_detail.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/image_strings.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';

import '../../../utils/constants/shadow.dart';

class JProductCardVertical extends StatelessWidget {
  const JProductCardVertical({super.key});

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);
    return GestureDetector(
      onTap: () => Get.to(() => const ProductDetailScreen()),
      child: Container(
        width: 180,
        decoration: BoxDecoration(
          boxShadow: [JShadowStyle.verticalProductShadow],
          borderRadius: BorderRadius.circular(JSizes.productImageRadius),
          color: dark ? JColors.darkGrey : JColors.white,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product Image with Favorite Button
            Stack(
              children: [
                JRoundedImage(
                  imageUrl: JImages.product3,
                  applyImageRadius: true,
                  fit: BoxFit.cover, // Ensures the image fills the entire space
                ),
              ],
            ),

            const SizedBox(height: 8),

            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Category
                  const Text(
                    "Skirt",
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: Colors.grey),
                  ),

                  // Product Title
                  const Text(
                    "Hand Made Sweater",
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  const SizedBox(height: 4),

                  // Rating Stars
                  Row(
                    children: List.generate(
                      5,
                      (index) => const Icon(Icons.star,
                          color: Colors.orange, size: 14),
                    ),
                  ),

                  const SizedBox(height: 4),

                  // Availability and Price
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Text(
                              "₱199.99",
                              style: TextStyle(
                                  fontSize: 18, fontWeight: FontWeight.bold),
                              overflow: TextOverflow.ellipsis,
                              softWrap: false,
                            ),
                          ],
                        ),
                      ),
                    ],
                  )
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class JCircularIcon extends StatelessWidget {
  const JCircularIcon({
    super.key,
    this.width,
    this.height,
    this.size = JSizes.lg,
    required this.icon,
    this.color,
    this.backgroundColor,
    this.onPressed,
  });

  final double? width, height, size;
  final IconData icon;
  final Color? color;
  final Color? backgroundColor;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
          color: backgroundColor != null
              ? backgroundColor!
              : JHelperFunctions.isDarkMode(context)
                  ? JColors.black.withOpacity(0.9)
                  : JColors.white.withOpacity(0.9),
          borderRadius: BorderRadius.circular(100)),
      child: IconButton(
          onPressed: onPressed, icon: Icon(icon, color: color, size: size)),
    );
  }
}
