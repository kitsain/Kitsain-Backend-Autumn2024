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

