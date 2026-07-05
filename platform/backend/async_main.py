#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PureData - FastAPI 异步HTTP服务器（高性能版）
提供更高性能的异步 HTTP 服务

服务类型：
    异步非阻塞HTTP服务器，基于 FastAPI + uvicorn

适用场景：
    - 生产环境部署
    - 高并发请求场景
    - 需要自动API文档的场景
    - 需要后台任务处理的场景

启动方式：
    方式1 - 直接运行：
        python async_main.py
    
    方式2 - uvicorn命令（推荐生产环境）：
        uvicorn async_main:app --host 0.0.0.0 --port 8000 --workers 4
    
    方式3 - 开发模式（热重载）：
        uvicorn async_main:app --host 0.0.0.0 --port 8000 --reload

访问地址：
    - 前台：http://localhost:8000
    - API文档：http://localhost:8000/docs
    - ReDoc文档：http://localhost:8000/redoc

与同步版本的区别：
    - 同步版本（simple_main.py）：开发测试、简单部署
    - 异步版本（async_main.py）：生产环境、高并发场景

依赖安装：
    pip install fastapi uvicorn python-multipart
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from core.exception_handler import module_loader

fastapi_module = module_loader.load('fastapi', [
    'FastAPI', 'HTTPException', 'BackgroundTasks'
])
if not fastapi_module:
    print("[ERROR] FastAPI 未安装，请运行: pip install fastapi uvicorn")
    sys.exit(1)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

BACKEND_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BACKEND_DIR))

START_TIME = time.time()
VERSION = "2.2.0"

app = FastAPI(
    title="PureData API",
    description="AI 训练数据生成平台 - 异步版本",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks: Dict[str, Dict] = {}
task_lock = asyncio.Lock()

class GenerateRequest(BaseModel):
    domain: str = Field(default="人工智能", description="生成领域")
    count: int = Field(default=100, ge=1, le=100000, description="生成数量")
    quality: str = Field(default="normal", description="质量模式")
    format: str = Field(default="json", description="输出格式")
    callback_url: Optional[str] = Field(default=None, description="回调URL")

@app.on_event("startup")
async def startup_event():
    print("[OK] PureData 异步服务已启动")


@app.on_event("shutdown")
async def shutdown_event():
    print("[OK] PureData 异步服务已停止")


@app.get("/")
async def root():
    return {
        "name": "PureData",
        "version": "2.2.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    uptime = int(time.time() - START_TIME)
    return {
        "status": "ok",
        "version": VERSION,
        "uptime": uptime
    }


@app.get("/domains")
async def get_domains():
    return {
        "domains": [
            {"id": "人工智能", "name": "人工智能", "description": "AI训练数据"},
            {"id": "医疗", "name": "医疗健康", "description": "医疗健康数据"},
            {"id": "金融", "name": "金融财经", "description": "金融财经数据"},
            {"id": "劳动合同", "name": "劳动合同", "description": "劳动法律数据"}
        ]
    }


@app.get("/quality_modes")
async def get_quality_modes():
    return {
        "modes": [
            {"id": "ultra", "name": "Ultra", "description": "最高质量"},
            {"id": "high", "name": "High", "description": "高质量"},
            {"id": "normal", "name": "Standard", "description": "标准质量"},
            {"id": "mixed", "name": "Mixed", "description": "混合质量"},
            {"id": "free", "name": "Free Trial", "description": "免费试用"}
        ]
    }


@app.post("/generate")
async def generate_data(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    import secrets
    task_id = secrets.token_urlsafe(16)
    
    async with task_lock:
        tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "domain": request.domain,
            "count": request.count,
            "quality": request.quality,
            "format": request.format,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "result": None,
            "error": None
        }
    
    background_tasks.add_task(
        run_generation_task,
        task_id,
        request.domain,
        request.count,
        request.quality
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"任务已创建，正在后台生成 {request.count} 条 {request.domain} 数据"
    }


async def run_generation_task(task_id: str, domain: str, count: int, quality: str):
    try:
        async with task_lock:
            tasks[task_id]["status"] = "running"
            tasks[task_id]["started_at"] = datetime.now().isoformat()
        
        try:
            from datagenpro import DataGenerator
            generator = DataGenerator()
            
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: generator.generate(domain=domain, count=count, quality=quality)
            )
            
            async with task_lock:
                tasks[task_id]["status"] = "completed"
                tasks[task_id]["progress"] = 100
                tasks[task_id]["result"] = data[:100] if isinstance(data, list) else data
                tasks[task_id]["total_count"] = len(data) if isinstance(data, list) else 1
                tasks[task_id]["completed_at"] = datetime.now().isoformat()
                
        except ImportError:
            await asyncio.sleep(1)
            
            mock_data = []
            for i in range(min(count, 10)):
                mock_data.append({
                    "id": i + 1,
                    "domain": domain,
                    "content": f"示例数据 {i+1}",
                    "quality": quality
                })
            
            async with task_lock:
                tasks[task_id]["status"] = "completed"
                tasks[task_id]["progress"] = 100
                tasks[task_id]["result"] = mock_data
                tasks[task_id]["total_count"] = count
                tasks[task_id]["completed_at"] = datetime.now().isoformat()
                tasks[task_id]["note"] = "使用模拟数据（DataGenerator 不可用）"
                
    except Exception as e:
        async with task_lock:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = str(e)
            tasks[task_id]["completed_at"] = datetime.now().isoformat()


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    async with task_lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        return tasks[task_id]


@app.get("/tasks")
async def list_tasks():
    async with task_lock:
        return {"tasks": list(tasks.values())}


def run_server():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    workers = int(os.environ.get("WORKERS", 1))
    
    print(f"\n{'='*60}")
    print("PureData - FastAPI 异步服务")
    print(f"{'='*60}")
    print(f"服务地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"工作进程: {workers}")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "async_main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        access_log=True
    )


if __name__ == "__main__":
    run_server()
