const translations = {
    en: {
        "page-title": "Open Source Projects - Eduvia",
        "meta-desc": "Explore open-source projects on Eduvia. Contribute to exciting tasks, earn rewards, and collaborate with instructors and students.",
        "meta-keywords": "open source projects, Eduvia projects, programming projects, student collaboration, coding tasks, instructor-led projects",
        "og-title": "Open Source Projects - Eduvia",
        "og-desc": "Join Eduvia's open-source projects to collaborate, contribute, and grow your coding skills.",
        "twitter-title": "Open Source Projects - Eduvia",
        "twitter-desc": "Join Eduvia's open-source projects to collaborate, contribute, and grow your coding skills.",
        "hero-title": "Open Source Projects",
        "hero-desc": "Collaborate on exciting open-source projects, contribute to tasks, and earn rewards!",
        "contribute-btn": "Start Contributing!",
        "category-label": "Category:",
        "status-label": "Status:",
        "view-details": "View Details",
        "no-projects": "No projects available.",
        "add-project": "Add New Project",
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
        "schema-name": "Open Source Projects - Eduvia",
        "schema-desc": "Explore open-source projects on Eduvia. Contribute to exciting tasks, earn rewards, and collaborate with instructors and students.",
        "breadcrumb-home": "Home",
        "breadcrumb-projects": "Projects"
    },
    ar: {
        "page-title": "مشاريع مفتوحة المصدر - إدوفيا",
        "meta-desc": "استكشف المشاريع مفتوحة المصدر على إدوفيا. ساهم في مهام مثيرة، اربح مكافآت، وتعاون مع المدربين والطلاب.",
        "meta-keywords": "مشاريع مفتوحة المصدر, مشاريع إدوفيا, مشاريع برمجة, تعاون الطلاب, مهام البرمجة, مشاريع بقيادة المدربين",
        "og-title": "مشاريع مفتوحة المصدر - إدوفيا",
        "og-desc": "انضم إلى مشاريع إدوفيا مفتوحة المصدر للتعاون، المساهمة، وتطوير مهارات البرمجة الخاصة بك.",
        "twitter-title": "مشاريع مفتوحة المصدر - إدوفيا",
        "twitter-desc": "انضم إلى مشاريع إدوفيا مفتوحة المصدر للتعاون، المساهمة، وتطوير مهارات البرمجة الخاصة بك.",
        "hero-title": "مشاريع مفتوحة المصدر",
        "hero-desc": "تعاون في مشاريع مفتوحة المصدر مثيرة، ساهم في المهام، واربح مكافآت!",
        "contribute-btn": "ابدأ المساهمة!",
        "category-label": "الفئة:",
        "status-label": "الحالة:",
        "view-details": "عرض التفاصيل",
        "no-projects": "لا توجد مشاريع متاحة.",
        "add-project": "إضافة مشروع جديد",
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
        "schema-name": "مشاريع مفتوحة المصدر - إدوفيا",
        "schema-desc": "استكشف المشاريع مفتوحة المصدر على إدوفيا. ساهم في مهام مثيرة، اربح مكافآت، وتعاون مع المدربين والطلاب.",
        "breadcrumb-home": "الرئيسية",
        "breadcrumb-projects": "المشاريع"
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
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords' || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["page-title"];

    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData.name = translations[newLang]["schema-name"];
    schemaData.description = translations[newLang]["schema-desc"];
    schemaData.breadcrumb.itemListElement[0].name = translations[newLang]["breadcrumb-home"];
    schemaData.breadcrumb.itemListElement[1].name = translations[newLang]["breadcrumb-projects"];
    schema.textContent = JSON.stringify(schemaData, null, 2);

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
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords' || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["page-title"];

    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData.name = translations[savedLang]["schema-name"];
    schemaData.description = translations[savedLang]["schema-desc"];
    schemaData.breadcrumb.itemListElement[0].name = translations[savedLang]["breadcrumb-home"];
    schemaData.breadcrumb.itemListElement[1].name = translations[savedLang]["breadcrumb-projects"];
    schema.textContent = JSON.stringify(schemaData, null, 2);
});