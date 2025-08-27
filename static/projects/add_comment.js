const translations = {
    en: {
        "page-title": "Add Comment for Project: {{ project.title }} - Eduvia",
        "meta-desc": "Add a comment for project '{{ project.title }}' on Eduvia. Share your feedback and engage with the community.",
        "meta-keywords": "{{ project.title }}, Eduvia, add comment, project feedback, open source collaboration",
        "og-title": "Add Comment for {{ project.title }} - Eduvia",
        "og-desc": "Add a comment for '{{ project.title }}' on Eduvia. Share your feedback and engage with the community.",
        "hero-title": "Add Comment for Project: {{ project.title }}",
        "hero-desc": "Share your feedback for the project '{{ project.title }}'.",
        "back-btn": "Back to Project Details",
        "content-title": "Add Comment for Project: {{ project.title }}",
        "comment-label": "Comment",
        "invalid-feedback": "Please enter a comment.",
        "submit-btn": "Add Comment",
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
        "page-title": "إضافة تعليق للمشروع: {{ project.title }} - إدوفيا",
        "meta-desc": "أضف تعليقًا لمشروع '{{ project.title }}' على إدوفيا. شارك بتعليقاتك وتفاعل مع المجتمع.",
        "meta-keywords": "{{ project.title }}, إدوفيا, إضافة تعليق, تعليقات المشروع, تعاون المصادر المفتوحة",
        "og-title": "إضافة تعليق لـ {{ project.title }} - إدوفيا",
        "og-desc": "أضف تعليقًا لمشروع '{{ project.title }}' على إدوفيا. شارك بتعليقاتك وتفاعل مع المجتمع.",
        "hero-title": "إضافة تعليق للمشروع: {{ project.title }}",
        "hero-desc": "شارك بتعليقاتك لمشروع '{{ project.title }}'.",
        "back-btn": "العودة إلى تفاصيل المشروع",
        "content-title": "إضافة تعليق للمشروع: {{ project.title }}",
        "comment-label": "التعليق",
        "invalid-feedback": "يرجى إدخال تعليق.",
        "submit-btn": "إضافة تعليق",
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
    
    // Get the project title from the page
    const projectTitle = document.querySelector('h1[data-translate="hero-title"]').textContent
        .replace(translations[currentLang]['hero-title'].replace('{{ project.title }}', ''), '')
        .trim() || 'Project';
    
    // Update lang and direction
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[newLang][key].replace('{{ project.title }}', projectTitle);
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
    document.title = translations[newLang]["page-title"].replace('{{ project.title }}', projectTitle);

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

    const projectTitle = document.querySelector('h1[data-translate="hero-title"]').textContent
        .replace(translations[savedLang]['hero-title'].replace('{{ project.title }}', ''), '')
        .trim() || 'Project';

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[savedLang][key].replace('{{ project.title }}', projectTitle);
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

    document.title = translations[savedLang]["page-title"].replace('{{ project.title }}', projectTitle);
});