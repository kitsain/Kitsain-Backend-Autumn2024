let map, marker, placesService;

function initMap() {
    // Default location (center of Finland or any desired location)
    const defaultLocation = { lat: 60.1695, lng: 24.9354 }; // Helsinki, Finland

    // Initialize map
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLocation,
        zoom: 12,
    });

    // Add a draggable marker to the map
    marker = new google.maps.Marker({
        position: defaultLocation,
        map: map,
        draggable: true,
    });

    // Initialize the Places service
    placesService = new google.maps.places.PlacesService(map);

    // Update GPS coordinates in the form when marker is dragged
    marker.addListener("dragend", () => {
        const position = marker.getPosition();
        document.getElementById("gps").value = `${position.lat().toFixed(6)}, ${position.lng().toFixed(6)}`;
    });

    // Geocode address when "Find on Map" is clicked
    document.getElementById("locateButton").addEventListener("click", () => {
        const address = document.getElementById("location_address").value;
        if (address) {
            geocodeAddress(address);
        } else {
            alert("Please enter an address to locate.");
        }
    });

    // Update map and marker when GPS coordinates are entered manually
    document.getElementById("gps").addEventListener("change", () => {
        const coords = document.getElementById("gps").value.split(",");
        if (coords.length === 2) {
            const lat = parseFloat(coords[0].trim());
            const lng = parseFloat(coords[1].trim());
            if (!isNaN(lat) && !isNaN(lng)) {
                const position = { lat, lng };
                updateMap(position);
            } else {
                alert("Invalid GPS coordinates.");
            }
        }
    });

    // Add click listener on the map to fetch and fill shop details
    map.addListener("click", (event) => {
        const clickedLocation = event.latLng;
        marker.setPosition(clickedLocation);
        document.getElementById("gps").value = `${clickedLocation.lat().toFixed(6)}, ${clickedLocation.lng().toFixed(6)}`;
        fetchPlaceDetails(clickedLocation);
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

function fetchPlaceDetails(location) {
    const request = {
        location: location,
        radius: 50, // Adjust the search radius as needed
        type: ["store", "establishment"], // Add more types to ensure coverage
    };

    placesService.nearbySearch(request, (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && results[0]) {
            const place = results[0];
            fillFormWithPlaceDetails(place);
        } else {
            console.warn("No place details found or error:", status);
        }
    });
}

function fillFormWithPlaceDetails(place) {
    // Fill form fields based on the place details
    if (place.name) {
        document.getElementById("store_name").value = place.name;
    }

    if (place.vicinity) {
        document.getElementById("location_address").value = place.vicinity;
    }

    if (place.geometry && place.geometry.location) {
        const location = place.geometry.location;
        document.getElementById("gps").value = `${location.lat().toFixed(6)}, ${location.lng().toFixed(6)}`;
    }

    if (place.types && place.types.includes("chain")) {
        document.getElementById("chain").value = place.types.join(", "); // Example logic
    }

    // Leave shopkeepers field blank since it's optional
    document.getElementById("shopkeepers").value = "";
}

// Initialize map when the page is fully loaded
document.addEventListener("DOMContentLoaded", initMap);
