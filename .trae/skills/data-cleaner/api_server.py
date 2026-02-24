#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据生成API服务
带完整安全防护
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from security import (
    init_security_db, validate_api_key, rate_limiter, 
    anti_crawler, log_access, SECURITY_CONFIG
)
from generate import generate_data, DOMAINS

# 初始化
init_security_db()

class APIHandler(BaseHTTPRequestHandler):
    """API请求处理器"""
    
    def _send_response(self, status, data):
        """发送响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-RateLimit-Limit', str(SECURITY_CONFIG["rate_limit"]["requests_per_minute"]))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _get_client_ip(self):
        """获取客户端IP"""
        return self.client_address[0]
    
    def _parse_request(self):
        """解析请求"""
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        return parsed.path, {k: v[0] if len(v) == 1 else v for k, v in params.items()}
    
    def do_GET(self):
        """处理GET请求"""
        path, params = self._parse_request()
        client_ip = self._get_client_ip()
        user_agent = self.headers.get('User-Agent', '')
        
        # 反爬虫检查
        allowed, msg = anti_crawler.check_request(client_ip, user_agent)
        if not allowed:
            self._send_response(403, {"error": msg})
            return
        
        # 路由
        if path == '/api/generate':
            self._handle_generate(params, client_ip)
        elif path == '/api/types':
            self._handle_types()
        elif path == '/api/stats':
            self._handle_stats(params)
        elif path == '/health':
            self._send_response(200, {"status": "ok"})
        else:
            self._send_response(404, {"error": "未找到接口"})
    
    def _handle_generate(self, params, client_ip):
        """处理生成请求"""
        # 认证
        api_key = params.get('api_key')
        if not api_key:
            self._send_response(401, {"error": "缺少API Key"})
            return
        
        user = validate_api_key(api_key)
        if not user:
            self._send_response(401, {"error": "无效的API Key"})
            return
        
        # 限流
        key = f"{user['user_id']}:minute"
        if not rate_limiter.is_allowed(key, SECURITY_CONFIG["rate_limit"]["requests_per_minute"], 60):
            self._send_response(429, {"error": "请求过于频繁"})
            return
        
        # 参数验证
        domain = params.get('type', '人工智能')
        count = int(params.get('count', 100))
        format_type = params.get('format', 'json')
        
        if domain not in DOMAINS:
            self._send_response(400, {"error": f"未知领域: {domain}"})
            return
        
        if count > 10000:
            self._send_response(400, {"error": "单次最多生成10000条"})
            return
        
        # 根据套餐限制
        plan_limits = {'basic': 100, 'pro': 1000, 'enterprise': 10000}
        max_count = plan_limits.get(user['plan'], 100)
        if count > max_count:
            self._send_response(403, {"error": f"当前套餐最多生成{max_count}条，请升级套餐"})
            return
        
        # 生成数据
        data = generate_data(domain, count, format_type)
        
        # 记录日志
        log_access(user['user_id'], client_ip, '/api/generate')
        
        if data:
            self._send_response(200, {
                "status": "success",
                "count": len(data),
                "data": data[:10],  # 只返回前10条预览
                "download_url": f"/api/download?task_id={user['user_id']}_{int(__import__('time').time())}"
            })
        else:
            self._send_response(500, {"error": "生成失败"})
    
    def _handle_types(self):
        """获取可用领域"""
        types = [{"name": k, "keywords": len(v['keywords'])} for k, v in DOMAINS.items()]
        self._send_response(200, {"types": types})
    
    def _handle_stats(self, params):
        """获取统计"""
        api_key = params.get('api_key')
        if not api_key:
            self._send_response(401, {"error": "缺少API Key"})
            return
        
        user = validate_api_key(api_key)
        if not user:
            self._send_response(401, {"error": "无效的API Key"})
            return
        
        self._send_response(200, {
            "user_id": user['user_id'],
            "plan": user['plan'],
            "rate_limit": {
                "remaining": rate_limiter.get_remaining(f"{user['user_id']}:minute", 60, 60)
            }
        })
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[{self.log_date_time_string()}] {self._get_client_ip()} - {format % args}")


def run_server(port=8080):
    """启动服务器"""
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"\n{'='*50}")
    print(f"数据生成API服务")
    print(f"端口: {port}")
    print(f"{'='*50}")
    print(f"\n接口文档:")
    print(f"  GET /api/types           - 获取可用领域")
    print(f"  GET /api/generate        - 生成数据")
    print(f"    参数: api_key, type, count, format")
    print(f"  GET /api/stats           - 获取统计")
    print(f"  GET /health              - 健康检查")
    print(f"\n示例:")
    print(f"  curl 'http://localhost:{port}/api/generate?api_key=YOUR_KEY&type=人工智能&count=100'")
    print(f"\n{'='*50}\n")
    
    server.serve_forever()


if __name__ == '__main__':
    run_server()