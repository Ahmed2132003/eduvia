const translations = {
    en: {
        "title": "Upload Recording - {{ session.title }} - Eduvia",
        "meta-desc": "Upload a recording for the '{{ session.title }}' live session on Eduvia to share with learners.",
        "meta-keywords": "Eduvia, live session, workshop, recording, upload, online learning, education platform",
        "og-title": "Upload Recording - {{ session.title }} - Eduvia",
        "og-desc": "Upload your video recording for the '{{ session.title }}' live session on Eduvia.",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "hero-title": "Upload Recording for {{ session.title }}",
        "hero-subtitle": "Share your session recording with learners to enhance their educational experience.",
        "hero-btn": "Upload Now",
        "container-title": "Upload Recording for {{ session.title }}",
        "form-label": "Video URL",
        "submit-btn": "Upload Recording",
        "back-btn": "Back to Sessions",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "title": "رفع تسجيل - {{ session.title }} - إدوفيا",
        "meta-desc": "ارفع تسجيلًا للجلسة المباشرة '{{ session.title }}' على إدوفيا لمشاركته مع المتعلمين.",
        "meta-keywords": "إدوفيا, جلسة مباشرة, ورشة عمل, تسجيل, رفع, تعلم عبر الإنترنت, منصة تعليمية",
        "og-title": "رفع تسجيل - {{ session.title }} - إدوفيا",
        "og-desc": "ارفع تسجيل الفيديو الخاص بك للجلسة المباشرة '{{ session.title }}' على إدوفيا.",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "hero-title": "رفع تسجيل لـ {{ session.title }}",
        "hero-subtitle": "شارك تسجيل جلستك مع المتعلمين لتحسين تجربتهم التعليمية.",
        "hero-btn": "ارفع الآن",
        "container-title": "رفع تسجيل لـ {{ session.title }}",
        "form-label": "رابط الفيديو",
        "submit-btn": "رفع التسجيل",
        "back-btn": "العودة إلى الجلسات",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود. جميع الحقوق محفوظة."
    }
};

function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
}

// Dark Mode Toggle
function toggleDarkMode() {
    const body = document.body;
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    body.classList.toggle('dark-mode');
    
    if (body.classList.contains('dark-mode')) {
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        toggleIcon.classList.remove('fa-sun');
        toggleIcon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
    }
}

// Language Toggle
function toggleLanguage() {
    const htmlRoot = document.getElementById('html-root');
    const currentLang = htmlRoot.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    
    // Update lang and direction
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    // Update the title
    document.title = translations[newLang]["title"];
    
    localStorage.setItem('language', newLang);
}

// Apply saved theme and language on page load
document.addEventListener('DOMContentLoaded', () => {
    // Apply Dark Mode
    const savedTheme = localStorage.getItem('theme');
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
    }

    // Apply Language
    const savedLang = localStorage.getItem('language') || 'en';
    const htmlRoot = document.getElementById('html-root');
    htmlRoot.setAttribute('lang', savedLang);
    htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["title"];

    // Validate Google Drive URL
    const form = document.getElementById('upload-form-element');
    const urlInput = document.getElementById('video_file');
    const errorMessage = document.getElementById('url-error');

    form.addEventListener('submit', (event) => {
        const url = urlInput.value;
        if (!url.startsWith('https://drive.google.com/file/d/')) {
            event.preventDefault();
            errorMessage.style.display = 'block';
        } else {
            errorMessage.style.display = 'none';
        }
    });
});