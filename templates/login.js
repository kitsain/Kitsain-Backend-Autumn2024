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