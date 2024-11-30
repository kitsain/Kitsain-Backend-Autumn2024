let map, marker;

function initMap() {
    // Default location (e.g., center of the country or city)
    const defaultLocation = { lat: 60.1695, lng: 24.9354 }; // Example: Helsinki, Finland

    // Initialize map
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLocation,
        zoom: 12,
    });

    // Add a marker
    marker = new google.maps.Marker({
        position: defaultLocation,
        map: map,
        draggable: true, // Allow the marker to be dragged
    });

    // Update form fields when marker is dragged
    marker.addListener("dragend", () => {
        const position = marker.getPosition();
        document.getElementById("gps").value = `${position.lat().toFixed(6)}, ${position.lng().toFixed(6)}`;
    });

    // Geocode address on "Find on Map" button click
    document.getElementById("locateButton").addEventListener("click", () => {
        const address = document.getElementById("location_address").value;
        if (address) {
            geocodeAddress(address);
        }
    });

    // Update map when GPS coordinates are manually entered
    document.getElementById("gps").addEventListener("change", () => {
        const coords = document.getElementById("gps").value.split(",");
        if (coords.length === 2) {
            const lat = parseFloat(coords[0].trim());
            const lng = parseFloat(coords[1].trim());
            if (!isNaN(lat) && !isNaN(lng)) {
                const position = { lat, lng };
                updateMap(position);
            }
        }
    });
}

function geocodeAddress(address) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: address }, (results, status) => {
        if (status === "OK" && results[0]) {
            const location = results[0].geometry.location;
            updateMap(location);
            document.getElementById("gps").value = `${location.lat().toFixed(6)}, ${location.lng().toFixed(6)}`;
        } else {
            alert("Geocode was not successful for the following reason: " + status);
        }
    });
}

function updateMap(position) {
    map.setCenter(position);
    marker.setPosition(position);
}

// Initialize map when the page is loaded
document.addEventListener("DOMContentLoaded", initMap);
