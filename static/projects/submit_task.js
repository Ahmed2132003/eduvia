const translations = {
    en: {
        "page-title": "Submit Solution for Task: {taskTitle} - Eduvia",
        "meta-desc": "Submit your solution for task '{taskTitle}' in project '{projectTitle}' on Eduvia. Provide links and describe your work.",
        "meta-keywords": "{taskTitle}, {projectTitle}, Eduvia, task submission, open source collaboration, project solutions",
        "og-title": "Submit Solution for {taskTitle} - Eduvia",
        "og-desc": "Submit your solution for '{taskTitle}' in '{projectTitle}' on Eduvia. Provide links and describe your work.",
        "twitter-title": "Submit Solution for {taskTitle} - Eduvia",
        "twitter-desc": "Submit your solution for '{taskTitle}' in '{projectTitle}' on Eduvia. Provide links and describe your work.",
        "hero-title": "Submit Solution for Task: {taskTitle}",
        "hero-desc": "Submit your solution for the task in project '{projectTitle}'.",
        "back-to-project": "Back to Project Details",
        "content-title": "Submit Solution for Task: {taskTitle}",
        "project-label": "Project:",
        "solution-link-label": "Solution Link (e.g., Pull Request)",
        "solution-link-help": "Enter the solution link if available (optional).",
        "file-url-label": "File URL",
        "file-url-help": "Enter the URL for your file (e.g., Google Drive, GitHub, etc.) (optional).",
        "file-url-error": "Please provide a valid file URL.",
        "description-label": "Solution Description",
        "description-error": "Please provide a description for the solution.",
        "submit-btn": "Submit Solution",
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
        "footer-text": "© 2025 Eduvia. All rights reserved.",
        "schema-name": "Submit Solution for Task: {taskTitle} - Eduvia",
        "schema-desc": "Submit your solution for task '{taskTitle}' in project '{projectTitle}' on Eduvia. Provide links and describe your work.",
        "breadcrumb-home": "Home",
        "breadcrumb-projects": "Projects",
        "breadcrumb-submit-task": "Submit Solution for Task: {taskTitle}"
    },
    ar: {
        "page-title": "تقديم الحل لمهمة: {taskTitle} - إدوفيا",
        "meta-desc": "قدم حلك لمهمة '{taskTitle}' في مشروع '{projectTitle}' على إدوفيا. قدم الروابط وصف عملك.",
        "meta-keywords": "{taskTitle}, {projectTitle}, إدوفيا, تقديم المهمة, التعاون مفتوح المصدر, حلول المشروع",
        "og-title": "تقديم الحل لـ {taskTitle} - إدوفيا",
        "og-desc": "قدم حلك لـ '{taskTitle}' في '{projectTitle}' على إدوفيا. قدم الروابط وصف عملك.",
        "twitter-title": "تقديم الحل لـ {taskTitle} - إدوفيا",
        "twitter-desc": "قدم حلك لـ '{taskTitle}' في '{projectTitle}' على إدوفيا. قدم الروابط وصف عملك.",
        "hero-title": "تقديم الحل لمهمة: {taskTitle}",
        "hero-desc": "قدم حلك للمهمة في مشروع '{projectTitle}'.",
        "back-to-project": "العودة إلىفاصيل إلى المشروع",
        "content-title": "تقديم الحل لمهمة: {taskTitle}",
        "project-label": "المشروع:",
        "solution-link-label": "رابط الحل (مثل: طلب السحب)",
        "solution-link-help": "أدخل رابط الحل إذا كان متاحًا (اختياري).",
        "file-url-label": "رابط الملف",
        "file-url-help": "أدخل رابط الملف (مثل Google Drive، GitHub، إلخ) (اختياري).",
        "file-url-error": "يرجى تقديم رابط ملف صالح.",
        "description-label": "وصف الحل",
        "description-error": "يرجى تقديم وصف للحل.",
        "submit-btn": "تقديم الحل",
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
        "footer-text": "© 2025 إدوفيا إدوفيا. جميع الحقوق محفوظة.",
        "schema-name": "تقديم الحل لمهمة: {taskTitle} - إدوفيا",
        "schema-desc": "قدم حلك لمهمة '{taskTitle}' في مشروع '{projectTitle}' على إدوفيا. قدم الروابط وصف عملك.",
        "breadcrumb-home": "الرئيسية",
        "breadcrumb-projects": "المشاريع",
        "breadcrumb-submit-task": "تقديم الحل لمهمة: {taskTitle}"
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
    const currentLang = htmlRoot.getAttribute('lang') || 'en';
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    
    // Ensure taskTitle and projectTitle are defined
    const taskTitle = window.taskTitle || 'Task';
    const projectTitle = window.projectTitle || 'Project';
    
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[newLang][key];
        if (text) {
            text = text.replace('{taskTitle}', taskTitle).replace('{projectTitle}', projectTitle);
            if (element.tagName.toLowerCase() === 'meta') {
                if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords' || element.getAttribute('name')?.startsWith('twitter:')) {
                    element.setAttribute('content', text);
                } else if (element.getAttribute('property')?.startsWith('og:')) {
                    element.setAttribute('content', text);
                }
            } else {
                element.textContent = text;
            }
        }
    });

    document.title = translations[newLang]["page-title"].replace('{taskTitle}', taskTitle);
    
    const schema = document.getElementById('schema-markup');
    if (schema) {
        const schemaData = JSON.parse(schema.textContent);
        schemaData.name = translations[newLang]["schema-name"].replace('{taskTitle}', taskTitle);
        schemaData.description = translations[newLang]["schema-desc"].replace('{taskTitle}', taskTitle).replace('{projectTitle}', projectTitle);
        schemaData.breadcrumb.itemListElement[0].name = translations[newLang]["breadcrumb-home"];
        schemaData.breadcrumb.itemListElement[1].name = translations[newLang]["breadcrumb-projects"];
        schemaData.breadcrumb.itemListElement[2].name = translations[newLang]["breadcrumb-submit-task"].replace('{taskTitle}', taskTitle);
        schema.textContent = JSON.stringify(schemaData, null, 2);
    }
    
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

    // Ensure taskTitle and projectTitle are defined
    const taskTitle = window.taskTitle || 'Task';
    const projectTitle = window.projectTitle || 'Project';
    
    const savedLang = localStorage.getItem('language') || 'en';
    const htmlRoot = document.getElementById('html-root');
    htmlRoot.setAttribute('lang', savedLang);
    htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[savedLang][key];
        if (text) {
            text = text.replace('{taskTitle}', taskTitle).replace('{projectTitle}', projectTitle);
            if (element.tagName.toLowerCase() === 'meta') {
                if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords' || element.getAttribute('name')?.startsWith('twitter:')) {
                    element.setAttribute('content', text);
                } else if (element.getAttribute('property')?.startsWith('og:')) {
                    element.setAttribute('content', text);
                }
            } else {
                element.textContent = text;
            }
        }
    });

    document.title = translations[savedLang]["page-title"].replace('{taskTitle}', taskTitle);
    
    const schema = document.getElementById('schema-markup');
    if (schema) {
        const schemaData = JSON.parse(schema.textContent);
        schemaData.name = translations[savedLang]["schema-name"].replace('{taskTitle}', taskTitle);
        schemaData.description = translations[savedLang]["schema-desc"].replace('{taskTitle}', taskTitle).replace('{projectTitle}', projectTitle);
        schemaData.breadcrumb.itemListElement[0].name = translations[savedLang]["breadcrumb-home"];
        schemaData.breadcrumb.itemListElement[1].name = translations[savedLang]["breadcrumb-projects"];
        schemaData.breadcrumb.itemListElement[2].name = translations[savedLang]["breadcrumb-submit-task"].replace('{taskTitle}', taskTitle);
        schema.textContent = JSON.stringify(schemaData, null, 2);
    }

    // Form Validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});