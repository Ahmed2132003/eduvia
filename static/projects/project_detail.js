const translations = {
    en: {
        "page-title": "Project Details - {{ project.title }} - Eduvia",
        "meta-desc": "View details of {{ project.title }} on Eduvia. Explore tasks, submit solutions, and collaborate with the community.",
        "meta-keywords": "{{ project.title }}, Eduvia project, open source tasks, coding collaboration, project details, {{ project.get_category_display }}",
        "og-title": "{{ project.title }} - Eduvia",
        "og-desc": "Explore {{ project.title }} on Eduvia. Join tasks, submit solutions, and engage with the open-source community.",
        "twitter-title": "{{ project.title }} - Eduvia",
        "twitter-desc": "Explore {{ project.title }} on Eduvia. Join tasks, submit solutions, and engage with the open-source community.",
        "hero-desc": "Explore tasks and contribute to this open-source project!",
        "back-btn": "Back to Projects",
        "repo-label": "Repository:",
        "status-label": "Status:",
        "category-label": "Category:",
        "tasks-title": "Tasks",
        "priority-label": "Priority:",
        "xp-label": "XP Points:",
        "coins-label": "Coins:",
        "due-date-label": "Due Date:",
        "not-specified": "Not specified",
        "view-solutions": "View Solutions",
        "join-task": "Join Task",
        "joined-task": "You are joined to this task!",
        "submit-solution": "Submit Solution",
        "no-tasks": "No tasks available.",
        "add-task": "Add Task",
        "comments-title": "Comments",
        "comment-date": "Date:",
        "no-comments": "No comments yet.",
        "add-comment-title": "Add a Comment",
        "submit-comment": "Submit Comment",
        "content-invalid": "Please enter a comment.",
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
        "footer-text": "© 2025 Eduvia. All rights reserved.",
        "schema-name": "Project Details - {{ project.title }} - Eduvia",
        "schema-desc": "View details of {{ project.title }} on Eduvia. Explore tasks, submit solutions, and collaborate with the community.",
        "breadcrumb-home": "Home",
        "breadcrumb-projects": "Projects",
        "breadcrumb-project-title": "{{ project.title }}"
    },
    ar: {
        "page-title": "تفاصيل المشروع - {{ project.title }} - إدوفيا",
        "meta-desc": "عرض تفاصيل {{ project.title }} على إدوفيا. استكشف المهام، قدم الحلول، وتعاون مع المجتمع.",
        "meta-keywords": "{{ project.title }}, مشروع إدوفيا, مهام مفتوحة المصدر, تعاون البرمجة, تفاصيل المشروع, {{ project.get_category_display }}",
        "og-title": "{{ project.title }} - إدوفيا",
        "og-desc": "استكشف {{ project.title }} على إدوفيا. انضم إلى المهام، قدم الحلول، وتفاعل مع مجتمع المصادر المفتوحة.",
        "twitter-title": "{{ project.title }} - إدوفيا",
        "twitter-desc": "استكشف {{ project.title }} على إدوفيا. انضم إلى المهام، قدم الحلول، وتفاعل مع مجتمع المصادر المفتوحة.",
        "hero-desc": "استكشف المهام وساهم في هذا المشروع مفتوح المصدر!",
        "back-btn": "العودة إلى المشاريع",
        "repo-label": "المستودع:",
        "status-label": "الحالة:",
        "category-label": "الفئة:",
        "tasks-title": "المهام",
        "priority-label": "الأولوية:",
        "xp-label": "نقاط الخبرة:",
        "coins-label": "النقاط:",
        "due-date-label": "تاريخ الاستحقاق:",
        "not-specified": "غير محدد",
        "view-solutions": "عرض الحلول",
        "join-task": "الانضمام إلى المهمة",
        "joined-task": "لقد انضممت إلى هذه المهمة!",
        "submit-solution": "تقديم الحل",
        "no-tasks": "لا توجد مهام متاحة.",
        "add-task": "إضافة مهمة",
        "comments-title": "التعليقات",
        "comment-date": "التاريخ:",
        "no-comments": "لا توجد تعليقات بعد.",
        "add-comment-title": "إضافة تعليق",
        "submit-comment": "إرسال التعليق",
        "content-invalid": "يرجى إدخال تعليق.",
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
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة.",
        "schema-name": "تفاصيل المشروع - {{ project.title }} - إدوفيا",
        "schema-desc": "عرض تفاصيل {{ project.title }} على إدوفيا. استكشف المهام، قدم الحلول، وتعاون مع المجتمع.",
        "breadcrumb-home": "الرئيسية",
        "breadcrumb-projects": "المشاريع",
        "breadcrumb-project-title": "{{ project.title }}"
    }
};

const projectTitle = "{{ project.title|escapejs|default:'Project' }}";
const projectCategory = "{{ project.get_category_display|escapejs|default:'Category' }}";

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
        let text = translations[newLang][key].replace('{{ project.title }}', projectTitle).replace('{{ project.get_category_display }}', projectCategory);
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords' || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["page-title"].replace('{{ project.title }}', projectTitle);

    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData.name = translations[newLang]["schema-name"].replace('{{ project.title }}', projectTitle);
    schemaData.description = translations[newLang]["schema-desc"].replace('{{ project.title }}', projectTitle);
    schemaData.breadcrumb.itemListElement[0].name = translations[newLang]["breadcrumb-home"];
    schemaData.breadcrumb.itemListElement[1].name = translations[newLang]["breadcrumb-projects"];
    schemaData.breadcrumb.itemListElement[2].name = translations[newLang]["breadcrumb-project-title"].replace('{{ project.title }}', projectTitle);
    schema.textContent = JSON.stringify(schemaData, null, 2);

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
        let text = translations[savedLang][key].replace('{{ project.title }}', projectTitle).replace('{{ project.get_category_display }}', projectCategory);
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords' || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["page-title"].replace('{{ project.title }}', projectTitle);

    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData.name = translations[savedLang]["schema-name"].replace('{{ project.title }}', projectTitle);
    schemaData.description = translations[savedLang]["schema-desc"].replace('{{ project.title }}', projectTitle);
    schemaData.breadcrumb.itemListElement[0].name = translations[savedLang]["breadcrumb-home"];
    schemaData.breadcrumb.itemListElement[1].name = translations[savedLang]["breadcrumb-projects"];
    schemaData.breadcrumb.itemListElement[2].name = translations[savedLang]["breadcrumb-project-title"].replace('{{ project.title }}', projectTitle);
    schema.textContent = JSON.stringify(schemaData, null, 2);
});