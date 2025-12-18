import 'package:flutter/material.dart';
import 'package:readmore/readmore.dart';
import 'package:shewear/common/widgets/product_detail/star_rating.dart';
import 'package:shewear/utils/constants/sizes.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/image_strings.dart';

class UserReviewCard extends StatelessWidget {
  const UserReviewCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Divider(),
        const SizedBox(
          height: JSizes.spaceBtwItems,
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundImage: AssetImage(JImages.defaultProfile),
                ),
                const SizedBox(
                  width: JSizes.spaceBtwItems,
                ),
                Text(
                  "John Doe",
                  style: Theme.of(context).textTheme.titleLarge,
                )
              ],
            ),
            IconButton(onPressed: () {}, icon: const Icon(Icons.more_vert))
          ],
        ),
        const SizedBox(
          height: JSizes.spaceBtwItems,
        ),
        Row(
          children: [
            JRatingBarIndicator(rating: 4),
            const SizedBox(
              width: JSizes.spaceBtwItems,
            ),
            Text(
              "June 5, 2003",
              style: Theme.of(context).textTheme.bodyMedium,
            )
          ],
        ),
        const SizedBox(
          height: JSizes.spaceBtwItems,
        ),
        ReadMoreText(
          " Amazing product!!! That's what I was looking for – excellent quality and fast delivery. Impressed with [Product Name] – its quality, style, features, and worth every penny.",
          trimLines: 2,
          trimExpandedText: " Show Less",
          trimCollapsedText: " Show More",
          trimMode: TrimMode.Line,
          moreStyle: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: JColors.primary),
          lessStyle: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: JColors.primary),
        ),
        const SizedBox(
          height: JSizes.spaceBtwItems,
        ),
      ],
    );
  }
}
