var modal = document.getElementById("addProductModal");
var discardBtn = document.getElementById("discardChangesBtn");
var closeBtn = document.getElementsByClassName("close")[0];

function closeModal() {
    modal.style.display = "none";
}

discardBtn.onclick = function() {
    closeModal();
}

closeBtn.onclick = function() {
    closeModal();
}

window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
}

var modal = document.getElementById("editProductModal");
var discardBtn = document.getElementById("edit_discardChangesBtn");
var closeBtn = document.getElementsByClassName("close")[0];

function closeModal() {
    modal.style.display = "none";
}

discardBtn.onclick = function() {
    closeModal();
}

closeBtn.onclick = function() {
    closeModal();
}

window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
}
