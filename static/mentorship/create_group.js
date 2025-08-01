// Translation object
const translations = {
    en: {
        "create-group-title": "Create Group - Eduvia",
        "create-group-meta-desc": "Create a mentorship group in Eduvia's Mentorship System.",
        "create-group-meta-keywords": "create group, Eduvia, mentorship",
        "create-group-og-title": "Create Group - Eduvia",
        "create-group-og-desc": "Create a mentorship group in Eduvia's Mentorship System.",
        "hero-title": "Create a Group",
        "hero-desc": "Create a mentorship group to connect with others in Eduvia",
        "form-heading": "Create a New Group",
        "group-name-label": "Group Name",
        "description-label": "Description",
        "is-public-label": "Make this group public (visible to everyone)",
        "create-button": "Create Group",
        "back-to-dashboard": "Back to Dashboard",
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
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "create-group-title": "إنشاء مجموعة - إدوفيا",
        "create-group-meta-desc": "إنشاء مجموعة إرشاد في نظام الإرشاد بمنصة إدوفيا.",
        "create-group-meta-keywords": "إنشاء مجموعة, إدوفيا, الإرشاد",
        "create-group-og-title": "إنشاء مجموعة - إدوفيا",
        "create-group-og-desc": "إنشاء مجموعة إرشاد في نظام الإرشاد بمنصة إدوفيا.",
        "hero-title": "إنشاء مجموعة",
        "hero-desc": "إنشاء مجموعة إرشاد للتواصل مع الآخرين في إدوفيا",
        "form-heading": "إنشاء مجموعة جديدة",
        "group-name-label": "اسم المجموعة",
        "description-label": "الوصف",
        "is-public-label": "جعل هذه المجموعة عامة (مرئية للجميع)",
        "create-button": "إنشاء المجموعة",
        "back-to-dashboard": "العودة إلى لوحة التحكم",
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
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
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
    document.title = translations[newLang]["create-group-title"];

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

    // Set the title on page load
    document.title = translations[savedLang]["create-group-title"];
});