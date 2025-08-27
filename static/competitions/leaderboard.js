const translations = {
    en: {
        "leaderboard-title": "Leaderboard | Eduvia",
        "leaderboard-meta-desc": "View the leaderboard for educational competitions on the Eduvia platform and see student rankings based on XP and coins!",
        "leaderboard-meta-keywords": "leaderboard, educational competitions, Eduvia platform, interactive learning, learning challenges, XP, coins",
        "leaderboard-og-title": "Leaderboard | Eduvia",
        "leaderboard-og-desc": "View the leaderboard for educational competitions on the Eduvia platform and see student rankings based on XP and coins!",
        "leaderboard-meta-desc-en": "View the leaderboard for educational competitions on the Eduvia platform and see student rankings based on XP and coins!",
        "leaderboard-meta-keywords-en": "leaderboard, educational competitions, Eduvia platform, interactive learning, learning challenges, XP, coins",
        "hero-title": "Leaderboard: {{ competition.title }}",
        "content-title": "Leaderboard: {{ competition.title }}",
        "table-rank": "Rank",
        "table-student": "Student",
        "table-xp": "XP",
        "table-coins": "Coins",
        "table-no-participants": "No participants yet.",
        "back-link": "Back to Competition",
        "certificate-link": "Download Certificate",
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
        "leaderboard-title": "لوحة المتصدرين | إدوفيا",
        "leaderboard-meta-desc": "اطلع على لوحة المتصدرين للمسابقات التعليمية على منصة Eduvia وشاهد ترتيب الطلاب بناءً على نقاط XP والكوينز!",
        "leaderboard-meta-keywords": "لوحة المتصدرين, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, XP, كوينز",
        "leaderboard-og-title": "لوحة المتصدرين | إدوفيا",
        "leaderboard-og-desc": "اطلع على لوحة المتصدرين للمسابقات التعليمية على منصة Eduvia وشاهد ترتيب الطلاب بناءً على نقاط XP والكوينز!",
        "leaderboard-meta-desc-en": "اطلع على لوحة المتصدرين للمسابقات التعليمية على منصة Eduvia وشاهد ترتيب الطلاب بناءً على نقاط XP والكوينز!",
        "leaderboard-meta-keywords-en": "لوحة المتصدرين, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, XP, كوينز",
        "hero-title": "لوحة المتصدرين: {{ competition.title }}",
        "content-title": "لوحة المتصدرين: {{ competition.title }}",
        "table-rank": "المركز",
        "table-student": "الطالب",
        "table-xp": "XP",
        "table-coins": "النقاط",
        "table-no-participants": "لا يوجد متسابقون بعد.",
        "back-link": "العودة إلى المسابقة",
        "certificate-link": "تحميل الشهادة",
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
    
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (['hero-title', 'content-title'].includes(key)) {
            const competitionTitle = element.textContent.match(/Leaderboard: (.*)/)?.[1] || '{{ competition.title }}';
            text = translations[newLang][key].replace('{{ competition.title }}', competitionTitle);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["leaderboard-title"];
    
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
        } else if (['hero-title', 'content-title'].includes(key)) {
            const competitionTitle = element.textContent.match(/Leaderboard: (.*)/)?.[1] || '{{ competition.title }}';
            text = translations[savedLang][key].replace('{{ competition.title }}', competitionTitle);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["leaderboard-title"];
});