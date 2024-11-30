// Attach an event listener to the "use_off_info" checkbox
document.getElementById("use_off_info").addEventListener("change", async function () {
    const useOffInfoChecked = this.checked;
    const barcode = document.getElementById("barcode_detailed").value.trim();

    // If the checkbox is checked and barcode length is sufficient, fetch the product details
    if (useOffInfoChecked && barcode.length >= 8) {
        try {
            // Make an API call to fetch product details
            const response = await fetch(`/fetch_product_details/${barcode}`);
            
            if (!response.ok) {
                throw new Error("Failed to fetch product details");
            }

            const productData = await response.json();

            // Populate the fields if the API returns data
            if (productData) {
                populateFields(productData);
            }
        } catch (error) {
            console.error("Error fetching product details:", error);
        }
    } else {
        // Clear the fields if the checkbox is unchecked
        clearFields();
    }
});

// Attach an event listener to the barcode field
document.getElementById("barcode_detailed").addEventListener("input", async function () {
    const barcode = this.value.trim();
    const useOffInfoChecked = document.getElementById("use_off_info").checked;

    // Proceed only if the checkbox is checked and the barcode length is sufficient
    if (useOffInfoChecked && barcode.length >= 8) {
        try {
            // Make an API call to fetch product details
            const response = await fetch(`/fetch_product_details/${barcode}`);
            
            if (!response.ok) {
                throw new Error("Failed to fetch product details");
            }

            const productData = await response.json();

            // Populate the fields if the API returns data
            if (productData) {
                populateFields(productData);
            }
        } catch (error) {
            console.error("Error fetching product details:", error);
        }
    } else {
        // Clear the fields if the checkbox is unchecked
        clearFields();
    }
});

// Button listeners for setting gluten-free options
document.getElementById("yesButton").addEventListener("click", function () {
    document.getElementById("gluten_free").value = "Yes";
    this.classList.add("active");
    document.getElementById("noButton").classList.remove("active");
});

document.getElementById("noButton").addEventListener("click", function () {
    document.getElementById("gluten_free").value = "No";
    this.classList.add("active");
    document.getElementById("yesButton").classList.remove("active");
});

// Function to populate fields with fetched product data
function populateFields(productData) {
    document.getElementById("product_name_detailed").value = productData.product_name || '';
    document.getElementById("brand").value = productData.brand || '';
    document.getElementById("parent_company").value = productData.parent_company || '';
    document.getElementById("volume_ml").value = productData.volume_l ? (productData.volume_l * 1000).toFixed(2) : ''; // Convert liters to ml
    document.getElementById("weight").value = productData.weight_g || '';
    document.getElementById("category").value = productData.category || '';
    document.getElementById("esg_score").value = productData.esg_score || '';
    document.getElementById("CO2").value = productData.co2_footprint || '';
    document.getElementById("product_page_url").value = productData.information_links || '';
    document.getElementById("product_image_url").value = productData.image || '';

    // Handle gluten-free status
    const glutenFree = productData.gluten_free;
    if (glutenFree === true) {
        document.getElementById("yesButton").classList.add("active");
        document.getElementById("noButton").classList.remove("active");
        document.getElementById("gluten_free").value = "Yes";
    } else if (glutenFree === false) {
        document.getElementById("noButton").classList.add("active");
        document.getElementById("yesButton").classList.remove("active");
        document.getElementById("gluten_free").value = "No";
    } else {
        document.getElementById("gluten_free").value = "";
    }
}

// Function to clear fields
function clearFields() {
    document.getElementById("product_name_detailed").value = '';
    document.getElementById("brand").value = '';
    document.getElementById("parent_company").value = '';
    document.getElementById("volume_ml").value = '';
    document.getElementById("weight").value = '';
    document.getElementById("category").value = '';
    document.getElementById("esg_score").value = '';
    document.getElementById("CO2").value = '';
    document.getElementById("product_page_url").value = '';
    document.getElementById("product_image_url").value = '';

    // Reset gluten-free status buttons
    document.getElementById("yesButton").classList.remove("active");
    document.getElementById("noButton").classList.remove("active");
    document.getElementById("gluten_free").value = "";
}
