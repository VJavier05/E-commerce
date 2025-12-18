import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/device/device_utility.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';

class JTabBar extends StatelessWidget implements PreferredSizeWidget {
  final List<Tab> tabs;

  const JTabBar({
    super.key,
    required this.tabs,
  });

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);
    return Material(
      color: dark ? JColors.black : JColors.white,
      child: TabBar(
        tabAlignment: TabAlignment.start,
        isScrollable: true,
        indicatorColor: JColors.primary, // Change as needed
        labelColor: dark ? JColors.white : JColors.primary,
        tabs: tabs,
      ),
    );
  }

  @override
  Size get preferredSize =>
      Size.fromHeight(JDeviceUtils.getAppBarHeight()); // Define height
}
