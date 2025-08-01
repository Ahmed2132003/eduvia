const translations = {
    en: {
        "page-title": "Edit Group - Eduvia",
        "meta-desc": "Edit your mentorship group and manage members in Eduvia's Mentorship System.",
        "meta-keywords": "edit group, manage members, Eduvia, mentorship",
        "og-title": "Edit Group - Eduvia",
        "og-desc": "Edit your mentorship group and manage members in Eduvia's Mentorship System.",
        "hero-title": "Edit Group",
        "hero-desc": "Modify your mentorship group and manage its members",
        "edit-heading": "Edit Group: {{ group.name }}",
        "members-heading": "Current Members",
        "no-members": "No members in this group yet.",
        "add-member-heading": "Add New Member",
        "update-group": "Update Group",
        "add-member": "Add Member",
        "remove-member": "Remove",
        "admin-label": "(Admin)",
        "back-to-group": "Back to Group",
        "mentor-dashboard": "Mentor Dashboard",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-skills-market": "Skills Market",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "page-title": "تعديل المجموعة - إدوفيا",
        "meta-desc": "عدّل مجموعتك الإرشادية وأدر الأعضاء في نظام الإرشاد بمنصة إدوفيا.",
        "meta-keywords": "تعديل المجموعة, إدارة الأعضاء, إدوفيا, الإرشاد",
        "og-title": "تعديل المجموعة - إدوفيا",
        "og-desc": "عدّل مجموعتك الإرشادية وأدر الأعضاء في نظام الإرشاد بمنصة إدوفيا.",
        "hero-title": "تعديل المجموعة",
        "hero-desc": "قم بتعديل مجموعتك الإرشادية وإدارة أعضائها",
        "edit-heading": "تعديل المجموعة: {{ group.name }}",
        "members-heading": "الأعضاء الحاليون",
        "no-members": "لا يوجد أعضاء في هذه المجموعة بعد.",
        "add-member-heading": "إضافة عضو جديد",
        "update-group": "تحديث المجموعة",
        "add-member": "إضافة عضو",
        "remove-member": "إزالة",
        "admin-label": "(المسؤول)",
        "back-to-group": "العودة إلى المجموعة",
        "mentor-dashboard": "لوحة تحكم المرشد",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-skills-market": "سوق المهارات",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
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
        if (key === 'edit-heading') {
            const groupName = element.textContent.match(/Edit Group: (.*)/)?.[1] || '{{ group.name }}';
            text = translations[newLang][key].replace('{{ group.name }}', groupName);
        }
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
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
        if (key === 'edit-heading') {
            const groupName = element.textContent.match(/Edit Group: (.*)/)?.[1] || '{{ group.name }}';
            text = translations[savedLang][key].replace('{{ group.name }}', groupName);
        }
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });
    document.title = translations[savedLang]["page-title"];
});