console.log("test");
const emailForm = document.getElementById('emailForm');

console.log(emailForm);
sendButton.addEventListener('on_submit', function(event)
{
    console.log('Button clicked');
    event.preventDefault();
});

document.getElementById('sendbutton').addEventListener('click', function(event)
{
    console.log('Button clicked');
    event.preventDefault();
});
/*
    event.preventDefault();

    const email = document.querySelector("#email");

    const emailagain = document.querySelector("#emailagain");
    
    if (email.value != emailagain.value) 
        {
            console.log("Kenttien arvojen on oltava samat!");
        }*/