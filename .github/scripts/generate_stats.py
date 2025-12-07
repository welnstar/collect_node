#!/usr/bin/env python3
"""
GitHub 项目根目录 *_latest.txt 和 *_latest.yaml 文件统计脚本
生成 HTML 报告
"""

import os
import re
import yaml
import json
from datetime import datetime
from pathlib import Path
import hashlib

def find_latest_files(root_dir):
    """查找根目录下的所有 *_latest.txt 和 *_latest.yaml 文件"""
    root_path = Path(root_dir)
    
    # 只查找根目录下的文件，不递归子目录
    txt_files = [f for f in root_path.glob('*_latest.txt') if f.is_file()]
    yaml_files = [f for f in root_path.glob('*_latest.yaml') if f.is_file()]
    yml_files = [f for f in root_path.glob('*_latest.yml') if f.is_file()]
    
    all_files = txt_files + yaml_files + yml_files
    return sorted(all_files, key=lambda x: str(x).lower())

def read_txt_file(file_path):
    """读取 TXT 文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        return {
            'content': content,
            'line_count': len(lines),
            'size': os.path.getsize(file_path),
            'lines': lines
        }
    except Exception as e:
        return {
            'content': '',
            'line_count': 0,
            'size': 0,
            'lines': [],
            'error': str(e)
        }

def read_yaml_file(file_path):
    """读取 YAML 文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            data = yaml.safe_load(content)
        return {
            'content': content,
            'data': data,
            'size': os.path.getsize(file_path),
            'keys_count': len(data.keys()) if isinstance(data, dict) else 0,
            'type': type(data).__name__
        }
    except Exception as e:
        return {
            'content': '',
            'data': None,
            'size': 0,
            'keys_count': 0,
            'type': 'error',
            'error': str(e)
        }

def get_file_info(file_path):
    """获取文件基本信息"""
    stat = file_path.stat()
    return {
        'name': file_path.name,
        'path': str(file_path),
        'relative_path': str(file_path.relative_to(Path('.'))),
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'extension': file_path.suffix.lower()
    }

def analyze_files(file_paths):
    """分析所有文件"""
    results = {
        'txt_files': [],
        'yaml_files': [],
        'total_files': 0,
        'total_size': 0,
        'stats': {
            'txt_count': 0,
            'yaml_count': 0,
            'total_count': 0
        }
    }
    
    for file_path in file_paths:
        file_info = get_file_info(file_path)
        
        if file_path.suffix.lower() in ['.txt']:
            content_info = read_txt_file(file_path)
            file_info.update(content_info)
            results['txt_files'].append(file_info)
            results['stats']['txt_count'] += 1
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            content_info = read_yaml_file(file_path)
            file_info.update(content_info)
            results['yaml_files'].append(file_info)
            results['stats']['yaml_count'] += 1
        
        results['total_size'] += file_info['size']
        results['stats']['total_count'] += 1
    
    return results

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def get_run_info():
    """获取运行信息 - 完全不使用 Git"""
    return {
        'branch': os.environ.get('GITHUB_REF_NAME', 'main'),
        'commit_hash': os.environ.get('GITHUB_SHA', 'unknown')[:8],
        'workflow_name': os.environ.get('GITHUB_WORKFLOW', 'unknown'),
        'run_number': os.environ.get('GITHUB_RUN_NUMBER', 'unknown'),
        'actor': os.environ.get('GITHUB_ACTOR', 'unknown')
    }

def generate_html_report(stats_data):
    """生成 HTML 报告到根目录"""
    run_info = get_run_info()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Root Directory Latest Files Statistics - {Path('.').resolve().name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .run-info {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 0.9em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .file-section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #007bff;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .file-path {{
            font-family: monospace;
            font-size: 0.9em;
            color: #6c757d;
        }}
        .content-preview {{
            max-height: 100px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.8em;
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .error {{
            color: #dc3545;
            font-weight: bold;
        }}
        .success {{
            color: #28a745;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 0.8em;
        }}
        .search-box {{
            margin-bottom: 20px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
            box-sizing: border-box;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #6c757d;
            font-size: 0.8em;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Root Directory Latest Files Statistics</h1>
        <p>Repository: {Path('.').resolve().name}</p>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="run-info">
            <strong>Run Info:</strong> Branch: {run_info['branch']} | 
            Workflow: {run_info['workflow_name']} | 
            Run: #{run_info['run_number']} | 
            Actor: {run_info['actor']}
        </div>
        <div class="warning">
            <strong>注意:</strong> 此统计仅包含根目录下的 *_latest.txt 和 *_latest.yaml 文件
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{stats_data['stats']['total_count']}</div>
            <div class="stat-label">Total Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats_data['stats']['txt_count']}</div>
            <div class="stat-label">TXT Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats_data['stats']['yaml_count']}</div>
            <div class="stat-label">YAML Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{format_size(stats_data['total_size'])}</div>
            <div class="stat-label">Total Size</div>
        </div>
    </div>

    <div class="file-section">
        <h2 class="section-title">TXT Files in Root Directory ({stats_data['stats']['txt_count']} files)</h2>
        <input type="text" class="search-box" placeholder="Search TXT files..." onkeyup="searchTable('txt-table')">
        <table id="txt-table">
            <thead>
                <tr>
                    <th>File Name</th>
                    <th>Path</th>
                    <th>Size</th>
                    <th>Lines</th>
                    <th>Modified</th>
                    <th>Preview</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for file_info in stats_data['txt_files']:
        preview = file_info.get('content', '')[:200] + '...' if len(file_info.get('content', '')) > 200 else file_info.get('content', '')
        preview = preview.replace('<', '&lt;').replace('>', '&gt;')
        
        error_class = 'error' if 'error' in file_info else 'success'
        error_text = f" (Error: {file_info.get('error', '')})" if 'error' in file_info else ''
        
        html_content += f"""
                <tr>
                    <td>{file_info['name']}<br><span class="{error_class}">{error_text}</span></td>
                    <td><span class="file-path">{file_info['relative_path']}</span></td>
                    <td>{format_size(file_info['size'])}</td>
                    <td>{file_info.get('line_count', 0)}</td>
                    <td>{file_info['modified'][:19]}</td>
                    <td><div class="content-preview">{preview}</div></td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </div>

    <div class="file-section">
        <h2 class="section-title">YAML Files in Root Directory ({stats_data['stats']['yaml_count']} files)</h2>
        <input type="text" class="search-box" placeholder="Search YAML files..." onkeyup="searchTable('yaml-table')">
        <table id="yaml-table">
            <thead>
                <tr>
                    <th>File Name</th>
                    <th>Path</th>
                    <th>Size</th>
                    <th>Type</th>
                    <th>Keys Count</th>
                    <th>Modified</th>
                    <th>Preview</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for file_info in stats_data['yaml_files']:
        preview = json.dumps(file_info.get('data', {}), ensure_ascii=False, indent=2)[:500] + '...' if len(json.dumps(file_info.get('data', {}), ensure_ascii=False, indent=2)) > 500 else json.dumps(file_info.get('data', {}), ensure_ascii=False, indent=2)
        preview = preview.replace('<', '&lt;').replace('>', '&gt;')
        
        error_class = 'error' if 'error' in file_info else 'success'
        error_text = f" (Error: {file_info.get('error', '')})" if 'error' in file_info else ''
        
        html_content += f"""
                <tr>
                    <td>{file_info['name']}<br><span class="{error_class}">{error_text}</span></td>
                    <td><span class="file-path">{file_info['relative_path']}</span></td>
                    <td>{format_size(file_info['size'])}</td>
                    <td>{file_info.get('type', 'unknown')}</td>
                    <td>{file_info.get('keys_count', 0)}</td>
                    <td>{file_info['modified'][:19]}</td>
                    <td><div class="content-preview">{preview}</div></td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>Generated by GitHub Actions | Branch: {run_info['branch']} | Workflow: {run_info['workflow_name']}</p>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Scope:</strong> Root directory only (files matching *_latest.txt and *_latest.yaml patterns)</p>
    </div>

    <script>
        function searchTable(tableId) {
            const input = event.target;
            const filter = input.value.toUpperCase();
            const table = document.getElementById(tableId);
            const tr = table.getElementsByTagName("tr");
            
            for (let i = 1; i < tr.length; i++) {
                let td = tr[i].getElementsByTagName("td");
                let found = false;
                
                for (let j = 0; j < td.length; j++) {
                    if (td[j]) {
                        if (td[j].textContent.toUpperCase().indexOf(filter) > -1) {
                            found = true;
                            break;
                        }
                    }
                }
                
                tr[i].style.display = found ? "" : "none";
            }
        }
        
        // Add click to expand preview functionality
        document.addEventListener('DOMContentLoaded', function() {
            const previews = document.querySelectorAll('.content-preview');
            previews.forEach(preview => {
                preview.style.cursor = 'pointer';
                preview.addEventListener('click', function() {
                    if (this.style.maxHeight === 'none') {
                        this.style.maxHeight = '100px';
                    } else {
                        this.style.maxHeight = 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>
    """
    
    # 写入根目录的 index.html 文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 生成 JSON 数据文件（便于后续处理）
    with open('stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2, default=str)

def main():
    """主函数"""
    branch_name = os.environ.get('GITHUB_REF_NAME', 'main')
    print(f"当前分支: {branch_name}")
    
    if branch_name != 'main':
        print("非 main 分支，跳过执行")
        return
    
    print("开始分析根目录下的 *_latest.txt 和 *_latest.yaml 文件...")
    
    # 查找文件
    files = find_latest_files('.')
    print(f"找到 {len(files)} 个根目录文件")
    
    if not files:
        print("根目录下未找到任何 *_latest.txt 或 *_latest.yaml 文件")
        return
    
    # 分析文件
    stats_data = analyze_files(files)
    print(f"分析完成: {stats_data['stats']}")
    
    # 生成 HTML 报告到根目录
    generate_html_report(stats_data)
    print(f"HTML 报告已生成到根目录 index.html")
    
    # 打印摘要
    print("\n=== 统计摘要 ===")
    print(f"总文件数: {stats_data['stats']['total_count']}")
    print(f"TXT 文件: {stats_data['stats']['txt_count']}")
    print(f"YAML 文件: {stats_data['stats']['yaml_count']}")
    print(f"总大小: {format_size(stats_data['total_size'])}")
    print(f"生成分支: {branch_name}")
    
    # 列出找到的文件
    print("\n=== 找到的文件 ===")
    for file_path in files:
        print(f"- {file_path}")

if __name__ == "__main__":
    main()
