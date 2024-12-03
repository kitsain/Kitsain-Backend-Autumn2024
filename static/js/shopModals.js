/**
 * Handles the opening and closing of the Add Product modal.
 * This function assigns event listeners to the 'Add Product' button, the close button,
 * and the window to control the display of the modal.
 */
function handleAddShopModal() {
    var modal = document.getElementById("addProductModal");
    var btn = document.getElementById("addButton");
    var span = modal.getElementsByClassName("close")[0];

    btn.onclick = function(event) {
        event.preventDefault();
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

/**
 * Handles the opening and closing of the Filter Products modal.
 * This function assigns event listeners to the 'Filter Products' button, the close button,
 * and the window to control the display of the modal.
 */
function handleFilterShopModal() {
    var modal = document.getElementById("filterShopsModal");
    var btn = document.getElementById("filterButton");
    var span = modal.getElementsByClassName("close")[0];

    btn.onclick = function(event) {
        event.preventDefault();
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

// Initialize modals
handleAddShopModal();
handleFilterShopModal();
