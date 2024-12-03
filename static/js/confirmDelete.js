let productIdToDelete = null; 

async function deleteProduct(productId) {
    productIdToDelete = productId; 
    document.getElementById("deleteConfirmationModal").style.display = "block"; 
}

confirmDeleteButton.onclick = async function() {
    try {
        const response = await fetch(`/remove_product/${productIdToDelete}`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error('Failed to delete product');
        }

        window.location.href = '/products_page'; 
    } catch (error) {
        console.error('There was a problem with deleting the product:', error);
        alert('Error deleting product: ' + error.message); 
    }
};

cancelDeleteButton.onclick = function() {
    deleteConfirmationModal.style.display = "none"; 
};

window.onclick = function(event) {
    if (event.target == deleteConfirmationModal) {
        deleteConfirmationModal.style.display = "none";
    }
};

document.getElementsByClassName("close-delete")[0].onclick = function() {
    deleteConfirmationModal.style.display = "none"; 
};
