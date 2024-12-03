document.addEventListener("DOMContentLoaded", function () {
    const addDetailedInfo = document.getElementById("addDetailedInfoModal");
    const previousModal = document.getElementById("addProductModal");

    const cancelBtn = document.getElementById("cancelBtn");

    if (cancelBtn) {
        cancelBtn.onclick = function () {
            addDetailedInfo.style.display = "none";
            previousModal.style.display = "block";
        };
    }

    window.onclick = function (event) {
        if (event.target === addDetailedInfo) {
            addDetailedInfo.style.display = "none";
        } else if (event.target === previousModal) {
            previousModal.style.display = "none";
        }
    };
});

document.addEventListener("DOMContentLoaded", function () {
    const addDetailedInfo = document.getElementById("editDetailedInfoModal");
    const previousModal = document.getElementById("editProductModal");

    const cancelBtn = document.getElementById("cancelBtn-edit");

    if (cancelBtn) {
        cancelBtn.onclick = function () {
            addDetailedInfo.style.display = "none";
            previousModal.style.display = "block";
        };
    }

    window.onclick = function (event) {
        if (event.target === addDetailedInfo) {
            addDetailedInfo.style.display = "none";
        } else if (event.target === previousModal) {
            previousModal.style.display = "none";
        }
    };
});
