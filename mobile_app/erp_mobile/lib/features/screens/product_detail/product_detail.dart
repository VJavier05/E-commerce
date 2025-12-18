import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:readmore/readmore.dart';
import 'package:shewear/common/widgets/appbar/appbar.dart';
import 'package:shewear/common/widgets/curved_edge/curved_edge_widget.dart';
import 'package:shewear/common/widgets/text/section_header.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/image_strings.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';

import '../../../common/widgets/appbar/bottom_add_to_cart.dart';
import '../../../common/widgets/shop_products/choice_chip_selector.dart';
import 'product_review.dart';

class ProductDetailScreen extends StatefulWidget {
  const ProductDetailScreen({super.key});

  @override
  _ProductDetailScreenState createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  int _selectedImageIndex = 0; // Tracks the selected thumbnail image
  String selectedColor = "Red"; // Default color
  String selectedSize = "Medium"; // Default size

  final List<String> productImages = [
    JImages.product1,
    JImages.product2,
    JImages.product3,
    JImages.product4,
  ];

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);

    return Scaffold(
      bottomNavigationBar: JBottomAddToCart(),
      backgroundColor: dark ? JColors.dark : Colors.white,
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            /// Product Image Section**
            JCurvedWidget(
              child: Container(
                height: 400,
                width: double.infinity,
                decoration: BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage(productImages[_selectedImageIndex]),
                    fit: BoxFit.cover,
                  ),
                ),
                child: Stack(
                  children: [
                    /// Image Thumbnails**
                    JAppBar(
                      showBackArrow: true,
                    ),
                    Positioned(
                      right: 0,
                      bottom: 20,
                      left: JSizes.defaultSpace,
                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: SizedBox(
                          height: 80,
                          child: ListView.separated(
                            scrollDirection: Axis.horizontal,
                            itemCount: productImages.length,
                            separatorBuilder: (_, __) =>
                                const SizedBox(width: JSizes.spaceBtwItems),
                            itemBuilder: (context, index) {
                              return GestureDetector(
                                onTap: () {
                                  setState(() {
                                    _selectedImageIndex = index;
                                  });
                                },
                                child: Container(
                                  width: 80,
                                  decoration: BoxDecoration(
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(
                                      color: _selectedImageIndex == index
                                          ? JColors.primary
                                          : Colors.transparent,
                                      width: 2,
                                    ),
                                    image: DecorationImage(
                                      image: AssetImage(productImages[index]),
                                      fit: BoxFit.cover,
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            /// Product Details Section**
            Padding(
              padding: const EdgeInsets.only(
                right: JSizes.defaultSpace,
                left: JSizes.defaultSpace,
                bottom: JSizes.defaultSpace,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Stylish Summer Dress",
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: dark ? Colors.white : Colors.black,
                    ),
                  ),
                  const SizedBox(height: 5),

                  /// Ratings**
                  Row(
                    children: [
                      const Icon(Icons.star, color: Colors.orange, size: 18),
                      const Icon(Icons.star, color: Colors.orange, size: 18),
                      const Icon(Icons.star, color: Colors.orange, size: 18),
                      const Icon(Icons.star, color: Colors.orange, size: 18),
                      const Icon(Icons.star_half,
                          color: Colors.orange, size: 18),
                      const SizedBox(width: 8),
                      Text(
                        "4.5 (1,234 reviews)",
                        style: TextStyle(
                          fontSize: 14,
                          color: dark ? Colors.white70 : Colors.grey,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 10),

                  /// Price**
                  Text(
                    "₱999.00",
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: JColors.primary,
                    ),
                  ),

                  const SizedBox(height: 10),

                  /// Description**
                  ///

                  ReadMoreText(
                    "This stylish summer dress is perfect for all occasions. Made from high-quality materials for ultimate comfort and durability. Made from high-quality materials for ultimate comfort and durability. Made from high-quality materials for ultimate comfort and durability. Made from high-quality materials for ultimate comfort and durability.",
                    trimLines: 2,
                    trimMode: TrimMode.Line,
                    trimCollapsedText: 'Show more',
                    trimExpandedText: 'Show less',
                    moreStyle: const TextStyle(
                        fontSize: 14, fontWeight: FontWeight.w800),
                    lessStyle: const TextStyle(
                        fontSize: 14, fontWeight: FontWeight.w800),
                  ),

                  // Text(
                  //   "This stylish summer dress is perfect for all occasions. Made from high-quality materials for ultimate comfort and durability. Made from high-quality materials for ultimate comfort and durability. Made from high-quality materials for ultimate comfort and durability. Made from high-quality materials for ultimate comfort and durability.",
                  //   style: TextStyle(
                  //     fontSize: 14,
                  //     color: dark ? Colors.white70 : Colors.black87,
                  //   ),
                  // ),

                  const SizedBox(height: JSizes.spaceBtwItems),

                  /// Size Selection**
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      /// 🟢 **Color Selection**
                      ChoiceChipSelector(
                        title: "Select Color",
                        options: ["Red", "Blue", "Orange"],
                        onSelected: (color) {
                          setState(() {
                            selectedColor = color;
                          });
                        },
                      ),

                      const SizedBox(height: JSizes.spaceBtwItems),

                      ///Size Selection**
                      ChoiceChipSelector(
                        title: "Select Size",
                        options: ["Small", "Medium", "Large"],
                        onSelected: (size) {
                          setState(() {
                            selectedSize = size;
                          });
                        },
                      ),
                    ],
                  ),

                  const SizedBox(height: JSizes.spaceBtwSections),

                  SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                          onPressed: () {}, child: Text("Checkout"))),

                  const SizedBox(height: JSizes.spaceBtwSections),
                  const Divider(),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      JSectionHeading(
                        title: "Reviews(199)",
                        showActionBtn: false,
                      ),
                      IconButton(
                          onPressed: () =>
                              Get.to(() => const ProductReviewScreen()),
                          icon: const Icon(
                            Icons.arrow_forward_ios,
                            size: 16,
                          ))
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
