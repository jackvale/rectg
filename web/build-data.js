import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const README_PATH = path.resolve(__dirname, '../README.md');
const OUT_DIR = path.resolve(__dirname, 'public');
const OUT_FILE = path.resolve(OUT_DIR, 'data.json');

function main() {
    const content = fs.readFileSync(README_PATH, 'utf-8');
    const lines = content.split('\n');

    const data = {
        categories: [],
        types: []
    };

    let currentType = null;
    let currentCategory = null;
    let currentItem = null;
    let currentItemProps = [];
    const categorySet = new Set();
    const categoriesList = [];
    const typeMap = {};

    function cleanMarkdownText(text) {
        return text
            .replace(/\\([\[\]])/g, '$1')
            .trim();
    }

    function extractDesc(descCell) {
        const hiddenMatch = descCell.match(/<!--\s*rectg-desc:([A-Za-z0-9+/=]+)\s*-->/);
        if (hiddenMatch) {
            try {
                return Buffer.from(hiddenMatch[1], 'base64').toString('utf8').trim();
            } catch {
                // Fall back to the visible README text if the hidden payload is malformed.
            }
        }

        return cleanMarkdownText(descCell.replace(/<!--.*?-->/g, '').trim());
    }

    function parseTableRow(rawLine) {
        const trimmed = rawLine.trim();
        if (
            !trimmed.startsWith('|') ||
            trimmed === '| --- | --- | ---: | --- |' ||
            trimmed === '| --- | ---: | --- |' ||
            trimmed === '| 名称 | 链接 | 订阅数 | 简介 |' ||
            trimmed === '| 资源 | 人数 | 简介 |'
        ) {
            return null;
        }

        const parts = trimmed
            .split('|')
            .slice(1, -1)
            .map(part => part.trim());

        if (parts.length < 3) {
            return null;
        }

        let title;
        let url;
        let countStr;
        let desc;

        if (parts.length >= 4) {
            const [titleCell, linkCell, countCell, descCell] = parts;
            const urlMatch = linkCell.match(/\[(.*?)\]\((.*?)\)/);
            if (!urlMatch) {
                return null;
            }
            title = cleanMarkdownText(titleCell);
            url = urlMatch[2];
            countStr = countCell;
            desc = descCell;
        } else {
            const [resourceCell, countCell, descCell] = parts;
            const resourceMatch = resourceCell.match(/\[(.*?)\]\((.*?)\)/);
            if (!resourceMatch) {
                return null;
            }
            title = cleanMarkdownText(resourceMatch[1]);
            url = resourceMatch[2];
            countStr = countCell;
            desc = descCell;
        }

        let id = title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '').toLowerCase();

        if (url.includes('t.me/')) {
            const urlPart = url.split('t.me/')[1];
            if (urlPart) {
                const rawId = urlPart
                    .replace('joinchat/', '')
                    .split('?')[0]
                    .replace(/[^a-zA-Z0-9_\-]/g, '')
                    .toLowerCase();
                if (rawId) id = rawId;
            }
        }

        const parsedDesc = extractDesc(desc);

        return {
            title,
            url,
            countStr,
            desc: parsedDesc === '-' ? '' : parsedDesc,
            id
        };
    }

    const seoKeywords = {
        "新闻快讯": "吃瓜播报 一手资讯 热点追踪 国际新闻",
        "加密货币": "区块链资讯 Web3 新闻 市场动态",
        "影视剧集": "影视资讯 剧集推荐 观影讨论"
    };

    for (const rawLine of lines) {
        if (!rawLine.trim()) {
            if (currentItem && currentType && currentCategory) {
                typeMap[currentType][currentCategory].push(currentItem);
                currentItem = null;
            }
            continue;
        }

        if (rawLine.startsWith('## ') && !rawLine.startsWith('### ') && ['## 频道', '## 群组', '## 机器人'].includes(rawLine.trim())) {
            currentType = rawLine.substring(3).trim();
            if (!typeMap[currentType]) typeMap[currentType] = {};
            currentCategory = null;
            currentItem = null;
        } else if (rawLine.startsWith('### ')) {
            const fullCat = rawLine.substring(4).trim();
            currentCategory = fullCat;
            if (currentType && !typeMap[currentType][currentCategory]) {
                typeMap[currentType][currentCategory] = [];
            }
            if (!categorySet.has(fullCat)) {
                categorySet.add(fullCat);
                // Extract icon and name (e.g. "📰 新闻快讯" -> icon: "📰", name: "新闻快讯")
                // Use a simpler regex that splits by the first whitespace to safely handle compound ZWJ emojis
                const match = fullCat.match(/^(\S+)\s+(.*)$/);
                if (match) {
                    const catName = match[2].trim();
                    categoriesList.push({
                        icon: match[1],
                        name: catName,
                        fullName: fullCat,
                        keywords: seoKeywords[catName] || "",
                        id: catName.toLowerCase()
                    });
                } else {
                    categoriesList.push({ icon: '📌', name: fullCat, fullName: fullCat, keywords: seoKeywords[fullCat.trim()] || "", id: fullCat.trim() });
                }
            }
            currentItem = null;
        } else if (rawLine.startsWith('| ') && currentType && currentCategory) {
            const tableItem = parseTableRow(rawLine);
            if (tableItem) {
                typeMap[currentType][currentCategory].push(tableItem);
            }
        } else if (rawLine.startsWith('- ')) {
            if (currentItem && currentType && currentCategory) {
                typeMap[currentType][currentCategory].push(currentItem);
            }
            const title = rawLine.substring(2).trim();
            currentItem = { title, desc: '' };
            currentItem.id = title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '').toLowerCase(); // Fallback ID
            currentItemProps = [];
        } else if (rawLine.startsWith('  - ') && currentItem) {
            currentItemProps.push(rawLine.substring(4).trim());
            if (currentItemProps.length === 1) {
                currentItem.typeLabel = currentItemProps[0];
            } else if (currentItemProps.length === 2) {
                const urlMatch = currentItemProps[1].match(/\[.*?\]\((.*?)\)/);
                currentItem.url = urlMatch ? urlMatch[1] : '';
                if (currentItem.url.includes('t.me/')) {
                    const parts = currentItem.url.split('t.me/');
                    if (parts.length > 1) {
                        let rawId = parts[1].replace('joinchat/', '').split('?')[0].replace(/[^a-zA-Z0-9_\-]/g, '').toLowerCase();
                        if (rawId) currentItem.id = rawId;
                    }
                }
            } else if (currentItemProps.length === 3) {
                currentItem.countStr = currentItemProps[2];
            } else if (currentItemProps.length === 4) {
                currentItem.desc = currentItemProps[3];
            }
        }
    }
    if (currentItem && currentType && currentCategory) {
        typeMap[currentType][currentCategory].push(currentItem);
    }

    data.categories = categoriesList;

    // Sort categories list based on existing sequence, or just leave as is (it matches README)
    // Flatten types map
    data.types = Object.keys(typeMap).map(type => {
        return {
            name: type,
            categories: Object.keys(typeMap[type]).map(catFullName => {
                return {
                    fullName: catFullName,
                    items: typeMap[type][catFullName]
                };
            }).filter(c => c.items.length > 0)
        };
    }).filter(t => t.categories.length > 0);

    if (!fs.existsSync(OUT_DIR)) {
        fs.mkdirSync(OUT_DIR, { recursive: true });
    }
    fs.writeFileSync(OUT_FILE, JSON.stringify(data, null, 2));
    console.log(`✅ Generated data.json with ${data.categories.length} categories.`);

    // Generate Sitemap
    let sitemapUrls = `  <url>
    <loc>https://www.rectg.com/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>`;

    // Add detail pages to sitemap
    data.types.forEach(t => {
        t.categories.forEach(c => {
            c.items.forEach(item => {
                if (item.id) {
                    sitemapUrls += `\n  <url>
    <loc>https://www.rectg.com/p/${item.id}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`;
                }
            });
        });
    });

    const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapUrls}
</urlset>`;
    const sitemapPath = path.resolve(OUT_DIR, 'sitemap.xml');
    fs.writeFileSync(sitemapPath, sitemapContent, 'utf-8');
    console.log(`✅ Generated sitemap.xml at ${sitemapPath}`);

    // Generate Robots.txt
    const robotsContent = `User-agent: *
Allow: /

Sitemap: https://www.rectg.com/sitemap.xml`;
    const robotsPath = path.resolve(OUT_DIR, 'robots.txt');
    fs.writeFileSync(robotsPath, robotsContent, 'utf-8');
    console.log(`✅ Generated robots.txt at ${robotsPath}`);
}

main();
