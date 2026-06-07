function safeSetStorage(key, value) {
    try {
        window.localStorage.setItem(key, value);
        return true;
    } catch (error) {
        console.warn('[rectg] localStorage set failed:', error);
        return false;
    }
}

let toastTimeout;

function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast.classList.remove('show'), 2000);
}

async function copyUrl(url) {
    const clipboard = window.navigator?.clipboard;
    try {
        if (clipboard?.writeText) {
            await clipboard.writeText(url);
            return true;
        }
    } catch (error) {
        console.warn('[rectg] clipboard api failed, falling back:', error);
    }

    const textarea = document.createElement('textarea');
    textarea.value = url;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.top = '0';
    textarea.style.left = '0';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);

    try {
        return document.execCommand('copy');
    } finally {
        document.body.removeChild(textarea);
    }
}

function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeMeta = document.getElementById('theme-color-meta');

    function syncThemeMeta() {
        themeMeta?.setAttribute('content', document.body.classList.contains('dark') ? '#111418' : '#ffffff');
    }

    syncThemeMeta();

    themeToggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        safeSetStorage('theme', isDark ? 'dark' : 'light');
        syncThemeMeta();
    });
}

function initCopyButtons() {
    document.getElementById('content-container')?.addEventListener('click', async (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;

        const button = target.closest('.card-copy-btn');
        if (!button) return;

        event.preventDefault();
        const url = button.getAttribute('data-url') || '';

        try {
            showToast((await copyUrl(url)) ? '已复制链接' : '复制失败');
        } catch {
            showToast('复制失败');
        }
    });
}

function init() {
    initTheme();
    initCopyButtons();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
