const translations = {
    en: {
        "page-title": "Applicant Chat - Eduvia",
        "meta-desc": "Chat with providers or applicants in Eduvia's Skills Market.",
        "meta-keywords": "applicant chat, Eduvia, skills market",
        "og-title": "Applicant Chat - Eduvia",
        "og-desc": "Chat with providers or applicants in Eduvia's Skills Market.",
        "hero-title": "Applicant Chat",
        "hero-desc": "Communicate with providers or applicants in Eduvia's Skills Market",
        "chat-service-title": "Chat for Order:",
        "chat-opportunity-title": "Chat for Opportunity:",
        "chat-provider": "Provider:",
        "chat-status": "Status:",
        "chat-created": "Created At:",
        "message-sent-at": "{{ message.sent_at|date:'F d, Y H:i' }}",
        "message-file": "View Attachment",
        "no-messages": "No messages yet.",
        "send-message": "Send Message",
        "file-url-label": "File URL",
        "back-to-services": "Back to Services",
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
        "page-title": "دردشة المتقدم - إدوفيا",
        "meta-desc": "تواصل مع مقدمي الخدمات أو المتقدمين في سوق المهارات بإدوفيا.",
        "meta-keywords": "دردشة المتقدم, إدوفيا, سوق المهارات",
        "og-title": "دردشة المتقدم - إدوفيا",
        "og-desc": "تواصل مع مقدمي الخدمات أو المتقدمين في سوق المهارات بإدوفيا.",
        "hero-title": "دردشة المتقدم",
        "hero-desc": "تواصل مع مقدمي الخدمات أو المتقدمين في سوق المهارات بإدوفيا",
        "chat-service-title": "دردشة الطلب:",
        "chat-opportunity-title": "دردشة الفرصة:",
        "chat-provider": "مقدم الخدمة:",
        "chat-status": "الحالة:",
        "chat-created": "تاريخ الإنشاء:",
        "message-sent-at": "{{ message.sent_at|date:'d F Y H:i' }}",
        "message-file": "عرض المرفق",
        "no-messages": "لا توجد رسائل بعد.",
        "send-message": "إرسال رسالة",
        "file-url-label": "رابط الملف",
        "back-to-services": "العودة إلى الخدمات",
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