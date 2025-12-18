function loadProvinces(regionCode) {
    if (regionCode) {
        $.ajax({
            url: '/get_provinces/' + regionCode,
            type: 'GET',
            success: function(data) {
                $('#courierProvince').empty(); // Clear existing options
                $('#courierProvince').append('<option value="">Select Province</option>');
                $.each(data, function(index, province) {
                    $('#courierProvince').append('<option value="' + province[0] + '">' + province[1] + '</option>');
                });
            },
            error: function() {
                // Handle errors if needed
                console.error('Error fetching provinces');
            }
        });
    } else {
        $('#courierProvince').empty(); // Clear existing options if no region is selected
        $('#courierProvince').append('<option value="">Select Province</option>');
    }
}

    function loadCities(provinceCode) {
        if (provinceCode) {
            $.ajax({
                url: '/get_cities/' + provinceCode,
                type: 'GET',
                success: function(data) {
                    console.log(data);
                    $('#courierCity').empty(); // Clear existing options
                    $('#courierCity').append('<option value="">Select City</option>');
                    $.each(data, function(index, city) {
                        $('#courierCity').append('<option value="' + city[0] + '">' + city[1] + '</option>');
                    });
                    
                    // Clear barangay options when a new city is selected
                    $('#courierBarangay').empty().append('<option value="">Select Barangay</option>');
                },
                error: function() {
                    console.error('Error fetching cities');
                }
            });
        } else {
            $('#courierCity').empty(); // Clear existing options if no province is selected
            $('#courierCity').append('<option value="">Select City</option>');
            $('#courierBarangay').empty().append('<option value="">Select Barangay</option>'); // Clear barangays
        }
    }

    function loadBarangays(cityCode) {
        if (cityCode) {
            $.ajax({
                url: '/get_barangays/' + cityCode,
                type: 'GET',
                success: function(data) {
                    $('#courierBarangay').empty(); // Clear existing options
                    $('#courierBarangay').append('<option value="">Select Barangay</option>');
                    $.each(data, function(index, barangay) {
                        $('#courierBarangay').append('<option value="' + barangay[0] + '">' + barangay[1] + '</option>');
                    });
                },
                error: function() {
                    console.error('Error fetching barangays');
                }
            });
        } else {
            $('#courierBarangay').empty(); // Clear existing options if no city is selected
            $('#courierBarangay').append('<option value="">Select Barangay</option>');
        }
    }

    $(document).ready(function() {
        $('#courierProvince').change(function() {
            loadCities($(this).val());
        });

        $('#courierCity').change(function() {
            loadBarangays($(this).val());
        });
    });
