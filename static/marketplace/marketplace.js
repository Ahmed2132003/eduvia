/* =============================================
   Eduvia Marketplace JS
   Matches home.js patterns exactly
   ============================================= */

// ---- Menu Toggle ----
function toggleMenu() {
    const menu = document.querySelector('.menu');
    if (menu) menu.classList.toggle('active');
}

// ---- Dark Mode ----
function toggleDarkMode() {
    const body = document.body;
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    body.classList.toggle('dark-mode');
    if (body.classList.contains('dark-mode')) {
        if (toggleIcon) { toggleIcon.classList.remove('fa-moon'); toggleIcon.classList.add('fa-sun'); }
        localStorage.setItem('theme', 'dark');
    } else {
        if (toggleIcon) { toggleIcon.classList.remove('fa-sun'); toggleIcon.classList.add('fa-moon'); }
        localStorage.setItem('theme', 'light');
    }
}

// ---- Language Toggle ----
const marketplaceTranslations = {
    en: {
        "title": "Eduvia Platform",
        "nav-home": "Home", "nav-courses": "Courses", "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions", "nav-performance": "Performance",
        "nav-about": "About Us", "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard", "nav-profile": "Profile",
        "nav-messages": "Messages", "nav-logout": "Logout",
        "nav-coins": "Coins:", "nav-login": "Login",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved.",

        /* access_restricted */
        "ar-hero-title": "Access Restricted",
        "ar-hero-sub": "This area requires an active course enrollment.",
        "ar-card-title": "Enrollment Required",
        "ar-card-desc": "You need at least one active course enrollment to access this area. Start your learning journey today!",
        "ar-btn-buy": "Browse Courses",

        /* checkout */
        "co-hero-title": "Course Checkout",
        "co-hero-sub": "Secure your learning journey today.",
        "co-enroll-title": "Activate with Code",
        "co-enroll-placeholder": "Enter enrollment code",
        "co-enroll-btn": "Activate",
        "co-pay-btn": "Proceed to Payment",

        /* wallet */
        "wa-hero-title": "Instructor Wallet",
        "wa-hero-sub": "Track your earnings and transactions.",
        "wa-pending": "Pending", "wa-available": "Available", "wa-withdrawn": "Withdrawn",
        "wa-tx-title": "Recent Transactions",
        "wa-no-tx": "No transactions yet.",

        /* my_courses */
        "mc-hero-title": "My Courses",
        "mc-hero-sub": "Continue your learning journey.",
        "mc-code-placeholder": "Course ID",
        "mc-enroll-placeholder": "Enrollment Code",
        "mc-apply-btn": "Apply Code",
        "mc-no-courses": "You are not enrolled in any course yet.",
    },
    ar: {
        "title": "منصة إدوفيا",
        "nav-home": "الرئيسية", "nav-courses": "الدورات", "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات", "nav-performance": "الأداء",
        "nav-about": "معلومات عنا", "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم", "nav-profile": "الملف الشخصي",
        "nav-messages": "الرسائل", "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:", "nav-login": "تسجيل الدخول",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود. جميع الحقوق محفوظة.",

        "ar-hero-title": "وصول مقيد",
        "ar-hero-sub": "هذه المنطقة تتطلب تسجيلًا نشطًا في دورة.",
        "ar-card-title": "يلزم التسجيل",
        "ar-card-desc": "تحتاج إلى التسجيل في دورة واحدة على الأقل للوصول إلى هذه المنطقة.",
        "ar-btn-buy": "استعرض الدورات",

        "co-hero-title": "الدفع",
        "co-hero-sub": "احجز رحلتك التعليمية اليوم.",
        "co-enroll-title": "تفعيل برمز",
        "co-enroll-placeholder": "أدخل رمز التسجيل",
        "co-enroll-btn": "تفعيل",
        "co-pay-btn": "الانتقال للدفع",

        "wa-hero-title": "محفظة المدرب",
        "wa-hero-sub": "تتبع أرباحك ومعاملاتك.",
        "wa-pending": "معلق", "wa-available": "متاح", "wa-withdrawn": "مسحوب",
        "wa-tx-title": "المعاملات الأخيرة",
        "wa-no-tx": "لا توجد معاملات بعد.",

        "mc-hero-title": "دوراتي",
        "mc-hero-sub": "تابع رحلتك التعليمية.",
        "mc-code-placeholder": "معرّف الدورة",
        "mc-enroll-placeholder": "رمز التسجيل",
        "mc-apply-btn": "تطبيق الرمز",
        "mc-no-courses": "لم تنضم إلى أي دورة بعد.",
    }
};

function toggleLanguage() {
    const htmlRoot = document.getElementById('html-root');
    const currentLang = htmlRoot.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    applyTranslations(newLang);
    localStorage.setItem('language', newLang);
}

function applyTranslations(lang) {
    const t = marketplaceTranslations[lang];
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (t[key] !== undefined) {
            if (el.tagName === 'INPUT' && el.type === 'text') {
                el.placeholder = t[key];
            } else {
                el.textContent = t[key];
            }
        }
    });
    document.querySelectorAll('[data-translate-placeholder]').forEach(el => {
        const key = el.getAttribute('data-translate-placeholder');
        if (t[key] !== undefined) el.placeholder = t[key];
    });
    document.title = t['title'] || document.title;
}

// ---- Scroll Animation ----
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
}

// ---- Card hover tilt effect ----
function initCardTilt() {
    document.querySelectorAll('.card, .card-glass').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(600px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg) translateY(-6px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}

// ---- Init on DOMContentLoaded ----
document.addEventListener('DOMContentLoaded', () => {
    // Apply saved theme
    const savedTheme = localStorage.getItem('theme');
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (toggleIcon) { toggleIcon.classList.remove('fa-moon'); toggleIcon.classList.add('fa-sun'); }
    }

    // Apply saved language
    const savedLang = localStorage.getItem('language') || 'en';
    const htmlRoot = document.getElementById('html-root');
    if (htmlRoot) {
        htmlRoot.setAttribute('lang', savedLang);
        htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');
        applyTranslations(savedLang);
    }

    initScrollAnimations();
    initCardTilt();
});