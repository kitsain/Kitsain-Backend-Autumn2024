   // Get the button and modal elements
   const addProductModal = document.getElementById('addProductModal');
   const addDetailedInfoModal = document.getElementById('addDetailedInfoModal');
   const closeAddDetailedInfoModal = addDetailedInfoModal.querySelector('.close');
   const addProductForm = document.getElementById('add-product-form');

   // Get the input fields for detailed
   const barcodeDetailedInput = document.getElementById('barcode_detailed');
   const productNameDetailedInput = document.getElementById('product_name_detailed');

   // Get the input fields for detailed and other elements
   const barcodeInput = document.getElementById('barcode');
   const productNameInput = document.getElementById('product_name');
   const shopInput = document.getElementById('shop_add');
   const priceInput = document.getElementById('add-price');
   const discountPriceInput = document.getElementById('discount_price');
   const discountValidFromInput = document.getElementById('discount_valid_from');
   const discountValidToInput = document.getElementById('discount_valid_to');
   const wasteDiscountInput = document.getElementById('waste_discount_add');
   const expirationDateInput = document.getElementById('expiration_date');
   const productAmountInput = document.getElementById('product_amount');


   // Handle "More product information" button click
   moreInfoBtn.addEventListener('click', function () {

       if (addProductForm.checkValidity()) {
           barcodeDetailedInput.value = barcodeInput.value;
           productNameDetailedInput.value = productNameInput.value;

           localStorage.setItem('barcode', barcodeInput.value);
           localStorage.setItem('product_name', productNameInput.value);
           localStorage.setItem('shop', shopInput.value);
           localStorage.setItem('price', priceInput.value);
           localStorage.setItem('discount_price', discountPriceInput.value);
           localStorage.setItem('discount_valid_from', discountValidFromInput.value);
           localStorage.setItem('discount_valid_to', discountValidToInput.value);
           localStorage.setItem('waste_discount', wasteDiscountInput.value);
           localStorage.setItem('expiration_date', expirationDateInput.value);
           localStorage.setItem('product_amount', productAmountInput.value);

           console.log(shopInput.value);
           console.log(expirationDateInput.value);

           // Send the data to the server using Fetch API
           fetch('/save_product_data', {
               method: 'POST',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify({
                   barcode: barcodeInput.value,
                   product_name: productNameInput.value,
                   shop: shopInput.value,
                   price: priceInput.value,
                   discount_price: discountPriceInput.value,
                   discount_valid_from: discountValidFromInput.value,
                   discount_valid_to: discountValidToInput.value,
                   waste_discount: wasteDiscountInput.value,
                   expiration_date: expirationDateInput.value,
                   product_amount: productAmountInput.value
               })
           })
           .then(response => response.json())
           .then(data => {
               console.log('Product data saved:', data);
               // Optionally do something with the response from the server
           })
           .catch(error => {
               console.error('Error saving product data:', error);
           });

           //addProductForm.submit();

           addProductModal.style.display = 'none';
           addDetailedInfoModal.style.display = 'block';

       } else {
           // Show validation errors if the form is invalid
           addProductForm.reportValidity();
       }
   });

   // Close the addDetailedInfoModal when the close button is clicked
   closeAddDetailedInfoModal.addEventListener('click', function() {
       addDetailedInfoModal.style.display = 'none';
   });

   // Close the modal when clicked outside the modal
   window.addEventListener('click', function(event) {
       if (event.target === addDetailedInfoModal) {
           addDetailedInfoModal.style.display = 'none';
       }
   });

   // Handle discard changes button functionality
   const discardChangesBtn = document.getElementById('discardChangesBtn');
   discardChangesBtn.addEventListener('click', function() {
       addProductModal.style.display = 'none';
   });

   // Close the addProductModal when the close button is clicked
   const closeAddProductModal = addProductModal.querySelector('.close');
   closeAddProductModal.addEventListener('click', function() {
       addProductModal.style.display = 'none';
   });