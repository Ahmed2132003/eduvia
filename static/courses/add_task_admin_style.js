// static/courses/add_task_admin_style.js

const translations = {
    en: {
        "page-title": "Add Task - Eduvia",
        "meta-desc": "Add a new task to your course on Eduvia's Instructor Dashboard. Create and manage tasks with questions for better engagement.",
        "meta-keywords": "Eduvia, add task, instructor tools, course management, online education",
        "og-title": "Add Task - Eduvia",
        "og-desc": "Create tasks for your course videos on Eduvia's Instructor Dashboard.",
        "twitter-title": "Add Task - Eduvia",
        "twitter-desc": "Create tasks for your course videos on Eduvia's Instructor Dashboard.",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-subscribe": "subscribe",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "hero-title": "Add New Task",
        "form-label-video": "Video",
        "form-label-title": "Task Title",
        "form-label-order": "Task Order",
        "form-label-questions": "Questions (JSON - Copy from Django Admin)",
        "submit-btn": "Save Task",
        "back-link": "Cancel",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved.",
    },
    ar: {
        "page-title": "إضافة مهمة - إدوفيا",
        "meta-desc": "إضافة مهمة جديدة إلى دورتك على لوحة تحكم المدربين في إدوفيا. أنشئ وأدر المهام مع الأسئلة لتعزيز التفاعل.",
        "meta-keywords": "إدوفيا، إضافة مهمة، أدوات المدربين، إدارة الدورات، التعليم عبر الإنترنت",
        "og-title": "إضافة مهمة - إدوفيا",
        "og-desc": "إنشاء مهام لفيديوهات دورتك على لوحة تحكم المدربين في إدوفيا.",
        "twitter-title": "إضافة مهمة - إدوفيا",
        "twitter-desc": "إنشاء مهام لفيديوهات دورتك على لوحة تحكم المدربين في إدوفيا.",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-subscribe": "اشتراك",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "hero-title": "إضافة مهمة جديدة",
        "form-label-video": "الفيديو",
        "form-label-title": "عنوان المهمة",
        "form-label-order": "ترتيب المهمة",
        "form-label-questions": "الأسئلة (JSON - نسخ من لوحة الإدارة في جانجو)",
        "submit-btn": "حفظ المهمة",
        "back-link": "إلغاء",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة.",
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

    document.title = translations[newLang]["page-title"];
    
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

    document.title = translations[savedLang]["page-title"];
});