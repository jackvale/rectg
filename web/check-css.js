import fs from 'fs';

const css = fs.readFileSync('src/styles/style.css', 'utf-8');
const failures = [];

if (/(^|\n)\s*main\s*\{/.test(css)) {
  failures.push('Use #app-scoped selectors instead of a global main selector.');
}

if (/(^|\n)\s*header\s*\{/.test(css)) {
  failures.push('Use #app-scoped selectors instead of a global header selector.');
}

[
  '.mobile-category-strip',
  '.result-status',
  '.copy-label',
  '#app > main > header',
].forEach((selector) => {
  if (!css.includes(selector)) {
    failures.push(`Missing expected selector: ${selector}`);
  }
});

if (failures.length) {
  console.error(failures.join('\n'));
  process.exit(1);
}

console.log('✅ css ok');
