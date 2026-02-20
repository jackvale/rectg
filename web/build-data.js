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

    for (const rawLine of lines) {
        if (!rawLine.trim()) {
            if (currentItem && currentType && currentCategory) {
                typeMap[currentType][currentCategory].push(currentItem);
                currentItem = null;
            }
            continue;
        }

        if (rawLine.startsWith('## ') && !rawLine.startsWith('### ') && rawLine.trim() !== '## Star History') {
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
                    categoriesList.push({
                        icon: match[1],
                        name: match[2],
                        fullName: fullCat,
                        id: match[2].toLowerCase()
                    });
                } else {
                    categoriesList.push({ icon: '📌', name: fullCat, fullName: fullCat, id: fullCat });
                }
            }
            currentItem = null;
        } else if (rawLine.startsWith('- ')) {
            if (currentItem && currentType && currentCategory) {
                typeMap[currentType][currentCategory].push(currentItem);
            }
            const title = rawLine.substring(2).trim();
            currentItem = { title, desc: '' };
            currentItemProps = [];
        } else if (rawLine.startsWith('  - ') && currentItem) {
            currentItemProps.push(rawLine.substring(4).trim());
            if (currentItemProps.length === 1) {
                currentItem.typeLabel = currentItemProps[0];
            } else if (currentItemProps.length === 2) {
                const urlMatch = currentItemProps[1].match(/\[.*?\]\((.*?)\)/);
                currentItem.url = urlMatch ? urlMatch[1] : '';
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
    const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.rectg.com/</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>`;
    const sitemapPath = path.resolve(OUT_DIR, 'sitemap.xml');
    fs.writeFileSync(sitemapPath, sitemapContent, 'utf-8');
    console.log(`✅ Generated sitemap.xml at ${sitemapPath}`);
}

main();
