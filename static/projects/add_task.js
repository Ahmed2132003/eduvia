const translations = {
    en: {
        "page-title": "Add New Task for Project: {{ project.title }} - Eduvia",
        "meta-desc": "Add a new task for project '{{ project.title }}' on Eduvia. Specify task details, rewards, and assign students.",
        "meta-keywords": "{{ project.title }}, Eduvia, add task, project management, open source collaboration, task creation",
        "og-title": "Add New Task for {{ project.title }} - Eduvia",
        "og-desc": "Add a new task for '{{ project.title }}' on Eduvia. Specify task details, rewards, and assign students.",
        "hero-title": "Add New Task for Project: {{ project.title }}",
        "hero-desc": "Create a new task for the project '{{ project.title }}'.",
        "back-btn": "Back to Project Details",
        "content-title": "Add New Task for Project: {{ project.title }}",
        "title-label": "Task Title",
        "title-invalid": "Please enter a title for the task.",
        "desc-label": "Description",
        "desc-invalid": "Please enter a description for the task.",
        "issue-label": "Issue Link (Optional)",
        "priority-label": "Priority",
        "xp-label": "Experience Points (XP)",
        "xp-invalid": "Please enter a valid value for experience points.",
        "coins-label": "Coins",
        "coins-invalid": "Please enter a valid value for coins.",
        "due-date-label": "Due Date (Optional)",
        "assign-label": "Assign to Students (Optional)",
        "assign-hint": "Select the students you want to assign the task to.",
        "submit-btn": "Add Task",
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
        "page-title": "إضافة مهمة جديدة للمشروع: {{ project.title }} - إدوفيا",
        "meta-desc": "أضف مهمة جديدة لمشروع '{{ project.title }}' على إدوفيا. حدد تفاصيل المهمة، المكافآت، وقم بتخصيص الطلاب.",
        "meta-keywords": "{{ project.title }}, إدوفيا, إضافة مهمة, إدارة المشاريع, تعاون المصادر المفتوحة, إنشاء مهمة",
        "og-title": "إضافة مهمة جديدة لـ {{ project.title }} - إدوفيا",
        "og-desc": "أضف مهمة جديدة لمشروع '{{ project.title }}' على إدوفيا. حدد تفاصيل المهمة، المكافآت، وقم بتخصيص الطلاب.",
        "hero-title": "إضافة مهمة جديدة للمشروع: {{ project.title }}",
        "hero-desc": "أنشئ مهمة جديدة لمشروع '{{ project.title }}'.",
        "back-btn": "العودة إلى تفاصيل المشروع",
        "content-title": "إضافة مهمة جديدة للمشروع: {{ project.title }}",
        "title-label": "عنوان المهمة",
        "title-invalid": "يرجى إدخال عنوان للمهمة.",
        "desc-label": "الوصف",
        "desc-invalid": "يرجى إدخال وصف للمهمة.",
        "issue-label": "رابط المشكلة (اختياري)",
        "priority-label": "الأولوية",
        "xp-label": "نقاط الخبرة (XP)",
        "xp-invalid": "يرجى إدخال قيمة صالحة لنقاط الخبرة.",
        "coins-label": "النقاط",
        "coins-invalid": "يرجى إدخال قيمة صالحة للنقاط.",
        "due-date-label": "تاريخ الاستحقاق (اختياري)",
        "assign-label": "تخصيص للطلاب (اختياري)",
        "assign-hint": "اختر الطلاب الذين تريد تخصيص المهمة لهم.",
        "submit-btn": "إضافة المهمة",
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
    
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    const projectTitle = document.querySelector('h1[data-translate="hero-title"]').textContent.match(/Add New Task for Project: (.*)/)?.[1] || 'Project';
    
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

    const projectTitle = document.querySelector('h1[data-translate="hero-title"]').textContent.match(/Add New Task for Project: (.*)/)?.[1] || 'Project';

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