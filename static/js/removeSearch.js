        document.getElementById("remove-search")?.addEventListener("click", function(event) {
            event.preventDefault();
    
            const searchInput = document.querySelector("input[name='query']");
            searchInput.value = '';
    
            window.location.href = '/index';

        });