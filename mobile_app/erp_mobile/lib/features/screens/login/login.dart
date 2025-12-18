// import 'package:erp_mobile/utils/constants/colors.dart';
import 'package:shewear/common/widgets/navigation_menu.dart';
import 'package:shewear/features/screens/signup.widget/signup.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/image_strings.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/constants/text_strings.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../common/styles/spacing_style.dart';
import '../../../utils/http/http_client.dart';
import '../../../utils/validators/validation.dart';
import '../forgot_password/forgot_password.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isObscured = true; // Password visibility state
  bool _isRememberMe = false; // Checkbox state
  bool _isLoading = false; // Loading state
  String? _errorMessage; // Store login error messages

  final _formKey = GlobalKey<FormState>(); // Form Key
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      Map<String, dynamic> response = await JHttpHelper.post(
        "api/login",
        {
          "email": _emailController.text.trim(),
          "password": _passwordController.text.trim(),
        },
      );

      if (response.containsKey("message")) {
        if (response["message"] == "Login successful") {
          print("✅ Login successful! User ID: ${response['user_id']}");

          // Extract user role and JWT token
          String userRole = response['role'];
          String accessToken = response['access_token']; // Get the JWT token

          // Store JWT Token for future API requests
          SharedPreferences prefs = await SharedPreferences.getInstance();
          await prefs.setString("access_token", accessToken);

          // Navigate based on role
          if (userRole == "admin") {
            print("ADMIN");
            // Get.offAll(() => AdminDashboard());
          } else if (userRole == "seller") {
            // Get.offAll(() => SellerDashboard());
            print("SELLER");
          } else if (userRole == "courier") {
            // Get.offAll(() => CourierDashboard());
            print("COURIER");
          } else {
            Get.offAll(() => NavigationMenu());
            print("USER");
          }

          return;
        } else {
          // Wrong credentials
          setState(() {
            _errorMessage = response["message"];
          });
          return;
        }
      }

      // Handle unexpected response
      setState(() {
        _errorMessage = "Unexpected server response.";
      });
    } catch (e) {
      setState(() {
        _errorMessage = "Network error: $e";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);

    return Scaffold(
      body: SingleChildScrollView(
        child: Padding(
          padding: JSpacingStyle.paddingwithAppbarheight,
          child: Column(
            children: [
              // LOGO, TITLE AND SUBTITLE

              // HEADER
              Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // LOGO
                  SizedBox(
                    height: 100,
                    width: 200,
                    child: Image.asset(
                      dark ? JImages.shewearLogoLight : JImages.shewearLogoDark,
                      fit: BoxFit
                          .cover, // Maintains aspect ratio but crops if needed
                    ),
                  ),

                  // WELCOME BACK TEXT
                  Text(
                    JTexts.loginTitle,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(
                    height: JSizes.sm,
                  ),

                  // LOGIN SUBTEXT
                  Text(
                    JTexts.loginSubTitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
              Form(
                key: _formKey,
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                      vertical: JSizes.spaceBtwSections),
                  child: Column(
                    children: [
                      // EMAIL INPUT
                      TextFormField(
                        controller: _emailController,
                        decoration: InputDecoration(
                            prefixIcon: Icon(Iconsax.direct_right),
                            labelText: JTexts.email),
                        validator: JValidator.validateEmail, // Using validator
                      ),
                      const SizedBox(height: JSizes.spaceBtwInputFields),

                      // PASSWORD INPUT
                      TextFormField(
                        controller: _passwordController,
                        obscureText: _isObscured, // Toggle password visibility
                        decoration: InputDecoration(
                          prefixIcon: Icon(Iconsax.password_check),
                          labelText: JTexts.password,
                          suffixIcon: IconButton(
                            icon: Icon(_isObscured
                                ? Iconsax.eye_slash
                                : Iconsax.eye), // Toggle icon
                            onPressed: () {
                              setState(() {
                                _isObscured =
                                    !_isObscured; // Change visibility state
                              });
                            },
                          ),
                        ),
                        validator:
                            JValidator.validatePasswordEmpty, // Using validator
                      ),

                      const SizedBox(height: JSizes.spaceBtwInputFields / 2),

                      // REMEMBER ME & FORGET PASS
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          //  REMEMBER ME
                          Expanded(
                            child: Row(
                              children: [
                                Checkbox(
                                  value:
                                      _isRememberMe, // Use the state variable
                                  onChanged: (value) {
                                    setState(() {
                                      _isRememberMe =
                                          value!; // Update the state
                                    });
                                  },
                                ),
                                Flexible(child: const Text(JTexts.rememberMe)),
                              ],
                            ),
                          ),

                          // FORGET PASSWORD
                          TextButton(
                              onPressed: () =>
                                  Get.to(() => const ForgotPassword()),
                              child: Text(JTexts.forgetPassword))
                        ],
                      ),
                      const SizedBox(height: JSizes.spaceBtwSections),
                      if (_errorMessage != null)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 2.0),
                          child: Text(
                            _errorMessage!,
                            style:
                                TextStyle(color: JColors.error, fontSize: 14),
                          ),
                        ),

                      // LOGIN BTN
                      SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: _isLoading
                                ? null
                                : _submitForm, // Disable when loading
                            child: _isLoading
                                ? const SizedBox(
                                    width: 24,
                                    height: 24,
                                    child: CircularProgressIndicator(
                                      color: JColors
                                          .primary, // Match the button text color
                                      strokeWidth: 2,
                                    ),
                                  )
                                : Text(JTexts.signIn),
                          )),
                      const SizedBox(height: JSizes.spaceBtwItems),

                      // CREATE ACCOUNT BTN
                      SizedBox(
                          width: double.infinity,
                          child: OutlinedButton(
                              onPressed: () =>
                                  Get.to(() => const SignupScreen()),
                              child: Text(JTexts.createAccount))),
                    ],
                  ),
                ),
              ),
              // DIVIDER
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Flexible(
                    child: Divider(
                      color: dark ? JColors.darkGrey : JColors.grey,
                      thickness: 0.5,
                      indent: 60,
                      endIndent: 5,
                    ),
                  ),
                  Text(
                    JTexts.orJoinUs.capitalize!,
                    style: Theme.of(context).textTheme.labelMedium,
                  ),
                  Flexible(
                    child: Divider(
                      color: dark ? JColors.darkGrey : JColors.grey,
                      thickness: 0.5,
                      indent: 5,
                      endIndent: 60,
                    ),
                  ),
                ],
              ),
              const SizedBox(
                height: JSizes.spaceBtwSections,
              ),

              // REGISTER AS SELLER
              SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                      onPressed: () {}, child: Text(JTexts.createSeller)))
            ],
          ),
        ),
      ),
    );
  }
}
