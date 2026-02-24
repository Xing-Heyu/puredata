# DataGen Pro - API文档

## 基础信息

- **基础URL**: `http://localhost:8000`
- **内容类型**: `application/json`
- **认证方式**: Bearer Token（登录后获取）

---

## 数据生成API

### 生成数据

**POST** `/api/generate`

**请求体**:
```json
{
    "domain": "人工智能",
    "count": 100,
    "quality": "high",
    "keywords": ["机器学习", "深度学习"]
}
```

**响应**:
```json
{
    "task_id": "task_20250222_123456",
    "status": "success",
    "count": 100,
    "data": [
        {
            "id": 1,
            "word": "机器学习",
            "text": "机器学习是人工智能的核心技术...",
            "quality_tier": "high",
            "quality_score": 0.85
        }
    ]
}
```

---

### 查询任务状态

**GET** `/api/task/{task_id}`

**响应**:
```json
{
    "task_id": "task_20250222_123456",
    "status": "completed",
    "progress": 100,
    "count": 100,
    "created_at": "2025-02-22T12:34:56"
}
```

---

## 领域API

### 获取支持领域

**GET** `/api/domains`

**响应**:
```json
{
    "domains": ["人工智能", "劳动合同", "医疗", "金融"]
}
```

---

### 获取领域关键词

**GET** `/api/domains/{domain}/keywords`

**响应**:
```json
{
    "domain": "人工智能",
    "keywords": ["机器学习", "深度学习", "神经网络", "自然语言处理", ...]
}
```

---

## 质量模式API

### 获取质量模式配置

**GET** `/api/quality/modes`

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

## 用户API

### 用户注册

**POST** `/api/register`

**请求体**:
```json
{
    "username": "user123",
    "email": "user@example.com",
    "password": "Password123"
}
```

**注意**：密码需包含大小写字母和数字，至少8位。

---

### 用户登录

**POST** `/api/login`

**请求体**:
```json
{
    "username": "user123",
    "password": "Password123"
}
```

**响应**:
```json
{
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": "user_1",
        "username": "user123",
        "role": "user"
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
    "version": "2.0.0",
    "uptime": 3600
}
```

---

## 错误响应

所有错误响应格式：

```json
{
    "error": {
        "code": "INVALID_DOMAIN",
        "message": "不支持的领域: xxx",
        "details": {}
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
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 请求限制

| 模式 | 每日限制 | 每月限制 |
|------|---------|---------|
| 免费用户 | 100条 | 1000条 |
| VIP用户 | 1000条 | 10000条 |
| 企业用户 | 无限制 | 无限制 |
