// document.addEventListener("DOMContentLoaded", function() {
//     const wordGrid = document.querySelector('.word-grid');
//     const animations = ['fadeIn', 'slideIn', 'rotate3D' ];
// const translations = [
//     "word ", // English
//     "palabra ", // Spanish
//     "mot ", // French
//     "Wort ", // German
//     "palavra ", // Portuguese
//     "woord ", // Dutch
//     "słowo ", // Polish
//     "parola ", // Italian
//     "ord ", // Swedish
//     "sana ", // Finnish
//     "kata ", // Indonesian
//     "szó ", // Hungarian
//     "slovo ", // Czech
//     "kelime ", // Turkish
//     "ordet ", // Norwegian
//     "duma ", // Russian
//     "hituzi ", // Japanese
//     "danǎo ", // Chinese Simplified
//     "shabd ", // Hindi
//     "từ ", // Vietnamese
//     "salita ", // Filipino
//     "slovo ", // Slovak
//     "mots ", // Haitian Creole
//     "vorto ", // Esperanto
//     "sõna ", // Estonian
//     "vārds ", // Latvian
//     "žodis ", // Lithuanian
//     "leat ", // Samoan
//     "sanaa ", // Swahili
//     "cuvânt ", // Romanian
//     "slovo ", // Serbian
//     "tangos ", // Maltese
//     "palavra ", // Galician
//     "fjalë ", // Albanian
//     "bywoord ", // Afrikaans
//     "erey ", // Somali
//     "sana ", // Zulu
//     "kupu ", // Maori
//     "slovo ", // Croatian
//     "tutvumine " // Icelandic
// ];


//     for (let i = 1; i <= 40; i++) {
//         const wordDiv = document.createElement('div');
//         wordDiv.className = 'word';
//         wordDiv.textContent = translations[i-1] || 'wordUpp'; // Replace with the translated words
//         const randomAnimation = animations[Math.floor(Math.random() * animations.length)];
//         const delay = (i * 0.1).toFixed(1);
//         wordDiv.style.animation = `${randomAnimation} 6s infinite alternate`;
//         wordDiv.style.animationDelay = `${delay}s`;
//         wordGrid.appendChild(wordDiv);
//     }
// });



document.addEventListener("DOMContentLoaded", function() {
    const wordGrid = document.querySelector('.word-grid');
    const animations = ['fadeIn', 'slideIn', 'rotate3D' ];
    const colors = ['--pink', '--red', '--yellow'];
    const translations = [
        "word ", // English
        "palabra ", // Spanish
        "mot ", // French
        "Wort ", // German
        "palavra ", // Portuguese
        "woord ", // Dutch
        "słowo ", // Polish
        "parola ", // Italian
        "ord ", // Swedish
        "sana ", // Finnish
        "kata ", // Indonesian
        "szó ", // Hungarian
        "slovo ", // Czech
        "kelime ", // Turkish
        "ordet ", // Norwegian
        "duma ", // Russian
        "hituzi ", // Japanese
        "danǎo ", // Chinese Simplified
        "shabd ", // Hindi
        "từ ", // Vietnamese
        "salita ", // Filipino
        "slovo ", // Slovak
        "mots ", // Haitian Creole
        "vorto ", // Esperanto
        "sõna ", // Estonian
        "vārds ", // Latvian
        "žodis ", // Lithuanian
        "leat ", // Samoan
        "sanaa ", // Swahili
        "cuvânt ", // Romanian
        "slovo ", // Serbian
        "tangos ", // Maltese
        "palavra ", // Galician
        "fjalë ", // Albanian
        "bywoord ", // Afrikaans
        "erey ", // Somali
        "sana ", // Zulu
        "kupu ", // Maori
        "slovo ", // Croatian
        "tutvumine " // Icelandic
    ];
    
    // Function to apply a random animation to a word element
    const applyRandomAnimation = (wordDiv, delay) => {
        const randomAnimation = animations[Math.floor(Math.random() * animations.length)];
        wordDiv.style.animation = `${randomAnimation} 6s infinite alternate`;
        wordDiv.style.animationDelay = `${delay}s`;
    };

    
    // Create the word divs and populate the grid
    for (let i = 1; i <= 40; i++) {
        const wordDiv = document.createElement('div');
        wordDiv.className = 'word';
        wordDiv.textContent = translations[i-1];
        const delay = (i * 0.1).toFixed(1);
        applyRandomAnimation(wordDiv, delay);
        wordGrid.appendChild(wordDiv);

        // Change the animation when an iteration finishes
        wordDiv.addEventListener('animationiteration', () => {
            applyRandomAnimation(wordDiv, 0);
        });
    }
    
    // Function to randomly assign colors to 3 divs
    const assignRandomColors = () => {
        const words = document.querySelectorAll('.word');
        words.forEach(word => word.style.removeProperty('color')); // Remove existing colors

        const shuffledIndices = Array.from({ length: 40 }, (_, i) => i);
        for (let i = shuffledIndices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffledIndices[i], shuffledIndices[j]] = [shuffledIndices[j], shuffledIndices[i]];
        }

        // Assign new colors to random divs
        for (let i = 0; i < 3; i++) {
            const color = getComputedStyle(document.documentElement).getPropertyValue(colors[i]);
            words[shuffledIndices[i]].style.color = color;
        }
    };

    // Initially assign colors
    assignRandomColors();

    // Re-assign colors every 4 seconds (to align with animation duration)
    setInterval(assignRandomColors, 6000);
});
