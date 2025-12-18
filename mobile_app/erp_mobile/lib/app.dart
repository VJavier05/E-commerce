import 'package:shewear/utils/theme/theme.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'common/widgets/navigation_menu.dart';

// import 'features/authentication/screens/login/login.dart';

// import 'services/api_service.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      // PASS THE MODE DEPENDING ON THE SYSTEM
      themeMode: ThemeMode.system,
      theme: JAppTheme.lightTheme,
      darkTheme: JAppTheme.darkTheme,
      debugShowCheckedModeBanner: false,

      // Change here for debugging
      home: NavigationMenu(),
    );
  }
}


// NavigationMenu (USER HOME )


