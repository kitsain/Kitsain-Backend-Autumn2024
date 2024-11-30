document.addEventListener("DOMContentLoaded", function () {
    const discountPrice = document.getElementById("discount_price");
    const discountValidFrom = document.getElementById("discount_valid_from");
    const discountValidTo = document.getElementById("discount_valid_to");

    const wasteDiscountAdd = document.getElementById("waste_discount_add");
    const expirationDate = document.getElementById("expiration_date");
    const productAmount = document.getElementById("product_amount");

    function toggleWasteDiscountFields() {
        if (discountPrice.value || discountValidFrom.value || discountValidTo.value) {
            disableWasteDiscountFields();
        } else {
            enableWasteDiscountFields();
        }
    }

    function toggleDiscountCampaignFields() {
        if (wasteDiscountAdd.value || expirationDate.value || productAmount.value) {
            disableDiscountCampaignFields();
        } else {
            enableDiscountCampaignFields();
        }
    }

    function disableWasteDiscountFields() {
        wasteDiscountAdd.disabled = true;
        expirationDate.disabled = true;
        productAmount.disabled = true;
    }

    function enableWasteDiscountFields() {
        wasteDiscountAdd.disabled = false;
        expirationDate.disabled = false;
        productAmount.disabled = false;
    }

    function disableDiscountCampaignFields() {
        discountPrice.disabled = true;
        discountValidFrom.disabled = true;
        discountValidTo.disabled = true;
    }

    function enableDiscountCampaignFields() {
        discountPrice.disabled = false;
        discountValidFrom.disabled = false;
        discountValidTo.disabled = false;
    }

    discountPrice.addEventListener("input", toggleWasteDiscountFields);
    discountValidFrom.addEventListener("input", toggleWasteDiscountFields);
    discountValidTo.addEventListener("input", toggleWasteDiscountFields);

    wasteDiscountAdd.addEventListener("input", toggleDiscountCampaignFields);
    expirationDate.addEventListener("input", toggleDiscountCampaignFields);
    productAmount.addEventListener("input", toggleDiscountCampaignFields);

    toggleWasteDiscountFields();
    toggleDiscountCampaignFields();
});
