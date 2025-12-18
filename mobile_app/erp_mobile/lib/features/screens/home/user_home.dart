import 'package:carousel_slider/carousel_slider.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import 'package:shewear/features/screens/home/home_controller.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/features/screens/message/userchat.dart';
import '../../../common/widgets/appbar/home_appbar.dart';
import '../../../common/widgets/containers/circular_container.dart';
import '../../../common/widgets/containers/home_Category.dart';
import '../../../common/widgets/containers/search_container.dart';
import '../../../common/widgets/curved_edge/curved_edge_widget.dart';
import '../../../common/widgets/product_cards/productCard_vertical.dart';
import '../../../common/widgets/text/section_header.dart';
import '../../../utils/constants/image_strings.dart';
import 'package:shewear/features/screens/cart/addtocart.dart';

class UserHome extends StatelessWidget {
  const UserHome({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // HEADER
            JPrimaryHeaderContainer(
              child: Column(
                children: [
                  // APP BAR (WIDGET - HOME APPBAR)
                  JHomeAppBar(),

                  const SizedBox(
                    height: JSizes.spaceBtwSections,
                  ),

                  // SEARCH BAR
                  JSearchContainer(
                    hintText: "Search for products...",
                    onChanged: (query) {
                      print("User searched: $query");
                    },
                  ),
                  const SizedBox(
                    height: JSizes.spaceBtwSections,
                  ),

                  // TITLE TEXT
                  Padding(
                    padding: EdgeInsets.only(left: JSizes.defaultSpace),
                    child: Column(
                      children: [
                        JSectionHeading(
                          title: "Product Categories",
                          showActionBtn: false,
                          textColor: JColors.white,
                        ),
                        const SizedBox(
                          height: JSizes.spaceBtwItems,
                        ),

                        // CATEGORIES (MGA BILOG)
                        JHomeCategories()
                      ],
                    ),
                  ),
                  SizedBox(
                    height: JSizes.spaceBtwSections,
                  )
                ],
              ),
            ),

            Padding(
                padding: const EdgeInsets.all(JSizes.defaultSpace),
                child: Column(
                  children: [
                    JPromoSlider(
                      banners: [
                        JImages.banner1,
                        JImages.banner2,
                        JImages.banner3,
                      ],
                    ),
                    const SizedBox(
                      height: JSizes.spaceBtwSections,
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        JSectionHeading(
                          title: "Feature Products",
                          showActionBtn: false,
                          textColor: JColors.dark,
                        ),
                        const SizedBox(
                          height: JSizes.spaceBtwItems,
                        ),
                        SizedBox(
                          height: 280, // Adjust based on item height
                          child: ListView.builder(
                            scrollDirection:
                                Axis.horizontal, // Enables horizontal scrolling
                            itemCount: 4,
                            itemBuilder: (_, index) => Padding(
                              padding: EdgeInsets.only(
                                  right: JSizes.gridViewSpacing),
                              child: Padding(
                                padding: const EdgeInsets.all(2),
                                child: JProductCardVertical(),
                              ),
                            ),
                          ),
                        ),
                      ],
                    )
                  ],
                )),
          ],
        ),
      ),
    );
  }
}

class JPromoSlider extends StatelessWidget {
  const JPromoSlider({
    super.key,
    required this.banners,
  });

  final List<String> banners;

  @override
  Widget build(BuildContext context) {
    final HomeController controller = Get.put(HomeController());

    return Column(
      children: [
        //  CAROUSEL SLIDER
        CarouselSlider(
          options: CarouselOptions(
            height: 180, //  Adjusted height for better balance
            viewportFraction: 0.9, // Slightly reduced to add spacing effect
            autoPlay: true, // Auto-play for a dynamic feel
            autoPlayInterval: const Duration(seconds: 4),
            autoPlayCurve: Curves.fastOutSlowIn,
            enlargeCenterPage: true, //  Adds a zoom effect
            onPageChanged: (index, _) => controller.updatePageIndecator(index),
          ),
          items: banners
              .map((url) => JRoundedImage(
                  imageUrl: url, borderRadius: 16)) // Added rounded corners
              .toList(),
        ),

        const SizedBox(height: JSizes.spaceBtwItems),

        // 🔹 DOT INDICATORS
        Obx(() => _buildDotIndicators(controller.carouselCurrentIndex.value)),
      ],
    );
  }

  /// Builds Dot Indicators with a sleek transition effect
  Widget _buildDotIndicators(int currentIndex) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(
        banners.length,
        (index) => AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          margin: const EdgeInsets.symmetric(horizontal: 4),
          width: currentIndex == index ? 16 : 6, // 🔥 Enlarges active dot
          height: 6,
          decoration: BoxDecoration(
            color: currentIndex == index ? JColors.primary : JColors.grey,
            borderRadius: BorderRadius.circular(6),
          ),
        ),
      ),
    );
  }
}

class JRoundedImage extends StatelessWidget {
  const JRoundedImage({
    super.key,
    this.width,
    this.height,
    required this.imageUrl,
    this.applyImageRadius = true,
    this.border,
    this.backgroundColor = JColors.light,
    this.fit = BoxFit.cover,
    this.padding,
    this.isNetworkImage = false,
    this.onPressed,
    this.borderRadius = JSizes.md,
  });

  final double? width, height;
  final String imageUrl;
  final bool applyImageRadius; //IMAGE BORDER
  final BoxBorder? border;
  final Color backgroundColor;
  final BoxFit fit;
  final EdgeInsetsGeometry? padding;
  final bool isNetworkImage;
  final VoidCallback? onPressed;
  final double borderRadius;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: width,
        height: height,
        padding: padding,
        decoration: BoxDecoration(
          border: border,
          color: backgroundColor,
          borderRadius: BorderRadius.circular(borderRadius),
        ),
        child: ClipRRect(
            borderRadius: applyImageRadius
                ? BorderRadius.circular(borderRadius)
                : BorderRadius.zero,
            child: Image(
              image: isNetworkImage
                  ? NetworkImage(imageUrl)
                  : AssetImage(imageUrl) as ImageProvider,
              fit: fit,
            )),
      ),
    );
  }
}

// HOME CATEGORIES CONTAINER
class JHomeCategories extends StatelessWidget {
  const JHomeCategories({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final List<Map<String, String>> categories = [
      {"image": JImages.dressIcon, "title": "Dress"},
      {"image": JImages.topIcon, "title": "Blouse"},
      {"image": JImages.activeIcon, "title": "Activewear"},
      {"image": JImages.lingIcon, "title": "Lingerie"},
      {"image": JImages.jacketIcon, "title": "Jacket"},
      {"image": JImages.coatIcon, "title": "Coats"},
      {"image": JImages.shoesIcon, "title": "Watch"},
      {"image": JImages.necklaceIcon, "title": "Accessories"},
    ];

    return SizedBox(
      height: 80,
      child: ListView.builder(
        shrinkWrap: true,
        itemCount: categories.length,
        scrollDirection: Axis.horizontal,
        itemBuilder: (context, index) {
          // CATEGORIES WIDGET
          return JVerticalImageText(
            image: categories[index]["image"]!,
            title: categories[index]["title"]!,
            onTap: () {
              print("Clicked on ${categories[index]["title"]}");
            },
          );
        },
      ),
    );
  }
}

class JCountCounterIcon extends StatelessWidget {
  const JCountCounterIcon({
    super.key,
    required this.onPressed,
    required this.iconColor,
  });

  final VoidCallback onPressed;
  final Color iconColor;

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none, // Allows badges to overflow
      children: [
        // CART ICON
        IconButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (context) =>
                      const AddToCart()), // Navigate to AddToCart screen
            );
          },
          icon: Icon(
            CupertinoIcons.shopping_cart,
            color: iconColor,
          ),
        ),

        // CART COUNTER
        Positioned(
          right: 0,
          top:
              0, // Ensure the counter appears at the top-right corner of the cart icon
          child: Container(
            width: 18,
            height: 18,
            decoration: BoxDecoration(
              color: JColors.error.withOpacity(0.9),
              borderRadius: BorderRadius.circular(100),
            ),
            child: Center(
              child: Text(
                "3", // Replace with dynamic cart count
                style: Theme.of(context)
                    .textTheme
                    .labelLarge!
                    .apply(color: JColors.white, fontSizeFactor: 0.9),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// HEADER BUONG TOP SIDE
class JPrimaryHeaderContainer extends StatelessWidget {
  const JPrimaryHeaderContainer({
    super.key,
    required this.child,
  });

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return JCurvedWidget(
      child: Container(
        // BACKGROUND COLOR
        color: JColors.primary,
        padding: const EdgeInsets.all(0),
        child: Stack(
          children: [
            //CIRCLE DUN SA HEADER
            Positioned(
              top: -150,
              right: -250,
              child: JCircularContainer(
                backgroundcolor: JColors.textWhite.withOpacity(0.1),
              ),
            ),
            Positioned(
              top: 120,
              left: -200,
              child: JCircularContainer(
                backgroundcolor: JColors.textWhite.withOpacity(0.1),
              ),
            ),
            child
          ],
        ),
      ),
    );
  }
}
