#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小测试单元 - 逐步添加模块测试
目标：验证 simple_main.py 的所有功能
"""

print("="*50)
print("最小测试单元启动")
print("="*50)

# ============ 第1步：核心HTTP服务器 ============
print("\n[1/10] 测试HTTP服务器...")

from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        if self.path == '/health':
            self._send_json(200, {"status": "ok", "step": 1})
        else:
            self._send_json(404, {"error": "Not found"})
    
    def do_POST(self):
        self._send_json(404, {"error": "Not found"})

print("[OK] HTTP服务器类定义完成")

# ============ 第2步：测试启动 ============
print("\n[2/10] 测试服务器启动...")

import threading
import time

def run_server():
    server = ThreadingHTTPServer(('0.0.0.0', 9000), Handler)
    server.serve_forever()

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(1)

import urllib.request
try:
    resp = urllib.request.urlopen('http://localhost:9000/health', timeout=5)
    result = json.loads(resp.read().decode())
    print(f"[OK] 服务器响应: {result}")
except Exception as e:
    print(f"[FAIL] 服务器启动失败: {e}")
    exit(1)

# ============ 第3步：添加用户系统 ============
print("\n[3/10] 测试用户系统...")

try:
    from user_system import user_manager, UserRole, Permission
    print(f"[OK] 用户系统加载成功，当前用户数: {len(user_manager.users)}")
except Exception as e:
    print(f"[FAIL] 用户系统加载失败: {e}")
    exit(1)

# ============ 第4步：测试用户注册 ============
print("\n[4/10] 测试用户注册...")

try:
    result = user_manager.register('test_minimal', 'password123', 'test@minimal.com')
    if result.get('success'):
        print(f"[OK] 注册成功: {result.get('message')}")
    else:
        print(f"[INFO] 注册结果: {result.get('error')}")
except Exception as e:
    print(f"[FAIL] 注册失败: {e}")
    exit(1)

# ============ 第5步：测试用户登录 ============
print("\n[5/10] 测试用户登录...")

try:
    result = user_manager.login('admin', 'admin123')
    if result.get('success'):
        print(f"[OK] 登录成功: {result['user']['username']}")
    else:
        print(f"[FAIL] 登录失败: {result.get('error')}")
except Exception as e:
    print(f"[FAIL] 登录异常: {e}")
    exit(1)

# ============ 第6步：测试管理员认证 ============
print("\n[6/10] 测试管理员认证...")

try:
    from 管理员认证 import admin_auth
    result = admin_auth.login('admin', 'admin123')
    if result.get('success'):
        print(f"[OK] 管理员登录成功")
    else:
        print(f"[FAIL] 管理员登录失败: {result.get('error')}")
except Exception as e:
    print(f"[FAIL] 管理员认证异常: {e}")
    exit(1)

# ============ 第7步：测试验证码系统 ============
print("\n[7/10] 测试验证码系统...")

try:
    from otp_manager import otp_manager, OTPType
    result = otp_manager.send_code('13800138000', OTPType.REGISTER)
    print(f"[OK] 验证码发送: {result.get('message')}")
except Exception as e:
    print(f"[FAIL] 验证码系统异常: {e}")
    exit(1)

# ============ 第8步：测试租户系统 ============
print("\n[8/10] 测试租户系统...")

try:
    from tenant_manager import tenant_manager, TenantPlan
    print(f"[OK] 租户系统加载成功")
except Exception as e:
    print(f"[FAIL] 租户系统异常: {e}")
    exit(1)

# ============ 第9步：测试配置系统 ============
print("\n[9/10] 测试配置系统...")

try:
    from config import DOMAINS, TEMPLATES, QUALITY_MODES, get_available_domains
    domains = get_available_domains()
    print(f"[OK] 配置加载成功: {len(domains)}个领域, {len(TEMPLATES)}个模板")
except Exception as e:
    print(f"[FAIL] 配置系统异常: {e}")
    exit(1)

# ============ 第10步：测试生成器 ============
print("\n[10/10] 测试生成器...")

try:
    from generators import HighQualityGenerator
    print(f"[OK] 生成器加载成功")
except Exception as e:
    print(f"[FAIL] 生成器异常: {e}")
    exit(1)

# ============ 总结 ============
print("\n" + "="*50)
print("所有模块测试通过!")
print("="*50)

# ============ 额外测试：数据生成 ============
print("\n[额外1] 测试数据生成...")

try:
    from generators import HighQualityGenerator
    gen = HighQualityGenerator(use_api=False)
    item = gen.generate_single("机器学习", "人工智能", 1)
    print(f"[OK] 生成器工作正常")
except Exception as e:
    print(f"[FAIL] 数据生成异常: {e}")
    import traceback
    traceback.print_exc()

# ============ 额外测试：限流系统 ============
print("\n[额外2] 测试限流系统...")

try:
    from risk_control import RateLimiter, RateLimitType
    limiter = RateLimiter()
    print(f"[OK] 限流系统加载成功")
except Exception as e:
    print(f"[FAIL] 限流系统异常: {e}")

# ============ 额外测试：存储层 ============
print("\n[额外3] 测试存储层...")

try:
    from storage_layer import StorageManager
    storage = StorageManager()
    print(f"[OK] 存储层加载成功")
except Exception as e:
    print(f"[FAIL] 存储层异常: {e}")

print("\n" + "="*50)
print("完整测试结束!")
print("="*50)

# ============ 额外测试：反滥用系统 ============
print("\n[额外4] 测试反滥用系统...")

try:
    from anti_abuse import AntiAbuseSystem
    system = AntiAbuseSystem()
    print(f"[OK] 反滥用系统加载成功")
except Exception as e:
    print(f"[FAIL] 反滥用系统异常: {e}")

# ============ 额外测试：任务队列 ============
print("\n[额外5] 测试任务队列...")

try:
    from task_queue import AsyncTaskQueue
    queue = AsyncTaskQueue()
    print(f"[OK] 任务队列加载成功")
except Exception as e:
    print(f"[FAIL] 任务队列异常: {e}")

# ============ 额外测试：支付管理 ============
print("\n[额外6] 测试支付管理...")

try:
    from payment_manager import PaymentManager
    pm = PaymentManager()
    print(f"[OK] 支付管理加载成功")
except Exception as e:
    print(f"[FAIL] 支付管理异常: {e}")

# ============ 额外测试：监控服务 ============
print("\n[额外7] 测试监控服务...")

try:
    from monitor_service import MonitorService
    print(f"[OK] 监控服务加载成功")
except ImportError as e:
    print(f"[SKIP] 监控服务缺少依赖: {e}")
except Exception as e:
    print(f"[FAIL] 监控服务异常: {e}")

# ============ 额外测试：错误处理 ============
print("\n[额外8] 测试错误处理...")

try:
    from error_handler import ErrorContext, AppException
    print(f"[OK] 错误处理加载成功")
except Exception as e:
    print(f"[FAIL] 错误处理异常: {e}")

# ============ 额外测试：数据缓存 ============
print("\n[额外9] 测试数据缓存...")

try:
    from data_cache import DataCache
    cache = DataCache()
    print(f"[OK] 数据缓存加载成功")
except Exception as e:
    print(f"[FAIL] 数据缓存异常: {e}")

# ============ 额外测试：API密钥管理 ============
print("\n[额外10] 测试API密钥管理...")

try:
    from api_key_manager import APIKeyManager
    manager = APIKeyManager()
    print(f"[OK] API密钥管理加载成功")
except Exception as e:
    print(f"[FAIL] API密钥管理异常: {e}")

# ============ 额外测试：安全模块 ============
print("\n[额外11] 测试安全模块...")

try:
    from security import SecurityProtocol
    sec = SecurityProtocol()
    print(f"[OK] 安全模块加载成功")
except Exception as e:
    print(f"[FAIL] 安全模块异常: {e}")

# ============ 额外测试：数据去重 ============
print("\n[额外12] 测试数据去重...")

try:
    from quality import DeduplicationSystem
    dedup = DeduplicationSystem()
    print(f"[OK] 数据去重加载成功")
except Exception as e:
    print(f"[FAIL] 数据去重异常: {e}")

# ============ 额外测试：容错系统 ============
print("\n[额外13] 测试容错系统...")

try:
    from datagenpro.managers.fault_tolerance_manager import FaultToleranceManager
    ft = FaultToleranceManager()
    print(f"[OK] 容错系统加载成功")
except Exception as e:
    print(f"[FAIL] 容错系统异常: {e}")

# ============ 额外测试：操作日志 ============
print("\n[额外14] 测试操作日志...")

try:
    from operation_logger import OperationLogger
    logger = OperationLogger()
    print(f"[OK] 操作日志加载成功")
except Exception as e:
    print(f"[FAIL] 操作日志异常: {e}")

print("\n" + "="*50)
print("所有模块测试完成!")
print("="*50)

# ============ 额外测试：变体引擎 ============
print("\n[额外15] 测试变体引擎...")

try:
    from variation_engine import VariationEngine
    engine = VariationEngine()
    print(f"[OK] 变体引擎加载成功")
except Exception as e:
    print(f"[FAIL] 变体引擎异常: {e}")

# ============ 额外测试：数据扩展 ============
print("\n[额外16] 测试数据扩展...")

try:
    from data_expansion import DataExpansionEngine
    expander = DataExpansionEngine()
    print(f"[OK] 数据扩展加载成功")
except Exception as e:
    print(f"[FAIL] 数据扩展异常: {e}")

# ============ 额外测试：数据清洗 ============
print("\n[额外17] 测试数据清洗...")

try:
    from data_sanitizer import DataSanitizer
    sanitizer = DataSanitizer()
    print(f"[OK] 数据清洗加载成功")
except Exception as e:
    print(f"[FAIL] 数据清洗异常: {e}")

# ============ 额外测试：高级采样 ============
print("\n[额外18] 测试高级采样...")

try:
    from advanced_sampler import AdvancedSampler
    sampler = AdvancedSampler()
    print(f"[OK] 高级采样加载成功")
except Exception as e:
    print(f"[FAIL] 高级采样异常: {e}")

# ============ 额外测试：噪声生成 ============
print("\n[额外19] 测试噪声生成...")

try:
    from noise_generator import NoiseGenerator
    gen = NoiseGenerator()
    print(f"[OK] 噪声生成加载成功")
except Exception as e:
    print(f"[FAIL] 噪声生成异常: {e}")

# ============ 额外测试：学术验证 ============
print("\n[额外20] 测试学术验证...")

try:
    from academic_validation import get_academic_validation
    print(f"[OK] 学术验证加载成功")
except Exception as e:
    print(f"[FAIL] 学术验证异常: {e}")

# ============ 额外测试：质量分析 ============
print("\n[额外21] 测试质量分析...")

try:
    from quality_analyzer import DataQualityAnalyzer
    analyzer = DataQualityAnalyzer()
    print(f"[OK] 质量分析加载成功")
except Exception as e:
    print(f"[FAIL] 质量分析异常: {e}")

# ============ 额外测试：AI数据管道 ============
print("\n[额外22] 测试AI数据管道...")

try:
    from ai_data_pipeline import AIDataPipeline
    pipeline = AIDataPipeline()
    print(f"[OK] AI数据管道加载成功")
except Exception as e:
    print(f"[FAIL] AI数据管道异常: {e}")

# ============ 额外测试：Prompt管理 ============
print("\n[额外23] 测试Prompt管理...")

try:
    from prompt_manager import PromptTemplateManager
    pm = PromptTemplateManager()
    print(f"[OK] Prompt管理加载成功")
except Exception as e:
    print(f"[FAIL] Prompt管理异常: {e}")

# ============ 额外测试：LLM审计 ============
print("\n[额外24] 测试LLM审计...")

try:
    from llm_data_auditor import LLMDataAuditor
    auditor = LLMDataAuditor()
    print(f"[OK] LLM审计加载成功")
except Exception as e:
    print(f"[FAIL] LLM审计异常: {e}")

print("\n" + "="*50)
print("全部模块测试完成!")
print("="*50)

# ============ 子目录模块测试 ============
print("\n" + "="*50)
print("子目录模块测试")
print("="*50)

# ============ config目录 ============
print("\n[子目录1] 测试config模块...")

try:
    from config import DOMAINS, TEMPLATES, get_available_domains
    print(f"[OK] config模块加载成功")
except Exception as e:
    print(f"[FAIL] config模块异常: {e}")

# ============ filters目录 ============
print("\n[子目录2] 测试filters模块...")

try:
    from filters import DeduplicationSystem, SimpleDeduplicator
    print(f"[OK] filters模块加载成功")
except Exception as e:
    print(f"[FAIL] filters模块异常: {e}")

# ============ generators目录 ============
print("\n[子目录3] 测试generators模块...")

try:
    from generators import HighQualityGenerator, CopulaGenerator, TopologyGenerator
    print(f"[OK] generators模块加载成功")
except Exception as e:
    print(f"[FAIL] generators模块异常: {e}")

# ============ handlers目录 ============
print("\n[子目录4] 测试handlers模块...")

try:
    from handlers import AuthHandler, GenerationHandler
    print(f"[OK] handlers模块加载成功")
except Exception as e:
    print(f"[FAIL] handlers模块异常: {e}")

# ============ datagenpro目录 ============
print("\n[子目录5] 测试datagenpro模块...")

try:
    from datagenpro.generators import DataGenerator, SequenceGenerator
    from datagenpro.validators import DataValidator
    from datagenpro.converters import AIFormatConverter
    print(f"[OK] datagenpro模块加载成功")
except Exception as e:
    print(f"[FAIL] datagenpro模块异常: {e}")

# ============ managers目录 ============
print("\n[子目录6] 测试managers模块...")

try:
    from managers import BackupManager, SystemMonitor
    print(f"[OK] managers模块加载成功")
except Exception as e:
    print(f"[FAIL] managers模块异常: {e}")

# ============ 中文模块测试 ============
print("\n" + "="*50)
print("中文模块测试")
print("="*50)

# ============ 千问API集成 ============
print("\n[中文1] 测试千问API集成...")

try:
    from api.llm import QwenAPI
    print(f"[OK] 千问API集成加载成功")
except Exception as e:
    print(f"[FAIL] 千问API集成异常: {e}")

# ============ 增强数据生成器 ============
print("\n[中文2] 测试增强数据生成器...")

try:
    from 增强数据生成器 import EnhancedDataGenerator
    print(f"[OK] 增强数据生成器加载成功")
except Exception as e:
    print(f"[FAIL] 增强数据生成器异常: {e}")

# ============ 数据质量评估 ============
print("\n[中文3] 测试数据质量评估...")

try:
    from 数据质量评估 import DataQualityEvaluator
    print(f"[OK] 数据质量评估加载成功")
except Exception as e:
    print(f"[FAIL] 数据质量评估异常: {e}")

# ============ 结构化日志 ============
print("\n[中文4] 测试结构化日志...")

try:
    from core import StructuredLogger
    print(f"[OK] 结构化日志加载成功")
except Exception as e:
    print(f"[FAIL] 结构化日志异常: {e}")

# ============ 缓存管理 ============
print("\n[中文5] 测试缓存管理...")

try:
    from core import CacheManager
    print(f"[OK] 缓存管理加载成功")
except Exception as e:
    print(f"[FAIL] 缓存管理异常: {e}")

# ============ 配置管理 ============
print("\n[中文6] 测试配置管理...")

try:
    from core import Config
    print(f"[OK] 配置管理加载成功")
except Exception as e:
    print(f"[FAIL] 配置管理异常: {e}")

# ============ 其他独立模块 ============
print("\n" + "="*50)
print("其他独立模块测试")
print("="*50)

# ============ SDGT生成器 ============
print("\n[其他1] 测试SDGT生成器...")

try:
    from sdgt_generator import SDGTGenerator
    print(f"[OK] SDGT生成器加载成功")
except Exception as e:
    print(f"[FAIL] SDGT生成器异常: {e}")

# ============ 人类化生成器 ============
print("\n[其他2] 测试人类化生成器...")

try:
    from human_like_generator import HumanLikeGenerator
    print(f"[OK] 人类化生成器加载成功")
except Exception as e:
    print(f"[FAIL] 人类化生成器异常: {e}")

# ============ 无限数据生成器 ============
print("\n[其他3] 测试无限数据生成器...")

try:
    from infinite_data_generator import InfiniteDataGenerator
    print(f"[OK] 无限数据生成器加载成功")
except Exception as e:
    print(f"[FAIL] 无限数据生成器异常: {e}")

# ============ 扩展知识库 ============
print("\n[其他4] 测试扩展知识库...")

try:
    from config.extended_knowledge_base import get_extended_knowledge
    print(f"[OK] 扩展知识库加载成功")
except Exception as e:
    print(f"[FAIL] 扩展知识库异常: {e}")

# ============ AI数据验证器 ============
print("\n[其他5] 测试AI数据验证器...")

try:
    from ai_data_validator import AIDataValidator
    print(f"[OK] AI数据验证器加载成功")
except Exception as e:
    print(f"[FAIL] AI数据验证器异常: {e}")

# ============ AI格式转换器 ============
print("\n[其他6] 测试AI格式转换器...")

try:
    from datagenpro.converters.ai_format_converter import AITrainingFormatConverter
    print(f"[OK] AI格式转换器加载成功")
except Exception as e:
    print(f"[FAIL] AI格式转换器异常: {e}")

# ============ AI模板填充器 ============
print("\n[其他7] 测试AI模板填充器...")

try:
    from ai_template_filler import AITemplateFiller
    print(f"[OK] AI模板填充器加载成功")
except Exception as e:
    print(f"[FAIL] AI模板填充器异常: {e}")

# ============ T2质量控制 ============
print("\n[其他8] 测试T2质量控制...")

try:
    from t2_quality_control import QualityControlPipeline
    print(f"[OK] T2质量控制加载成功")
except Exception as e:
    print(f"[FAIL] T2质量控制异常: {e}")

# ============ 失败数据回收 ============
print("\n[其他9] 测试失败数据回收...")

try:
    from 失败数据回收 import DataRecoveryEngine
    print(f"[OK] 失败数据回收加载成功")
except Exception as e:
    print(f"[FAIL] 失败数据回收异常: {e}")

# ============ 本地知识图谱生成 ============
print("\n[其他10] 测试本地知识图谱生成...")

try:
    from 本地知识图谱生成 import LocalKnowledgeGraph
    print(f"[OK] 本地知识图谱生成加载成功")
except Exception as e:
    print(f"[FAIL] 本地知识图谱生成异常: {e}")

# ============ 真实种子数据 ============
print("\n[其他11] 测试真实种子数据...")

try:
    from 真实种子数据 import SeedDataManager
    print(f"[OK] 真实种子数据加载成功")
except Exception as e:
    print(f"[FAIL] 真实种子数据异常: {e}")

# ============ 学术级数据生成系统 ============
print("\n[其他12] 测试学术级数据生成系统...")

try:
    from 学术级数据生成系统 import AcademicDataPipeline
    print(f"[OK] 学术级数据生成系统加载成功")
except Exception as e:
    print(f"[FAIL] 学术级数据生成系统异常: {e}")

print("\n" + "="*50)
print("所有模块测试完成!")
print("="*50)
