// Translation object
const translations = {
    en: {
        "add-question-title": "Add Question | Eduvia",
        "add-question-meta-desc": "Add new questions to educational competitions on the Eduvia platform to create engaging and interactive learning challenges for students!",
        "add-question-meta-keywords": "add questions, educational competitions, Eduvia platform, interactive learning, learning challenges, multiple choice questions, text questions",
        "add-question-og-title": "Add Question | Eduvia",
        "add-question-og-desc": "Add new questions to educational competitions on the Eduvia platform to create engaging and interactive learning challenges for students!",
        "hero-title": "Add Question to {{ competition.title }}",
        "hero-desc": "Create engaging questions to challenge students and enhance their learning experience!",
        "content-title": "Add Question to {{ competition.title }}",
        "label-question-text": "Question Text:",
        "label-question-type": "Question Type:",
        "option-mcq": "Multiple Choice",
        "option-text": "Text Answer",
        "label-choices": "Choices (comma-separated, for MCQ):",
        "label-correct-answer": "Correct Answer:",
        "label-points": "Points:",
        "label-coins": "Coins:",
        "button-add-question": "Add Question",
        "button-back": "Back to Competition",
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
        "add-question-title": "إضافة سؤال | إدوفيا",
        "add-question-meta-desc": "أضف أسئلة جديدة إلى المسابقات التعليمية على منصة إدوفيا لتصميم تحديات تعليمية ممتعة وتفاعلية للطلاب!",
        "add-question-meta-keywords": "إضافة أسئلة, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, أسئلة اختيارية, أسئلة نصية",
        "add-question-og-title": "إضافة سؤال | إدوفيا",
        "add-question-og-desc": "أضف أسئلة جديدة إلى المسابقات التعليمية على منصة إدوفيا لتصميم تحديات تعليمية ممتعة وتفاعلية للطلاب!",
        "hero-title": "إضافة سؤال إلى {{ competition.title }}",
        "hero-desc": "أنشئ أسئلة جذابة لتحدي الطلاب وتعزيز تجربة التعلم الخاصة بهم!",
        "content-title": "إضافة سؤال إلى {{ competition.title }}",
        "label-question-text": "نص السؤال:",
        "label-question-type": "نوع السؤال:",
        "option-mcq": "اختيار متعدد",
        "option-text": "إجابة نصية",
        "label-choices": "الخيارات (مفصولة بفواصل، للاختيار المتعدد):",
        "label-correct-answer": "الإجابة الصحيحة:",
        "label-points": "النقاط:",
        "label-coins": "النقاط المكتسبة:",
        "button-add-question": "إضافة السؤال",
        "button-back": "العودة إلى المسابقة",
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
        const text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'label') {
            const input = element.querySelector('input') || element.querySelector('select');
            element.childNodes[0].textContent = text + " ";
            if (input) input.parentNode.insertBefore(element.childNodes[0], input);
        } else {
            element.textContent = text;
        }
    });

    // Update the title (handle dynamic competition title)
    const compTitle = "{{ competition.title }}";
    document.title = translations[newLang]["add-question-title"];
    document.querySelectorAll('[data-translate="hero-title"]').forEach(element => {
        element.textContent = translations[newLang]["hero-title"].replace("{{ competition.title }}", compTitle);
    });
    document.querySelectorAll('[data-translate="content-title"]').forEach(element => {
        element.textContent = translations[newLang]["content-title"].replace("{{ competition.title }}", compTitle);
    });

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

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        const text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'label') {
            const input = element.querySelector('input') || element.querySelector('select');
            element.childNodes[0].textContent = text + " ";
            if (input) input.parentNode.insertBefore(element.childNodes[0], input);
        } else {
            element.textContent = text;
        }
    });

    // Set the title and dynamic content on page load
    const compTitle = "{{ competition.title }}";
    document.title = translations[savedLang]["add-question-title"];
    document.querySelectorAll('[data-translate="hero-title"]').forEach(element => {
        element.textContent = translations[savedLang]["hero-title"].replace("{{ competition.title }}", compTitle);
    });
    document.querySelectorAll('[data-translate="content-title"]').forEach(element => {
        element.textContent = translations[savedLang]["content-title"].replace("{{ competition.title }}", compTitle);
    });
});