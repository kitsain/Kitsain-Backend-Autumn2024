function populateEditModals(productId) {
    // Get the edit modal and associated elements
    const editModal = document.getElementById("editProductModal");

    // Use the productId to find the relevant product box
    const productBox = document.querySelector(`.product-box[data-product-id="${productId}"]`);

    if (!productBox) {
        console.error(`Product with ID ${productId} not found.`);
        return;
    }

    // Helper function to safely set a field's value
    function setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value;
        } else {
            console.error(`Field with ID ${fieldId} not found.`);
        }
    }

    // Helper function to format DateTime to YYYY-MM-DD
    function formatDateForInput(datetime) {
        if (!datetime) return ""; // If datetime is empty, return an empty string

        // Convert to Date object and format to YYYY-MM-DD
        const date = new Date(datetime);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Month is zero-indexed
        const day = String(date.getDate()).padStart(2, '0'); // Day of the month

        return `${year}-${month}-${day}`; // Return in YYYY-MM-DD format
    }

    function transformExpirationDate(dateString) {
        if (!dateString) return ""; // If no date, return empty string
    
        // Remove leading/trailing spaces and check if the date format is correct
        const trimmedDateString = dateString.trim();
    
        const dateParts = trimmedDateString.split(".");
        if (dateParts.length === 3) {
            // Return in the correct format YYYY-MM-DD
            return `${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}`;
        }
    
        // Log the format of the date if it's unexpected
        console.error(`Unexpected date format: ${trimmedDateString}`);
        return ""; // Return an empty string if the format is unexpected
    }
    

    // Populate visible fields
    setFieldValue("edit_product_id", productId);
    setFieldValue("edit_product_name", productBox.querySelector(".product-name")?.textContent || "");
    // Populate the 'Shop' dropdown with the correct selected value
    const shopId = productBox.querySelector(".product-shop-id")?.textContent; // Assuming the shop ID is available
    const shopSelect = document.getElementById("edit_shop");
    if (shopSelect && shopId) {
        // Loop through all options and set the selected one
        for (const option of shopSelect.options) {
            if (option.value == shopId) {
                option.selected = true;
                break; // Exit once the correct option is found
            }
        }
    }

    setFieldValue("edit_price", productBox.querySelector(".product-price")?.textContent.replace(' €', '') || "");
    setFieldValue("edit_discount_price", productBox.querySelector(".product-discount_price")?.textContent.replace(' €', '') || "");
    setFieldValue("edit_waste_discount", productBox.querySelector(".product-discount")?.textContent.replace(' - ', '').replace('%', '').trim() || "");
    
    const expirationDate = transformExpirationDate(productBox.querySelector(".product-expiration")?.textContent);

    setFieldValue("edit_expiration_date", expirationDate);

    // Populate hidden fields
    setFieldValue("edit_barcode", productBox.querySelector("#barcode")?.value || "");
    setFieldValue("edit_shop", productBox.querySelector("#shop-id")?.value || "");
    //setFieldValue("edit_amount_in_stock", productBox.querySelector("#amount-in-stock")?.value || "");
    // Populate stock amount buttons based on the value
    const stockAmount = productBox.querySelector("#amount-in-stock")?.value;

    const stockButtons = document.querySelectorAll(".btn-secondary-add-edit");
    
    // Remove any active class from buttons
    //stockButtons.forEach(button => button.classList.remove('active'));

    // Determine which button to select based on stockAmount
    if (stockAmount === "Few") {
        selectedButton = document.getElementById("fewButton-edit");
    } else if (stockAmount === "Moderate") {
        selectedButton = document.getElementById("moderateButton-edit");
    } else if (stockAmount === "Many") {
        selectedButton = document.getElementById("manyButton-edit");
    }

    // Remove 'active' class from all buttons in the second form first
    document.querySelectorAll('.btn-secondary-add-edit').forEach(button => {
        button.classList.remove('active');
    });

    // Add 'active' class to the selected button
    if (selectedButton) {
        selectedButton.classList.add('active');
        // Update the hidden input field
        document.getElementById('edit_product_amount').value = selectedButton.dataset.value;
    }

    // Format and populate date fields (discount_valid_from, discount_valid_to)
    const discountValidFrom = productBox.querySelector("#discount_valid_from")?.value;
    const discountValidTo = productBox.querySelector("#discount_valid_to")?.value;

    setFieldValue("edit_discount_valid_from", formatDateForInput(discountValidFrom));
    setFieldValue("edit_discount_valid_to", formatDateForInput(discountValidTo));

    setFieldValue("edit_gluten_free", productBox.querySelector("#gluten_free")?.value || "");
    setFieldValue("edit_co2_footprint", productBox.querySelector("#co2_footprint")?.value || "");
    setFieldValue("edit_esg_score", productBox.querySelector("#esg-score")?.value || "");
    setFieldValue("edit_product_image_url", productBox.querySelector("#product-image-url")?.value || "");
    setFieldValue("edit_brand", productBox.querySelector("#brand")?.value || "");
    setFieldValue("edit_sub_brand", productBox.querySelector("#sub_brand")?.value || "");
    setFieldValue("edit_parent_company", productBox.querySelector("#parent_company")?.value || "");
    setFieldValue("edit_weight", productBox.querySelector("#weight")?.value || "");
    setFieldValue("edit_volume_ml", productBox.querySelector("#volume_ml")?.value || "");
    setFieldValue("edit_category", productBox.querySelector("#category")?.value || "");
    setFieldValue("edit_CO2", productBox.querySelector("#CO2")?.value || "");

    // Show the modal
    editModal.style.display = "block";

    // Close modal on close button click
    document.getElementsByClassName("close-edit")[0].onclick = function() {
        editModal.style.display = "none";
    };

    // Close modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target === editModal) {
            editModal.style.display = "none";
        }
    };
}

document.getElementById("editForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent default form submission

    // Get values from form inputs
    const product_id = document.getElementById("edit_product_id").value;
    const product_name = document.getElementById("edit_product_name").value;
    const shop = document.getElementById("edit_shop").value;
    const price = document.getElementById("edit_price").value;
    const waste_discount = document.getElementById("edit_waste_discount").value;
    const expiration_date = document.getElementById("edit_expiration_date").value;
    const product_amount = document.querySelector(".btn-secondary-add-edit.active")?.getAttribute("data-value");
    const discount_price = document.getElementById("edit_discount_price").value;
    const discount_valid_from = document.getElementById("edit_discount_valid_from").value;
    const discount_valid_to = document.getElementById("edit_discount_valid_to").value;

    // Create the request payload
    const payload = {
        product_id,
        product_name,
        shop,
        price,
        waste_discount,
        expiration_date,
        product_amount,
        discount_price,
        discount_valid_from,
        discount_valid_to
    };

    // Send PUT request to update the product
    fetch('/update_product', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        //alert(data.message);  // Show success or failure message

        // Close the modal
        document.getElementById("editProductModal").style.display = "none";  // Hide modal

        // Redirect to products page
        window.location.href = "/products_page";  // Or the appropriate URL for your products page
    })
    .catch(error => {
        console.error('Error updating product:', error);
    });
});
