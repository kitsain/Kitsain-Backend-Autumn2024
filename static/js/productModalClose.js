const addProductModal = document.getElementById("addProductModal");
const discardBtn = document.getElementById("discardChangesBtn");
const closeBtn = document.getElementsByClassName("close")[0];

function closeModal() {
    addProductModal.style.display = "none";
}

discardBtn.onclick = function() {
    closeModal();
}

closeBtn.onclick = function() {
    closeModal();
}

window.onclick = function(event) {
    if (event.target == addProductModal) {
        closeModal();
    }
}

const editProductModal = document.getElementById("editProductModal");
const discardBtn = document.getElementById("edit_discardChangesBtn");
const closeBtn = document.getElementsByClassName("close")[0];

function closeModal() {
    editProductModal.style.display = "none";
}

discardBtn.onclick = function() {
    closeModal();
}

closeBtn.onclick = function() {
    closeModal();
}

window.onclick = function(event) {
    if (event.target == editProductModal) {
        closeModal();
    }
}
