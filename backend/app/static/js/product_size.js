document.addEventListener('DOMContentLoaded', function() {
    // Function to update the hidden input fields based on user selections
    function updateCartDetails() {
        const selectedColor = document.querySelector('input[name="colorOptions"]:checked');
        const selectedSize = document.querySelector('input[name^="sizeOptions"]:checked');
        const quantityInput = document.getElementById('qty');
        
        if (selectedColor) {
            document.getElementById('selected-color').value = selectedColor.value;
        }

        if (selectedSize) {
            document.getElementById('selected-size').value = selectedSize.value;
            // Update the price based on the selected size
            document.getElementById('product-price-hidden').value = selectedSize.getAttribute('data-price');
        }else {
            document.getElementById('selected-size').value = ''; // Clear hidden field
            document.getElementById('product-price-hidden').value = '0.00'; // Reset price
        }


        // Update the quantity
        document.getElementById('cart-quantity').value = quantityInput.value;
    }

    // Add event listeners to color and size options
    const colorOptions = document.querySelectorAll('input[name="colorOptions"]');
    const sizeOptions = document.querySelectorAll('input[name^="sizeOptions"]');
    
    colorOptions.forEach(option => {
        option.addEventListener('change', updateCartDetails);
    });

    sizeOptions.forEach(option => {
        option.addEventListener('change', updateCartDetails);
    });

    // Initial update on page load
    updateCartDetails();
});