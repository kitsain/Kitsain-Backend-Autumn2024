function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        // default language english
        pageLanguage: 'en',
        // languages available: English, Finnish, Swedish
        includedLanguages: 'en,fi,sv',
        // simple layout
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,

    }, 'google_translate_element');
}

// loads the google translate script
function loadGoogleTranslateScript() {
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    document.body.appendChild(script);
}

loadGoogleTranslateScript();