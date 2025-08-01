const translations = {
    en: {
        "title": "Register - Eduvia",
        "heading": "Create Your Eduvia Account",
        "subheading": "Join us and start your learning journey today!",
        "button-register": "Register",
        "footer-text": "Already have an account? ",
        "footer-link": "Login here",
        "label-username": "Username:",
        "label-email": "Email:",
        "label-password1": "Password:",
        "label-password2": "Confirm Password:",
        "label-role": "Role:"
    },
    ar: {
        "title": "التسجيل - إدوفيا",
        "heading": "إنشاء حسابك في إدوفيا",
        "subheading": "انضم إلينا وابدأ رحلتك التعليمية اليوم!",
        "button-register": "تسجيل",
        "footer-text": "هل لديك حساب بالفعل؟ ",
        "footer-link": "تسجيل الدخول هنا",
        "label-username": "اسم المستخدم:",
        "label-email": "البريد الإلكتروني:",
        "label-password1": "كلمة المرور:",
        "label-password2": "تأكيد كلمة المرور:",
        "label-role": "الدور:"
    }
};

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
        if (translations[newLang][key]) {
            element.textContent = translations[newLang][key];
        } else {
            console.warn(`Translation key "${key}" not found for language "${newLang}"`);
        }
    });

    document.querySelectorAll('form p label').forEach(label => {
        const forAttr = label.getAttribute('for');
        if (forAttr) {
            const fieldName = forAttr.toLowerCase();
            const translationKey = `label-${fieldName}`;
            if (translations[newLang][translationKey]) {
                label.textContent = translations[newLang][translationKey];
                label.setAttribute('data-translate', translationKey);
            }
        }
    });

    document.title = translations[newLang]["title"];
    
    localStorage.setItem('language', newLang);

    const loginButton = document.querySelector('button.login-btn[data-translate="footer-link"]');
    if (loginButton) {
        loginButton.style.display = 'inline-block';
        loginButton.style.visibility = 'visible';
        console.log('Login button text after language change:', loginButton.textContent);
    }
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
        if (translations[savedLang][key]) {
            element.textContent = translations[savedLang][key];
        } else {
            console.warn(`Translation key "${key}" not found for language "${savedLang}"`);
        }
    });

    document.querySelectorAll('form p label').forEach(label => {
        const forAttr = label.getAttribute('for');
        if (forAttr) {
            const fieldName = forAttr.toLowerCase();
            const translationKey = `label-${fieldName}`;
            if (translations[savedLang][translationKey]) {
                label.textContent = translations[savedLang][translationKey];
                label.setAttribute('data-translate', translationKey);
            }
        }
    });

    document.title = translations[savedLang]["title"];

    const loginButton = document.querySelector('button.login-btn[data-translate="footer-link"]');
    if (loginButton) {
        loginButton.style.display = 'inline-block';
        loginButton.style.visibility = 'visible';
        console.log('Login button text:', loginButton.textContent);
    } else {
        console.error('Login button element not found');
    }
});