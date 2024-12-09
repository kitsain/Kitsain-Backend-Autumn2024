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