/**
 * Handles the behavior of the "Add Product" modal.
 * This function opens the modal when the "Add" button is clicked,
 * and closes it when the close button or outside the modal is clicked.
 */
function handleAddProductModal() {
    const addProductModal = document.getElementById("addProductModal");
    const btn = document.getElementById("addButton");
    const span = addProductModal.getElementsByClassName("close")[0];

    btn.onclick = function(event) {
        event.preventDefault(); 
       addProductModal.style.display = "block";
    }

    span.onclick = function() {
        addProductModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == addProductModal) {
            addProductModal.style.display = "none";
        }
    }
}

document.addEventListener("DOMContentLoaded", handleAddProductModal);

/**
 * Handles the behavior of the "Filter Product" modal.
 * This function opens the modal when the "Filter" button is clicked,
 * and closes it when the close button or outside the modal is clicked.
 */
function handleFilterProductModal() {
    const filterProductModal = document.getElementById("filterProductModal");
    const btn = document.getElementById("filterButton");
    const span = filterProductModal.getElementsByClassName("close")[0];

    btn.onclick = function(event) {
        event.preventDefault(); 
        filterProductModal.style.display = "block";
    }

    span.onclick = function() {
        addProductModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == filterProductModal) {
            filterProductModal.style.display = "none";
        }
    }
}

document.addEventListener("DOMContentLoaded", handleFilterProductModal);

/**
 * Fetches the user's geolocation and displays a list of shops within the specified radius.
 * The user’s latitude and longitude are saved in hidden input fields, and a dropdown list of nearby shops is populated.
 * If an error occurs during the geolocation fetch or shop data fetch, an error message is displayed.
 */
document.getElementById('findShopsBtn').addEventListener('click', () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const radius = document.getElementById('shop_radius').value || 10; // Default to 10km if not provided

                // Save GPS coordinates in hidden inputs
                document.getElementById('gps_lat').value = lat;
                document.getElementById('gps_lon').value = lon;

                // Fetch the closest shops within the radius
                try {
                    const response = await fetch(`/get_closest_shops?lat=${lat}&lon=${lon}&radius=${radius}`);
                    const shops = await response.json();

                    // Populate the shop dropdown
                    const shopFilter = document.getElementById('shop_filter');
                    shopFilter.innerHTML = '<option value="">Select a shop</option>'; // Reset options

                    if (shops.length > 0) {
                        shops.forEach((shop, index) => {
                            const option = document.createElement('option');
                            option.value = shop.shop_id;
                            option.textContent = `${shop.store_name} (${shop.distance.toFixed(2)} km)`;
                            shopFilter.appendChild(option);

                            // Select the first shop by default
                            if (index === 0) {
                                shopFilter.value = shop.shop_id;
                            }
                        });
                    } else {
                        alert('No shops found within the specified radius.');
                    }
                } catch (error) {
                    console.error('Error fetching closest shops:', error);
                    alert('Failed to fetch shops. Please try again later.');
                }
            },
            (error) => {
                console.error('Error getting location:', error);
                alert('Unable to get your location. Please try again or allow location access.');
            }
        );
    } else {
        alert('Geolocation is not supported by your browser.');
    }
});

/**
 * Handles the behavior of the "Edit Product" modal.
 * This function opens the modal when the "Edit" button is clicked,
 * and closes it when the close button or outside the modal is clicked.
 * It also handles switching to the detailed info modal when the "More Info" button is clicked.
 */
function handleEditProductModal() {
    const modal = document.getElementById("editProductModal");
    const span = modal.getElementsByClassName("close-edit")[0];

    const moreInfoBtn = document.getElementById("edit_moreInfoBtn");

    const detailedModal = document.getElementById("editDetailedInfoModal");
    const detailedSpan = detailedModal.getElementsByClassName("close-edit")[0];

    span.onclick = function() {
        modal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target == modal || event.target == detailedModal) {
            modal.style.display = "none";
            detailedModal.style.display = "none";
        }
    };

    moreInfoBtn.onclick = function() {
        modal.style.display = "none";
        detailedModal.style.display = "block";

        document.getElementById("edit_barcode_detailed").value = document.getElementById("edit_barcode").value;
        document.getElementById("edit_product_name_detailed").value = document.getElementById("edit_product_name").value;
    };
}

document.addEventListener("DOMContentLoaded", handleEditProductModal);

/**
 * Handles the behavior of the "Edit Detailed Info" modal.
 * This function opens the modal when the "Edit More Info" button is clicked,
 * and closes it when the close button or outside the modal is clicked.
 */
function handleEditDetailedInfoModal() {
    const modal = document.getElementById("editDetailedInfoModal");
    const span = modal.getElementsByClassName("close")[0]; 

    span.onclick = function() {
        modal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
}

document.addEventListener("DOMContentLoaded", handleEditDetailedInfoModal);

const addProductForm = document.getElementById("add-product-form"); 
const moreInfoBtn = document.getElementById("moreInfoBtn");
const barcodeInput = document.getElementById("barcode");
const barcodeDetailedInput = document.getElementById("barcode_detailed");
const productNameDetailedInput = document.getElementById("product_name_detailed");
const productNameInput = document.getElementById("product_name");
const shopInput = document.getElementById("shop_add");
const priceInput = document.getElementById("add-price");
const discountPriceInput = document.getElementById("discount_price");
const discountValidFromInput = document.getElementById("discount_valid_from");
const discountValidToInput = document.getElementById("discount_valid_to");
const wasteDiscountInput = document.getElementById("waste_discount_add");
const expirationDateInput = document.getElementById("expiration_date");
const productAmountInput = document.getElementById("product_amount");

/**
 * Handles the submission of the "Add Product" form, saving the form data to localStorage and sending it to the server.
 * If the form is valid, the data is stored and the "Add Product" modal is hidden, while the "Add Detailed Info" modal is displayed.
 * If the form is invalid, the validation errors are shown.
 */
moreInfoBtn.addEventListener('click', function () {
    if (addProductForm.checkValidity()) {
        barcodeDetailedInput.value = barcodeInput.value;
        productNameDetailedInput.value = productNameInput.value;

        localStorage.setItem('barcode', barcodeInput.value);
        localStorage.setItem('product_name', productNameInput.value);
        localStorage.setItem('shop', shopInput.value);
        localStorage.setItem('price', priceInput.value);

        if (discountPriceInput.value) {
            localStorage.setItem('discount_price', discountPriceInput.value);
        }
        if (discountValidFromInput.value) {
            localStorage.setItem('discount_valid_from', discountValidFromInput.value);
        }
        if (discountValidToInput.value) {
            localStorage.setItem('discount_valid_to', discountValidToInput.value);
        }

        if (wasteDiscountInput.value) {
            localStorage.setItem('waste_discount', wasteDiscountInput.value);
        }
        if (expirationDateInput.value) {
            localStorage.setItem('expiration_date', expirationDateInput.value);
        }
        if (productAmountInput.value) {
            localStorage.setItem('product_amount', productAmountInput.value);
        }

        // Prepare data for sending to the server, excluding null or empty values
        const productData = {
            barcode: barcodeInput.value,
            product_name: productNameInput.value,
            shop: shopInput.value,
            price: priceInput.value,
            discount_price: discountPriceInput.value || null,
            discount_valid_from: discountValidFromInput.value || null,
            discount_valid_to: discountValidToInput.value || null,
            waste_discount: wasteDiscountInput.value || null,
            expiration_date: expirationDateInput.value || null,
            product_amount: productAmountInput.value || null
        };

        // Send the data to the server using Fetch API
        fetch('/save_product_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Product data saved:', data);
        })
        .catch(error => {
            console.error('Error saving product data:', error);
        });

        addProductModal.style.display = 'none';
        addDetailedInfoModal.style.display = 'block';
    } else {
        // Show validation errors if the form is invalid
        addProductForm.reportValidity();
    }
});
