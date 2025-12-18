// Function to update the displayed price based on selected color and size
function updatePrice() {
    // Get the currently selected color and size elements
    let selectedColor = document.querySelector('input[name="colorOptions"]:checked');
    let selectedSizeGroup = document.querySelector(`.size-group[data-color="${selectedColor.value}"]`);
    let selectedSize = selectedSizeGroup ? selectedSizeGroup.querySelector('input[name^="sizeOptions"]:checked') : null;
    let priceDisplay = document.getElementById('product-price');

    if (selectedColor && selectedSize) {
        // Get the price from the selected size option
        let sizePrice = parseFloat(selectedSize.getAttribute('data-price'));
        if (!isNaN(sizePrice)) {
            priceDisplay.textContent = sizePrice.toFixed(2);
        }
    } else {
        // If no size is selected, reset the price display
        priceDisplay.textContent = '0.00';
    }
}

// Function to initialize the size visibility based on the selected color
function initializeSizeGroups() {
    // Get the currently selected color
    let selectedColor = document.querySelector('input[name="colorOptions"]:checked');

    if (selectedColor) {
        // Loop through each size group and set the visibility based on the selected color
        document.querySelectorAll('.size-group').forEach(group => {
            group.classList.toggle('visible', group.dataset.color === selectedColor.value);
            group.classList.toggle('hidden', group.dataset.color !== selectedColor.value);

            // Clear any selected size within hidden size groups
            if (group.dataset.color !== selectedColor.value) {
                group.querySelectorAll('input[name^="sizeOptions"]').forEach(sizeOption => {
                    sizeOption.checked = false; // Uncheck the sizes that belong to the hidden groups
                });
            }
        });
    }
}

// Event listeners for color and size changes
document.querySelectorAll('input[name="colorOptions"]').forEach(option => {
    option.addEventListener('change', () => {
        // Update the visibility of size options when the color changes
        initializeSizeGroups();
        // Update the price when the color changes
        updatePrice();
    });
});

document.querySelectorAll('.size-option').forEach(option => {
    option.addEventListener('change', updatePrice);
});

// Initialize size groups and price on page load
initializeSizeGroups();
updatePrice();
