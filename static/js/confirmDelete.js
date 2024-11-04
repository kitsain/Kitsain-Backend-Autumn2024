// JavaScript for handling deletion confirmation
let productIdToDelete = null; // Variable to store the product ID to delete

async function deleteProduct(productId) {
    productIdToDelete = productId; // Store the ID of the product to delete
    document.getElementById("deleteConfirmationModal").style.display = "block"; // Show the confirmation modal
}

// Confirm deletion
confirmDeleteButton.onclick = async function() {
    try {
        const response = await fetch(`/remove_product/${productIdToDelete}`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error('Failed to delete product');
        }

        // Redirect to the products_page after successful deletion
        window.location.href = '/products_page'; // Redirect to the products page
    } catch (error) {
        console.error('There was a problem with deleting the product:', error);
        alert('Error deleting product: ' + error.message); // Provide feedback on error
    }
};

// Cancel deletion
cancelDeleteButton.onclick = function() {
    deleteConfirmationModal.style.display = "none"; // Hide the modal if canceled
};

// Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target == deleteConfirmationModal) {
        deleteConfirmationModal.style.display = "none";
    }
};

// Close modal when clicking on the close button (x)
document.getElementsByClassName("close-delete")[0].onclick = function() {
    deleteConfirmationModal.style.display = "none"; // Hide the modal
};
