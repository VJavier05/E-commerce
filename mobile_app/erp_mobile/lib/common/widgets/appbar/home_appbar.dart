import 'package:flutter/material.dart';

import '../../../features/screens/home/user_home.dart';
import '../../../utils/constants/colors.dart';
import '../../../utils/constants/text_strings.dart';
import 'appbar.dart';

class JHomeAppBar extends StatelessWidget {
  const JHomeAppBar({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return JAppBar(
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(JTexts.homeAppbarTitle,
              style: Theme.of(context)
                  .textTheme
                  .labelMedium!
                  .apply(color: JColors.grey)),
          Text(JTexts.homeAppbarSubTitle,
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall!
                  .apply(color: JColors.white)),
        ],
      ),
      actions: [
        JCountCounterIcon(
          onPressed: () {},
          iconColor: JColors.white,
        )
      ],
    );
  }
}
