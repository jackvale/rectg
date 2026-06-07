import PinyinMatchModule from 'pinyin-match';

const PinyinMatch = PinyinMatchModule?.default || PinyinMatchModule;

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

function readDirectoryData() {
    const payload = document.getElementById('directory-data');
    if (!payload?.textContent) return { sections: [], allItems: [] };

    try {
        return JSON.parse(payload.textContent);
    } catch (error) {
        console.error('[rectg] failed to parse directory data:', error);
        return { sections: [], allItems: [] };
    }
}

let sidebar;
let sidebarOverlay;
let menuBtn;
let closeSidebarBtn;
let themeToggle;
let searchInput;
let clearSearchBtn;
let toast;
let backToTopBtn;
let progressBar;
let emptyState;
let contentContainer;
let activeSection;
let activeSectionTitle;
let activeSectionMeta;
let activeSectionDesc;
let activeGrid;
let resultStatus;
let resultStatusText;
let resultClearBtn;
let directoryData = { sections: [], allItems: [] };
let sections = [];
let allItems = [];
let currentSectionId = 'featured';
let toastTimeout;

function collectDomRefs() {
    sidebar = document.getElementById('sidebar');
    sidebarOverlay = document.getElementById('sidebar-overlay');
    menuBtn = document.getElementById('menu-btn');
    closeSidebarBtn = document.getElementById('close-sidebar-btn');
    themeToggle = document.getElementById('theme-toggle');
    searchInput = document.getElementById('search-input');
    clearSearchBtn = document.getElementById('clear-search-btn');
    toast = document.getElementById('toast');
    backToTopBtn = document.getElementById('back-to-top');
    progressBar = document.getElementById('progress-bar');
    emptyState = document.getElementById('empty-state');
    contentContainer = document.getElementById('content-container');
    activeSection = document.getElementById('active-section');
    activeSectionTitle = document.getElementById('active-section-title');
    activeSectionMeta = document.getElementById('active-section-meta');
    activeSectionDesc = document.getElementById('active-section-desc');
    activeGrid = document.getElementById('active-grid');
    resultStatus = document.getElementById('result-status');
    resultStatusText = document.getElementById('result-status-text');
    resultClearBtn = document.getElementById('result-clear-btn');
    directoryData = readDirectoryData();
    sections = Array.isArray(directoryData.sections) ? directoryData.sections : [];
    allItems = Array.isArray(directoryData.allItems)
        ? directoryData.allItems
        : sections
            .filter((section) => section.id !== 'featured')
            .flatMap((section) => section.items || []);
    currentSectionId = activeSection?.dataset.currentId || 'featured';
}

function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast.classList.remove('show'), 2000);
}

function hashText(value) {
    let hash = 2166136261;
    for (let i = 0; i < value.length; i += 1) {
        hash ^= value.charCodeAt(i);
        hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
}

function getAvatarColorClass(value) {
    return `avatar-color-${hashText(value || '?') % 6}`;
}

function getTelegramUsername(url) {
    if (!url || !url.includes('t.me/')) return '';
    const parts = url.split('t.me/');
    return parts[1]?.split('/')[0]?.split('?')[0] || '';
}

function parseCount(countStr) {
    if (!countStr || countStr === '-') return 0;
    const parsed = Number.parseInt(String(countStr).replace(/,/g, ''), 10);
    return Number.isFinite(parsed) ? parsed : 0;
}

function categoryPath(categoryId) {
    return `/category/${encodeURIComponent(categoryId)}/`;
}

function setHighlightedText(target, text, matchPositions) {
    if (!target) return;
    target.textContent = '';

    if (!matchPositions || !Array.isArray(matchPositions)) {
        target.textContent = text;
        return;
    }

    const start = Math.max(0, Math.min(text.length, matchPositions[0]));
    const end = Math.max(start, Math.min(text.length - 1, matchPositions[1]));

    target.appendChild(document.createTextNode(text.substring(0, start)));

    const mark = document.createElement('mark');
    mark.textContent = text.substring(start, end + 1);
    target.appendChild(mark);

    target.appendChild(document.createTextNode(text.substring(end + 1)));
}

function createCopyIcon() {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '14');
    svg.setAttribute('height', '14');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');

    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', '9');
    rect.setAttribute('y', '9');
    rect.setAttribute('width', '13');
    rect.setAttribute('height', '13');
    rect.setAttribute('rx', '2');
    rect.setAttribute('ry', '2');

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1');

    svg.append(rect, path);
    return svg;
}

function createCard(item, matches = {}) {
    const title = item.title || '';
    const desc = item.desc || '';
    const url = item.url || '';
    const categoryName = item.categoryName || item.categoryFullName || '';
    const username = getTelegramUsername(url);
    const firstLetter = title ? title.substring(0, 1).toUpperCase() : '?';
    const article = document.createElement('article');

    article.className = 'card';
    article.dataset.title = title;
    article.dataset.desc = desc;
    article.dataset.url = url;
    article.dataset.category = [item.categoryFullName, item.categoryKeywords, item.typeName].filter(Boolean).join(' ');

    const header = document.createElement('div');
    header.className = 'card-header';

    const icon = document.createElement('div');
    icon.className = `card-icon ${getAvatarColorClass(firstLetter)}`;
    icon.setAttribute('aria-hidden', 'true');
    if (username) {
        const img = document.createElement('img');
        img.src = `https://unavatar.io/telegram/${username}`;
        img.loading = 'lazy';
        img.decoding = 'async';
        img.alt = username;
        img.addEventListener('error', () => {
            icon.textContent = firstLetter;
        });
        icon.appendChild(img);
    } else {
        icon.textContent = firstLetter;
    }

    const titleWrap = document.createElement('div');
    titleWrap.className = 'card-title-wrap';

    const titleLink = document.createElement('a');
    titleLink.href = `/p/${item.id}/`;
    titleLink.className = 'card-title';
    titleLink.title = title;
    setHighlightedText(titleLink, title, matches.title);

    const meta = document.createElement('div');
    meta.className = 'card-meta';

    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = item.typeName || '资源';

    const categoryTag = document.createElement('span');
    categoryTag.className = 'tag category-tag';
    categoryTag.title = categoryName;
    categoryTag.textContent = categoryName || '未分类';

    const count = document.createElement('span');
    count.className = 'resource-count';
    count.textContent = `人数 ${item.countStr || '-'}`;
    meta.append(tag, categoryTag, count);
    titleWrap.append(titleLink, meta);
    header.append(icon, titleWrap);

    const descEl = document.createElement('div');
    descEl.className = 'card-desc';
    descEl.title = desc;
    setHighlightedText(descEl, desc || '暂无简介', matches.desc);

    const actions = document.createElement('div');
    actions.className = 'card-actions';

    const directLink = document.createElement('a');
    directLink.className = 'card-action card-action-primary';
    directLink.href = url;
    directLink.target = '_blank';
    directLink.rel = 'noopener noreferrer';
    directLink.textContent = '打开';

    const detailLink = document.createElement('a');
    detailLink.className = 'card-action';
    detailLink.href = `/p/${item.id}/`;
    detailLink.textContent = '详情';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'card-action card-copy-btn';
    copyBtn.type = 'button';
    copyBtn.setAttribute('aria-label', '复制链接');
    copyBtn.dataset.url = url;
    const copyLabel = document.createElement('span');
    copyLabel.className = 'copy-label';
    copyLabel.textContent = '复制';
    copyBtn.append(createCopyIcon(), copyLabel);

    actions.append(detailLink, directLink, copyBtn);
    article.append(header, descEl, actions);
    return article;
}

function renderCards(items, matchMap = new Map()) {
    if (!activeGrid) return;
    const fragment = document.createDocumentFragment();
    items.forEach((item) => {
        fragment.appendChild(createCard(item, matchMap.get(item.id) || {}));
    });
    activeGrid.replaceChildren(fragment);
}

function setActiveNav(id) {
    document.querySelectorAll('.nav-item, .mobile-category-item').forEach((item) => {
        item.classList.toggle('active', item.dataset.id === id);
    });
}

function updateUrl({ sectionId, query, replace = false }) {
    const url = new URL(window.location);
    if (query) {
        url.pathname = '/';
        url.searchParams.set('q', query);
        url.searchParams.delete('c');
    } else if (sectionId && sectionId !== 'featured') {
        url.pathname = categoryPath(sectionId);
        url.search = '';
        url.hash = '';
    } else {
        url.pathname = '/';
        url.searchParams.delete('c');
        url.searchParams.delete('q');
    }

    const method = replace ? 'replaceState' : 'pushState';
    window.history[method]({}, '', url);
}

function getSectionDescription(section) {
    if (!section) return '';
    if (section.id === 'featured') return '从全站目录选出的一组入口，按主题分布和人数参考整理。';
    const keywords = section.keywords ? `，关联关键词：${section.keywords}` : '';
    return `${section.items?.length || 0} 个资源，按订阅或成员数排序${keywords}。`;
}

function setSectionHeader(title, count, subtitle = '', description = '') {
    if (activeSectionTitle) activeSectionTitle.textContent = title;
    if (activeSectionMeta) {
        activeSectionMeta.textContent = subtitle || `(${count})`;
    }
    if (activeSectionDesc) {
        activeSectionDesc.textContent = description;
    }
}

function setResultStatus(message = '', show = false) {
    if (!resultStatus) return;
    resultStatus.hidden = !show;
    if (resultStatusText) resultStatusText.textContent = message;
}

function renderSection(id, options = {}) {
    const section = sections.find((candidate) => candidate.id === id) || sections[0];
    if (!section) return;

    currentSectionId = section.id;
    if (activeSection) activeSection.dataset.currentId = section.id;
    setActiveNav(section.id);
    setSectionHeader(
        section.fullName || section.name,
        section.items?.length || 0,
        '',
        getSectionDescription(section),
    );
    renderCards(section.items || []);
    setResultStatus('', false);
    if (emptyState) emptyState.style.display = 'none';
    if (activeSection) activeSection.style.display = '';
    if (searchInput && options.clearSearch) searchInput.value = '';
    clearSearchBtn?.classList.toggle('visible', Boolean(searchInput?.value?.trim()));
    if (options.updateUrl) updateUrl({ sectionId: section.id });
    if (options.scroll) {
        const top = activeSection
            ? activeSection.getBoundingClientRect().top + window.pageYOffset - 80
            : 0;
        window.scrollTo({ top, behavior: 'smooth' });
    }
}

function getMatches(item, query) {
    const title = item.title || '';
    const desc = item.desc || '';
    const url = item.url || '';
    const category = [item.categoryFullName, item.categoryKeywords, item.typeName].filter(Boolean).join(' ');
    const titleLower = title.toLowerCase();
    const descLower = desc.toLowerCase();
    const categoryLower = category.toLowerCase();
    const urlLower = url.toLowerCase();
    const matchTitle = PinyinMatch.match(title, query);
    const matchDesc = PinyinMatch.match(desc, query);
    const directTitle = titleLower.includes(query);
    const directDesc = descLower.includes(query);
    const matchCategory = categoryLower.includes(query);
    const matchUrl = urlLower.includes(query);

    if (!matchTitle && !directTitle && !matchDesc && !directDesc && !matchCategory && !matchUrl) return null;

    let score = 4;
    if (matchTitle || directTitle) score = titleLower.startsWith(query) ? 0 : 1;
    else if (matchCategory) score = 2;
    else if (matchDesc || directDesc) score = 3;

    return {
        title: matchTitle || (directTitle ? [titleLower.indexOf(query), titleLower.indexOf(query) + query.length - 1] : null),
        desc: matchDesc || (directDesc ? [descLower.indexOf(query), descLower.indexOf(query) + query.length - 1] : null),
        score,
    };
}

function renderSearch(rawQuery, options = {}) {
    const query = rawQuery.trim().toLowerCase();
    if (!query) {
        renderSection(currentSectionId, { updateUrl: options.updateUrl, clearSearch: false });
        return;
    }

    const matchMap = new Map();
    const results = allItems.reduce((items, item) => {
        const matches = getMatches(item, query);
        if (!matches) return items;
        matchMap.set(item.id, matches);
        items.push(item);
        return items;
    }, []).sort((a, b) => {
        const matchA = matchMap.get(a.id);
        const matchB = matchMap.get(b.id);
        if ((matchA?.score || 0) !== (matchB?.score || 0)) {
            return (matchA?.score || 0) - (matchB?.score || 0);
        }
        return parseCount(b.countStr) - parseCount(a.countStr);
    });

    setActiveNav('');
    setSectionHeader(
        '搜索结果',
        results.length,
        `“${rawQuery.trim()}” · ${results.length} 个资源`,
        results.length ? '按标题、分类、简介和 t.me 链接匹配。' : '换一个关键词，或使用左侧分类继续浏览。',
    );
    renderCards(results, matchMap);
    setResultStatus(
        results.length
            ? `按相关性排序，正在查看 “${rawQuery.trim()}”`
            : `没有找到 “${rawQuery.trim()}”`,
        true,
    );
    if (emptyState) emptyState.style.display = results.length ? 'none' : 'block';
    if (activeSection) activeSection.style.display = results.length ? '' : 'none';
    clearSearchBtn?.classList.toggle('visible', true);
    if (options.updateUrl) updateUrl({ query: rawQuery.trim(), replace: true });
}

function initTheme() {
    const savedTheme = safeGetStorage('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const themeMeta = document.getElementById('theme-color-meta');

    function syncThemeMeta() {
        themeMeta?.setAttribute('content', document.body.classList.contains('dark') ? '#111418' : '#ffffff');
    }

    document.body.classList.toggle('dark', savedTheme === 'dark' || (!savedTheme && prefersDark));
    syncThemeMeta();

    themeToggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        safeSetStorage('theme', isDark ? 'dark' : 'light');
        syncThemeMeta();
    });
}

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

    document.querySelectorAll('.nav-item, .mobile-category-item').forEach((item) => {
        item.addEventListener('click', (event) => {
            const id = item.dataset.id || 'featured';
            const href = item.getAttribute('href');
            if (href && id !== 'featured') {
                if (window.innerWidth <= 768) closeSidebar();
                return;
            }
            event.preventDefault();
            renderSection(id, { updateUrl: true, clearSearch: true, scroll: true });
            if (window.innerWidth <= 768) closeSidebar();
        });
    });
}

function initSearch() {
    function clearSearch({ focus = true } = {}) {
        if (!searchInput) return;
        searchInput.value = '';
        renderSection(currentSectionId, { updateUrl: true, clearSearch: false, scroll: false });
        clearSearchBtn?.classList.remove('visible');
        setResultStatus('', false);
        if (focus) searchInput.focus();
    }

    searchInput?.addEventListener('input', (event) => {
        renderSearch(event.target.value || '', { updateUrl: true });
    });

    clearSearchBtn?.addEventListener('click', () => clearSearch());
    resultClearBtn?.addEventListener('click', () => clearSearch());

    contentContainer?.addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const action = target.closest('[data-empty-action]')?.getAttribute('data-empty-action');
        if (!action) return;

        if (action === 'featured') {
            if (searchInput) searchInput.value = '';
            renderSection('featured', { updateUrl: true, clearSearch: false, scroll: true });
            clearSearchBtn?.classList.remove('visible');
            setResultStatus('', false);
        } else if (action === 'clear') {
            clearSearch();
        }
    });
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

function initInteractions() {
    contentContainer?.addEventListener('click', async (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;

        const btn = target.closest('.card-copy-btn');
        if (!btn) return;

        event.preventDefault();
        const url = btn.getAttribute('data-url') || '';
        try {
            showToast((await copyUrl(url)) ? '已复制链接' : '复制失败');
        } catch {
            showToast('复制失败');
        }
    });
}

function initScrollFeatures() {
    window.addEventListener('scroll', () => {
        backToTopBtn?.classList.toggle('show', window.scrollY > 500);

        if (progressBar) {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            progressBar.style.width = height > 0 ? `${(winScroll / height) * 100}%` : '0';
        }
    });

    backToTopBtn?.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

function initRouting() {
    const params = new URLSearchParams(window.location.search);
    const cat = params.get('c');
    const query = params.get('q');

    if (cat && !query) {
        window.location.replace(categoryPath(cat));
        return;
    }

    if (query && searchInput) {
        searchInput.value = query;
        renderSearch(query, { updateUrl: false });
    }
}

function init() {
    collectDomRefs();

    const initTasks = [
        ['theme', initTheme],
        ['sidebar', initSidebar],
        ['search', initSearch],
        ['interactions', initInteractions],
        ['scrollFeatures', initScrollFeatures],
        ['routing', initRouting],
    ];

    initTasks.forEach(([name, task]) => {
        try {
            task();
        } catch (error) {
            console.error(`[rectg] init failed: ${name}`, error);
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
