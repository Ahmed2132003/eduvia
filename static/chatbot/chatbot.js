/* ═══════════════════════════════════════════════
   EDUVIA Chatbot JS — Premium Edition
   ═══════════════════════════════════════════════ */

const translations = {
    en: {
        "chatbot-title": "Chatbot - Eduvia",
        "chatbot-meta-desc": "Interact with Eduvia's chatbot. Ask questions about programming, mathematics, English, or our platform!",
        "chatbot-meta-keywords": "Eduvia, chatbot, online learning, programming, mathematics, English",
        "chatbot-og-title": "Chatbot - Eduvia",
        "chatbot-og-desc": "Interact with Eduvia's chatbot.",
        "chatbot-twitter-title": "Chatbot - Eduvia",
        "chatbot-twitter-desc": "Interact with Eduvia's chatbot.",
        "chatbot-hero-title": "Welcome to Eduvia's Chatbot",
        "chatbot-hero-desc": "Eduvia's Chatbot is here to help you with programming, mathematics, and English. Feel free to ask any questions related to these topics or our platform!",
        "chatbot-hero-btn": "Start Chatting",
        "chatbot-input-placeholder": "Type your message here...",
        "chatbot-send": "Send",
        "chatbot-loading": "Thinking",
        "chatbot-chats-title": "Your Chats",
        "chatbot-new-chat": "New Chat",
        "chatbot-no-chats": "No chats yet.",
        "chatbot-message-limit": "Messages today: ",
        "chatbot-limit-reached-free": "You have reached the daily message limit (5 messages). Please subscribe to continue chatting.",
        "chatbot-limit-reached-basic": "You have reached the daily message limit (30 messages). Please upgrade to Pro to continue chatting.",
        "chatbot-limit-reached-pro": "You have reached the daily message limit (60 messages). Please upgrade to Premium to continue chatting.",
        "chatbot-subscribe": "Subscribe Now",
        "chatbot-error": "Error: ",
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
        "search-placeholder": "Search for a course...",
        "search-btn": "Search",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "chatbot-title": "روبوت الدردشة - إدوفيا",
        "chatbot-meta-desc": "تفاعل مع روبوت الدردشة الخاص بـ إدوفيا. اطرح أسئلتك حول البرمجة، الرياضيات، الإنجليزية، أو منصتنا!",
        "chatbot-meta-keywords": "إدوفيا، روبوت الدردشة، التعلم عبر الإنترنت، البرمجة، الرياضيات، الإنجليزية",
        "chatbot-og-title": "روبوت الدردشة - إدوفيا",
        "chatbot-og-desc": "تفاعل مع روبوت الدردشة الخاص بـ إدوفيا.",
        "chatbot-twitter-title": "روبوت الدردشة - إدوفيا",
        "chatbot-twitter-desc": "تفاعل مع روبوت الدردشة الخاص بـ إدوفيا.",
        "chatbot-hero-title": "مرحبًا بك في روبوت الدردشة الخاص بإدوفيا",
        "chatbot-hero-desc": "روبوت الدردشة الخاص بإدوفيا هنا لمساعدتك في البرمجة، الرياضيات، والإنجليزية. لا تتردد في طرح أي أسئلة تتعلق بهذه المواضيع أو منصتنا!",
        "chatbot-hero-btn": "ابدأ الدردشة",
        "chatbot-input-placeholder": "اكتب رسالتك هنا...",
        "chatbot-send": "إرسال",
        "chatbot-loading": "جارٍ التفكير",
        "chatbot-chats-title": "محادثاتك",
        "chatbot-new-chat": "محادثة جديدة",
        "chatbot-no-chats": "لا توجد محادثات بعد.",
        "chatbot-message-limit": "الرسائل اليوم: ",
        "chatbot-limit-reached-free": "لقد وصلت إلى الحد الأقصى للرسائل اليومية (5 رسائل). يرجى الاشتراك لمواصلة الدردشة.",
        "chatbot-limit-reached-basic": "لقد وصلت إلى الحد الأقصى للرسائل اليومية (30 رسالة). يرجى ترقية باقتك إلى Pro لمواصلة الدردشة.",
        "chatbot-limit-reached-pro": "لقد وصلت إلى الحد الأقصى للرسائل اليومية (60 رسالة). يرجى ترقية باقتك إلى Premium لمواصلة الدردشة.",
        "chatbot-subscribe": "اشترك الآن",
        "chatbot-error": "خطأ: ",
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
        "search-placeholder": "ابحث عن دورة...",
        "search-btn": "بحث",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود. جميع الحقوق محفوظة."
    }
};

/* ─── Helpers ─── */
function getLang() {
    return document.getElementById('html-root').getAttribute('lang') || 'en';
}

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }
    return null;
}

function applyTranslations(lang) {
    const t = translations[lang];
    if (!t) return;

    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        const text = t[key];
        if (!text) return;

        const tag = el.tagName.toLowerCase();
        if (tag === 'meta') {
            if (el.getAttribute('name') === 'description' ||
                el.getAttribute('name') === 'keywords' ||
                el.getAttribute('property')?.startsWith('og:') ||
                el.getAttribute('name')?.startsWith('twitter:')) {
                el.setAttribute('content', text);
            }
        } else if (tag === 'input' && el.getAttribute('type') === 'text') {
            el.setAttribute('placeholder', text);
        } else {
            // Preserve child icons — only update text nodes
            const iconEl = el.querySelector('i');
            if (iconEl) {
                // Set text after the icon
                const textNode = [...el.childNodes].find(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim());
                if (textNode) textNode.textContent = ' ' + text;
                else el.appendChild(document.createTextNode(' ' + text));
            } else {
                el.textContent = text;
            }
        }
    });

    document.title = t["chatbot-title"] || document.title;
}

/* ─── Send Message ─── */
async function sendMessage() {
    const inputField  = document.getElementById("user-input");
    const sendButton  = document.getElementById("send-button");
    const messagesDiv = document.getElementById("chat-messages");
    const loadingDiv  = document.getElementById("loading");
    const errorDiv    = document.getElementById("error-message");
    const lang        = getLang();
    const userMessage = inputField.value.trim();

    if (!userMessage) {
        errorDiv.textContent = (translations[lang]["chatbot-error"] || "Error: ") + "Message cannot be empty";
        errorDiv.style.display = "block";
        return;
    }

    errorDiv.style.display = "none";

    // Append user message bubble
    const userDiv = document.createElement("div");
    userDiv.className = "message user-message";
    userDiv.textContent = userMessage;
    messagesDiv.appendChild(userDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Disable UI
    sendButton.disabled = true;
    loadingDiv.style.display = "block";
    inputField.value = "";

    try {
        const response = await fetch(window.location.href, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();

        if (data.redirect) {
            window.location.href = data.redirect;
            return;
        }

        if (data.error) {
            errorDiv.textContent = (translations[lang]["chatbot-error"] || "Error: ") + data.error;
            errorDiv.style.display = "block";
        } else {
            const botDiv = document.createElement("div");
            botDiv.className = "message bot-message";
            botDiv.textContent = data.response;
            messagesDiv.appendChild(botDiv);

            // Update sidebar if new chat created
            if (data.chat_id && !document.querySelector(`.sidebar ul li a[href="/chatbot/${data.chat_id}/"]`)) {
                const chatList = document.querySelector('.sidebar ul');
                const newItem  = document.createElement('li');
                newItem.innerHTML = `<a href="/chatbot/${data.chat_id}/" class="active">
                    <i class="fas fa-comment-dots" style="font-size:11px;opacity:.5;margin-inline-end:6px;"></i>
                    ${data.chat_title} · ${new Date().toLocaleDateString()}</a>`;
                chatList.insertBefore(newItem, chatList.firstChild);
                chatList.querySelectorAll('a').forEach(a => {
                    if (a.getAttribute('href') !== `/chatbot/${data.chat_id}/`) a.classList.remove('active');
                });
            }

            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    } catch (err) {
        errorDiv.textContent = (translations[lang]["chatbot-error"] || "Error: ") + err.message;
        errorDiv.style.display = "block";
        console.error('Fetch error:', err);
    } finally {
        sendButton.disabled = false;
        loadingDiv.style.display = "none";
    }
}

/* ─── Toggle Menu ─── */
function toggleMenu() {
    document.querySelector('.menu').classList.toggle('active');
}

/* ─── Toggle Dark Mode ─── */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const icon = document.getElementById('theme-icon');
    const isDark = document.body.classList.contains('dark-mode');
    // Only swap moon ↔ sun; globe icon is separate and never touched
    if (icon) icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

/* ─── Toggle Language ─── */
function toggleLanguage() {
    const html    = document.getElementById('html-root');
    const newLang = html.getAttribute('lang') === 'en' ? 'ar' : 'en';
    html.setAttribute('lang', newLang);
    html.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    localStorage.setItem('language', newLang);
    applyTranslations(newLang);
    // Globe icon stays — do NOT reassign language-toggle icon
}

/* ─── DOMContentLoaded ─── */
document.addEventListener('DOMContentLoaded', () => {
    // Restore theme
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        const icon = document.getElementById('theme-icon');
        if (icon) icon.className = 'fas fa-sun';
    }

    // Restore language
    const savedLang = localStorage.getItem('language') || 'en';
    const html = document.getElementById('html-root');
    html.setAttribute('lang', savedLang);
    html.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');
    applyTranslations(savedLang);

    // Enter key to send
    const input = document.getElementById("user-input");
    if (input) {
        input.addEventListener("keypress", e => {
            if (e.key === "Enter") { e.preventDefault(); sendMessage(); }
        });
    }

    // New chat cleanup
    const newChatBtn = document.querySelector('.new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => localStorage.removeItem('currentChatId'));
    }

    // Scroll chat to bottom on load
    const messagesDiv = document.getElementById("chat-messages");
    if (messagesDiv) messagesDiv.scrollTop = messagesDiv.scrollHeight;
});