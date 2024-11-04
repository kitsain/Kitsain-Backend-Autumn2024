    // Function to calculate waste discount percentage
    function calculateWasteDiscount() {
        const price = parseFloat(document.getElementById("add-price").value);
        const discountPrice = parseFloat(document.getElementById("discount_price").value);
        


        if (!isNaN(price) && !isNaN(discountPrice) && price > 0) {
            const wasteDiscount = ((price - discountPrice) / price) * 100;
            console.log(wasteDiscount);
            document.getElementById("waste_discount_add").value = wasteDiscount.toFixed(1); // Update waste discount field
        } else {
            document.getElementById("waste_discount_add").value = ''; // Clear waste discount if invalid
        }
    }

    // Add event listeners to the price and discount price fields
    document.getElementById("price").addEventListener("input", calculateWasteDiscount);
    document.getElementById("discount_price").addEventListener("input", calculateWasteDiscount);


    // Function to calculate discount price
function calculateDiscountPrice() {
    const price = parseFloat(document.getElementById("add-price").value);
    const wasteDiscount = parseFloat(document.getElementById("waste_discount_add").value);

    // Log values for debugging
    console.log("Price:", price);
    console.log("Waste Discount:", wasteDiscount);
    
    if (!isNaN(price) && !isNaN(wasteDiscount) && price > 0 && wasteDiscount >= 0) {
        // Calculate the discount price
        const discountPrice = price - (price * (wasteDiscount / 100));
        document.getElementById("discount_price").value = discountPrice.toFixed(2); // Update discount price field
    } else {
        document.getElementById("discount_price").value = ''; // Clear discount price if invalid
    }
}

// Add event listeners to the price and waste discount fields
document.getElementById("add-price").addEventListener("input", calculateDiscountPrice);
document.getElementById("waste_discount_add").addEventListener("input", calculateDiscountPrice);
