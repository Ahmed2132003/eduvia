// Translation object
const translations = {
    en: {
        "page-title": "Edit Video - Eduvia",
        "meta-desc": "Edit your video content on Eduvia's Instructor Dashboard. Update video details to enhance your course.",
        "meta-keywords": "Eduvia, edit video, instructor dashboard, online teaching, video management",
        "meta-desc-ar": "قم بتحرير محتوى الفيديو الخاص بك على لوحة تحكم المدربين في إدوفيا. قم بتحديث تفاصيل الفيديو لتحسين دورتك.",
        "meta-keywords-ar": "إدوفيا، تحرير فيديو، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "og-title": "Edit Video - Eduvia",
        "og-desc": "Update your video details on Eduvia's Instructor Dashboard to improve your course content.",
        "twitter-title": "Edit Video - Eduvia",
        "twitter-desc": "Update your video details on Eduvia's Instructor Dashboard to improve your course content.",
        "hero-title": "Edit Video",
        "hero-desc": "Update your video details to enhance the learning experience for your students.",
        "form-title": "Edit Video: {{ video.title }}",
        "update-btn": "Update Video",
        "cancel-btn": "Cancel",
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
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "page-title": "تحرير الفيديو - إدوفيا",
        "meta-desc": "قم بتحرير محتوى الفيديو الخاص بك على لوحة تحكم المدربين في إدوفيا. قم بتحديث تفاصيل الفيديو لتحسين دورتك.",
        "meta-keywords": "إدوفيا، تحرير فيديو، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "meta-desc-ar": "قم بتحرير محتوى الفيديو الخاص بك على لوحة تحكم المدربين في إدوفيا. قم بتحديث تفاصيل الفيديو لتحسين دورتك.",
        "meta-keywords-ar": "إدوفيا، تحرير فيديو، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "og-title": "تحرير الفيديو - إدوفيا",
        "og-desc": "قم بتحديث تفاصيل الفيديو على لوحة تحكم المدربين في إدوفيا لتحسين محتوى دورتك.",
        "twitter-title": "تحرير الفيديو - إدوفيا",
        "twitter-desc": "قم بتحديث تفاصيل الفيديو على لوحة تحكم المدربين في إدوفيا لتحسين محتوى دورتك.",
        "hero-title": "تحرير الفيديو",
        "hero-desc": "قم بتحديث تفاصيل الفيديو لتحسين تجربة التعلم لطلابك.",
        "form-title": "تحرير الفيديو: {{ video.title }}",
        "update-btn": "تحديث الفيديو",
        "cancel-btn": "إلغاء",
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

    // Update lang and direction
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');

    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            element.setAttribute('content', text);
        } else if (key === 'form-title') {
            const videoTitle = element.textContent.match(/Edit Video: (.+)/)?.[1] || '{{ video.title }}';
            text = translations[newLang][key].replace('{{ video.title }}', videoTitle);
            element.textContent = text;
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
        } else if (key === 'form-title') {
            const videoTitle = element.textContent.match(/Edit Video: (.+)/)?.[1] || '{{ video.title }}';
            text = translations[savedLang][key].replace('{{ video.title }}', videoTitle);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    // Set the title on page load
    document.title = translations[savedLang]["page-title"];
});