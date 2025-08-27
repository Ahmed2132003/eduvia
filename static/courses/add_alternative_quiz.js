const translations = {
    en: {
        "title": "Add Alternative Quiz - Eduvia",
        "meta-description": "Add a new alternative quiz to your course on Eduvia Platform. Create and manage quizzes to enhance your learning experience.",
        "meta-keywords": "Eduvia, add quiz, alternative quiz, course management, online learning, education platform",
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
        "hero-title": "Add Alternative Quiz",
        "submit-btn": "Add Quiz",
        "back-link": "Back to Course",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "title": "إضافة اختبار بديل - إدوفيا",
        "meta-description": "إضافة اختبار بديل جديد إلى دورتك على منصة إدوفيا. أنشئ وأدر الاختبارات لتعزيز تجربتك التعليمية.",
        "meta-keywords": "إدوفيا, إضافة اختبار, اختبار بديل, إدارة الدورات, التعلم عبر الإنترنت, منصة تعليمية",
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
        "hero-title": "إضافة اختبار بديل",
        "submit-btn": "إضافة الاختبار",
        "back-link": "العودة إلى الدورة",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة."
    }
};

function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
}

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

function toggleLanguage() {
    const htmlRoot = document.getElementById('html-root');
    const currentLang = htmlRoot.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        element.textContent = translations[newLang][key];
    });

    document.querySelectorAll('meta[data-translate]').forEach(meta => {
        const key = meta.getAttribute('data-translate');
        meta.setAttribute('content', translations[newLang][key]);
    });

    document.title = translations[newLang]["title"];
    
    localStorage.setItem('language', newLang);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
    }

    const savedLang = localStorage.getItem('language') || 'en';
    const htmlRoot = document.getElementById('html-root');
    htmlRoot.setAttribute('lang', savedLang);
    htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        element.textContent = translations[savedLang][key];
    });

    document.querySelectorAll('meta[data-translate]').forEach(meta => {
        const key = meta.getAttribute('data-translate');
        meta.setAttribute('content', translations[savedLang][key]);
    });

    document.title = translations[savedLang]["title"];
});