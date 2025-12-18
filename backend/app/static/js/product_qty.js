document.addEventListener('DOMContentLoaded', function() {
    const qtyInput = document.getElementById('qty');
    const btnMinus = document.getElementById('button-minus');
    const btnPlus = document.getElementById('button-plus');
    const cartQuantity = document.getElementById('cart-quantity'); // Hidden input for form submission
    const cartQuantity2 = document.getElementById('checkout-quantity'); 


    // Function to update the hidden input value
    function updateCartQuantity() {
        cartQuantity.value = qtyInput.value;
        cartQuantity2.value = qtyInput.value;
    }

    // Minus Button
    btnMinus.addEventListener('click', function() {
        let currentValue = parseInt(qtyInput.value);
        let minValue = parseInt(qtyInput.min);

        if (currentValue > minValue) {
            qtyInput.value = currentValue - 1;
            updateCartQuantity(); // Update hidden input value
        } else {
            qtyInput.value = minValue;  // Prevent going below minimum value
            updateCartQuantity(); // Update hidden input value
        }
    });

    // Plus Button
    btnPlus.addEventListener('click', function() {
        let currentValue = parseInt(qtyInput.value);
        let maxValue = parseInt(qtyInput.max);

        if (currentValue < maxValue) {
            qtyInput.value = currentValue + 1;
            updateCartQuantity(); // Update hidden input value
        } else {
            qtyInput.value = maxValue;  // Prevent going above maximum value
            updateCartQuantity(); // Update hidden input value
        }
    });

    // Update the hidden input value when the user manually changes the quantity
    qtyInput.addEventListener('input', updateCartQuantity);
});
