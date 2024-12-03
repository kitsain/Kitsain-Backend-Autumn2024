document.querySelectorAll(".btn-secondary-add").forEach(button => {
    button.addEventListener("click", function () {
        if (this.classList.contains("selected")) {
            this.classList.remove("selected");
            document.getElementById("product_amount").value = ""; 
        } else {
            document.querySelectorAll(".btn-secondary-add").forEach(btn => btn.classList.remove("selected"));
            this.classList.add("selected");
            const selectedValue = this.getAttribute("data-value");
            document.getElementById("product_amount").value = selectedValue;
        }
    });
});

document.querySelectorAll(".btn-secondary-add-edit").forEach(button => {
    button.addEventListener("click", function () {
        if (this.classList.contains("active")) {
            this.classList.remove("active");
            document.getElementById("product_amount").value = ""; 
        } else {
            document.querySelectorAll(".btn-secondary-add-edit").forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");
            const selectedValue = this.getAttribute("data-value");
            document.getElementById("product_amount").value = selectedValue; 
        }
    });
});
