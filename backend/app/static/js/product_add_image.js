


document.getElementById('product-images-input').addEventListener('change', function(event) {
    const previewContainer = document.getElementById('image-preview');
    // Clear previous previews to avoid stacking images on top of each other
    previewContainer.innerHTML = ''; 

    const files = event.target.files;

    if (files.length > 0) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const reader = new FileReader();

            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.width = '100px'; // Set the width of the image
                img.style.height = '100px'; // Set the height of the image
                img.style.objectFit = 'cover'; // Maintain aspect ratio
                img.style.marginRight = '10px'; // Space between images
                img.style.marginBottom = '10px'; // Space below images
                img.style.display = 'inline-block'; // Ensure images are side by side

                previewContainer.appendChild(img);
            }

            reader.readAsDataURL(file); // Convert the file to a data URL
        }
    }
});
