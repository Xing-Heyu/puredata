"""
路由模块包
将simple_main.py中的路由处理逻辑拆分到独立模块
"""

from .generate_routes import handle_generate_routes
from .cache_routes import handle_cache_request
from .static_routes import handle_static_routes
from .download_routes import handle_download_routes
from .batch_routes import handle_batch_routes
from .academic_routes import handle_academic_routes

__all__ = [
    'handle_generate_routes',
    'handle_cache_request',
    'handle_static_routes',
    'handle_download_routes',
    'handle_batch_routes',
    'handle_academic_routes',
    'handle_all_routes',
    'handle_all_get_routes',
    'handle_all_post_routes'
]

def handle_all_get_routes(handler, path, context):
    """
    处理所有GET请求
    """
    handlers = [
        lambda h, p, m, b, c: handle_static_routes(h, p, c),
        handle_generate_routes,
        handle_cache_request,
        lambda h, p, m, b, c: handle_download_routes(h, p, c),
        lambda h, p, m, b, c: handle_academic_routes(h, p, c),
    ]
    
    for handle_func in handlers:
        result = handle_func(handler, path, 'GET', {}, context)
        if result:
            return True
    
    return False

def handle_all_post_routes(handler, path, body, context):
    """
    处理所有POST请求
    """
    print(f"[DEBUG] handle_all_post_routes: path={path}, body={body}")
    
    handlers = [
        ('generate', handle_generate_routes),
        ('cache', handle_cache_request),
        ('batch', lambda h, p, m, b, c: handle_batch_routes(h, p, c)),
    ]
    
    for name, handle_func in handlers:
        try:
            result = handle_func(handler, path, 'POST', body, context)
            if result:
                print(f"[DEBUG] 由 {name} 处理")
                return True
        except Exception as e:
            print(f"[ERROR] {name} 处理异常: {e}")
            import traceback
            traceback.print_exc()
            handler._send_json(500, {"success": False, "error": "服务器内部错误"})
            return True
    
    print(f"[DEBUG] 没有处理器匹配")
    return False

def handle_all_routes(handler, path, method, body, context):
    """
    统一路由处理入口
    按顺序尝试各个路由模块，直到找到匹配的处理
    """
    if method == 'GET':
        return handle_all_get_routes(handler, path, context)
    elif method == 'POST':
        return handle_all_post_routes(handler, path, body, context)
    return False
