"use strict";

const fs = require("fs");
const path = require("path");
const { marked } = require("marked");

const mdPath = path.join(__dirname, "..", "README.md");
const outDir = path.join(__dirname, "..", "public");
const outPath = path.join(outDir, "index.html");

const md = fs.readFileSync(mdPath, "utf8");

marked.setOptions({
  mangle: false,
  headerIds: true,
  gfm: true,
});

const body = marked.parse(md);

const html = `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>rectg - Telegram 导航</title>
  <style>
    :root {
      --bg: #f7f7fb;
      --card: #ffffff;
      --text: #1f2933;
      --muted: #52606d;
      --link: #2563eb;
      --border: #e5e7eb;
      --table-stripe: #f1f5f9;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 16px/1.6 "Helvetica Neue","PingFang SC","Microsoft YaHei",Arial,sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    main {
      max-width: 960px;
      margin: 32px auto 64px;
      padding: 0 20px 40px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 12px 30px rgba(15,23,42,0.05);
    }
    h1, h2, h3, h4 {
      font-weight: 700;
      line-height: 1.2;
      color: #0f172a;
      margin-top: 1.6em;
      margin-bottom: 0.6em;
    }
    h1 { font-size: 28px; margin-top: 0; }
    h2 { font-size: 22px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
    h3 { font-size: 18px; }
    p { margin: 0 0 1em; color: var(--muted); }
    ul, ol { padding-left: 20px; color: var(--muted); }
    a { color: var(--link); text-decoration: none; }
    a:hover { text-decoration: underline; }
    blockquote { margin: 0 0 1em; padding: 12px 16px; border-left: 4px solid var(--link); background: #eef2ff; color: #111827; border-radius: 6px; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 24px;
      font-size: 14px;
    }
    th, td {
      padding: 10px 12px;
      border: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
    }
    thead th {
      background: #f8fafc;
      font-weight: 700;
      color: #0f172a;
    }
    tbody tr:nth-child(odd) td { background: var(--table-stripe); }
    code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; font-size: 13px; }
    pre { background: #0f172a; color: #e2e8f0; padding: 12px; border-radius: 10px; overflow: auto; }
    hr { border: 0; border-top: 1px solid var(--border); margin: 32px 0; }
    @media (max-width: 720px) {
      main { margin: 16px auto 40px; padding: 0 14px 28px; }
      table, thead, tbody, th, td, tr { display: block; }
      thead { display: none; }
      tr { margin-bottom: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
      td { border: 0; border-bottom: 1px solid var(--border); }
      td:last-child { border-bottom: 0; }
      td::before { content: attr(data-label); display: block; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
    }
  </style>
</head>
<body>
  <main>
    ${body}
  </main>
</body>
</html>`;

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(outPath, html);
console.log(`Built to ${outPath}`);
