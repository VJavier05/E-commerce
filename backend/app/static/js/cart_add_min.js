// Function to increment the quantity
function incrementQuantity(button) {
    const productId = button.getAttribute('data-product-id');
    const color = button.getAttribute('data-color');
    const size = button.getAttribute('data-size');
    const qtyInput = document.getElementById(`qty-${productId}-${color}-${size}`);
    let currentValue = parseInt(qtyInput.value, 10); // Ensure we parse as base 10
    if (currentValue < qtyInput.max) {
        qtyInput.value = currentValue + 1;
        updateTotalPrice(qtyInput); // Update total price when quantity changes
        updateSummaryTotal(); // Update the summary total
    }
}

// Function to decrement the quantity
function decrementQuantity(button) {
    const productId = button.getAttribute('data-product-id');
    const color = button.getAttribute('data-color');
    const size = button.getAttribute('data-size');
    const qtyInput = document.getElementById(`qty-${productId}-${color}-${size}`);
    let currentValue = parseInt(qtyInput.value, 10); // Ensure we parse as base 10
    if (currentValue > qtyInput.min) {
        qtyInput.value = currentValue - 1;
        updateTotalPrice(qtyInput); // Update total price when quantity changes
        updateSummaryTotal(); // Update the summary total
    }
}

// Function to update the total price based on the quantity
function updateTotalPrice(inputElement) {
    const productId = inputElement.id.split('-')[1]; // Get product ID
    const color = inputElement.id.split('-')[2]; // Get color
    const size = inputElement.id.split('-')[3]; // Get size
    const unitPrice = parseFloat(inputElement.getAttribute('data-price'));
    const quantity = parseInt(inputElement.value, 10);

    if (!isNaN(unitPrice) && !isNaN(quantity)) {
        const totalPrice = unitPrice * quantity;
        // Update the total price display for this specific product variation
        document.getElementById(`total-${productId}-${color}-${size}`).textContent = `${totalPrice.toFixed(2)}`; // Updated line
    }
}

// Function to update the summary total
function updateSummaryTotal() {
    let subtotal = 0;
    const totalElements = document.querySelectorAll('[id^="total-"]'); // Select all total price elements

    totalElements.forEach(totalElement => {
        const price = parseFloat(totalElement.textContent) || 0;
        subtotal += price; // Accumulate total
    });

    const shippingCost = 45.00; // Your shipping cost
    const grandTotal = subtotal + shippingCost;

    // Update the summary total display
    const summaryTotalElement = document.querySelector('.summary-total td:nth-child(2)');
    summaryTotalElement.textContent = `₱${grandTotal.toFixed(2)}`; // Update with grand total

    const summarysubtotal = document.querySelector('.summary-subtotal td:nth-child(2)');
    summarysubtotal.textContent = `₱${subtotal.toFixed(2)}`; // Update with grand total


}

// Load quantities when the page loads
window.onload = function() {
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        const productId = input.id.split('-')[1]; // Get product ID
        const color = input.id.split('-')[2]; // Get color
        const size = input.id.split('-')[3]; // Get size
        updateTotalPrice(input); // Update total price display for initial values
    });
    
    // Update the summary total on page load
    updateSummaryTotal();
};
