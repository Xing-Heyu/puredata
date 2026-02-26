"""
缓存相关路由处理
"""

def handle_cache_request(handler, path, method, body, context):
    """处理缓存相关请求"""
    import json
    
    admin_auth = context.get('admin_auth')
    get_data_cache = context.get('get_data_cache')
    
    def _is_admin(token):
        return admin_auth.validate_token(token) is not None if admin_auth else False
    
    if path == '/api/cache/stats':
        cache = get_data_cache()
        if cache:
            stats = cache.get_stats()
            handler._send_json(200, {"success": True, "stats": stats})
        else:
            handler._send_json(200, {"success": True, "stats": {}})
        return True
    
    elif path == '/api/cache/clear':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"success": False, "error": "权限不足"})
            return True
        cache = get_data_cache()
        count = cache.clear_all() if cache else 0
        handler._send_json(200, {"success": True, "cleared": count})
        return True
    
    elif path == '/api/core_cache/stats':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"success": False, "error": "权限不足"})
            return True
        try:
            from core.cache_impl import cache_manager, template_cache, domain_cache, keyword_cache, api_cache
            stats = {
                "template_cache": template_cache.get_stats(),
                "domain_cache": domain_cache.get_stats(),
                "keyword_cache": keyword_cache.get_stats(),
                "api_cache": api_cache.get_stats()
            }
            handler._send_json(200, {"success": True, "stats": stats})
        except Exception as e:
            handler._send_json(500, {"success": False, "error": str(e)})
        return True
    
    elif path == '/api/core_cache/invalidate':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"success": False, "error": "权限不足"})
            return True
        try:
            domain = body.get('domain')
            cache_type = body.get('cache_type')
            from core.cache_impl import invalidate_cache
            invalidate_cache(domain, cache_type)
            handler._send_json(200, {"success": True, "message": f"已清理缓存: domain={domain}, type={cache_type}"})
        except Exception as e:
            handler._send_json(500, {"success": False, "error": str(e)})
        return True
    
    return None
