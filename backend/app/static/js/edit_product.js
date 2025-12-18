document.querySelector('form').addEventListener('submit', function() {
    const variations = [];
    const variationItems = document.querySelectorAll('.variation-item');

    variationItems.forEach(item => {
        const color = item.querySelector('input[name="variation_color[]"]').value;
        const size = item.querySelector('select[name="variation_size[]"]').value;
        const price = item.querySelector('input[name="variation_price[]"]').value;
        const stock = item.querySelector('input[name="variation_stock[]"]').value;

        variations.push({ color: color, size: size, price: price, stock: stock });
    });

    document.getElementById('variations-data').value = JSON.stringify(variations);
});

function removeVariation(variationId) {
    const variationDiv = document.getElementById(variationId);
    if (variationDiv) {
        variationDiv.remove();
        updateTable();
    }
}

function updateTable() {
    const tableBody = document.querySelector('#variations-table tbody');
    tableBody.innerHTML = '';

    const variations = [];

    document.querySelectorAll('.variation-item').forEach(item => {
        const color = item.querySelector('input[name="variation_color[]"]').value;
        const size = item.querySelector('select[name="variation_size[]"]').value;
        const price = item.querySelector('input[name="variation_price[]"]').value;
        const stock = item.querySelector('input[name="variation_stock[]"]').value;

        variations.push({ color: color, size: size, price: price, stock: stock });

        const newRow = `
            <tr>
                <td>${color}</td>
                <td>${size} (Stock: ${stock}, Price: ₱${price})</td>
            </tr>
        `;
        tableBody.innerHTML += newRow;
    });

    document.getElementById('variations-data').value = JSON.stringify(variations);
}

function addVariation() {
    const variationContainer = document.getElementById('color-variations-container');

    // Generate a unique ID for the new variation
    const newId = `variation-${Date.now()}`;

    const newVariation = document.createElement('div');
    newVariation.className = 'row mb-3 variation-item';
    newVariation.id = newId;

    newVariation.innerHTML = `
        <div class="col-md-3">
            <label class="form-label">Color</label>
            <input type="text" name="variation_color[]" class="form-control" placeholder="Enter color">
        </div>
        <div class="col-md-3">
            <label class="form-label">Size</label>
            <select name="variation_size[]" class="form-select">
                <option value="" disabled selected>Select size</option>
                <option value="XS">XS</option>
                <option value="S">S</option>
                <option value="M">M</option>
                <option value="L">L</option>
                <option value="XL">XL</option>
                <option value="XXL">XXL</option>
            </select>
        </div>
        <div class="col-md-2">
            <label class="form-label">Price</label>
            <input type="number" name="variation_price[]" class="form-control" placeholder="Enter price">
        </div>
        <div class="col-md-2">
            <label class="form-label">Stock</label>
            <input type="number" name="variation_stock[]" class="form-control" placeholder="Enter stock">
        </div>
        <div class="col-md-1 d-flex align-items-end">
            <button type="button" class="btn btn-danger" onclick="removeVariation('${newId}')">Remove</button>
        </div>
    `;

    variationContainer.appendChild(newVariation);
    updateTable();
}
