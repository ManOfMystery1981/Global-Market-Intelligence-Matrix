// Vercel Speed Insights initialization
// This script injects Vercel Speed Insights to track Core Web Vitals
(function() {
    // Create the Speed Insights queue before the library loads
    window.si = window.si || function () { 
        (window.siq = window.siq || []).push(arguments); 
    };
    
    // Load the Speed Insights script
    var script = document.createElement('script');
    script.defer = true;
    script.src = '/_vercel/speed-insights/script.js';
    document.head.appendChild(script);
})();
