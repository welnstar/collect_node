// generate_index.js
const fs = require('fs');
const path = require('path');

function walk(dir, fileList = []) {
  const items = fs.readdirSync(dir);
  for (const item of items) {
    // 跳过隐藏文件/目录（如 .git, .github, .gitignore 等）
    if (item.startsWith('.')) {
      continue;
    }

    const fullPath = path.join(dir, item);
    const relPath = path.relative('.', fullPath).replace(/\\/g, '/'); // 统一用正斜杠
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      walk(fullPath, fileList);
    } else if (/\.(txt|md|json|csv|log|ini|xml|yaml|yml)$/i.test(item)) {
      fileList.push(relPath);
    }
  }
  return fileList;
}

const files = walk('.').sort(); // 稳定排序

let html = `<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>文件下载列表</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 2rem; max-width: 800px; margin: 0 auto; }
    h1 { color: #333; }
    ul { list-style: none; padding: 0; }
    li { margin: 0.6rem 0; }
    a { color: #0066cc; text-decoration: none; font-size: 1.1em; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>📁 文件下载列表</h1>
  <ul>
`;

files.forEach(file => {
  const encoded = encodeURI(file);
  html += `    <li><a href="${encoded}">${file}</a></li>\n`;
});

html += `  </ul>
  <p><small>文件列表由自动化脚本生成</small></p>
</body>
</html>`;

// 仅当内容变化时才写入文件，避免无意义提交
let shouldWrite = true;
const outputPath = 'index.html';
if (fs.existsSync(outputPath)) {
  const existing = fs.readFileSync(outputPath, 'utf8');
  if (existing === html) {
    console.log('⏩ index.html 无变化，跳过写入');
    shouldWrite = false;
  }
}

if (shouldWrite) {
  fs.writeFileSync(outputPath, html, 'utf8');
  console.log(`✅ 已更新 index.html，共 ${files.length} 个文件`);
} else {
  console.log(`ℹ️ 当前文件数：${files.length}`);
}
