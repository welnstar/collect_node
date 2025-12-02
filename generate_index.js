// generate_index.js
const fs = require('fs');
const path = require('path');

const rootDir = '.'; // 仓库根目录
const outputFile = 'index.html';

function walk(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat && stat.isDirectory()) {
      results = results.concat(walk(fullPath));
    } else {
      // 只列出文本类文件（可按需调整扩展名）
      if (/\.(txt|md|json|csv|log|ini|xml|yaml|yml)$/i.test(file)) {
        // 转为相对路径（用于 href）
        results.push(fullPath.replace(/^\.\/?/, ''));
      }
    }
  });
  return results;
}

const files = walk(rootDir).sort();

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
  const encoded = encodeURI(file); // 处理中文或特殊字符
  html += `    <li><a href="${encoded}">${file}</a></li>\n`;
});

html += `  </ul>
  <p><small>更新时间: ${new Date().toLocaleString('zh-CN')}</small></p>
</body>
</html>`;

fs.writeFileSync(outputFile, html);
console.log(`✅ 已生成 ${outputFile}，共 ${files.length} 个文件`);
