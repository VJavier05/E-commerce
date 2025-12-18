import 'package:flutter/material.dart';
import 'package:shewear/common/widgets/product_cards/productCard_vertical.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';

class JBottomAddToCart extends StatelessWidget {
  const JBottomAddToCart({super.key});

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);
    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: JSizes.defaultSpace, vertical: JSizes.defaultSpace / 2),
      decoration: BoxDecoration(
          color: dark ? JColors.darkGrey : JColors.light,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(JSizes.cardRadiusLg),
            topRight: Radius.circular(JSizes.cardRadiusLg),
          )),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              JCircularIcon(
                icon: Icons.remove,
                backgroundColor: JColors.darkGrey,
                width: 40,
                height: 40,
                color: JColors.white,
              ),
              const SizedBox(
                width: JSizes.spaceBtwItems,
              ),
              Text(
                "2",
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(
                width: JSizes.spaceBtwItems,
              ),
              JCircularIcon(
                icon: Icons.add,
                backgroundColor: JColors.black,
                width: 40,
                height: 40,
                color: JColors.white,
              ),
            ],
          ),
          ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.all(JSizes.md),
                backgroundColor: JColors.black,
                side: const BorderSide(color: JColors.black)),
            child: const Text("Add to Cart"),
          ),
        ],
      ),
    );
  }
}
