document.getElementById('checkout-form').addEventListener('submit', function () {
    const quantityInputs = document.querySelectorAll('input[type="number"]');

    quantityInputs.forEach(function (input) {
        const productId = input.getAttribute('id').split('-')[1];
        const color = input.getAttribute('id').split('-')[2];
        const size = input.getAttribute('id').split('-')[3];

        const hiddenInput = document.getElementById(`hidden-qty-${productId}-${color}-${size}`);
        hiddenInput.value = input.value; // Sync the visible quantity to the hidden input
    });
});