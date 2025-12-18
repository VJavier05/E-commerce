import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/image_strings.dart';

class JUserProfile extends StatelessWidget {
  const JUserProfile({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundImage: AssetImage(JImages.defaultProfile),
      ),
      title: Text(
        "Vincent Angelo Javier",
        style: Theme.of(context)
            .textTheme
            .headlineSmall!
            .apply(color: JColors.white),
      ),
      subtitle: Text(
        "angelojavierjj@gmail.com",
        style:
            Theme.of(context).textTheme.bodyMedium!.apply(color: JColors.white),
      ),
      trailing: IconButton(
          onPressed: () {},
          icon: const Icon(
            Iconsax.edit,
            color: JColors.white,
          )),
    );
  }
}
