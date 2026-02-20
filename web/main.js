import './style.css';

// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const menuBtn = document.getElementById('menu-btn');
const closeSidebarBtn = document.getElementById('close-sidebar-btn');
const themeToggle = document.getElementById('theme-toggle');
const categoryNav = document.getElementById('category-nav');
const contentContainer = document.getElementById('content-container');
const searchInput = document.getElementById('search-input');
const bulletinText = document.getElementById('bulletin-text');
const toast = document.getElementById('toast');
const backToTopBtn = document.getElementById('back-to-top');

let appData = null;
let currentSearch = '';

// Utilities
function getHashColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return Math.abs(hash) % 6; // Matching .avatar-color-X in CSS
}

function highlightText(text, search) {
    if (!search) return text;
    const escapedSearch = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedSearch})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

let toastTimeout;
function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

// Theme Handling
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark');
    } else {
        document.body.classList.remove('dark');
    }

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

// Mobile Sidebar Handling
function initSidebar() {
    function openSidebar() {
        sidebar.classList.add('open');
        sidebarOverlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
        document.body.style.overflow = '';
    }

    menuBtn.addEventListener('click', openSidebar);
    closeSidebarBtn.addEventListener('click', closeSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);

    // Close sidebar when clicking a nav link on mobile
    categoryNav.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && e.target.closest('.nav-item')) {
            closeSidebar();
        }
    });
}

// Data Fetching
async function loadData() {
    // Show skeleton screen
    contentContainer.innerHTML = `
        <div class="skeleton-wrapper">
            ${Array.from({ length: 12 }).map(() => `
                <div class="skeleton-card">
                    <div class="skeleton-header">
                        <div class="skeleton skeleton-avatar"></div>
                        <div class="skeleton-title-wrap">
                            <div class="skeleton skeleton-title"></div>
                            <div class="skeleton skeleton-meta"></div>
                        </div>
                    </div>
                    <div class="skeleton skeleton-line"></div>
                    <div class="skeleton skeleton-line"></div>
                    <div class="skeleton skeleton-line"></div>
                </div>
            `).join('')}
        </div>
    `;

    try {
        const res = await fetch('/data.json');
        appData = await res.json();

        // Count total items
        let totalItems = 0;
        appData.types.forEach(t => {
            t.categories.forEach(c => {
                totalItems += c.items.length;
            });
        });

        bulletinText.textContent = `本站数据基于 GitHub README 自动构建部署，已收录 ${totalItems}+ 高质量内容。`;

        renderSidebar();
        renderContent();
    } catch (err) {
        console.error('Failed to load data:', err);
        contentContainer.innerHTML = '<div class="empty-state">加载数据失败，请检查网络...</div>';
    }
}

// Render Sidebar
function renderSidebar() {
    categoryNav.innerHTML = '';

    appData.categories.forEach(cat => {
        const item = document.createElement('div');
        item.className = 'nav-item';
        item.dataset.id = cat.id;
        item.innerHTML = `
            <span class="nav-icon">${cat.icon}</span>
            <span>${cat.name}</span>
        `;

        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');

            // Scroll to section
            const section = document.getElementById(`cat-${cat.id}`);
            if (section) {
                const headerOffset = 80;
                const elementPosition = section.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });

        categoryNav.appendChild(item);
    });
}

// Render Content
function renderContent() {
    contentContainer.innerHTML = '';

    if (!appData) return;

    let hasResults = false;

    // Group all items by category across all types to match reference site layout
    // The reference site doesn't group by "Channel/Group", it just groups by category

    const categoryGroups = {};
    appData.categories.forEach(c => {
        categoryGroups[c.id] = { meta: c, items: [] };
    });

    appData.types.forEach(typeObj => {
        typeObj.categories.forEach(catObj => {
            const catMeta = appData.categories.find(c => c.fullName === catObj.fullName);
            if (catMeta) {
                categoryGroups[catMeta.id].items.push(...catObj.items.map(item => ({ ...item, typeName: typeObj.name })));
            }
        });
    });

    Object.values(categoryGroups).forEach(group => {
        const filteredItems = group.items.filter(item => {
            if (!currentSearch) return true;
            const s = currentSearch.toLowerCase();
            return (item.title && item.title.toLowerCase().includes(s)) ||
                (item.desc && item.desc.toLowerCase().includes(s)) ||
                (item.url && item.url.toLowerCase().includes(s));
        });

        if (filteredItems.length === 0) return;
        hasResults = true;

        // Sort items by count (highest first)
        filteredItems.sort((a, b) => {
            const countA = a.countStr ? parseInt(a.countStr.replace(/,/g, '')) : 0;
            const countB = b.countStr ? parseInt(b.countStr.replace(/,/g, '')) : 0;
            return countB - countA;
        });

        const section = document.createElement('div');
        section.className = 'category-section';
        section.id = `cat-${group.meta.id}`;

        section.innerHTML = `
            <h3 class="category-title">
                ${group.meta.fullName}
                <span style="color: var(--text-muted); font-size: 0.9rem; font-weight: normal;">(${filteredItems.length})</span>
            </h3>
            <div class="grid">
                ${filteredItems.map(item => {
            // Extract Telegram username for avatar
            let username = '';
            if (item.url && item.url.includes('t.me/')) {
                const parts = item.url.split('t.me/');
                if (parts.length > 1) {
                    username = parts[1].split('/')[0].split('?')[0]; // Handle extra paths or queries
                }
            }

            const avatarUrl = username ? `https://unavatar.io/telegram/${username}` : '';
            const firstLetter = item.title ? item.title.substring(0, 1).toUpperCase() : '?';
            const colorClass = `avatar-color-${getHashColor(firstLetter)}`;

            const displayTitle = highlightText(item.title, currentSearch);
            const displayDesc = highlightText(item.desc || '没有描述', currentSearch);

            return `
                    <div class="card">
                        <a href="${item.url}" target="_blank" rel="noopener" class="card-link"></a>
                        <button class="card-copy-btn" aria-label="复制链接" data-url="${item.url}">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        </button>
                        <div class="card-header">
                            <div class="card-icon ${colorClass}">
                                ${avatarUrl ?
                    `<img src="${avatarUrl}" loading="lazy" alt="${username}" onerror="this.onerror=null; this.parentNode.innerHTML='${firstLetter}';" />`
                    : firstLetter}
                            </div>
                            <div class="card-title-wrap">
                                <div class="card-title" title="${item.title}">${displayTitle}</div>
                                <div class="card-meta">
                                    <span class="tag">${item.typeName || '频道'}</span>
                                    <span>${item.countStr ? '👥 ' + item.countStr : ''}</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-desc" title="${item.desc}">${displayDesc}</div>
                    </div>
                    `;
        }).join('')}
            </div>
        `;
        contentContainer.appendChild(section);
    });

    // Setup copy button event listeners
    document.querySelectorAll('.card-copy-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const url = btn.getAttribute('data-url');
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(() => showToast('已复制链接')).catch(() => showToast('复制失败'));
            } else {
                showToast('当前环境不支持快捷复制');
            }
        });
    });

    if (!hasResults) {
        contentContainer.innerHTML = `
            <div class="empty-state">
                <h3>未找到匹配的结果</h3>
                <p>尝试搜索其他关键词</p>
            </div>
        `;
    }
}

// Search Handling
function initSearch() {
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value.trim();
        renderContent();
    });
}

// Intersection Observer for active nav item
function initScrollSpy() {
    // Simple scroll spy logic
    window.addEventListener('scroll', () => {
        if (!appData) return;
        let currentId = null;

        // Find the section that is currently most visible in the viewport
        const sections = document.querySelectorAll('.category-section');
        for (const section of sections) {
            const rect = section.getBoundingClientRect();
            // If the top of the section is somewhat near the top of viewport but not totally scrolled past
            if (rect.top <= 100 && rect.bottom >= 100) {
                currentId = section.id.replace('cat-', '');
                break;
            }
        }

        if (currentId) {
            document.querySelectorAll('.nav-item').forEach(el => {
                if (el.dataset.id === currentId) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });
        }
    });
}

// Back to top logic
function initBackToTop() {
    if (!backToTopBtn) return;
    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Init
function init() {
    initTheme();
    initSidebar();
    initSearch();
    initBackToTop();
    loadData().then(() => {
        initScrollSpy();
    });
}

init();
