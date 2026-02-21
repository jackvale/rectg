import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
import { JSDOM } from 'jsdom';

try {
  const html = readFileSync('dist/index.html', 'utf-8');
  console.log('HTML loaded, length:', html.length);
} catch(e) { console.error(e) }
