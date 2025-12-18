import 'package:flutter/material.dart';

class JSectionHeading extends StatelessWidget {
  const JSectionHeading({
    super.key,
    this.textColor,
    this.showActionBtn = false,
    required this.title,
    this.buttonTitle = "Button Title",
    this.onPressed,
  });

  final Color? textColor;
  final bool showActionBtn;
  final String title, buttonTitle;
  final void Function()? onPressed;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          title,
          style: Theme.of(context)
              .textTheme
              .headlineSmall!
              .apply(color: textColor),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        if (showActionBtn)
          TextButton(onPressed: onPressed, child: Text(buttonTitle))
      ],
    );
  }
}
