document.getElementById('togglePassword').addEventListener('click', function(event) {
    const passwordInput = document.getElementById('userpassword');
    event.preventDefault();

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        this.textContent = 'Hide';
    } else {
        passwordInput.type = 'password';
        this.textContent = 'Reveal';
    }
});


document.getElementById('loginForm').addEventListener('submit', function(event) {
    

    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('userpassword').value;
    const errorMessage = document.getElementById('errorMessage');

    if (username === "" || password === "") {
        errorMessage.textContent = 'Please fill both fields!'
        errorMessage.style.visibility = 'visible';
    } else {
        errorMessage.textContent = "";
        errorMessage.style.visibility = 'hidden';
        window.location.href = 'index.html';
    }

});

function togglePasswordVisibility() {
    const passwordInput = document.getElementById("userpassword");
    const toggleButton = document.getElementById("togglePassword");
    if (passwordInput.type === "password") {
        passwordInput.type = "text"; 
        toggleButton.innerHTML = "&#128275;"; 
    } else {
        passwordInput.type = "password"; 
        toggleButton.innerHTML = "&#128274;";
    }
}
// Halutaanko zoomaus ominaisuus vai ei?
// document.addEventListener('wheel', function(event) {
//     if (event.ctrlKey) {
//         event.preventDefault();
//     }
// }, { passive: false });

// document.addEventListener('touchmove', function(event) {
//     if (event.scale !== 1) {
//         event.preventDefault();
//     }
// }, { passive: false });