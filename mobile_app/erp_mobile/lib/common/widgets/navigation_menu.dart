import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import 'package:shewear/features/screens/shop/user_shop.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';
import '../../features/screens/home/user_home.dart';
import '../../features/screens/setting/setting.dart';
import '../../features/screens/notification/user_notification.dart';

// Navigation bottom appbar
class NavigationMenu extends StatelessWidget {
  NavigationMenu({super.key});

  final NavigationController controller = Get.put(NavigationController());

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);

    return Scaffold(
      body: Obx(() => IndexedStack(
            index: controller.selectedIndex.value,
            children: controller.screens,
          )),
      bottomNavigationBar: Obx(
        () => NavigationBar(
          height: 70,
          elevation: 3,
          selectedIndex: controller.selectedIndex.value,
          onDestinationSelected: controller.onTabChanged,
          backgroundColor: dark ? JColors.black : Colors.white,
          indicatorColor: dark
              ? JColors.white.withOpacity(0.1)
              : JColors.black.withOpacity(0.1),
          destinations: const [
            NavigationDestination(icon: Icon(Iconsax.home), label: "Home"),
            NavigationDestination(icon: Icon(Iconsax.shop), label: "Store"),
            NavigationDestination(
                icon: Icon(Iconsax.notification), label: "Notifications"),
            NavigationDestination(icon: Icon(Iconsax.user), label: "Profile"),
          ],
        ),
      ),
    );
  }
}

// Destination Change here for screens
class NavigationController extends GetxController {
  final Rx<int> selectedIndex = 0.obs;

  final screens = [
    const UserHome(),
    const UserStore(),
    const UserNotification(),
    const SettingScreen(),
  ];

  void onTabChanged(int index) {
    selectedIndex.value = index;
  }
}
