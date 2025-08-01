const translations = {
    en: {
        "page-title": "Opportunities - Eduvia",
        "meta-desc": "Discover job opportunities in Eduvia's Skills Market, connecting students with career prospects.",
        "meta-keywords": "job opportunities, skills market, student jobs, Eduvia, freelance",
        "og-title": "Opportunities - Eduvia",
        "og-desc": "Discover job opportunities in Eduvia's Skills Market, connecting students with career prospects.",
        "hero-title": "Job Opportunities",
        "hero-desc": "Discover job opportunities in Eduvia's Skills Market, connecting students with career prospects.",
        "card-provider": "Provider:",
        "card-salary": "Salary:",
        "card-coins": "Coins",
        "card-address": "Address:",
        "card-apply": "Apply Now",
        "no-opportunities": "No opportunities available.",
        "btn-add-opportunity": "Add Opportunity",
        "btn-view-applications": "View Applications",
        "btn-applicant-messages": "Applicant Messages",
        "btn-provider-messages": "Provider Messages",
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
        "page-title": "الفرص - إدوفيا",
        "meta-desc": "اكتشف فرص العمل في سوق المهارات بإدوفيا، الذي يربط الطلاب بآفاق مهنية.",
        "meta-keywords": "فرص عمل, سوق المهارات, وظائف الطلاب, إدوفيا, عمل حر",
        "og-title": "الفرص - إدوفيا",
        "og-desc": "اكتشف فرص العمل في سوق المهارات بإدوفيا، الذي يربط الطلاب بآفاق مهنية.",
        "hero-title": "فرص العمل",
        "hero-desc": "اكتشف فرص العمل في سوق المهارات بإدوفيا، الذي يربط الطلاب بآفاق مهنية.",
        "card-provider": "المزود:",
        "card-salary": "الراتب:",
        "card-coins": "نقاط",
        "card-address": "العنوان:",
        "card-apply": "قدّم الآن",
        "no-opportunities": "لا توجد فرص متاحة.",
        "btn-add-opportunity": "إضافة فرصة",
        "btn-view-applications": "عرض الطلبات",
        "btn-applicant-messages": "رسائل المتقدم",
        "btn-provider-messages": "رسائل المزود",
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