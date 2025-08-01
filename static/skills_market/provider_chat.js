const translations = {
    en: {
        "page-title": "Provider Chat - Eduvia",
        "meta-desc": "Chat with buyers in Eduvia's Skills Market.",
        "meta-keywords": "provider chat, Eduvia, skills market",
        "og-title": "Provider Chat - Eduvia",
        "og-desc": "Chat with buyers in Eduvia's Skills Market.",
        "hero-title": "Provider Chat",
        "hero-desc": "Communicate with buyers in Eduvia's Skills Market",
        "chat-title": "Chat for Order: {{ order.service.title }}",
        "chat-buyer": "Buyer:",
        "chat-status": "Status:",
        "chat-created": "Created At:",
        "chat-attachment": "View Attachment",
        "chat-no-messages": "No messages yet.",
        "chat-file-label": "Attach File",
        "chat-send": "Send Message",
        "btn-back-messages": "Back to Messages",
        "btn-back-services": "Back to Services",
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
        "page-title": "دردشة المزود - إدوفيا",
        "meta-desc": "تواصل مع المشترين في سوق المهارات بإدوفيا.",
        "meta-keywords": "دردشة المزود, إدوفيا, سوق المهارات",
        "og-title": "دردشة المزود - إدوفيا",
        "og-desc": "تواصل مع المشترين في سوق المهارات بإدوفيا.",
        "hero-title": "دردشة المزود",
        "hero-desc": "تواصل مع المشترين في سوق المهارات بإدوفيا",
        "chat-title": "الدردشة للطلب: {{ order.service.title }}",
        "chat-buyer": "المشتري:",
        "chat-status": "الحالة:",
        "chat-created": "تاريخ الإنشاء:",
        "chat-attachment": "عرض المرفق",
        "chat-no-messages": "لا توجد رسائل بعد.",
        "chat-file-label": "إرفاق ملف",
        "chat-send": "إرسال رسالة",
        "btn-back-messages": "العودة إلى الرسائل",
        "btn-back-services": "العودة إلى الخدمات",
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