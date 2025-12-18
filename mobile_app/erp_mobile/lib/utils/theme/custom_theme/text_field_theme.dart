import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';

class JTextFormFieldTheme {
  JTextFormFieldTheme._();

  static InputDecorationTheme lightInputDecorationTheme = InputDecorationTheme(
    errorMaxLines: 3,
    prefixIconColor: JColors.darkGrey,
    suffixIconColor: JColors.darkGrey,
    // constraints: const BoxConstraints.expand(height: JSizes.inputFieldHeight),
    labelStyle: const TextStyle()
        .copyWith(fontSize: JSizes.fontSizeMd, color: JColors.black),
    hintStyle: const TextStyle()
        .copyWith(fontSize: JSizes.fontSizeSm, color: JColors.black),
    errorStyle: const TextStyle().copyWith(fontStyle: FontStyle.normal),
    floatingLabelStyle:
        const TextStyle().copyWith(color: JColors.black.withOpacity(0.8)),
    border: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.grey),
    ),
    enabledBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.grey),
    ),
    focusedBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.dark),
    ),
    errorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.warning),
    ),
    focusedErrorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 2, color: JColors.warning),
    ),
  );

  static InputDecorationTheme darkInputDecorationTheme = InputDecorationTheme(
    errorMaxLines: 2,
    prefixIconColor: JColors.darkGrey,
    suffixIconColor: JColors.darkGrey,
    // constraints: const BoxConstraints.expand(height: JSizes.inputFieldHeight),
    labelStyle: const TextStyle()
        .copyWith(fontSize: JSizes.fontSizeMd, color: JColors.white),
    hintStyle: const TextStyle()
        .copyWith(fontSize: JSizes.fontSizeSm, color: JColors.white),
    floatingLabelStyle:
        const TextStyle().copyWith(color: JColors.white.withOpacity(0.8)),
    border: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.darkGrey),
    ),
    enabledBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.darkGrey),
    ),
    focusedBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.white),
    ),
    errorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: JColors.warning),
    ),
    focusedErrorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 2, color: JColors.warning),
    ),
  );
}
