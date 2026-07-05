"""
下载路由处理
处理文件下载请求，包含权限验证
"""

import os
from urllib.parse import unquote


def handle_download_routes(handler, path, context):
    """
    处理文件下载请求（无需认证）
    
    context包含:
    - tasks: 任务字典
    - OUTPUT_DIR: 输出目录
    """
    
    if not path.startswith('/download/'):
        return False
    
    tasks = context.get('tasks', {})
    OUTPUT_DIR = context.get('OUTPUT_DIR', '')
    
    filename = path.split('/')[-1]
    
    safe_filename = os.path.basename(filename)
    if '..' in safe_filename or safe_filename.startswith('/') or safe_filename.startswith('\\'):
        handler._send_json(403, {"success": False, "error": "非法文件名"})
        return True
    
    filepath = os.path.join(OUTPUT_DIR, safe_filename)
    
    if os.path.exists(filepath):
        handler._serve_file(filepath, 'application/octet-stream', safe_filename)
    else:
        handler._send_json(404, {"success": False, "error": "文件不存在", "path": filepath})
    
    return True
