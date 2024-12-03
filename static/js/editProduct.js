function populateEditModals(productId) {
    const editModal = document.getElementById("editProductModal");

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
        if (!datetime) return ""; 

        const date = new Date(datetime);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); 
        const day = String(date.getDate()).padStart(2, '0'); 

        return `${year}-${month}-${day}`; 
    }

    function transformExpirationDate(dateString) {
        if (!dateString) return ""; 

        const trimmedDateString = dateString.trim();
    
        const dateParts = trimmedDateString.split(".");
        if (dateParts.length === 3) {
            return `${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}`;
        }
    
        console.error(`Unexpected date format: ${trimmedDateString}`);
        return ""; 
    }
    

    // Populate visible fields
    setFieldValue("edit_product_id", productId);
    setFieldValue("edit_product_name", productBox.querySelector(".product-name")?.textContent || "");
    const shopId = productBox.querySelector(".product-shop-id")?.textContent; 
    const shopSelect = document.getElementById("edit_shop");
    if (shopSelect && shopId) {
        for (const option of shopSelect.options) {
            if (option.value == shopId) {
                option.selected = true;
                break; 
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
    const stockAmount = productBox.querySelector("#amount-in-stock")?.value;

    let selectedButton = null;

    if (stockAmount === "Few") {
        selectedButton = document.getElementById("fewButton-edit");
    } else if (stockAmount === "Moderate") {
        selectedButton = document.getElementById("moderateButton-edit");
    } else if (stockAmount === "Many") {
        selectedButton = document.getElementById("manyButton-edit");
    }

    document.querySelectorAll('.btn-secondary-add-edit').forEach(button => {
        button.classList.remove('active');
    });

    if (selectedButton) {
        selectedButton.classList.add('active');
        document.getElementById('edit_product_amount').value = selectedButton.dataset.value;
    }

    const discountValidFrom = productBox.querySelector("#discount_valid_from")?.value;
    const discountValidTo = productBox.querySelector("#discount_valid_to")?.value;

    setFieldValue("edit_discount_valid_from", formatDateForInput(discountValidFrom));
    setFieldValue("edit_discount_valid_to", formatDateForInput(discountValidTo));

    setFieldValue("edit_gluten_free", productBox.querySelector("#gluten_free")?.value || "");
    setFieldValue("edit_esg_score", productBox.querySelector("#esg-score")?.value || "");
    setFieldValue("edit_product_image_url", productBox.querySelector("#product-image-url")?.value || "");
    setFieldValue("edit_brand", productBox.querySelector("#brand")?.value || "");
    setFieldValue("edit_sub_brand", productBox.querySelector("#sub_brand")?.value || "");
    setFieldValue("edit_parent_company", productBox.querySelector("#parent_company")?.value || "");
    setFieldValue("edit_weight", productBox.querySelector("#weight")?.value || "");
    setFieldValue("edit_volume_ml", productBox.querySelector("#volume_ml")?.value || "");
    setFieldValue("edit_category", productBox.querySelector("#category")?.value || "");
    setFieldValue("edit_CO2", productBox.querySelector("#CO2")?.value || "");

    const glutenFreeValue = productBox.querySelector("#gluten_free")?.value;
    console.log(glutenFreeValue);
    if (glutenFreeValue === "True") {
        document.getElementById("yesButton-edit").classList.add('active');
        document.getElementById("edit_gluten_free").value = "Yes";
    } else if (glutenFreeValue === "False") {
        document.getElementById("noButton-edit").classList.add('active');
        document.getElementById("edit_gluten_free").value = "No";
    }

    editModal.style.display = "block";

    document.getElementsByClassName("close-edit")[0].onclick = function() {
        editModal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target === editModal) {
            editModal.style.display = "none";
        }
    };
}

document.getElementById("editForm").addEventListener("submit", function(event) {
    event.preventDefault(); 

    const product_id = document.getElementById("edit_product_id").value;
    const barcode = document.getElementById("edit_barcode").value;
    const product_name = document.getElementById("edit_product_name").value;
    const shop = document.getElementById("edit_shop").value;
    const price = document.getElementById("edit_price").value;
    const waste_discount = document.getElementById("edit_waste_discount").value;
    const expiration_date = document.getElementById("edit_expiration_date").value;
    const product_amount = document.querySelector(".btn-secondary-add-edit.active")?.getAttribute("data-value");
    const discount_price = document.getElementById("edit_discount_price").value;
    const discount_valid_from = document.getElementById("edit_discount_valid_from").value;
    const discount_valid_to = document.getElementById("edit_discount_valid_to").value;

    const payload = {
        product_id,
        barcode,
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

        document.getElementById("editProductModal").style.display = "none"; 

        // Redirect to products page
        window.location.href = "/products_page";  
    })
    .catch(error => {
        console.error('Error updating product:', error);
    });
});

document.getElementById("editDetailedForm").addEventListener("submit", function(event) {
    event.preventDefault();  

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

    const barcode = document.getElementById("edit_barcode_detailed").value;
    const brand = document.getElementById("edit_brand").value;
    const parent_company = document.getElementById("edit_parent_company").value;
    const volume_ml = document.getElementById("edit_volume_ml").value;
    const gluten_free = document.getElementById("edit_gluten_free").value;
    const co2 = document.getElementById("edit_CO2").value;
    const product_image_url = document.getElementById("edit_product_image_url").value;
    const sub_brand = document.getElementById("edit_sub_brand").value;
    const weight = document.getElementById("edit_weight").value;
    const category = document.getElementById("edit_category").value;
    const esg_score = document.getElementById("edit_esg_score").value;
    const product_page_url = document.getElementById("edit_product_page_url").value;
    const product_image = document.getElementById("edit_product_image").value;

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
        discount_valid_to,
        barcode,
        brand,
        parent_company,
        volume_ml,
        gluten_free,
        co2,
        product_image_url,
        sub_brand,
        weight,
        category,
        esg_score,
        product_page_url,
        product_image
    };

    fetch('/edit_product_detail', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("editDetailedInfoModal").style.display = "none"; 

        window.location.href = "/products_page";  
    })
    .catch(error => {
        console.error('Error updating product:', error);
    });
});
