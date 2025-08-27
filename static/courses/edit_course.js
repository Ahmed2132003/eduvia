const translations = {
    en: {
        "page-title": "Edit Course - Eduvia",
        "meta-desc": "Edit your courses on Eduvia's Instructor Dashboard. Update course details and manage educational content with ease.",
        "meta-keywords": "Eduvia, edit course, instructor dashboard, course management, educational platform",
        "meta-desc-ar": "تعديل دوراتك على لوحة تحكم المدربين في إدوفيا. تحديث تفاصيل الدورة وإدارة المحتوى التعليمي بسهولة.",
        "meta-keywords-ar": "إدوفيا، تعديل الدورة، لوحة تحكم المدربين، إدارة الدورات، منصة تعليمية",
        "og-title": "Edit Course - Eduvia",
        "og-desc": "Easily update and manage your course content on Eduvia's Instructor Dashboard.",
        "twitter-title": "Edit Course - Eduvia",
        "twitter-desc": "Easily update and manage your course content on Eduvia's Instructor Dashboard.",
        "title": "Eduvia",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-subscribe": "Subscribe",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "hero-title": "Edit Course",
        "hero-desc": "Update your course details and manage your educational content with ease.",
        "edit-course-title": "Edit Course",
        "edit-course-desc": "Modify the course title, description, or category below.",
        "save-changes": "Save Changes",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "page-title": "تعديل الدورة - إدوفيا",
        "meta-desc": "تعديل دوراتك على لوحة تحكم المدربين في إدوفيا. تحديث تفاصيل الدورة وإدارة المحتوى التعليمي بسهولة.",
        "meta-keywords": "إدوفيا، تعديل الدورة، لوحة تحكم المدربين، إدارة الدورات، منصة تعليمية",
        "meta-desc-ar": "تعديل دوراتك على لوحة تحكم المدربين في إدوفيا. تحديث تفاصيل الدورة وإدارة المحتوى التعليمي بسهولة.",
        "meta-keywords-ar": "إدوفيا، تعديل الدورة، لوحة تحكم المدربين، إدارة الدورات، منصة تعليمية",
        "og-title": "تعديل الدورة - إدوفيا",
        "og-desc": "تحديث وإدارة محتوى دوراتك بسهولة على لوحة تحكم المدربين في إدوفيا.",
        "twitter-title": "تعديل الدورة - إدوفيا",
        "twitter-desc": "تحديث وإدارة محتوى دوراتك بسهولة على لوحة تحكم المدربين في إدوفيا.",
        "title": "إدوفيا",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-subscribe": "الاشتراك",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "hero-title": "تعديل الدورة",
        "hero-desc": "تحديث تفاصيل الدورة وإدارة المحتوى التعليمي بسهولة.",
        "edit-course-title": "تعديل الدورة",
        "edit-course-desc": "عدل عنوان الدورة، الوصف، أو الفئة أدناه.",
        "save-changes": "حفظ التغييرات",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة."
    }
};

function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
    console.log('Menu toggled:', menu.classList.contains('active')); // Debugging
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
        element.textContent = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'input' && element.getAttribute('type') === 'text') {
            element.setAttribute('placeholder', translations[newLang][key]);
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
        const text = translations[savedLang][key];
        element.textContent = text;
        if (element.tagName.toLowerCase() === 'input' && element.getAttribute('type') === 'text') {
            element.setAttribute('placeholder', text);
        }
    });

    document.title = translations[savedLang]["page-title"];
});