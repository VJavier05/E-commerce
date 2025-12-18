import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';

class ChoiceChipSelector extends StatefulWidget {
  final String title;
  final List<String> options;
  final ValueChanged<String> onSelected;

  const ChoiceChipSelector({
    super.key,
    required this.title,
    required this.options,
    required this.onSelected,
  });

  @override
  _ChoiceChipSelectorState createState() => _ChoiceChipSelectorState();
}

class _ChoiceChipSelectorState extends State<ChoiceChipSelector> {
  int _selectedIndex = 0; // Default selection index

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        /// 🔹 **Title (e.g., "Select Color" or "Select Size")**
        Text(widget.title,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),

        const SizedBox(height: 8),

        /// Choice Chips
        Wrap(
          spacing: 10,
          children: List.generate(widget.options.length, (index) {
            return ChoiceChip(
              label: Text(
                widget.options[index],
                style: TextStyle(
                  color: _selectedIndex == index ? Colors.white : Colors.black,
                ),
              ),
              selected: _selectedIndex == index,
              selectedColor: JColors.primary, // Highlighted color
              backgroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                side: BorderSide(
                  color: _selectedIndex == index
                      ? JColors.primary
                      : Colors.grey, // Border color
                  width: 1.5, // Border width
                ),
                borderRadius: BorderRadius.circular(10), // Rounded border
              ),
              onSelected: (selected) {
                setState(() {
                  _selectedIndex = index;
                  widget
                      .onSelected(widget.options[index]); // Pass selected value
                });
              },
            );
          }),
        ),
      ],
    );
  }
}
