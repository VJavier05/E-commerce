import 'package:flutter/material.dart';
import '../../constants/colors.dart';
import '../../constants/sizes.dart';

/* -- Light & Dark Elevated Button Themes -- */
class JElevatedButtonTheme {
  JElevatedButtonTheme._(); //To avoid creating instances

  /* -- Light Theme -- */
  static final lightElevatedButtonTheme = ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      elevation: 0,
      foregroundColor: JColors.light,
      backgroundColor: JColors.primary,
      disabledForegroundColor: JColors.darkGrey,
      disabledBackgroundColor: JColors.buttonDisabled,
      side: const BorderSide(color: JColors.primary),
      padding: const EdgeInsets.symmetric(vertical: JSizes.buttonHeight),
      textStyle: const TextStyle(
          fontSize: 16, color: JColors.textWhite, fontWeight: FontWeight.w600),
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(JSizes.buttonRadius)),
    ),
  );

  /* -- Dark Theme -- */
  static final darkElevatedButtonTheme = ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      elevation: 0,
      foregroundColor: JColors.light,
      backgroundColor: JColors.primary,
      disabledForegroundColor: JColors.darkGrey,
      disabledBackgroundColor: JColors.darkerGrey,
      side: const BorderSide(color: JColors.primary),
      padding: const EdgeInsets.symmetric(vertical: JSizes.buttonHeight),
      textStyle: const TextStyle(
          fontSize: 16, color: JColors.textWhite, fontWeight: FontWeight.w600),
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(JSizes.buttonRadius)),
    ),
  );
}
