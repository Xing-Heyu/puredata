"""
缓存相关路由处理
"""

def handle_cache_request(handler, path, method, body, context):
    """处理缓存相关请求"""
    import json
    
    get_data_cache = context.get('get_data_cache')
    
    if path == '/api/cache/stats':
        cache = get_data_cache()
        if cache:
            stats = cache.get_stats()
            handler._send_json(200, {"success": True, "stats": stats})
        else:
            handler._send_json(200, {"success": True, "stats": {}})
        return True
    
    elif path == '/api/cache/clear':
        cache = get_data_cache()
        count = cache.clear_all() if cache else 0
        handler._send_json(200, {"success": True, "cleared": count})
        return True
    
    elif path == '/api/core_cache/stats':
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
