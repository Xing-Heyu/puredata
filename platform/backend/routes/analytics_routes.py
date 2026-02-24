"""
分析和统计路由处理
"""

import json
import os
from datetime import datetime

def handle_analytics_routes(handler, path, method, body, context):
    """
    处理分析和统计相关请求
    
    context包含:
    - user_manager: 用户管理器
    - tasks: 任务字典
    - stats: 统计数据
    - DOMAINS: 领域配置
    - TEMPLATES: 模板配置
    - QUALITY_MODES: 质量模式配置
    - get_monitor_service: 获取监控服务
    """
    
    user_manager = context.get('user_manager')
    tasks = context.get('tasks', {})
    stats = context.get('stats', {})
    DOMAINS = context.get('DOMAINS', {})
    TEMPLATES = context.get('TEMPLATES', {})
    QUALITY_MODES = context.get('QUALITY_MODES', {})
    
    if path == '/analyze':
        token = handler._get_token_from_request()
        user = handler._get_current_user(token) if hasattr(handler, '_get_current_user') else None
        if not user:
            handler._send_json(401, {"error": "请先登录"})
            return True
        
        data = body.get('data', [])
        if not data:
            handler._send_json(400, {"error": "请提供数据"})
            return True
        
        analysis = {
            "count": len(data),
            "avg_length": sum(len(d.get('text', '')) for d in data) / len(data) if data else 0,
            "min_length": min(len(d.get('text', '')) for d in data) if data else 0,
            "max_length": max(len(d.get('text', '')) for d in data) if data else 0,
            "quality_distribution": {},
            "source_distribution": {},
            "word_frequency": {},
        }
        
        for item in data:
            quality = item.get('quality_tier', 'unknown')
            analysis["quality_distribution"][quality] = analysis["quality_distribution"].get(quality, 0) + 1
            
            source = item.get('source', 'unknown')
            analysis["source_distribution"][source] = analysis["source_distribution"].get(source, 0) + 1
            
            word = item.get('word', '')
            if word:
                analysis["word_frequency"][word] = analysis["word_frequency"].get(word, 0) + 1
        
        sorted_words = sorted(analysis["word_frequency"].items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["top_words"] = dict(sorted_words)
        del analysis["word_frequency"]
        
        handler._send_json(200, {"success": True, "analysis": analysis})
        return True
    
    elif path == '/stats':
        try:
            domain_count = len(DOMAINS) if DOMAINS else 0
            keyword_count = sum(len(v) for v in DOMAINS.values()) if DOMAINS else 0
            template_count = sum(len(TEMPLATES.get(k, [])) for k in TEMPLATES.keys()) if TEMPLATES else 0
            
            detailed_stats = {
                "total_data": stats.get("total", 0),
                "today_data": stats.get("today", 0),
                "total_tasks": len(tasks),
                "completed_tasks": len([t for t in tasks.values() if t.get("status") == "completed"]),
                "pending_tasks": len([t for t in tasks.values() if t.get("status") in ["pending", "processing"]]),
                "domains": domain_count,
                "total_keywords": keyword_count,
                "total_templates": template_count,
                "users": len(user_manager.users) if user_manager else 0,
            }
            
            get_monitor_service = context.get('get_monitor_service')
            if get_monitor_service:
                monitor = get_monitor_service()
                if monitor:
                    try:
                        detailed_stats["monitor"] = monitor.get_status()
                    except Exception as e:
                        print(f"[监控] 获取状态失败: {e}")
            
            handler._send_json(200, detailed_stats)
        except Exception as e:
            handler._send_json(500, {"error": str(e)})
        return True
    
    elif path == '/api/policies':
        BACKEND_DIR = context.get('BACKEND_DIR', '')
        policy_file = os.path.join(BACKEND_DIR, 'policy_data.json')
        if os.path.exists(policy_file):
            with open(policy_file, 'r', encoding='utf-8') as f:
                policies = json.load(f)
            handler._send_json(200, policies)
        else:
            default_policies = {
                "last_update": "2026年2月",
                "categories": {
                    "subsidy": {"name": "补贴政策", "icon": "💰", "color": "var(--success)", "policies": []},
                    "tax": {"name": "税收优惠", "icon": "📊", "color": "var(--primary)", "policies": []},
                    "certification": {"name": "资质认证", "icon": "🏛️", "color": "var(--warning)", "policies": []},
                    "industry": {"name": "产业政策", "icon": "📈", "color": "var(--danger)", "policies": []}
                },
                "resources": []
            }
            handler._send_json(200, default_policies)
        return True
    
    elif path == '/api/provenance':
        batch_id = body.get('batch_id', '')
        count = body.get('count', 0)
        domain = body.get('domain', '')
        quality_mode = body.get('quality_mode', 'standard')
        
        provenance_doc = {
            "document_type": "数据来源证明",
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "issuer": {
                "platform": "PureData",
                "description": "AI训练数据生成平台",
                "website": "https://puredata.ai"
            },
            "data_info": {
                "batch_id": batch_id,
                "count": count,
                "domain": domain,
                "quality_mode": quality_mode,
                "generator": "synthetic",
                "license": "PureData-Commercial-1.0"
            },
            "compliance": {
                "laws": ["数据安全法", "个人信息保护法", "著作权法"],
                "certifications": ["合成数据", "无个人信息", "无版权风险"],
                "data_type": "合成数据",
                "contains_pii": False,
                "contains_copyrighted_content": False
            }
        }
        handler._send_json(200, provenance_doc)
        return True
    
    return None
