import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/device/device_utility.dart';
import '../../../utils/helpers/helper_functions.dart';

class JSearchContainer extends StatelessWidget {
  const JSearchContainer(
      {super.key,
      this.hintText = "Search...",
      this.icon = Iconsax.search_normal,
      this.showBackground = true,
      this.showBorder = true,
      this.onChanged,
      this.padding =
          const EdgeInsets.symmetric(horizontal: JSizes.defaultSpace)});

  final String hintText;
  final IconData? icon;
  final bool showBackground, showBorder;
  final ValueChanged<String>? onChanged; // Callback for user input changes
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);

    return Padding(
      padding: padding,
      child: Container(
        width: JDeviceUtils.getScreenWidth(context),
        padding: const EdgeInsets.symmetric(horizontal: JSizes.md),
        decoration: BoxDecoration(
          color: showBackground
              ? dark
                  ? JColors.dark
                  : JColors.light
              : Colors.transparent,
          borderRadius: BorderRadius.circular(JSizes.cardRadiusLg),
          border: showBorder ? Border.all(color: JColors.grey) : null,
        ),
        child: Row(
          children: [
            Icon(icon, color: JColors.darkerGrey), // Search icon
            const SizedBox(width: JSizes.spaceBtwItems),
            Expanded(
              child: TextField(
                onChanged: onChanged, // Pass user input to the callback
                style: Theme.of(context).textTheme.bodyMedium,
                decoration: InputDecoration(
                  hintText: hintText,
                  hintStyle: TextStyle(color: JColors.darkerGrey),
                  border: InputBorder.none,
                  enabledBorder: InputBorder.none,
                  disabledBorder: InputBorder.none,
                  focusedBorder: InputBorder.none,
                  errorBorder: InputBorder.none,
                  focusedErrorBorder: InputBorder.none,
                  // Remove default borders
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
