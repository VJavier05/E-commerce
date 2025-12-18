import 'package:shewear/features/authentication/controllers.onboarding/onboarding_controller.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/image_strings.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/constants/text_strings.dart';
import 'package:shewear/utils/device/device_utility.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:iconsax/iconsax.dart';

// import 'package:get/get.dart';

class OnBoardingScreen extends StatelessWidget {
  const OnBoardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(OnBoardingController());

    return Scaffold(
      body: Stack(
        children: [
          // HORIZONTAL SCROLLABLE PAGE
          PageView(
            controller: controller.pageController,
            onPageChanged: controller.updatePageIndicator,
            children: const [
              OnBoardingPage(
                image: JImages.onBoardingImage1,
                title: JTexts.onBoardingTitle1,
                subtitle: JTexts.onBoardingSubTitle1,
              ),
              OnBoardingPage(
                image: JImages.onBoardingImage2,
                title: JTexts.onBoardingTitle2,
                subtitle: JTexts.onBoardingSubTitle2,
              ),
              OnBoardingPage(
                image: JImages.onBoardingImage3,
                title: JTexts.onBoardingTitle3,
                subtitle: JTexts.onBoardingSubTitle3,
              ),
            ],
          ),

          Positioned(
              top: JDeviceUtils.getAppBarHeight(),
              right: JSizes.defaultSpace,
              child: TextButton(
                  onPressed: () => OnBoardingController.instance.skipPage(),
                  child: const Text("Skip"))),

          OnBoardingDot(),

          OnBoardingNext(),
        ],
      ),
    );
  }
}

class OnBoardingNext extends StatelessWidget {
  const OnBoardingNext({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
        right: JSizes.defaultSpace,
        bottom: JDeviceUtils.getBottomNavigationBarHeight(),
        child: ElevatedButton(
            onPressed: () => OnBoardingController.instance.nextPage(),
            style: ElevatedButton.styleFrom(
                shape: CircleBorder(), backgroundColor: JColors.primary),
            child: Icon(
              Iconsax.arrow_right_3,
              color: Colors.white,
            )));
  }
}

class OnBoardingDot extends StatelessWidget {
  const OnBoardingDot({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);
    final controller = OnBoardingController.instance;

    return Positioned(
        bottom: JDeviceUtils.getBottomNavigationBarHeight() + 25,
        left: JSizes.defaultSpace,
        child: SmoothPageIndicator(
          controller: controller.pageController,
          onDotClicked: controller.dotNavigationClick,
          count: 3,
          effect: ExpandingDotsEffect(
              activeDotColor: dark ? JColors.light : JColors.dark,
              dotHeight: 6,
              dotWidth: 16),
        ));
  }
}

class OnBoardingPage extends StatelessWidget {
  const OnBoardingPage({
    super.key,
    required this.image,
    required this.title,
    required this.subtitle,
  });

  final String image, title, subtitle;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(JSizes.defaultSpace),
      child: Column(
        children: [
          Image(
            // WIDTH 80 OF SCREEN
            width: JHelperFunctions.screenWidth() * 0.8,
            // HEIGHT OF 60 SCREENS
            height: JHelperFunctions.screenHeight() * 0.6,
            image: AssetImage(image),
          ),
          Text(
            title,
            style: Theme.of(context).textTheme.headlineMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(
            height: JSizes.spaceBtwItems,
          ),
          Text(
            subtitle,
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
