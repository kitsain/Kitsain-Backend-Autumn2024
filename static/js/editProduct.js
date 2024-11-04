
    // Get the modals and other elements
    const editModal = document.getElementById("editProductModal");
    const editButtons = document.querySelectorAll(".btn-primary-edit");

    // Open the edit modal and populate fields
    editButtons.forEach(button => {
        button.onclick = function(event) {
            event.preventDefault();
            const productBox = this.closest(".product-box");
            document.getElementById("edit_product_id").value = productBox.dataset.productId;
            document.getElementById("edit_product_name").value = productBox.querySelector(".product-name").textContent;
            document.getElementById("edit_shop").value = productBox.querySelector(".product-shop").textContent;
            document.getElementById("edit_price").value = productBox.querySelector(".product-price").textContent.replace(' €', '');
            document.getElementById("edit_waste_discount").value = productBox.querySelector(".product-discount").textContent.replace(' - ', '').replace('%', '').trim();
            document.getElementById("edit_expiration_date").value = productBox.querySelector(".product-expiration").textContent;
            editModal.style.display = "block";
        };
    });

    // Close the edit modal
    document.getElementsByClassName("close-edit")[0].onclick = function() {
        editModal.style.display = "none";
    };

    // Close modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == editModal) {
            editModal.style.display = "none";
        }
    };

    // Handle the form submission for editing products
    document.addEventListener("DOMContentLoaded", () => {
        const editForm = document.getElementById("editForm");

        editForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const formData = new FormData(editForm);
            const data = Object.fromEntries(formData);

            try {
                const response = await fetch('/update_product', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const result = await response.json();
                alert(result.message);
                editForm.reset();
                editModal.style.display = "none"; // Close the modal after saving changes
                window.location.href = '/products_page';
            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
            }
        });
    });
