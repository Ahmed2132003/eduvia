const translations = {
    en: {
        "page-title": "Add Service - Eduvia",
        "meta-desc": "Add a new service to Eduvia's Skills Market.",
        "meta-keywords": "add service, Eduvia, skills market",
        "og-title": "Add Service - Eduvia",
        "og-desc": "Add a new service to Eduvia's Skills Market.",
        "hero-title": "Add a New Service",
        "hero-desc": "Offer your skills and services to the Eduvia community",
        "form-title": "Add Service",
        "label-title": "Service Title:",
        "label-skill": "Skill:",
        "label-price": "Price (Coins):",
        "label-delivery": "Delivery Time (Days):",
        "label-description": "Description:",
        "submit-btn": "Add Service",
        "back-to-services": "Back to Services",
        "view-skills": "View Skills",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-skills-market": "Skills Market",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "page-title": "إضافة خدمة - إدوفيا",
        "meta-desc": "أضف خدمة جديدة إلى سوق المهارات في إدوفيا.",
        "meta-keywords": "إضافة خدمة, إدوفيا, سوق المهارات",
        "og-title": "إضافة خدمة - إدوفيا",
        "og-desc": "أضف خدمة جديدة إلى سوق المهارات في إدوفيا.",
        "hero-title": "إضافة خدمة جديدة",
        "hero-desc": "اعرض مهاراتك وخدماتك لمجتمع إدوفيا",
        "form-title": "إضافة خدمة",
        "label-title": "عنوان الخدمة:",
        "label-skill": "المهارة:",
        "label-price": "السعر (نقاط):",
        "label-delivery": "وقت التسليم (أيام):",
        "label-description": "الوصف:",
        "submit-btn": "إضافة الخدمة",
        "back-to-services": "العودة إلى الخدمات",
        "view-skills": "عرض المهارات",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-skills-market": "سوق المهارات",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة."
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
    
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
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

    document.title = translations[newLang]["page-title"];
    localStorage.setItem('language', newLang);
}

// Apply saved theme and language on page load
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

    document.title = translations[savedLang]["page-title"];
});