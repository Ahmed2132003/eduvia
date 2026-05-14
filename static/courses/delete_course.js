// translations object for English and Arabic
const translations = {
    en: {
        "page-title": "Delete Course - Eduvia",
        "meta-desc": "Delete your course from Eduvia. Confirm deletion of course content and videos.",
        "meta-keywords": "Eduvia, delete course, instructor dashboard, course management",
        "meta-desc-ar": "Delete your course from Eduvia. Confirm deletion of course content and videos.",
        "meta-keywords-ar": "Eduvia, delete course, instructor dashboard, course management",
        "og-title": "Delete Course - Eduvia",
        "og-desc": "Confirm deletion of your course and all associated videos.",
        "title": "Eduvia",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-login": "Login",
        "hero-title": "Delete Course",
        "hero-desc": "Are you sure you want to delete this course? This action cannot be undone.",
        "confirm-delete": "Confirm Deletion",
        "delete-warning": "All videos, tasks, and student progress will be permanently deleted.",
        "delete-btn": "Yes, Delete Course",
        "cancel-btn": "Cancel",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "page-title": "حذف الدورة - إدوفيا",
        "meta-desc": "احذف دورتك من إدوفيا. تأكيد حذف المحتوى والفيديوهات.",
        "meta-keywords": "إدوفيا، حذف الدورة، لوحة تحكم المدربين، إدارة الدورات",
        "meta-desc-ar": "احذف دورتك من إدوفيا. تأكيد حذف المحتوى والفيديوهات.",
        "meta-keywords-ar": "إدوفيا، حذف الدورة، لوحة تحكم المدربين، إدارة الدورات",
        "og-title": "حذف الدورة - إدوفيا",
        "og-desc": "تأكيد حذف دورتك وجميع الفيديوهات المرتبطة.",
        "title": "إدوفيا",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-login": "تسجيل الدخول",
        "hero-title": "حذف الدورة",
        "hero-desc": "هل أنت متأكد من حذف هذه الدورة؟ هذا الإجراء لا يمكن التراجع عنه.",
        "confirm-delete": "تأكيد الحذف",
        "delete-warning": "سيتم حذف جميع الفيديوهات والمهام وتقدم الطلاب نهائيًا.",
        "delete-btn": "نعم، احذف الدورة",
        "cancel-btn": "إلغاء",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود. جميع الحقوق محفوظة."
    }
};

// Toggle mobile menu
function toggleMenu() {
    const menu = document.querySelector('.menu');
    if (menu) {
        menu.classList.toggle('active');
        console.log('Menu toggled:', menu.classList.contains('active'));
    }
}

// Toggle dark mode
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

// Toggle language between English and Arabic
function toggleLanguage() {
    const htmlRoot = document.getElementById('html-root');
    const currentLang = htmlRoot.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    
    // Update HTML lang and direction
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[newLang][key]) {
            element.textContent = translations[newLang][key];
        }
    });
    
    // Update page title
    document.title = translations[newLang]["page-title"];
    
    // Save preference
    localStorage.setItem('language', newLang);
}

// On page load
document.addEventListener('DOMContentLoaded', () => {
    // Restore theme
    const savedTheme = localStorage.getItem('theme');
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (toggleIcon) {
            toggleIcon.classList.remove('fa-moon');
            toggleIcon.classList.add('fa-sun');
        }
    }

    // Restore language
    const savedLang = localStorage.getItem('language') || 'en';
    const htmlRoot = document.getElementById('html-root');
    htmlRoot.setAttribute('lang', savedLang);
    htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');

    // Apply translations
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[savedLang][key]) {
            element.textContent = translations[savedLang][key];
        }
    });

    // Update title
    document.title = translations[savedLang]["page-title"];
});