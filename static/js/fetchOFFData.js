// Attach an event listener to the barcode field
document.getElementById("barcode_detailed").addEventListener("input", async function () {
    const barcode = this.value.trim();

    // Proceed only if the barcode length is sufficient (e.g., 8-13 digits for standard barcodes)
    if (barcode.length >= 8) {
        try {
            // Make an API call to fetch product details
            const response = await fetch(`/fetch_product_details/${barcode}`);
            
            if (!response.ok) {
                throw new Error("Failed to fetch product details");
            }

            const productData = await response.json();

            // Populate the fields if the API returns data
            if (productData) {
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
        } catch (error) {
            console.error("Error fetching product details:", error);
        }
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
