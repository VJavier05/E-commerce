import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';

class ImagePickerInput extends StatefulWidget {
  final String label;
  final Function(File?) onImagePicked;

  const ImagePickerInput({
    super.key,
    required this.label,
    required this.onImagePicked,
  });

  @override
  _ImagePickerInputState createState() => _ImagePickerInputState();
}

class _ImagePickerInputState extends State<ImagePickerInput> {
  File? _image;
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
      });
      widget.onImagePicked(_image);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label
        Text(
          widget.label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontSize: JSizes.fontSizeMd,
                color: JColors.black,
              ),
        ),
        const SizedBox(height: 8),

        // Image Picker Input Field
        InkWell(
          onTap: _pickImage,
          child: InputDecorator(
            decoration: InputDecoration(
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
                borderSide: const BorderSide(width: 1, color: JColors.grey),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
                borderSide: const BorderSide(width: 1, color: JColors.grey),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(JSizes.inputFieldRadius),
                borderSide: const BorderSide(width: 1, color: JColors.dark),
              ),
              prefixIcon: Icon(Iconsax.gallery, color: JColors.darkGrey),
              suffixIcon: _image != null
                  ? const Icon(Icons.check_circle, color: Colors.green)
                  : null,
              hintText: "Select an image",
              hintStyle:
                  TextStyle(fontSize: JSizes.fontSizeSm, color: JColors.black),
            ),
            child: _image != null
                ? Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.file(
                          _image!,
                          width: 50,
                          height: 50,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          "Image Selected",
                          style: TextStyle(fontSize: 14, color: JColors.black),
                        ),
                      ),
                    ],
                  )
                : Text(
                    "Tap to select an image",
                    style: TextStyle(
                        color: JColors.darkGrey, fontSize: JSizes.fontSizeSm),
                  ),
          ),
        ),
      ],
    );
  }
}
