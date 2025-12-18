// const minSlider = document.getElementById('min-slider');
// const maxSlider = document.getElementById('max-slider');
// const minPrice = document.getElementById('min-price');
// const maxPrice = document.getElementById('max-price');
// const minValue = document.getElementById('min-value');
// const maxValue = document.getElementById('max-value');
// const minInput = document.getElementById('min-input');
// const maxInput = document.getElementById('max-input');
// const sliderContainer = document.querySelector('.slider');

// function updateValues() {
//     let min = parseInt(minSlider.value);
//     let max = parseInt(maxSlider.value);

//     if (min > max) {
//         if (this === minSlider || this === minInput) {
//             min = max;
//         } else {
//             max = min;
//         }
//     }

//     minSlider.value = min;
//     maxSlider.value = max;
//     minInput.value = min;
//     maxInput.value = max;
//     minPrice.textContent = min;
//     maxPrice.textContent = max;
//     minValue.textContent = `₱${min}`;
//     maxValue.textContent = `₱${max}`;

//     const minPercentage = (min / maxSlider.max) * 100;
//     const maxPercentage = (max / maxSlider.max) * 100;

//     sliderContainer.style.background = `linear-gradient(to right, #ddd ${minPercentage}%, #696CFF ${minPercentage}%, #696CFF ${maxPercentage}%, #ddd ${maxPercentage}%)`;
// }

// minSlider.addEventListener('input', updateValues);
// maxSlider.addEventListener('input', updateValues);
// minInput.addEventListener('input', function() {
//     if (this.value === '') {
//         this.value = 0;
//     }
//     minSlider.value = this.value;
//     updateValues();
// });
// maxInput.addEventListener('input', function() {
//     if (this.value === '') {
//         maxSlider.value = 0;
//     } else {
//         maxSlider.value = this.value;
//     }
//     updateValues();
// });

// updateValues();