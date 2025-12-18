import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';

import '../../../utils/constants/colors.dart';

class JRatingBarIndicator extends StatelessWidget {
  const JRatingBarIndicator({
    super.key,
    required this.rating,
  });

  final double rating;

  @override
  Widget build(BuildContext context) {
    return RatingBarIndicator(
        rating: rating,
        itemSize: 20,
        unratedColor: JColors.grey,
        itemBuilder: (_, __) => Icon(
              Icons.star,
              color: JColors.primary,
            ));
  }
}
