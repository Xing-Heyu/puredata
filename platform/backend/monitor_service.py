#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PureData 监控告警系统
- 系统健康监控
- 性能指标采集
- 异常告警通知
- 日志聚合分析
"""

import os
import json
import time
import threading
import psutil
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
from typing import Dict, List, Optional, Callable
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('monitor')

# ============ 配置 ============
class MonitorConfig:
    MONITOR_INTERVAL = 60  # 监控间隔（秒）
    ALERT_COOLDOWN = 300  # 告警冷却时间（秒）
    
    # 阈值配置
    CPU_THRESHOLD = 80  # CPU使用率阈值
    MEMORY_THRESHOLD = 80  # 内存使用率阈值
    DISK_THRESHOLD = 90  # 磁盘使用率阈值
    RESPONSE_TIME_THRESHOLD = 5.0  # 响应时间阈值（秒）
    ERROR_RATE_THRESHOLD = 0.05  # 错误率阈值（5%）
    
    # 通知配置
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.qq.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    ALERT_EMAILS = os.environ.get('ALERT_EMAILS', '').split(',')
    
    # Webhook通知
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
    WEBHOOK_TOKEN = os.environ.get('WEBHOOK_TOKEN', '')

# ============ 指标采集 ============
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'response_times': [],
            'request_count': 0,
            'error_count': 0,
            'active_users': 0,
            'tasks_completed': 0,
            'data_generated': 0
        }
        self.lock = threading.Lock()
    
    def record_cpu(self, usage: float):
        with self.lock:
            self.metrics['cpu_usage'].append((time.time(), usage))
            self.metrics['cpu_usage'] = self.metrics['cpu_usage'][-100:]
    
    def record_memory(self, usage: float):
        with self.lock:
            self.metrics['memory_usage'].append((time.time(), usage))
            self.metrics['memory_usage'] = self.metrics['memory_usage'][-100:]
    
    def record_disk(self, usage: float):
        with self.lock:
            self.metrics['disk_usage'].append((time.time(), usage))
            self.metrics['disk_usage'] = self.metrics['disk_usage'][-100:]
    
    def record_response_time(self, response_time: float):
        with self.lock:
            self.metrics['response_times'].append((time.time(), response_time))
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def record_request(self, is_error: bool = False):
        with self.lock:
            self.metrics['request_count'] += 1
            if is_error:
                self.metrics['error_count'] += 1
    
    def record_task_completed(self, data_count: int):
        with self.lock:
            self.metrics['tasks_completed'] += 1
            self.metrics['data_generated'] += data_count
    
    def get_summary(self) -> Dict:
        with self.lock:
            cpu_avg = sum(u for _, u in self.metrics['cpu_usage'][-10:]) / 10 if self.metrics['cpu_usage'] else 0
            mem_avg = sum(u for _, u in self.metrics['memory_usage'][-10:]) / 10 if self.metrics['memory_usage'] else 0
            disk_current = self.metrics['disk_usage'][-1][1] if self.metrics['disk_usage'] else 0
            response_avg = sum(t for _, t in self.metrics['response_times'][-100:]) / 100 if self.metrics['response_times'] else 0
            error_rate = self.metrics['error_count'] / self.metrics['request_count'] if self.metrics['request_count'] > 0 else 0
            
            return {
                'cpu_usage': round(cpu_avg, 2),
                'memory_usage': round(mem_avg, 2),
                'disk_usage': round(disk_current, 2),
                'response_time_avg': round(response_avg, 3),
                'request_count': self.metrics['request_count'],
                'error_count': self.metrics['error_count'],
                'error_rate': round(error_rate, 4),
                'tasks_completed': self.metrics['tasks_completed'],
                'data_generated': self.metrics['data_generated'],
                'timestamp': datetime.now().isoformat()
            }
    
    def reset(self):
        with self.lock:
            self.metrics['request_count'] = 0
            self.metrics['error_count'] = 0

# ============ 告警系统 ============
class AlertManager:
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.alert_history = {}
        self.alert_handlers = []
    
    def add_handler(self, handler: Callable):
        self.alert_handlers.append(handler)
    
    def check_and_alert(self, metric_name: str, value: float, threshold: float, message: str):
        if value > threshold:
            now = time.time()
            last_alert = self.alert_history.get(metric_name, 0)
            
            if now - last_alert > self.config.ALERT_COOLDOWN:
                self.alert_history[metric_name] = now
                alert_data = {
                    'metric': metric_name,
                    'value': value,
                    'threshold': threshold,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
                self._trigger_alert(alert_data)
    
    def _trigger_alert(self, alert_data: Dict):
        logger.warning(f"告警触发: {alert_data['message']}")
        
        for handler in self.alert_handlers:
            try:
                handler(alert_data)
            except Exception as e:
                logger.error(f"告警处理器执行失败: {e}")
    
    def send_email(self, alert_data: Dict):
        if not self.config.SMTP_USER or not self.config.ALERT_EMAILS:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.SMTP_USER
            msg['To'] = ', '.join(self.config.ALERT_EMAILS)
            msg['Subject'] = f"[PureData告警] {alert_data['metric']}"
            
            body = f"""
告警通知

指标: {alert_data['metric']}
当前值: {alert_data['value']}
阈值: {alert_data['threshold']}
时间: {alert_data['timestamp']}

详情: {alert_data['message']}

---
PureData监控系统
            """
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP_SSL(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                server.sendmail(self.config.SMTP_USER, self.config.ALERT_EMAILS, msg.as_string())
            
            logger.info(f"告警邮件已发送: {alert_data['metric']}")
        except Exception as e:
            logger.error(f"发送告警邮件失败: {e}")
    
    def send_webhook(self, alert_data: Dict):
        if not self.config.WEBHOOK_URL:
            return
        
        try:
            import urllib.request
            data = json.dumps(alert_data).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.config.WEBHOOK_TOKEN}'
            }
            req = urllib.request.Request(self.config.WEBHOOK_URL, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    logger.info(f"Webhook通知已发送: {alert_data['metric']}")
        except Exception as e:
            logger.error(f"发送Webhook通知失败: {e}")

# ============ 监控服务 ============
class MonitorService:
    def __init__(self):
        self.config = MonitorConfig()
        self.collector = MetricsCollector()
        self.alert_manager = AlertManager(self.config)
        self.running = False
        self.monitor_thread = None
        
        # 注册告警处理器
        self.alert_manager.add_handler(self.alert_manager.send_email)
        self.alert_manager.add_handler(self.alert_manager.send_webhook)
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("监控服务已启动")
    
    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("监控服务已停止")
    
    def _monitor_loop(self):
        while self.running:
            try:
                self._collect_system_metrics()
                self._check_alerts()
                time.sleep(self.config.MONITOR_INTERVAL)
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(10)
    
    def _collect_system_metrics(self):
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        self.collector.record_cpu(cpu_usage)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.collector.record_memory(memory.percent)
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        self.collector.record_disk(disk.percent)
        
        logger.debug(f"系统指标: CPU={cpu_usage}%, Memory={memory.percent}%, Disk={disk.percent}%")
    
    def _check_alerts(self):
        summary = self.collector.get_summary()
        
        self.alert_manager.check_and_alert(
            'cpu_usage', summary['cpu_usage'], self.config.CPU_THRESHOLD,
            f"CPU使用率过高: {summary['cpu_usage']}% > {self.config.CPU_THRESHOLD}%"
        )
        
        self.alert_manager.check_and_alert(
            'memory_usage', summary['memory_usage'], self.config.MEMORY_THRESHOLD,
            f"内存使用率过高: {summary['memory_usage']}% > {self.config.MEMORY_THRESHOLD}%"
        )
        
        self.alert_manager.check_and_alert(
            'disk_usage', summary['disk_usage'], self.config.DISK_THRESHOLD,
            f"磁盘使用率过高: {summary['disk_usage']}% > {self.config.DISK_THRESHOLD}%"
        )
        
        self.alert_manager.check_and_alert(
            'response_time', summary['response_time_avg'], self.config.RESPONSE_TIME_THRESHOLD,
            f"响应时间过长: {summary['response_time_avg']}s > {self.config.RESPONSE_TIME_THRESHOLD}s"
        )
        
        self.alert_manager.check_and_alert(
            'error_rate', summary['error_rate'], self.config.ERROR_RATE_THRESHOLD,
            f"错误率过高: {summary['error_rate']*100}% > {self.config.ERROR_RATE_THRESHOLD*100}%"
        )
    
    def get_status(self) -> Dict:
        return {
            'running': self.running,
            'metrics': self.collector.get_summary(),
            'alerts': len(self.alert_manager.alert_history),
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }

# ============ 全局实例 ============
monitor = MonitorService()

# ============ 装饰器 ============
def monitor_request(func):
    """请求监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        is_error = False
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            is_error = True
            raise
        finally:
            response_time = time.time() - start_time
            monitor.collector.record_response_time(response_time)
            monitor.collector.record_request(is_error)
    return wrapper

def monitor_task(func):
    """任务监控装饰器"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, dict) and 'count' in result:
                monitor.collector.record_task_completed(result['count'])
            return result
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            raise
    return wrapper

# ============ 启动 ============
if __name__ == '__main__':
    print("=" * 50)
    print("PureData 监控服务")
    print("=" * 50)
    
    monitor.start()
    monitor.start_time = time.time()
    
    try:
        while True:
            time.sleep(60)
            status = monitor.get_status()
            print(f"\n[{datetime.now().isoformat()}] 系统状态:")
            print(f"  CPU: {status['metrics']['cpu_usage']}%")
            print(f"  内存: {status['metrics']['memory_usage']}%")
            print(f"  磁盘: {status['metrics']['disk_usage']}%")
            print(f"  请求数: {status['metrics']['request_count']}")
            print(f"  错误率: {status['metrics']['error_rate']*100:.2f}%")
    except KeyboardInterrupt:
        monitor.stop()
        print("\n监控服务已停止")
