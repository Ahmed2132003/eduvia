const translations = {
    en: {
        "competition-details-title": "Competition Details | Eduvia",
        "competition-details-meta-desc": "Explore the details of educational competitions on the Eduvia platform, participate in challenges, answer questions, and earn XP and coins!",
        "competition-details-meta-keywords": "competition details, educational competitions, Eduvia platform, interactive learning, learning challenges, XP, coins",
        "competition-details-og-title": "Competition Details | Eduvia",
        "competition-details-og-desc": "Explore the details of educational competitions on the Eduvia platform, participate in challenges, answer questions, and earn XP and coins!",
        "hero-title": "{{ competition.title }}",
        "hero-desc": "Participate in this exciting challenge and earn rewards!",
        "content-title": "{{ competition.title }}",
        "description-label": "Description:",
        "start-label": "Start:",
        "end-label": "End:",
        "status-label": "Status:",
        "status-ongoing": "Ongoing",
        "status-not-active": "Not Active",
        "questions-heading": "Questions",
        "no-questions": "No questions yet.",
        "add-question-link": "Add New Question",
        "edit-competition-link": "Edit Competition",
        "join-competition-button": "Join Competition",
        "progress-heading": "Your Progress",
        "xp-label": "XP:",
        "coins-label": "Coins:",
        "no-questions-available": "No questions available.",
        "answered-label": "Answered",
        "answer-link": "Answer",
        "student-only-message": "Only students can participate in competitions.",
        "leaderboard-link": "View Leaderboard",
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
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "competition-details-title": "تفاصيل المسابقة | إدوفيا",
        "competition-details-meta-desc": "اكتشف تفاصيل المسابقة التعليمية على منصة إدوفيا، وشارك في التحديات، وأجب على الأسئلة، واكسب نقاط XP وكوينز!",
        "competition-details-meta-keywords": "تفاصيل المسابقة, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, XP, كوينز",
        "competition-details-og-title": "تفاصيل المسابقة | إدوفيا",
        "competition-details-og-desc": "اكتشف تفاصيل المسابقة التعليمية على منصة إدوفيا، وشارك في التحديات، وأجب على الأسئلة، واكسب نقاط XP وكوينز!",
        "hero-title": "{{ competition.title }}",
        "hero-desc": "شارك في هذا التحدي المثير واكسب مكافآت!",
        "content-title": "{{ competition.title }}",
        "description-label": "الوصف:",
        "start-label": "البداية:",
        "end-label": "النهاية:",
        "status-label": "الحالة:",
        "status-ongoing": "جارية",
        "status-not-active": "غير نشطة",
        "questions-heading": "الأسئلة",
        "no-questions": "لا توجد أسئلة بعد.",
        "add-question-link": "إضافة سؤال جديد",
        "edit-competition-link": "تعديل المسابقة",
        "join-competition-button": "الانضمام إلى المسابقة",
        "progress-heading": "تقدمك",
        "xp-label": "نقاط الخبرة:",
        "coins-label": "النقاط المكتسبة:",
        "no-questions-available": "لا توجد أسئلة متاحة.",
        "answered-label": "تمت الإجابة",
        "answer-link": "الإجابة",
        "student-only-message": "يمكن للطلاب فقط المشاركة في المسابقات.",
        "leaderboard-link": "عرض قائمة المتصدرين",
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
        const text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'p' && ['description-label', 'start-label', 'end-label', 'status-label', 'xp-label', 'coins-label'].includes(key)) {
            const labelText = text + " ";
            const dynamicContent = element.childNodes[element.childNodes.length - 1].textContent.trim();
            element.textContent = labelText + dynamicContent;
        } else if (element.tagName.toLowerCase() === 'span' && ['status-ongoing', 'status-not-active', 'answered-label'].includes(key)) {
            element.textContent = text;
        } else if (element.tagName.toLowerCase() === 'li' && ['no-questions', 'no-questions-available'].includes(key)) {
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    const compTitle = "{{ competition.title }}";
    document.title = translations[newLang]["competition-details-title"];
    document.querySelectorAll('[data-translate="hero-title"]').forEach(element => {
        element.textContent = compTitle;
    });
    document.querySelectorAll('[data-translate="content-title"]').forEach(element => {
        element.textContent = compTitle;
    });

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
        const text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'p' && ['description-label', 'start-label', 'end-label', 'status-label', 'xp-label', 'coins-label'].includes(key)) {
            const labelText = text + " ";
            const dynamicContent = element.childNodes[element.childNodes.length - 1].textContent.trim();
            element.textContent = labelText + dynamicContent;
        } else if (element.tagName.toLowerCase() === 'span' && ['status-ongoing', 'status-not-active', 'answered-label'].includes(key)) {
            element.textContent = text;
        } else if (element.tagName.toLowerCase() === 'li' && ['no-questions', 'no-questions-available'].includes(key)) {
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    const compTitle = "{{ competition.title }}";
    document.title = translations[savedLang]["competition-details-title"];
    document.querySelectorAll('[data-translate="hero-title"]').forEach(element => {
        element.textContent = compTitle;
    });
    document.querySelectorAll('[data-translate="content-title"]').forEach(element => {
        element.textContent = compTitle;
    });
});