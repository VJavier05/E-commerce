
$(document).ready(function(){
    $(".owl-carousel").owlCarousel({
        nav: false, 
        dots: false,
        margin: 20,
        loop: false,
        responsive: {
            0: {
                items: 2
            },
            480: {
                items: 2
            },
            768: {
                items: 3
            },
            992: {
                items: 4
            },
            1200: {
                items: 5
            },
            1600: {
                items: 6,
                nav: true
            }
        }
    });


        // Mobile Menu Toggle - Show & Hide
        $('.mobile-menu-toggler').on('click', function (e) {
            $('body').toggleClass('mmenu-active');
            $(this).toggleClass('active');
            e.preventDefault();
        });
    
        $('.mobile-menu-overlay, .mobile-menu-close').on('click', function (e) {
            $('body').removeClass('mmenu-active');
            $('.mobile-menu-toggler').removeClass('active');
            e.preventDefault();
        });



        
});

$(document).ready(function() {
    var header = $('.header-bottom');
    var sticky = header.offset().top;

    $(window).scroll(function() {
        if (window.pageYOffset > sticky) {
            header.addClass('is-sticky');
            header.addClass('fixed'); // Add fixed class for animation
        } else {
            header.removeClass('is-sticky');
            header.removeClass('fixed'); // Remove fixed class
        }
    });
});


document.querySelectorAll('.input-group-text').forEach(item => {
    item.addEventListener('click', () => {
        const input = item.previousElementSibling; // Get the input element before the icon
        if (input.type === "password") {
            input.type = "text";
            item.querySelector('i').classList.replace('bi-eye-slash', 'bi-eye');
        } else {
            input.type = "password";
            item.querySelector('i').classList.replace('bi-eye', 'bi-eye-slash');
        }
    });
});






document.addEventListener('DOMContentLoaded', function() {
      // Select all elements with the class 'nav-link' and the data attribute 'data-bs-toggle="tab"'
    const tabLinks = document.querySelectorAll('.nav-link[data-bs-toggle="tab"]');
    
    // Iterate over each tab link
    tabLinks.forEach(link => {
      // Add a click event listener to each tab link
      link.addEventListener('click', () => {

        // REMOVE FIRST THE ACTIVE
        // Remove the 'active' class from all tab links
        tabLinks.forEach(link => {
          link.classList.remove('active');

          // Remove 'show' and 'active' classes from all tab content elements except 'My Vouchers' and 'Sign Out'
          if (link.getAttribute('href') !== '#tab-vouchers' && link.getAttribute('href') !== '#tab-signout') {
            document.querySelector(link.getAttribute('href')).classList.remove('show', 'active');
          }
        });

        // ADDING THE ACTIVE CLASS
        // Add the 'active' class to the clicked tab link
        link.classList.add('active');

        // Add 'show' and 'active' classes to the corresponding tab content element, except for 'My Vouchers' and 'Sign Out'
        if (link.getAttribute('href') !== '#tab-vouchers' && link.getAttribute('href') !== '#tab-signout') {
          document.querySelector(link.getAttribute('href')).classList.add('show', 'active');
        }
      });
    });
  });

  document.addEventListener('DOMContentLoaded', function () {
    const collapseElements = document.querySelectorAll('.collapse');

    document.querySelectorAll('.nav-link.dropdown-toggle').forEach(link => {
        link.addEventListener('click', function () {
            const targetId = this.getAttribute('href');
            collapseElements.forEach(collapse => {
                if (collapse.id !== targetId.substring(1)) {
                    new bootstrap.Collapse(collapse, { toggle: false }).hide();
                }
            });
        });
    });
});


document.addEventListener('DOMContentLoaded', function () {
  flatpickr("#dateOfBirthInput", {
      dateFormat: "Y-m-d", // The format should match the format used in WTForms
      altInput: true,
      altFormat: "F j, Y", // Optional: Human-readable format
      allowInput: true // Optional: Allow manual input
  });
});

function formatPhoneNumber(input) {
    // Remove non-digit characters
    let value = input.value.replace(/\D/g, '');

    // Ensure the number starts with "63" (Philippine country code)
    if (!value.startsWith('63')) {
        value = '63' + value;
    }

    // Handle mobile numbers (e.g., +63 912 345 6789)
    if (value.length === 12 || (value.length === 13 && value.startsWith('639'))) {
        input.value = `+63 ${value.slice(2, 5)} ${value.slice(5, 8)} ${value.slice(8, 12)}`;
    }
    // Handle landline numbers (e.g., +63 (02) 1234-5678 or +63 (049) 123-4567)
    else if (value.length === 10 || (value.length === 11 && value.startsWith('632'))) {
        // Format for Metro Manila numbers with area code (02)
        if (value.slice(2, 4) === '02') {
            input.value = `+63 (02) ${value.slice(4, 8)}-${value.slice(8)}`;
        }
        // Format for landline numbers outside Metro Manila
        else {
            input.value = `+63 (${value.slice(2, 4)}) ${value.slice(4, 7)}-${value.slice(7, 11)}`;
        }
    } else {
        // If the number is incomplete or too long, we just reset it to the correct initial state
        if (value.length <= 2) {
            input.value = `+63 `;
        } else if (value.length <= 5) {
            input.value = `+63 ${value.slice(2)}`;
        }
    }
}

// Attach the event listener for input formatting
document.querySelector('input[name="telephone_no"]').addEventListener('input', function(event) {
    formatPhoneNumber(event.target);
});


document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addressForm');
    const modal = document.getElementById('add_address');

    form.addEventListener('submit', function(event) {
        // Check if the form is valid
        if (!form.checkValidity()) {
            // Prevent form from submitting
            event.preventDefault();
            event.stopPropagation();
            
            // Show validation errors
            form.classList.add('was-validated');

            // Prevent modal from closing
            if (modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.show();
            }
        }
    });

    // Optional: You can also handle form field focus to hide validation messages when user starts typing
    form.addEventListener('input', function() {
        form.classList.remove('was-validated');
    });
});









