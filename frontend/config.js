/* Local: Flask runs on port 5000. Production: Render backend. */
window.PRANJAL_CONFIG = {
    API_BASE:
        (location.hostname === 'localhost' ||
         location.hostname === '127.0.0.1')
            ? 'http://127.0.0.1:5000'
            : 'https://pranjal-engitech.onrender.com'
};