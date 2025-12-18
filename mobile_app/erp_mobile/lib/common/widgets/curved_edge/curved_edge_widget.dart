import 'package:flutter/material.dart';

import 'curved_edge.dart';

class JCurvedWidget extends StatelessWidget {
  const JCurvedWidget({
    super.key,
    this.child,
  });

  final Widget? child;

  @override
  Widget build(BuildContext context) {
    return ClipPath(
      clipper: JCustomCurvedEdge(),
      child: child,
    );
  }
}
