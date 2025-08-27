const translations = {
    en: {
        "page-title": "Create Collaboration Room - Eduvia",
        "meta-desc": "Create a collaborative project development room on Eduvia to work with your team in real-time.",
        "meta-keywords": "collaborative room, project development, Eduvia, teamwork, collaborative learning",
        "og-title": "Create Collaboration Room - Eduvia",
        "og-desc": "Start a new collaboration room on Eduvia to work seamlessly with your team on educational projects.",
        "hero-title": "Create a Collaboration Room",
        "hero-desc": "Start a new space for your team to collaborate on projects in real-time.",
        "content-title": "Create a New Collaboration Room",
        "form-label-name": "Room Name",
        "form-label-description": "Description",
        "name-invalid": "Please enter a room name.",
        "description-invalid": "Please enter a description.",
        "submit-btn": "Create Room",
        "back-btn": "Back to Projects",
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
        "page-title": "إنشاء غرفة تعاون - إدوفيا",
        "meta-desc": "أنشئ غرفة تطوير مشاريع تعاونية على إدوفيا للعمل مع فريقك في الوقت الفعلي.",
        "meta-keywords": "غرفة تعاون, تطوير المشاريع, إدوفيا, العمل الجماعي, التعلم التعاوني",
        "og-title": "إنشاء غرفة تعاون - إدوفيا",
        "og-desc": "ابدأ غرفة تعاون جديدة على إدوفيا للعمل بسلاسة مع فريقك على المشاريع التعليمية.",
        "hero-title": "إنشاء غرفة تعاون",
        "hero-desc": "ابدأ مساحة جديدة لفريقك للتعاون في المشاريع في الوقت الفعلي.",
        "content-title": "إنشاء غرفة تعاون جديدة",
        "form-label-name": "اسم الغرفة",
        "form-label-description": "الوصف",
        "name-invalid": "يرجى إدخال اسم الغرفة.",
        "description-invalid": "يرجى إدخال وصف.",
        "submit-btn": "إنشاء الغرفة",
        "back-btn": "العودة إلى المشاريع",
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
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["page-title"];
    localStorage.setItem('language', newLang);
}

(function () {
    'use strict';
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();

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
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["page-title"];
});