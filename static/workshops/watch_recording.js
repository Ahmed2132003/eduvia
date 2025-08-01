const translations = {
    en: {
        "title": "Watch Recording - {{ recording.live_session.title }} - Eduvia",
        "meta-desc": "Watch the recorded session '{{ recording.live_session.title }}' on Eduvia to learn at your own pace.",
        "meta-keywords": "Eduvia, recorded session, workshop, watch recording, online learning, education platform",
        "og-title": "Watch Recording - {{ recording.live_session.title }} - Eduvia",
        "og-desc": "View the recording of '{{ recording.live_session.title }}' on Eduvia, uploaded by expert instructors.",
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
        "hero-title": "Watch Recording: {{ recording.live_session.title }}",
        "hero-subtitle": "Enjoy the recorded session '{{ recording.live_session.title }}' at your own pace.",
        "hero-btn": "Watch Now",
        "container-title": "Recording: {{ recording.live_session.title }}",
        "uploaded-label": "Uploaded:",
        "instructor-label": "Instructor:",
        "video-error": "Failed to load the video. Please check the URL or try again later.",
        "back-btn": "Back to Sessions",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "title": "مشاهدة التسجيل - {{ recording.live_session.title }} - إدوفيا",
        "meta-desc": "شاهد الجلسة المسجلة '{{ recording.live_session.title }}' على إدوفيا للتعلم بوتيرتك الخاصة.",
        "meta-keywords": "إدوفيا, جلسة مسجلة, ورشة عمل, مشاهدة تسجيل, تعلم عبر الإنترنت, منصة تعليمية",
        "og-title": "مشاهدة التسجيل - {{ recording.live_session.title }} - إدوفيا",
        "og-desc": "شاهد تسجيل '{{ recording.live_session.title }}' على إدوفيا، تم رفعه بواسطة مدربين خبراء.",
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
        "hero-title": "مشاهدة التسجيل: {{ recording.live_session.title }}",
        "hero-subtitle": "استمتع بمشاهدة الجلسة المسجلة '{{ recording.live_session.title }}' بوتيرتك الخاصة.",
        "hero-btn": "شاهد الآن",
        "container-title": "التسجيل: {{ recording.live_session.title }}",
        "uploaded-label": "تم الرفع:",
        "instructor-label": "المدرب:",
        "video-error": "فشل تحميل الفيديو. يرجى التحقق من الرابط أو المحاولة مرة أخرى لاحقًا.",
        "back-btn": "العودة إلى الجلسات",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
    }
};

// Function to convert Google Drive URL to embeddable format
function convertToEmbedUrl(url) {
    if (url.includes('drive.google.com/file/d/')) {
        return url.replace('/view', '/preview');
    }
    return url;
}

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

    // Convert Google Drive URL to embeddable format
    const iframe = document.querySelector('.video-iframe');
    if (iframe) {
        iframe.src = convertToEmbedUrl(iframe.src);
    }
});