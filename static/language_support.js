
// Google Translate initialization function
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'en', // default language
        includedLanguages: 'en,fi' // Available languages: English and Finnish
    }, 'google_translate_element');
}

// Function to load the Google Translate script
function loadGoogleTranslateScript() {
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    document.body.appendChild(script);
}

// Initialize the page with the default language (English)
loadGoogleTranslateScript();