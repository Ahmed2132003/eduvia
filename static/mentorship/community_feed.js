// Translation object
const translations = {
    en: {
        "feed-title": "Community Feed - Eduvia",
        "feed-meta-desc": "Join the Eduvia community feed to share and engage with programming and job market discussions.",
        "feed-meta-keywords": "community feed, Eduvia, programming, job market",
        "feed-og-title": "Community Feed - Eduvia",
        "feed-og-desc": "Join the Eduvia community feed to share and engage with programming and job market discussions.",
        "feed-heading": "Community Feed",
        "post-placeholder": "Share something about programming or job market...",
        "post-button": "Post",
        "like": "Like",
        "unlike": "Unlike",
        "dislike": "Dislike",
        "remove-dislike": "Remove Dislike",
        "comments": "Comments",
        "no-comments": "No comments yet.",
        "comment-placeholder": "Write a comment...",
        "comment-button": "Comment",
        "no-posts": "No posts yet!",
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
        "feed-title": "تغذية المجتمع - إدوفيا",
        "feed-meta-desc": "انضم إلى تغذية مجتمع إدوفيا لمشاركة النقاشات وتفاعلها حول البرمجة وسوق العمل.",
        "feed-meta-keywords": "تغذية المجتمع, إدوفيا, البرمجة, سوق العمل",
        "feed-og-title": "تغذية المجتمع - إدوفيا",
        "feed-og-desc": "انضم إلى تغذية مجتمع إدوفيا لمشاركة النقاشات وتفاعلها حول البرمجة وسوق العمل.",
        "feed-heading": "تغذية المجتمع",
        "post-placeholder": "شارك شيئًا عن البرمجة أو سوق العمل...",
        "post-button": "نشر",
        "like": "إعجاب",
        "unlike": "إلغاء الإعجاب",
        "dislike": "عدم الإعجاب",
        "remove-dislike": "إزالة عدم الإعجاب",
        "comments": "تعليقات",
        "no-comments": "لا توجد تعليقات بعد.",
        "comment-placeholder": "اكتب تعليقًا...",
        "comment-button": "تعليق",
        "no-posts": "لا توجد منشورات بعد!",
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
    document.querySelectorAll('[data-translate], [data-translate-placeholder], [data-translate-like], [data-translate-dislike]').forEach(element => {
        const key = element.getAttribute('data-translate') || element.getAttribute('data-translate-placeholder') || element.getAttribute('data-translate-like') || element.getAttribute('data-translate-dislike');
        let text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'textarea' && element.hasAttribute('data-translate-placeholder')) {
            element.setAttribute('placeholder', text);
        } else if (element.tagName.toLowerCase() === 'button' && (element.hasAttribute('data-translate-like') || element.hasAttribute('data-translate-dislike'))) {
            const action = element.hasAttribute('data-translate-like') ? element.getAttribute('data-translate-like') : element.getAttribute('data-translate-dislike');
            text = translations[newLang][action];
            if (element.textContent.includes('(')) {
                const count = element.textContent.match(/\(([^)]+)\)/)[1];
                text += ` (${count})`;
            }
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    // Update the title
    document.title = translations[newLang]["feed-title"];

    localStorage.setItem('language', newLang);
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

    document.querySelectorAll('[data-translate], [data-translate-placeholder], [data-translate-like], [data-translate-dislike]').forEach(element => {
        const key = element.getAttribute('data-translate') || element.getAttribute('data-translate-placeholder') || element.getAttribute('data-translate-like') || element.getAttribute('data-translate-dislike');
        let text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'textarea' && element.hasAttribute('data-translate-placeholder')) {
            element.setAttribute('placeholder', text);
        } else if (element.tagName.toLowerCase() === 'button' && (element.hasAttribute('data-translate-like') || element.hasAttribute('data-translate-dislike'))) {
            const action = element.hasAttribute('data-translate-like') ? element.getAttribute('data-translate-like') : element.getAttribute('data-translate-dislike');
            text = translations[savedLang][action];
            if (element.textContent.includes('(')) {
                const count = element.textContent.match(/\(([^)]+)\)/)[1];
                text += ` (${count})`;
            }
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    // Set the title on page load
    document.title = translations[savedLang]["feed-title"];
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.show-comments').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default link behavior
            const commentsSection = this.closest('.post').querySelector('.comments-section');
            if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
                commentsSection.style.display = 'block';
            } else {
                commentsSection.style.display = 'none';
            }
        });
    });
});