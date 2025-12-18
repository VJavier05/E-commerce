



   // Get references to both modals
   var viewAccountModal = new bootstrap.Modal(document.getElementById('ViewAccount'), {
    backdrop: 'static', // Disable background click closing
    keyboard: false // Disable keyboard closing
});

var imageModal = document.getElementById('imageModal');

// When the image modal is about to open
imageModal.addEventListener('show.bs.modal', function () {
    // Keep the ViewAccount modal open by not hiding it
    var originalImageSrc = document.getElementById('modal-image').src;
    document.getElementById('enlarged-image').src = originalImageSrc;
});

// When the image modal is closed
imageModal.addEventListener('hidden.bs.modal', function () {
    // Re-focus on the ViewAccount modal to make sure it's still active
    viewAccountModal.show();
});

// Handle the View Account modal content and approval form action
var viewAccountModal = document.getElementById('ViewAccount');

viewAccountModal.addEventListener('show.bs.modal', function (event) {
  // Button that triggered the modal
  var button = event.relatedTarget;

  // Extract user information from data-* attributes
  var firstName = button.getAttribute('data-firstname');
  var lastName = button.getAttribute('data-lastname');
  var image = button.getAttribute('data-image');
  var userId = button.getAttribute('data-user-id');
  var dateOfBirth = button.getAttribute('data-date_of_birth');
  var gender = button.getAttribute('data-gender');
  var userRole = button.getAttribute('data-role'); // Get the user role

  // Update the modal's content with the extracted information
  var modalFirstNameInput = document.getElementById('fname');
  var modalLastNameInput = document.getElementById('lname');
  var modalImage = document.getElementById('modal-image');
  var modalDOB = document.getElementById('dob');
  var modalGender = document.getElementById('gender');
  var approveForm = document.getElementById('approve-form');

  modalFirstNameInput.value = firstName;
  modalLastNameInput.value = lastName;
  modalImage.src = image;
  modalDOB.value = dateOfBirth;
  modalGender.value = gender;



  var shopName = button.getAttribute('data-shop-name');
  var shopCategory = button.getAttribute('data-shop-category');
  var shopAddress = button.getAttribute('data-shop-address');
  var shopPostal = button.getAttribute('data-shop-postal');
  var shopCreated = button.getAttribute('data-shop-created');
  var businessIdImage = button.getAttribute('data-business-id-image');


  var modalShopNameInput = document.getElementById('Shop');
  var modalShopCategoryInput = document.getElementById('Category');
  var modalShopAddressInput = document.getElementById('Address');
  var modalShopPostalInput = document.getElementById('Postal');
  var modalShopCreatedInput = document.getElementById('ShopCreated'); 
  var modalBusinessIdImage = document.getElementById('modal-business-id-image');

  modalShopNameInput.value = shopName;
  modalShopCategoryInput.value = shopCategory;
  modalShopAddressInput.value = shopAddress;
  modalShopPostalInput.value = shopPostal;
  modalShopCreatedInput.value = shopCreated; 
  modalBusinessIdImage.src = businessIdImage;





  // Update the form action dynamically for the approve process
  // approveForm.setAttribute('action', '/approve_user/' + userId);

  // Check if the button that triggered the modal is from the archive tab
  if (button.closest('table') && button.closest('table').id === 'archiveTable') {
    // Hide the approve form for archived users
    approveForm.style.display = 'none'; // Hide the form
  } else {
    // Show the approve form for pending users
    approveForm.style.display = 'block'; // Show the form
    // Update the form action dynamically for the approve process
    approveForm.setAttribute('action', '/approve_user/' + userId);
  }

  // Get the shop information container
  var shopInfoContainer = document.getElementById('shopInfoContainer'); // Ensure you have this container

  // Show or hide the shop information based on user role
  if (userRole === 'seller') {
    shopInfoContainer.style.display = 'block'; // Show shop information
  } else {
    shopInfoContainer.style.display = 'none'; // Hide shop information
  }
});



document.addEventListener('DOMContentLoaded', function () {
  var confirmReturnModal = document.getElementById('confirmReturnModal');

  confirmReturnModal.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      var button = event.relatedTarget; // Button that triggered the modal

      // Extract user information from data-* attributes
      var userId = button.getAttribute('data-user-id');
      var firstName = button.getAttribute('data-firstname');

      // Update the modal's content with the extracted information
      var modalUserName = document.getElementById('modal-user-return-name');
      var userIdInput = document.getElementById('user-id');

      modalUserName.textContent = firstName; // Set user name in modal
      userIdInput.value = userId; // Set user ID in hidden input
  });
});



// Handle the Approve action directly from the table
var confirmApproveModal = document.getElementById('confirmApproveModal');

confirmApproveModal.addEventListener('show.bs.modal', function (event) {
  // Button that triggered the modal
  var button = event.relatedTarget;

  // Extract user information from data-* attributes
  var userId = button.getAttribute('data-user-id');
  var firstName = button.getAttribute('data-firstname');

  // Update the confirmation message in the modal
  var modalUserName = document.getElementById('modal-user-name');
  modalUserName.textContent = firstName;

  // Get the approve form and update the action dynamically
  var confirmApproveForm = document.getElementById('confirm-approve-form');
  confirmApproveForm.setAttribute('action', '/approve_user/' + userId);
});

// Search functionality for filtering the table rows
function searchTable(tableId, searchInputId) {
  // Get the value of the search input
  var input = document.getElementById(searchInputId).value.toLowerCase();
  var table = document.getElementById(tableId).querySelector("tbody"); // Get the table body
  var rows = table.getElementsByTagName("tr"); // Get all the rows in the table body

  // Loop through all the rows and hide those that don't match the search query
  for (var i = 0; i < rows.length; i++) {
    var firstName = rows[i].getElementsByTagName("td")[0].textContent.toLowerCase(); // First Name
    var lastName = rows[i].getElementsByTagName("td")[1].textContent.toLowerCase(); // Last Name
    var email = rows[i].getElementsByTagName("td")[2].textContent.toLowerCase(); // Email

    // Check if any of the columns match the search query
    if (firstName.includes(input) || lastName.includes(input) || email.includes(input)) {
      rows[i].style.display = ""; // Show the row
    } else {
      rows[i].style.display = "none"; // Hide the row
    }
  }
}

document.addEventListener('DOMContentLoaded', function () {
  var confirmDisapproveModal = document.getElementById('confirmDisapproveModal');

  confirmDisapproveModal.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      var button = event.relatedTarget; // Button that triggered the modal

      // Extract user information from data-* attributes
      var userId = button.getAttribute('data-user-id');
      var firstName = button.getAttribute('data-firstname');

      // Update the modal's content with the extracted information
      var modalUserName = document.getElementById('disapprove-modal-user-name');
      var userIdInput = document.getElementById('disapprove-user-id');

      modalUserName.textContent = firstName; // Set user name in modal
      userIdInput.value = userId; // Set user ID in hidden input
  });
});


document.addEventListener('DOMContentLoaded', function () {
  var confirmDisapproveModal = document.getElementById('confirmReturnModalSeller');

  confirmDisapproveModal.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      var button = event.relatedTarget; // Button that triggered the modal

      // Extract user information from data-* attributes
      var userId = button.getAttribute('data-user-id');
      var firstName = button.getAttribute('data-firstname');

      // Update the modal's content with the extracted information
      var modalUserName = document.getElementById('disapprove-modal-user-name');
      var userIdInput = document.getElementById('disapprove-user-id');

      modalUserName.textContent = firstName; // Set user name in modal
      userIdInput.value = userId; // Set user ID in hidden input
  });
});



