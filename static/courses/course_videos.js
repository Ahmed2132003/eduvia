const translations = {
    en: {
        "page-title": "Course Videos - Eduvia",
        "meta-desc": "Manage videos for your course on Eduvia's Instructor Dashboard. Add, edit, and organize your video content.",
        "meta-keywords": "Eduvia, course videos, instructor dashboard, online teaching, video management",
        "meta-desc-ar": "إدارة فيديوهات دورتك على لوحة تحكم المدربين في إدوفيا. أضف، حرر، ونظم محتوى الفيديو الخاص بك.",
        "meta-keywords-ar": "إدوفيا، فيديوهات الدورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "og-title": "Course Videos - Eduvia",
        "og-desc": "Organize and manage your course videos on Eduvia's Instructor Dashboard.",
        "twitter-title": "Course Videos - Eduvia",
        "twitter-desc": "Organize and manage your course videos on Eduvia's Instructor Dashboard.",
        "hero-title": "Course Videos",
        "hero-desc": "Manage and organize the videos for your course: {{ course.title }}.",
        "card-title": "Videos for {{ course.title }}",
        "add-btn": "Add New Video",
        "order-label": "Order: {{ video.order }}",
        "edit-link": "Edit",
        "add-task": "Add Task",
        "add-alternative-quiz": "Add Alternative Quiz",
        "empty-text": "No videos found. Add your first video!",
        "back-link": "Back to Dashboard",
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
        "page-title": "فيديوهات الدورة - إدوفيا",
        "meta-desc": "إدارة فيديوهات دورتك على لوحة تحكم المدربين في إدوفيا. أضف، حرر، ونظم محتوى الفيديو الخاص بك.",
        "meta-keywords": "إدوفيا، فيديوهات الدورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "meta-desc-ar": "إدارة فيديوهات دورتك على لوحة تحكم المدربين في إدوفيا. أضف، حرر، ونظم محتوى الفيديو الخاص بك.",
        "meta-keywords-ar": "إدوفيا، فيديوهات الدورة، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "og-title": "فيديوهات الدورة - إدوفيا",
        "og-desc": "نظم وإدارة فيديوهات دورتك على لوحة تحكم المدربين في إدوفيا.",
        "twitter-title": "فيديوهات الدورة - إدوفيا",
        "twitter-desc": "نظم وإدارة فيديوهات دورتك على لوحة تحكم المدربين في إدوفيا.",
        "hero-title": "فيديوهات الدورة",
        "hero-desc": "إدارة وتنظيم فيديوهات دورتك: {{ course.title }}.",
        "card-title": "فيديوهات لـ {{ course.title }}",
        "add-btn": "إضافة فيديو جديد",
        "order-label": "الترتيب: {{ video.order }}",
        "edit-link": "تعديل",
        "add-task": "إضافة مهمة",
        "add-alternative-quiz": "إضافة اختبار بديل",
        "empty-text": "لم يتم العثور على فيديوهات. أضف أول فيديو لك!",
        "back-link": "العودة إلى لوحة التحكم",
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
        let text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            element.setAttribute('content', text);
        } else if (key === 'hero-desc' || key === 'card-title') {
            const courseTitle = element.textContent.match(/for your course: (.*?)\./)?.[1] || '{{ course.title }}';
            text = translations[newLang][key].replace('{{ course.title }}', courseTitle);
            element.textContent = text;
        } else if (key === 'order-label') {
            const order = element.textContent.match(/Order: (\d+)/)?.[1] || '{{ video.order }}';
            text = translations[newLang][key].replace('{{ video.order }}', order);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
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
        let text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            element.setAttribute('content', text);
        } else if (key === 'hero-desc' || key === 'card-title') {
            const courseTitle = element.textContent.match(/for your course: (.*?)\./)?.[1] || '{{ course.title }}';
            text = translations[savedLang][key].replace('{{ course.title }}', courseTitle);
            element.textContent = text;
        } else if (key === 'order-label') {
            const order = element.textContent.match(/Order: (\d+)/)?.[1] || '{{ video.order }}';
            text = translations[savedLang][key].replace('{{ video.order }}', order);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["page-title"];
});