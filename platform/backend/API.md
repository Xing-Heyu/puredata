# PureData - API文档

## 基础信息

- **基础URL**: `http://localhost:8000`
- **内容类型**: `application/json`

---

## 数据生成API

### 生成数据

**POST** `/generate`

**请求体**:
```json
{
    "domain": "人工智能",
    "count": 100,
    "format": "json",
    "mode": "hybrid",
    "quality_mode": "standard"
}
```

**响应**:
```json
{
    "success": true,
    "task_id": "20250222123456_abc12345"
}
```

---

### 查询任务状态

**GET** `/task/{task_id}`

**响应**:
```json
{
    "success": true,
    "task": {
        "id": "20250222123456_abc12345",
        "status": "completed",
        "progress": 100,
        "total": 100,
        "domain": "人工智能",
        "quality_mode": "standard",
        "created_at": "2025-02-22T12:34:56"
    }
}
```

---

## 领域API

### 获取支持领域

**GET** `/domains`

**响应**:
```json
{
    "success": true,
    "domains": [
        {"name": "人工智能", "keywords": 500},
        {"name": "医疗", "keywords": 500},
        {"name": "金融", "keywords": 500},
        {"name": "劳动合同", "keywords": 500}
    ]
}
```

---

## 质量模式API

### 获取质量模式配置

**GET** `/quality_modes`

**响应**:
```json
{
    "modes": {
        "ultra": {
            "high_ratio": 0.90,
            "description": "超高质量模式 - 全模块开启"
        },
        "high": {
            "high_ratio": 0.80,
            "description": "高质量模式 - 核心模块开启"
        },
        "standard": {
            "high_ratio": 0.50,
            "description": "标准质量模式"
        },
        "mixed": {
            "high_ratio": 0.25,
            "description": "混合质量模式"
        }
    }
}
```

---

## 健康检查

### 服务状态

**GET** `/health`

**响应**:
```json
{
    "status": "ok",
    "version": "1.0.0",
    "uptime": 3600
}
```

---

## 下载API

### 下载文件

**GET** `/download/{filename}`

**说明**: 下载生成的数据文件。

**响应**: 文件流

---

## 批量任务API

### 流式下载生成

**POST** `/api/generate/download`

**请求体**:
```json
{
    "domain": "人工智能",
    "count": 10000,
    "format": "jsonl",
    "quality_mode": "standard"
}
```

**响应**:
```json
{
    "success": true,
    "task_id": "abc123",
    "message": "已开始生成 10000 条数据，完成后可直接下载"
}
```

---

### 批量生成任务

**POST** `/api/batch/generate`

**请求体**:
```json
{
    "tasks": [
        {"domain": "人工智能", "count": 100},
        {"domain": "医疗", "count": 200}
    ]
}
```

**响应**:
```json
{
    "success": true,
    "results": [
        {"success": true, "task_id": "task_1"},
        {"success": true, "task_id": "task_2"}
    ],
    "total": 2
}
```

---

## 学术验证API

### 获取学术验证状态

**GET** `/api/academic_validation`

**响应**:
```json
{
    "success": true,
    "status": "active",
    "papers_count": 10
}
```

---

### 获取论文链接

**GET** `/api/paper_links`

**响应**:
```json
{
    "success": true,
    "papers": [
        {
            "title": "论文标题",
            "url": "https://...",
            "doi": "10.xxx/xxx"
        }
    ]
}
```

---

## 错误响应

所有错误响应格式：

```json
{
    "error": {
        "code": "INVALID_DOMAIN",
        "message": "不支持的领域: xxx"
    }
}
```

---

## HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
