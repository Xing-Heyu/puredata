"""
静态文件路由处理
"""

import os
from urllib.parse import unquote

def handle_static_routes(handler, path, context):
    """
    处理静态文件请求
    
    context包含:
    - FRONTEND_DIR: 前端目录
    """
    
    FRONTEND_DIR = context.get('FRONTEND_DIR', '')
    
    if path == '/' or path == '/index.html':
        handler._serve_file(os.path.join(FRONTEND_DIR, 'index.html'), 'text/html')
        return True
    
    elif path == '/admin' or path == '/admin.html':
        handler._serve_file(os.path.join(FRONTEND_DIR, 'admin.html'), 'text/html')
        return True
    
    elif path.startswith('/static/'):
        static_path = os.path.join(FRONTEND_DIR, path.lstrip('/'))
        if os.path.exists(static_path):
            if path.endswith('.png'):
                handler._serve_file(static_path, 'image/png')
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                handler._serve_file(static_path, 'image/jpeg')
            elif path.endswith('.gif'):
                handler._serve_file(static_path, 'image/gif')
            elif path.endswith('.svg'):
                handler._serve_file(static_path, 'image/svg+xml')
            elif path.endswith('.css'):
                handler._serve_file(static_path, 'text/css')
            elif path.endswith('.js'):
                handler._serve_file(static_path, 'application/javascript')
            else:
                handler._serve_file(static_path, 'application/octet-stream')
        else:
            handler._send_json(404, {"error": "文件不存在"})
        return True
    
    elif path == '/health':
        handler._send_json(200, {"status": "ok"})
        return True
    
    elif path == '/docs' or path == '/api/docs':
        handler._serve_swagger_ui()
        return True
    
    elif path == '/openapi.json':
        BACKEND_DIR = context.get('BACKEND_DIR', '')
        openapi_path = os.path.join(BACKEND_DIR, 'openapi.json')
        if os.path.exists(openapi_path):
            handler._serve_file(openapi_path, 'application/json')
        else:
            handler._send_json(404, {"error": "OpenAPI spec not found"})
        return True
    
    return None
