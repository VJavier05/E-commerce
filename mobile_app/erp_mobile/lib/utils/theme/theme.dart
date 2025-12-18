import 'package:shewear/utils/theme/custom_theme/appbar_theme.dart';
import 'package:shewear/utils/theme/custom_theme/bottom_sheet_theme.dart';
import 'package:shewear/utils/theme/custom_theme/checkbox_theme.dart';
import 'package:shewear/utils/theme/custom_theme/chip_theme.dart';
import 'package:shewear/utils/theme/custom_theme/elevated_button_theme.dart';
import 'package:shewear/utils/theme/custom_theme/outlined_button_theme.dart';
import 'package:shewear/utils/theme/custom_theme/text_field_theme.dart';
import 'package:shewear/utils/theme/custom_theme/text_theme.dart';
import 'package:flutter/material.dart';

import '../constants/colors.dart';

class JAppTheme {
  JAppTheme._();

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    fontFamily: 'Poppins',
    disabledColor: JColors.grey,
    brightness: Brightness.light,
    primaryColor: JColors.primary,
    textTheme: JTextTheme.lightTextTheme,
    chipTheme: JChipTheme.lightChipTheme,
    scaffoldBackgroundColor: JColors.white,
    appBarTheme: JAppBarTheme.lightAppBarTheme,
    checkboxTheme: JCheckboxTheme.lightCheckboxTheme,
    bottomSheetTheme: JBottomSheetTheme.lightBottomSheetTheme,
    elevatedButtonTheme: JElevatedButtonTheme.lightElevatedButtonTheme,
    outlinedButtonTheme: JOutlinedButtonTheme.lightOutlinedButtonTheme,
    inputDecorationTheme: JTextFormFieldTheme.lightInputDecorationTheme,
  );

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    fontFamily: 'Poppins',
    disabledColor: JColors.grey,
    brightness: Brightness.dark,
    primaryColor: JColors.primary,
    textTheme: JTextTheme.darkTextTheme,
    chipTheme: JChipTheme.darkChipTheme,
    scaffoldBackgroundColor: JColors.black,
    appBarTheme: JAppBarTheme.darkAppBarTheme,
    checkboxTheme: JCheckboxTheme.darkCheckboxTheme,
    bottomSheetTheme: JBottomSheetTheme.darkBottomSheetTheme,
    elevatedButtonTheme: JElevatedButtonTheme.darkElevatedButtonTheme,
    outlinedButtonTheme: JOutlinedButtonTheme.darkOutlinedButtonTheme,
    inputDecorationTheme: JTextFormFieldTheme.darkInputDecorationTheme,
  );
}
