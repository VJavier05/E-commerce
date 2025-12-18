// USER MESSAGE BOX MODAL
$(document).ready(function() {
    $('#chatButton').on('click', function(event) {
        event.preventDefault();

        let receiverId = $(this).data('receiver-id'); // Dynamically fetch receiver ID
        let chatUrl = `/user/chat/${receiverId}/`; // Construct URL dynamically

        $.ajax({
            url: chatUrl,
            type: "GET",
            success: function(data) {
                $('#messageBody').html(data); // Populate modal body with chat content
                $('#messageModal').modal('show'); // Show the modal
            },
            error: function() {
                alert('Error fetching chat content');
            }
        });
    });
});

// VOUCHER POP-UP NOTIFICATION
document.addEventListener("DOMContentLoaded", function () {
    // Fetch the checkVouchersURL from the global variable
    fetch(checkVouchersURL)
        .then((response) => response.json())
        .then((data) => {
            if (data.new_vouchers.length > 0) {
                let voucher = data.new_vouchers[0]; // Display the first voucher

                // Create the notification content
                let notificationContent = `
                    <div class="voucher-overlay">
                        <div class="voucher-notification" style="background-image: url('static/img/pop-up.jpg');">
                            <button class="close-btn-x" onclick="closeNotification()">×</button>
                            <h4 class="text-white">New Voucher Available!</h4>
                            <hr class="notification_hr">
                            <h2>Get ${
                                voucher.discount_percentage
                                    ? voucher.discount_percentage + "% Off"
                                    : voucher.discount_value
                                    ? "₱" + voucher.discount_value + " Off"
                                    : "N/A"
                            }</h2>
                            <h4 class="text-white"><strong>${voucher.voucher_name}</strong></h4>
                            <p>${voucher.voucher_message}</p>
                            <small>Valid until: <strong>${new Date(voucher.expiration_date).toLocaleString()}</strong></small>
                            <div class="action-buttons">
                                <a href="${shopVoucherURL}" class="claim-btn">Claim Now</a>
                            </div>
                        </div>
                    </div>
                `;

                // Insert the notification into the body
                document.body.insertAdjacentHTML("beforeend", notificationContent);
            }
        })
        .catch((error) => console.error("Error fetching vouchers:", error));
});

// Function to close the notification pop-up
function closeNotification() {
    document.querySelector(".voucher-overlay").remove();
}


// LAYOUT JS CODE FOR NOTIFICATION
// $(document).ready(function() {
//     $('#notificationBell').on('click', function(event) {
//         event.preventDefault(); // Prevent default anchor behavior
//         $.ajax({
//             url: "{{ url_for('user_notifications') }}", // Adjust the URL to your Flask route
//             type: "GET",
//             success: function(data) {
//                 $('#notificationBody').html(data); // Populate modal body with notifications
//                 $('#notificationModal').modal('show'); // Show the modal
//             },
//             error: function() {
//                 alert('Error fetching notifications');
//             }
//         });
//     });
// });

$(document).ready(function () {
    $('#notificationBell').on('click', function (event) {
        event.preventDefault(); // Prevent default behavior

        $.ajax({
            url: "/user/notifications", // Flask route for notifications
            type: "GET",
            success: function (data) {
                $('#notificationBody').html(data); // Populate modal body
                $('#notificationModal').modal('show'); // Show the modal
            },
            error: function (xhr, status, error) {
                console.error("Error fetching notifications: ", xhr.responseText);
                alert("Error fetching notifications. Please try again later.");
            },
        });
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const notificationIcon = document.getElementById("notification-icon");
    const notificationSidebar = document.getElementById("notification-sidebar");
    const closeNotificationSidebar = document.getElementById("close-notification-sidebar");
    const notificationList = document.getElementById("notification-list");

    // Show the notification sidebar
    notificationIcon.addEventListener("click", (e) => {
        e.stopPropagation();
        notificationSidebar.style.display = "block";
        fetch("/get_seller_notifications")
            .then(response => response.json())
            .then(data => {
                if (data.notifications.length) {
                    notificationList.innerHTML = data.notifications.map(n => `
                        <div class="notification-item border-${n.type}" 
                             data-id="${n.id}" 
                             style="${n.seen ? '' : 'border: 2px solid red; margin-bottom: 10px;'}">
                            <div class="notification-content">
                                <p><strong>${n.message}</strong></p>
                                <small>${n.date}</small>
                            </div>
                            <div class="notification-actions">
                                <a href="/edit_product/${n.product_id}" title="Edit Product">
                                <i class="bi bi-pencil-square"></i>
                                </a>
                                <button class="btn btn-danger mb-3" onclick="archiveNotification(${n.id})" title="Archive Notification">Delete</button>
                            </div>
                        </div>
                    `).join("");

                    markNotificationsAsSeen(data.notifications.map(n => n.id));
                } else {
                    notificationList.innerHTML = "<p class='text-muted text-center'>No notifications.</p>";
                }
            });
    });

    // Hide the notification sidebar when clicking outside
    document.addEventListener("click", (e) => {
        if (!notificationSidebar.contains(e.target) && e.target !== notificationIcon) {
            notificationSidebar.style.display = "none";
        }
    });

    // Close the notification sidebar
    closeNotificationSidebar.addEventListener("click", () => {
        notificationSidebar.style.display = "none";
    });

    // Archive Notification
    window.archiveNotification = (id) => {
        fetch(`/notifications/archive/${id}`, { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // document.querySelector(`[onclick="archiveNotification(${id})"]`)
                    //     .closest(".notification-item").remove();
                    document.querySelector(`[data-id="${id}"]`).remove();
                } else {
                    alert("Error archiving notification.");
                }
            });
    };

    // Function to mark notifications as seen
    function markNotificationsAsSeen(notificationIds) {
        fetch("/mark_notifications_seen", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ notification_ids: notificationIds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI to reflect the "seen" status
                notificationIds.forEach(id => {
                    const notification = document.querySelector(`.notification-item[data-id="${id}"]`);
                    if (notification) {
                        notification.classList.remove('bg-light'); // Remove highlight if seen
                    }
                });
            }
        });
    }
});
