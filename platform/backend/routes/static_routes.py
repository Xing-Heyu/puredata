"""
静态文件路由处理
"""

import os
import time

START_TIME = time.time()
VERSION = "2.2.0"

def handle_static_routes(handler, path, context):
    """
    处理静态文件请求
    
    context包含:
    - FRONTEND_DIR: 前端目录
    - BACKEND_DIR: 后端目录
    """
    
    FRONTEND_DIR = context.get('FRONTEND_DIR', '')
    BACKEND_DIR = context.get('BACKEND_DIR', '')
    
    def _safe_path_join(base_dir, user_path):
        """安全地连接路径，防止路径遍历攻击"""
        base_dir = os.path.normpath(base_dir)
        full_path = os.path.normpath(os.path.join(base_dir, user_path))
        if not full_path.startswith(base_dir + os.sep) and full_path != base_dir:
            return None
        return full_path
    
    if path == '/' or path == '/index.html':
        handler._serve_file(os.path.join(FRONTEND_DIR, 'index.html'), 'text/html')
        return True
    
    elif path == '/quality_showcase.html':
        handler._serve_file(os.path.join(FRONTEND_DIR, 'quality_showcase.html'), 'text/html')
        return True
    
    elif path.startswith('/static/'):
        static_path = _safe_path_join(FRONTEND_DIR, path.lstrip('/'))
        if static_path and os.path.exists(static_path):
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
            handler._send_json(404, {"success": False, "error": "文件不存在"})
        return True
    
    elif path.startswith('/css/'):
        css_path = _safe_path_join(FRONTEND_DIR, path.lstrip('/'))
        if css_path and os.path.exists(css_path):
            handler._serve_file(css_path, 'text/css')
        else:
            handler._send_json(404, {"success": False, "error": "CSS文件不存在"})
        return True
    
    elif path.startswith('/js/'):
        js_path = _safe_path_join(FRONTEND_DIR, path.lstrip('/'))
        if js_path and os.path.exists(js_path):
            handler._serve_file(js_path, 'application/javascript')
        else:
            handler._send_json(404, {"success": False, "error": "JS文件不存在"})
        return True
    
    elif path.startswith('/docs/'):
        docs_base = os.path.normpath(os.path.join(FRONTEND_DIR, '..', 'docs'))
        docs_path = _safe_path_join(docs_base, path[6:])
        if docs_path and os.path.exists(docs_path):
            if path.endswith('.md'):
                handler._serve_file(docs_path, 'text/markdown')
            elif path.endswith('.html'):
                handler._serve_file(docs_path, 'text/html')
            else:
                handler._serve_file(docs_path, 'text/plain')
        else:
            handler._send_json(404, {"success": False, "error": "文档不存在"})
        return True
    
    elif path == '/health':
        uptime = int(time.time() - START_TIME)
        handler._send_json(200, {
            "status": "ok",
            "version": VERSION,
            "uptime": uptime
        })
        return True
    
    elif path == '/docs' or path == '/api/docs':
        handler._serve_swagger_ui()
        return True
    
    elif path == '/openapi.json':
        openapi_path = os.path.join(BACKEND_DIR, 'openapi.json')
        if os.path.exists(openapi_path):
            handler._serve_file(openapi_path, 'application/json')
        else:
            handler._send_json(404, {"success": False, "error": "OpenAPI spec not found"})
        return True
    
    return None
