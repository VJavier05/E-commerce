import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/constants/text_strings.dart';

import 'reset_password.dart';

class ForgotPassword extends StatelessWidget {
  const ForgotPassword({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: Padding(
        padding: EdgeInsets.all(JSizes.defaultSpace),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // HEADING

            Text(
              JTexts.forgetPasswordTitle,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(
              height: JSizes.spaceBtwItems,
            ),
            Text(
              JTexts.forgetPasswordSubTitle,
              style: Theme.of(context).textTheme.labelMedium,
            ),
            const SizedBox(
              height: JSizes.spaceBtwSections * 2,
            ),

            // EMAIL FORGET PASS
            TextFormField(
              decoration: const InputDecoration(
                  labelText: JTexts.email,
                  prefixIcon: Icon(Iconsax.direct_right)),
            ),

            const SizedBox(
              height: JSizes.spaceBtwSections,
            ),

            // SUBMIT BTN
            SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                    onPressed: () => Get.off(() => const ResetPassword()),
                    child: Text(JTexts.submit)))
          ],
        ),
      ),
    );
  }
}
