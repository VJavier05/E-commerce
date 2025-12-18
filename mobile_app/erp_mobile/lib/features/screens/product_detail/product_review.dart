import 'package:flutter/material.dart';
import 'package:shewear/common/widgets/appbar/appbar.dart';
import 'package:shewear/utils/constants/sizes.dart';

import '../../../common/widgets/product_detail/rating_topside.dart';
import '../../../common/widgets/product_detail/star_rating.dart';
import '../../../common/widgets/product_detail/user_ReviewCard.dart';

class ProductReviewScreen extends StatelessWidget {
  const ProductReviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: JAppBar(
        title: Text("Reviews & Ratings"),
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(JSizes.defaultSpace),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                  "Ratings and reviews are verified and are from people who are use tha same type of device that you use"),
              SizedBox(
                height: JSizes.spaceBtwItems,
              ),
              JOverallProductRating(),
              JRatingBarIndicator(
                rating: 3.5,
              ),
              Text(
                "12,611",
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(
                height: JSizes.spaceBtwSections,
              ),
              UserReviewCard(),
              UserReviewCard(),
            ],
          ),
        ),
      ),
    );
  }
}
