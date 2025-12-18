import 'dart:io';

import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/constants/text_strings.dart';
import 'package:flutter/material.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';

import '../../../utils/theme/custom_theme/image_picker_input.dart';
import 'PrivacyPolicyScreen.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  bool _isObscured = true;
  bool _isObscured2 = true; // Password visibility state
  bool _isAgreePolicy = false; // Checkbox state
  String _selectedGender = "Male"; // Default value

  File? _image;
  final ImagePicker _picker = ImagePicker();

  final TextEditingController _dobController = TextEditingController();

  Future<void> _selectDate(BuildContext context) async {
    DateTime? pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime(2025), // Default date
      firstDate: DateTime(2000), // Earliest possible date
      lastDate: DateTime.now(), // Latest date (today)
    );

    if (pickedDate != null) {
      setState(() {
        _dobController.text = DateFormat('yyyy-MM-dd').format(pickedDate);
      });
    }
  }

  Future<void> _pickImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = JHelperFunctions.isDarkMode(context);
    return Scaffold(
      appBar: AppBar(),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(JSizes.defaultSpace),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // TITLE

              Text(
                JTexts.signupTitle,
                style: Theme.of(context).textTheme.headlineMedium,
              ),

              const SizedBox(
                height: JSizes.spaceBtwSections,
              ),
              // FORMS
              Form(
                  child: Column(
                children: [
                  Row(
                    children: [
                      // FIRST NAME
                      Expanded(
                        child: TextFormField(
                          expands: false,
                          decoration: const InputDecoration(
                              labelText: JTexts.firstName,
                              labelStyle: TextStyle(fontSize: 13.2),
                              prefixIcon: Icon(Iconsax.user)),
                        ),
                      ),
                      const SizedBox(
                        width: JSizes.spaceBtwInputFields,
                      ),
                      // LAST NAME
                      Expanded(
                        child: TextFormField(
                          expands: false,
                          decoration: const InputDecoration(
                              labelText: JTexts.lastName,
                              labelStyle: TextStyle(fontSize: 13.3),
                              prefixIcon: Icon(Iconsax.user)),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(
                    height: JSizes.spaceBtwInputFields,
                  ),
                  // EMAIL
                  TextFormField(
                    decoration: const InputDecoration(
                        labelText: JTexts.email,
                        labelStyle: TextStyle(fontSize: 13.3),
                        prefixIcon: Icon(Iconsax.direct)),
                  ),

                  const SizedBox(
                    height: JSizes.spaceBtwInputFields,
                  ),
                  // PASSWORD
                  TextFormField(
                    obscureText: _isObscured, // Toggle password visibility
                    decoration: InputDecoration(
                      prefixIcon: Icon(Iconsax.password_check),
                      labelText: JTexts.password,
                      labelStyle: const TextStyle(fontSize: 13.3),
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
                  ),

                  const SizedBox(
                    height: JSizes.spaceBtwInputFields,
                  ),
                  // CONFIRM PASSWORD
                  TextFormField(
                    obscureText: _isObscured2, // Toggle password visibility
                    decoration: InputDecoration(
                      prefixIcon: Icon(Iconsax.password_check),
                      labelText: JTexts.confirmpassword,
                      labelStyle: const TextStyle(fontSize: 13.3),
                      suffixIcon: IconButton(
                        icon: Icon(_isObscured2
                            ? Iconsax.eye_slash
                            : Iconsax.eye), // Toggle icon
                        onPressed: () {
                          setState(() {
                            _isObscured2 =
                                !_isObscured2; // Change visibility state
                          });
                        },
                      ),
                    ),
                  ),

                  const SizedBox(
                    height: JSizes.spaceBtwInputFields,
                  ),

                  // DATE PICKER
                  TextFormField(
                    controller: _dobController,
                    readOnly: true,
                    decoration: InputDecoration(
                      labelText: JTexts.dateofbirth,
                      labelStyle: const TextStyle(fontSize: 13.3),
                      prefixIcon: Icon(Iconsax.calendar_1),
                      border: OutlineInputBorder(),
                    ),
                    onTap: () => _selectDate(context),
                  ),

                  const SizedBox(
                    height: JSizes.spaceBtwInputFields,
                  ),

                  // GENDER
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        JTexts.gender, // Label for the radio buttons
                        style: TextStyle(fontSize: JSizes.fontSizeMd),
                      ),
                      Row(
                        children: [
                          Row(
                            children: [
                              Radio(
                                value: "Male",
                                groupValue: _selectedGender,
                                onChanged: (value) {
                                  setState(() {
                                    _selectedGender = value.toString();
                                  });
                                },
                              ),
                              Text("Male"),
                            ],
                          ),
                          const SizedBox(width: 20), // Space between options
                          Row(
                            children: [
                              Radio(
                                value: "Female",
                                groupValue: _selectedGender,
                                onChanged: (value) {
                                  setState(() {
                                    _selectedGender = value.toString();
                                  });
                                },
                              ),
                              Text("Female"),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),

                  const SizedBox(
                    height: JSizes.spaceBtwInputFields,
                  ),

                  ImagePickerInput(
                    label: "Upload ID",
                    onImagePicked: (File? image) {
                      // Handle the selected image
                    },
                  ),

                  const SizedBox(
                    height: JSizes.spaceBtwInputFields,
                  ),

                  // POLICY
                  Row(
                    children: [
                      SizedBox(
                        width: 24,
                        height: 24,
                        child: Checkbox(
                          value: _isAgreePolicy,
                          onChanged: (value) {
                            setState(() {
                              _isAgreePolicy = value!;
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: JSizes.spaceBtwItems),

                      // Clickable Text for Privacy Policy
                      Text.rich(
                        TextSpan(
                          children: [
                            TextSpan(
                              text: '${JTexts.iAgreeTo} ',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            WidgetSpan(
                              child: GestureDetector(
                                onTap: () {
                                  Get.to(() =>
                                      const PrivacyPolicyScreen()); // Navigate to Policy
                                },
                                child: Text(
                                  JTexts.privacyPolicy,
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodyMedium!
                                      .apply(
                                        color: dark
                                            ? JColors.white
                                            : JColors.primary,
                                        decoration: TextDecoration.underline,
                                        decorationColor: dark
                                            ? JColors.white
                                            : JColors.primary,
                                      ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: JSizes.spaceBtwSections),

                  // SIGN UP BTN
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                        onPressed: () {},
                        child: const Text(JTexts.createAccount)),
                  ),
                ],
              ))
            ],
          ),
        ),
      ),
    );
  }
}
