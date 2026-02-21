import PinyinMatch from 'pinyin-match';
import { inject } from '@vercel/analytics';

inject();

// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const menuBtn = document.getElementById('menu-btn');
const closeSidebarBtn = document.getElementById('close-sidebar-btn');
const themeToggle = document.getElementById('theme-toggle');
const searchInput = document.getElementById('search-input');
const toast = document.getElementById('toast');
const backToTopBtn = document.getElementById('back-to-top');
const progressBar = document.getElementById('progress-bar');
const categoryNav = document.getElementById('category-nav');
const emptyState = document.getElementById('empty-state');

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

    themeToggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

// Mobile Sidebar Handling
function initSidebar() {
    function openSidebar() {
        sidebar?.classList.add('open');
        sidebarOverlay?.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar?.classList.remove('open');
        sidebarOverlay?.classList.remove('open');
        document.body.style.overflow = '';
    }

    menuBtn?.addEventListener('click', openSidebar);
    closeSidebarBtn?.addEventListener('click', closeSidebar);
    sidebarOverlay?.addEventListener('click', closeSidebar);

    // Sidebar smooth scroll and active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');

            const id = item.dataset.id;
            const section = document.getElementById(`cat-${id}`);
            if (section) {
                const headerOffset = 80;
                const elementPosition = section.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }

            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    });
}

function highlightPinyin(text, matchPositions) {
    if (!matchPositions || !Array.isArray(matchPositions)) return text;
    const start = matchPositions[0];
    const end = matchPositions[1];
    return text.substring(0, start) + '<mark>' + text.substring(start, end + 1) + '</mark>' + text.substring(end + 1);
}

// Search Handling (DOM node filtering & highlighting)
function initSearch() {
    const sections = document.querySelectorAll('.category-section');
    let searchTimeout;

    searchInput?.addEventListener('input', (e) => {
        const query = (e.target.value || "").trim().toLowerCase();

        // PostHog analytics: wait 1 second after typing to capture the true search intent
        clearTimeout(searchTimeout);
        if (query.length > 0) {
            searchTimeout = setTimeout(() => {
                window.posthog?.capture('search_event', { search_query: query });
            }, 1500);
        }

        let hasVisibleCards = false;

        sections.forEach(section => {
            const sectionCards = section.querySelectorAll('.card');
            let visibleCount = 0;

            sectionCards.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const desc = card.getAttribute('data-desc') || '';
                const url = card.getAttribute('data-url') || '';
                const category = card.getAttribute('data-category') || '';

                const titleEl = card.querySelector('.card-title');
                const descEl = card.querySelector('.card-desc');

                if (!query) {
                    card.style.display = '';
                    visibleCount++;
                    // Reset HTML
                    if (titleEl) titleEl.textContent = title;
                    if (descEl) descEl.textContent = desc;
                } else {
                    const matchTitle = PinyinMatch.match(title, query);
                    const matchDesc = PinyinMatch.match(desc, query);
                    const matchCat = category.toLowerCase().includes(query);
                    const matchUrl = url.toLowerCase().includes(query);

                    if (matchTitle || matchDesc || matchUrl || matchCat) {
                        card.style.display = '';
                        visibleCount++;

                        // Apply highlights
                        if (titleEl) {
                            titleEl.innerHTML = Array.isArray(matchTitle) ? highlightPinyin(title, matchTitle) : title;
                        }
                        if (descEl) {
                            descEl.innerHTML = Array.isArray(matchDesc) ? highlightPinyin(desc, matchDesc) : desc;
                        }
                    } else {
                        card.style.display = 'none';
                    }
                }
            });

            if (visibleCount > 0) {
                section.style.display = '';
                hasVisibleCards = true;
            } else {
                section.style.display = 'none';
            }
        });

        if (emptyState) {
            emptyState.style.display = hasVisibleCards ? 'none' : 'block';
        }
    });
}

// Intersection Observer for active nav item
function initScrollSpy() {
    window.addEventListener('scroll', () => {
        let currentId = null;

        const sections = document.querySelectorAll('.category-section');
        for (const section of sections) {
            const rect = section.getBoundingClientRect();
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

// Interactions (Ripple, Copy)
function initInteractions() {
    // Ripple effect
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mousedown', function (event) {
            if (event.target.closest('.card-copy-btn')) return;

            const circle = document.createElement('span');
            const diameter = Math.max(card.clientWidth, card.clientHeight);
            const radius = diameter / 2;

            const rect = card.getBoundingClientRect();
            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${event.clientX - rect.left - radius}px`;
            circle.style.top = `${event.clientY - rect.top - radius}px`;
            circle.classList.add('ripple');

            const existingRipple = card.querySelector('.ripple');
            if (existingRipple) {
                existingRipple.remove();
            }

            card.appendChild(circle);

            setTimeout(() => {
                const r = card.querySelector('.ripple');
                if (r) r.remove();
            }, 600);
        });
    });

    // Copy buttons
    document.querySelectorAll('.card-copy-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const url = btn.getAttribute('data-url');

            // PostHog analytics: record which channel they copied
            const card = btn.closest('.card');
            const title = card ? card.getAttribute('data-title') : 'Unknown';
            window.posthog?.capture('copy_channel_link', { channel_name: title, channel_url: url });

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(() => showToast('已复制链接')).catch(() => showToast('复制失败'));
            } else {
                showToast('当前环境不支持快捷复制');
            }
        });
    });
}

// Back to top & Progress Bar logic
function initScrollFeatures() {
    window.addEventListener('scroll', () => {
        if (backToTopBtn) {
            if (window.scrollY > 500) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        }

        if (progressBar) {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + "%";
        }
    });

    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Init
function init() {
    initTheme();
    initSidebar();
    initSearch();
    initScrollSpy();
    initInteractions();
    initScrollFeatures();
}

// Astro executes script tags naturally via module, wait for DOM content is sometimes required, but module script handles it
// Using document.addEventListener('DOMContentLoaded', init) ensures it runs safely.
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
