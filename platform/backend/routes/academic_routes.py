"""
学术验证路由处理
处理学术验证相关的API请求
"""


def handle_academic_routes(handler, path, context):
    """
    处理学术验证请求
    
    context包含:
    - ACADEMIC_VALIDATION_AVAILABLE: 学术验证模块是否可用
    - get_academic_validation: 获取学术验证函数
    - get_paper_links: 获取论文链接函数
    - generate_validation_html: 生成验证HTML函数
    - FRONTEND_DIR: 前端目录
    """
    
    ACADEMIC_VALIDATION_AVAILABLE = context.get('ACADEMIC_VALIDATION_AVAILABLE', False)
    get_academic_validation = context.get('get_academic_validation')
    get_paper_links = context.get('get_paper_links')
    generate_validation_html = context.get('generate_validation_html')
    FRONTEND_DIR = context.get('FRONTEND_DIR', '')
    
    if path == '/api/academic_validation':
        if ACADEMIC_VALIDATION_AVAILABLE and get_academic_validation:
            validation = get_academic_validation()
            handler._send_json(200, {"success": True, **validation})
        else:
            handler._send_json(200, {"success": True, "message": "学术验证模块未启用"})
        return True
    
    elif path == '/api/paper_links':
        if ACADEMIC_VALIDATION_AVAILABLE and get_paper_links:
            links = get_paper_links()
            handler._send_json(200, {"success": True, "papers": links})
        else:
            handler._send_json(200, {"success": True, "papers": []})
        return True
    
    elif path == '/academic_validation.html':
        if ACADEMIC_VALIDATION_AVAILABLE and generate_validation_html:
            html = generate_validation_html()
            handler.send_response(200)
            handler.send_header('Content-type', 'text/html; charset=utf-8')
            handler.end_headers()
            handler.wfile.write(html.encode('utf-8'))
        else:
            handler._send_json(404, {"success": False, "error": "页面不存在"})
        return True
    
    return False
