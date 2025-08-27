// Translation object
const translations = {
    en: {
        "page-title": "Collaboration Rooms - Eduvia",
        "meta-desc": "Explore collaboration rooms on Eduvia. Join or create rooms to work on exciting projects with peers.",
        "meta-keywords": "collaboration rooms, Eduvia, teamwork, project collaboration, online learning",
        "og-title": "Collaboration Rooms - Eduvia",
        "og-desc": "Discover and join collaboration rooms on Eduvia to work on projects with peers and enhance your learning experience.",
        "hero-title": "Collaboration Rooms",
        "hero-desc": "Join or create rooms to collaborate on exciting projects with your peers!",
        "content-title": "Available Collaboration Rooms",
        "creator-label": "Creator:",
        "project-label": "Project:",
        "members-label": "Members:",
        "view-room": "View Room",
        "request-join": "Request to Join",
        "pending-request": "Your Request is Pending",
        "rejected-request": "Your Request was Rejected",
        "login-to-join": "Please log in to request to join.",
        "no-rooms": "No collaboration rooms are available.",
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
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved.",
        "schema-name": "Collaboration Rooms - Eduvia",
        "schema-desc": "Explore collaboration rooms on Eduvia. Join or create rooms to work on exciting projects with peers.",
        "breadcrumb-home": "Home",
        "breadcrumb-rooms": "Collaboration Rooms"
    },
    ar: {
        "page-title": "غرف التعاون - إدوفيا",
        "meta-desc": "استكشف غرف التعاون على إدوفيا. انضم أو أنشئ غرفًا للعمل على مشاريع مثيرة مع أقرانك.",
        "meta-keywords": "غرف التعاون, إدوفيا, العمل الجماعي, تعاون المشاريع, التعلم عبر الإنترنت",
        "og-title": "غرف التعاون - إدوفيا",
        "og-desc": "اكتشف وانضم إلى غرف التعاون على إدوفيا للعمل على المشاريع مع أقرانك وتعزيز تجربة التعلم الخاصة بك.",
        "hero-title": "غرف التعاون",
        "hero-desc": "انضم أو أنشئ غرفًا للتعاون في مشاريع مثيرة مع أقرانك!",
        "content-title": "غرف التعاون المتاحة",
        "creator-label": "المنشئ:",
        "project-label": "المشروع:",
        "members-label": "الأعضاء:",
        "view-room": "عرض الغرفة",
        "request-join": "طلب الانضمام",
        "pending-request": "طلبك معلق",
        "rejected-request": "تم رفض طلبك",
        "login-to-join": "يرجى تسجيل الدخول لطلب الانضمام.",
        "no-rooms": "لا توجد غرف تعاون متاحة.",
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
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة.",
        "schema-name": "غرف التعاون - إدوفيا",
        "schema-desc": "استكشف غرف التعاون على إدوفيا. انضم أو أنشئ غرفًا للعمل على مشاريع مثيرة مع أقرانك.",
        "breadcrumb-home": "الرئيسية",
        "breadcrumb-rooms": "غرف التعاون"
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
        element.textContent = translations[newLang][key];
    });

    // Update the title
    document.title = translations[newLang]["page-title"];

    // Update Schema Markup
    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData["@graph"][1].name = translations[newLang]["schema-name"];
    schemaData["@graph"][1].description = translations[newLang]["schema-desc"];
    schemaData["@graph"][2].itemListElement[0].name = translations[newLang]["breadcrumb-home"];
    schemaData["@graph"][2].itemListElement[1].name = translations[newLang]["breadcrumb-rooms"];
    schema.textContent = JSON.stringify(schemaData, null, 2);
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
        element.textContent = translations[savedLang][key];
    });

    // Set the title on page load
    document.title = translations[savedLang]["page-title"];

    // Update Schema Markup on page load
    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData["@graph"][1].name = translations[savedLang]["schema-name"];
    schemaData["@graph"][1].description = translations[savedLang]["schema-desc"];
    schemaData["@graph"][2].itemListElement[0].name = translations[savedLang]["breadcrumb-home"];
    schemaData["@graph"][2].itemListElement[1].name = translations[savedLang]["breadcrumb-rooms"];
    schema.textContent = JSON.stringify(schemaData, null, 2);
});