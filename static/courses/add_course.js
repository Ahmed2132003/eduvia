// Translation object
const translations = {
    en: {
        "add-course-title": "Add New Course - Eduvia",
        "add-course-meta-desc-en": "Create a new course on Eduvia's Instructor Dashboard. Share your expertise with students worldwide.",
        "add-course-meta-keywords-en": "Eduvia, add course, instructor dashboard, online teaching, course creation",
        "add-course-meta-desc-ar": "أنشئ دورة جديدة على لوحة تحكم المدربين في Eduvia. شارك خبراتك مع الطلاب حول العالم.",
        "add-course-meta-keywords-ar": "Eduvia، إضافة دورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إنشاء دورة",
        "add-course-og-title": "Add New Course - Eduvia",
        "add-course-og-desc": "Start teaching by creating a new course on Eduvia's Instructor Dashboard.",
        "add-course-twitter-title": "Add New Course - Eduvia",
        "add-course-twitter-desc": "Start teaching by creating a new course on Eduvia's Instructor Dashboard.",
        "hero-title": "Add New Course",
        "hero-desc": "Create a new course and share your expertise with students worldwide.",
        "form-title": "Add New Course",
        "form-submit": "Create Course",
        "form-cancel": "Cancel",
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
        "add-course-title": "إضافة دورة جديدة - إدوفيا",
        "add-course-meta-desc-en": "أنشئ دورة جديدة على لوحة تحكم المدربين في Eduvia. شارك خبراتك مع الطلاب حول العالم.",
        "add-course-meta-keywords-en": "Eduvia، إضافة دورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إنشاء دورة",
        "add-course-meta-desc-ar": "أنشئ دورة جديدة على لوحة تحكم المدربين في Eduvia. شارك خبراتك مع الطلاب حول العالم.",
        "add-course-meta-keywords-ar": "Eduvia، إضافة دورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إنشاء دورة",
        "add-course-og-title": "إضافة دورة جديدة - إدوفيا",
        "add-course-og-desc": "ابدأ التدريس بإنشاء دورة جديدة على لوحة تحكم المدربين في Eduvia.",
        "add-course-twitter-title": "إضافة دورة جديدة - إدوفيا",
        "add-course-twitter-desc": "ابدأ التدريس بإنشاء دورة جديدة على لوحة تحكم المدربين في Eduvia.",
        "hero-title": "إضافة دورة جديدة",
        "hero-desc": "أنشئ دورة جديدة وشارك خبراتك مع الطلاب حول العالم.",
        "form-title": "إضافة دورة جديدة",
        "form-submit": "إنشاء الدورة",
        "form-cancel": "إلغاء",
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
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    // Update the title
    document.title = translations[newLang]["add-course-title"];

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
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    // Set the title on page load
    document.title = translations[savedLang]["add-course-title"];
});