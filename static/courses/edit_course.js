const translations = {
    en: {
        "page-title": "Edit Course - Eduvia",
        "meta-desc": "Edit your courses on Eduvia's Instructor Dashboard. Update and organize your educational content with ease.",
        "meta-keywords": "Eduvia, edit course, instructor dashboard, online teaching, course management",
        "meta-desc-ar": "تعديل دوراتك على لوحة تحكم المدربين في إدوفيا. قم بتحديث وتنظيم محتواك التعليمي بسهولة.",
        "meta-keywords-ar": "إدوفيا، تعديل الدورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الدورات",
        "og-title": "Edit Course - Eduvia",
        "og-desc": "Update your teaching content with Eduvia's Instructor Dashboard. Edit courses and engage with students.",
        "twitter-title": "Edit Course - Eduvia",
        "twitter-desc": "Update your teaching content with Eduvia's Instructor Dashboard. Edit courses and engage with students.",
        "hero-title": "Edit Course",
        "hero-desc": "Update your course details and content to enhance the learning experience.",
        "edit-course-title": "Edit Course",
        "edit-course-desc": "Update your course details below.",
        "form-placeholder": "Course edit form goes here.",
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
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "page-title": "تعديل الدورة - إدوفيا",
        "meta-desc": "تعديل دوراتك على لوحة تحكم المدربين في إدوفيا. قم بتحديث وتنظيم محتواك التعليمي بسهولة.",
        "meta-keywords": "إدوفيا، تعديل الدورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الدورات",
        "meta-desc-ar": "تعديل دوراتك على لوحة تحكم المدربين في إدوفيا. قم بتحديث وتنظيم محتواك التعليمي بسهولة.",
        "meta-keywords-ar": "إدوفيا، تعديل الدورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الدورات",
        "og-title": "تعديل الدورة - إدوفيا",
        "og-desc": "قم بتحديث محتوى تدريسك مع لوحة تحكم المدربين في إدوفيا. تعديل الدورات والتفاعل مع الطلاب.",
        "twitter-title": "تعديل الدورة - إدوفيا",
        "twitter-desc": "قم بتحديث محتوى تدريسك مع لوحة تحكم المدربين في إدوفيا. تعديل الدورات والتفاعل مع الطلاب.",
        "hero-title": "تعديل الدورة",
        "hero-desc": "قم بتحديث تفاصيل دورتك ومحتواها لتحسين تجربة التعلم.",
        "edit-course-title": "تعديل الدورة",
        "edit-course-desc": "قم بتحديث تفاصيل دورتك أدناه.",
        "form-placeholder": "نموذج تعديل الدورة يوضع هنا.",
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
            element.setAttribute('content', text);
        } else {
            element.textContent = text;
        }
    });

    // Update the title
    document.title = translations[newLang]["page-title"];

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
            element.setAttribute('content', text);
        } else {
            element.textContent = text;
        }
    });

    // Set the title on page load
    document.title = translations[savedLang]["page-title"];
});