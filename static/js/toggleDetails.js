function toggleDetails(button) {
    const details = button.closest('.product-box').querySelector('.additional-details');
    if (details.style.display === "none" || details.style.display === "") {
        details.style.display = "block";
        button.textContent = "-"; 
    } else {
        details.style.display = "none";
        button.textContent = "+"; 
    }
}