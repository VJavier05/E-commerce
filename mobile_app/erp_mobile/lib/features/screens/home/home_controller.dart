import 'package:get/get.dart';

// FOR CONTROLLING CAROUSEL DOTS
class HomeController extends GetxController {
  static HomeController get Instance => Get.find();

  final carouselCurrentIndex = 0.obs;

  void updatePageIndecator(index) {
    carouselCurrentIndex.value = index;
  }
}
