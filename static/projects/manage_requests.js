const translations = {
    en: {
        "page-title": "Manage Join Requests - {{ room.title }} - Eduvia",
        "meta-desc": "Manage join requests for {{ room.title }} on Eduvia. Accept or reject user requests to join your collaboration room.",
        "meta-keywords": "{{ room.title }}, manage join requests, collaboration room, Eduvia, teamwork, project collaboration",
        "og-title": "Manage Join Requests - {{ room.title }} - Eduvia",
        "og-desc": "Administer join requests for {{ room.title }} on Eduvia. Approve or deny users seeking to join your collaboration room.",
        "twitter-title": "Manage Join Requests - {{ room.title }} - Eduvia",
        "twitter-desc": "Administer join requests for {{ room.title }} on Eduvia. Approve or deny users seeking to join your collaboration room.",
        "hero-title": "Manage Join Requests",
        "hero-desc": "Review and manage requests to join {{ room.title }}.",
        "content-title": "Manage Join Requests - {{ room.title }}",
        "user-label": "User:",
        "date-label": "Request Date:",
        "accept-btn": "Accept",
        "reject-btn": "Reject",
        "no-requests": "No pending join requests.",
        "invite-title": "Invite a User",
        "form-label-username": "Username",
        "username-invalid": "Please enter a username.",
        "invite-btn": "Send Invitation",
        "back-btn": "Back to Room",
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
        "schema-name": "Manage Join Requests - {{ room.title }} - Eduvia",
        "schema-desc": "Manage join requests for {{ room.title }} on Eduvia. Accept or reject user requests to join your collaboration room.",
        "breadcrumb-home": "Home",
        "breadcrumb-rooms": "Collaboration Rooms",
        "breadcrumb-room-title": "{{ room.title }}",
        "breadcrumb-manage": "Manage Join Requests"
    },
    ar: {
        "page-title": "إدارة طلبات الانضمام - {{ room.title }} - إدوفيا",
        "meta-desc": "إدارة طلبات الانضمام لـ {{ room.title }} على إدوفيا. قبول أو رفض طلبات المستخدمين للانضمام إلى غرفة التعاون الخاصة بك.",
        "meta-keywords": "{{ room.title }}, إدارة طلبات الانضمام, غرفة تعاون, إدوفيا, العمل الجماعي, تعاون المشاريع",
        "og-title": "إدارة طلبات الانضمام - {{ room.title }} - إدوفيا",
        "og-desc": "إدارة طلبات الانضمام لـ {{ room.title }} على إدوفيا. الموافقة أو الرفض للمستخدمين الذين يسعون للانضمام إلى غرفة التعاون الخاصة بك.",
        "twitter-title": "إدارة طلبات الانضمام - {{ room.title }} - إدوفيا",
        "twitter-desc": "إدارة طلبات الانضمام لـ {{ room.title }} على إدوفيا. الموافقة أو الرفض للمستخدمين الذين يسعون للانضمام إلى غرفة التعاون الخاصة بك.",
        "hero-title": "إدارة طلبات الانضمام",
        "hero-desc": "مراجعة وإدارة الطلبات للانضمام إلى {{ room.title }}.",
        "content-title": "إدارة طلبات الانضمام - {{ room.title }}",
        "user-label": "المستخدم:",
        "date-label": "تاريخ الطلب:",
        "accept-btn": "قبول",
        "reject-btn": "رفض",
        "no-requests": "لا توجد طلبات انضمام معلقة.",
        "invite-title": "دعوة مستخدم",
        "form-label-username": "اسم المستخدم",
        "username-invalid": "يرجى إدخال اسم المستخدم.",
        "invite-btn": "إرسال الدعوة",
        "back-btn": "العودة إلى الغرفة",
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
        "schema-name": "إدارة طلبات الانضمام - {{ room.title }} - إدوفيا",
        "schema-desc": "إدارة طلبات الانضمام لـ {{ room.title }} على إدوفيا. قبول أو رفض طلبات المستخدمين للانضمام إلى غرفة التعاون الخاصة بك.",
        "breadcrumb-home": "الرئيسية",
        "breadcrumb-rooms": "غرف التعاون",
        "breadcrumb-room-title": "{{ room.title }}",
        "breadcrumb-manage": "إدارة طلبات الانضمام"
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
        let text = translations[newLang][key].replace('{{ room.title }}', document.title.match(/Manage Join Requests - (.+?) - Eduvia/)?.[1] || 'Room');
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

    document.title = translations[newLang]["page-title"].replace('{{ room.title }}', document.title.match(/Manage Join Requests - (.+?) - Eduvia/)?.[1] || 'Room');

    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData.name = translations[newLang]["schema-name"].replace('{{ room.title }}', schemaData.name.match(/Manage Join Requests - (.+?) - Eduvia/)?.[1] || 'Room');
    schemaData.description = translations[newLang]["schema-desc"].replace('{{ room.title }}', schemaData.description.match(/Manage join requests for (.+?) on Eduvia/)?.[1] || 'Room');
    schemaData.breadcrumb.itemListElement[0].name = translations[newLang]["breadcrumb-home"];
    schemaData.breadcrumb.itemListElement[1].name = translations[newLang]["breadcrumb-rooms"];
    schemaData.breadcrumb.itemListElement[2].name = translations[newLang]["breadcrumb-room-title"].replace('{{ room.title }}', schemaData.breadcrumb.itemListElement[2].name || 'Room');
    schemaData.breadcrumb.itemListElement[3].name = translations[newLang]["breadcrumb-manage"];
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
        let text = translations[savedLang][key].replace('{{ room.title }}', document.title.match(/Manage Join Requests - (.+?) - Eduvia/)?.[1] || 'Room');
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

    document.title = translations[savedLang]["page-title"].replace('{{ room.title }}', document.title.match(/Manage Join Requests - (.+?) - Eduvia/)?.[1] || 'Room');

    const schema = document.getElementById('schema-markup');
    const schemaData = JSON.parse(schema.textContent);
    schemaData.name = translations[savedLang]["schema-name"].replace('{{ room.title }}', schemaData.name.match(/Manage Join Requests - (.+?) - Eduvia/)?.[1] || 'Room');
    schemaData.description = translations[savedLang]["schema-desc"].replace('{{ room.title }}', schemaData.description.match(/Manage join requests for (.+?) on Eduvia/)?.[1] || 'Room');
    schemaData.breadcrumb.itemListElement[0].name = translations[savedLang]["breadcrumb-home"];
    schemaData.breadcrumb.itemListElement[1].name = translations[savedLang]["breadcrumb-rooms"];
    schemaData.breadcrumb.itemListElement[2].name = translations[savedLang]["breadcrumb-room-title"].replace('{{ room.title }}', schemaData.breadcrumb.itemListElement[2].name || 'Room');
    schemaData.breadcrumb.itemListElement[3].name = translations[savedLang]["breadcrumb-manage"];
    schema.textContent = JSON.stringify(schemaData, null, 2);
});