import PinyinMatchModule from 'pinyin-match';
import { inject } from '@vercel/analytics';
import { injectSpeedInsights } from '@vercel/speed-insights';

const PinyinMatch = PinyinMatchModule?.default || PinyinMatchModule;

try {
    inject();
    injectSpeedInsights();
} catch (error) {
    console.warn('[rectg] analytics/speed-insights init failed:', error);
}

function safeGetStorage(key) {
    try {
        return window.localStorage.getItem(key);
    } catch (error) {
        console.warn('[rectg] localStorage get failed:', error);
        return null;
    }
}

function safeSetStorage(key, value) {
    try {
        window.localStorage.setItem(key, value);
        return true;
    } catch (error) {
        console.warn('[rectg] localStorage set failed:', error);
        return false;
    }
}

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
    const savedTheme = safeGetStorage('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark');
    } else {
        document.body.classList.remove('dark');
    }

    themeToggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        safeSetStorage('theme', isDark ? 'dark' : 'light');
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

                // Vercel Analytics Bounce Rate Optimization: 
                // Push state forces a new pageview record for every category click without reloading
                if (id !== 'featured') {
                    const url = new URL(window.location);
                    url.searchParams.set('c', id);
                    window.history.pushState({}, '', url);
                } else {
                    const url = new URL(window.location);
                    url.searchParams.delete('c');
                    window.history.pushState({}, '', url);
                }
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

    searchInput?.addEventListener('input', (e) => {
        const query = (e.target.value || "").trim().toLowerCase();
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
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            const url = btn.getAttribute('data-url') || '';
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(url);
                    showToast('已复制链接');
                } else {
                    const textarea = document.createElement('textarea');
                    textarea.value = url;
                    textarea.style.position = 'fixed';
                    textarea.style.opacity = '0';
                    document.body.appendChild(textarea);
                    textarea.select();
                    const copied = document.execCommand('copy');
                    document.body.removeChild(textarea);
                    showToast(copied ? '已复制链接' : '复制失败');
                }
            } catch {
                showToast('复制失败');
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

// Routing initialization for direct deep-links like ?c=crypto
function initRouting() {
    const params = new URLSearchParams(window.location.search);
    const cat = params.get('c');
    if (cat) {
        setTimeout(() => {
            const section = document.getElementById(`cat-${cat}`);
            if (section) {
                const headerOffset = 80;
                const elementPosition = section.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                window.scrollTo({ top: offsetPosition, behavior: 'smooth' });

                document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
                const navItem = document.querySelector(`.nav-item[data-id="${cat}"]`);
                if (navItem) navItem.classList.add('active');
            }
        }, 300); // Wait for DOM layout
    }
}

// Init Likes
function initLikes() {
    document.querySelectorAll('.like-btn').forEach(btn => {
        const id = btn.getAttribute('data-id');
        if (!id) return;
        const countSpan = btn.querySelector('.like-count');

        // Generate pseudo-random count 12-511 based on string chars
        let baseCount = 0;
        for (let i = 0; i < id.length; i++) {
            baseCount += id.charCodeAt(i);
        }
        baseCount = (baseCount % 500) + 12;

        const isLiked = safeGetStorage('liked_' + id);
        if (isLiked) {
            baseCount++;
            btn.classList.add('liked');
        }
        if (countSpan) countSpan.textContent = baseCount;

        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation(); // Stop card click event overlay
            if (btn.classList.contains('liked')) return;

            btn.classList.add('liked');
            const svg = btn.querySelector('svg');
            if (svg) svg.classList.add('like-animation');
            if (countSpan) countSpan.textContent = parseInt(countSpan.textContent) + 1;
            safeSetStorage('liked_' + id, 'true');
        });
    });
}

// Init
function init() {
    const initTasks = [
        ['theme', initTheme],
        ['sidebar', initSidebar],
        ['search', initSearch],
        ['scrollSpy', initScrollSpy],
        ['interactions', initInteractions],
        ['scrollFeatures', initScrollFeatures],
        ['routing', initRouting],
        ['likes', initLikes]
    ];

    initTasks.forEach(([name, task]) => {
        try {
            task();
        } catch (error) {
            console.error(`[rectg] init failed: ${name}`, error);
        }
    });
}

// Astro executes script tags naturally via module, wait for DOM content is sometimes required, but module script handles it
// Using document.addEventListener('DOMContentLoaded', init) ensures it runs safely.
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
