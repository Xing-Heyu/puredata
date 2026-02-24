# DataGen Pro API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **编码**: `UTF-8`

---

## 一、健康检查

### GET /health

检查服务是否正常运行。

**请求示例：**
```bash
curl http://localhost:8000/health
```

**响应示例：**
```json
{
  "status": "ok"
}
```

---

## 二、领域管理

### GET /domains

获取所有支持的领域列表。

**请求示例：**
```bash
curl http://localhost:8000/domains
```

**响应示例：**
```json
{
  "domains": [
    {"name": "人工智能", "keywords": 30},
    {"name": "劳动合同", "keywords": 27},
    {"name": "医疗", "keywords": 30},
    {"name": "金融", "keywords": 30}
  ]
}
```

---

## 三、统计数据

### GET /stats

获取数据生成统计信息。

**请求示例：**
```bash
curl http://localhost:8000/stats
```

**响应示例：**
```json
{
  "total_data": 1000,
  "today_data": 500
}
```

---

## 四、任务管理

### GET /tasks

获取所有任务列表。

**请求示例：**
```bash
curl http://localhost:8000/tasks
```

**响应示例：**
```json
{
  "tasks": [
    {
      "id": "abc123",
      "status": "completed",
      "domain": "人工智能",
      "count": 100
    }
  ]
}
```

### GET /task/{task_id}

查询指定任务状态。

**路径参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |

**请求示例：**
```bash
curl http://localhost:8000/task/abc123
```

**响应示例：**
```json
{
  "id": "abc123",
  "status": "completed",
  "domain": "人工智能",
  "count": 100,
  "progress": 100,
  "total": 100,
  "download_url": "/download/abc123_人工智能_100.json",
  "preview": [...],
  "elapsed": 0.05,
  "duplicates": 0
}
```

**任务状态说明：**
| 状态 | 说明 |
|------|------|
| pending | 等待处理 |
| processing | 处理中 |
| completed | 已完成 |
| failed | 失败 |

---

## 五、数据生成

### POST /generate

生成基础数据。

**请求参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| domain | string | 否 | 人工智能 | 领域名称 |
| count | integer | 否 | 100 | 生成数量 |
| format | string | 否 | json | 输出格式 |
| mode | string | 否 | hybrid | 生成模式 |

**生成模式说明：**
| 模式 | 说明 |
|------|------|
| clean | 干净数据，无噪声 |
| noisy | 高噪声数据 |
| hybrid | 混合模式（推荐） |

**请求示例：**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "人工智能",
    "count": 100,
    "format": "json",
    "mode": "hybrid"
  }'
```

**响应示例：**
```json
{
  "task_id": "abc123"
}
```

---

### POST /generate_sequence

生成用户行为序列数据。

**请求参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| domain | string | 否 | 电商 | 领域名称 |
| user_count | integer | 否 | 10 | 用户数量 |
| avg_length | integer | 否 | 10 | 平均序列长度 |
| format | string | 否 | json | 输出格式 |

**支持领域：**
- 电商
- 医疗
- 社交

**请求示例：**
```bash
curl -X POST http://localhost:8000/generate_sequence \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "电商",
    "user_count": 100,
    "avg_length": 10
  }'
```

**响应示例：**
```json
{
  "task_id": "def456",
  "type": "behavior_sequence"
}
```

---

## 六、文件下载

### GET /download/{filename}

下载生成的数据文件。

**路径参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 文件名 |

**请求示例：**
```bash
curl -O http://localhost:8000/download/abc123_人工智能_100.json
```

**响应：**
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename="文件名"`

---

## 七、错误响应

所有错误响应格式：

```json
{
  "error": "错误描述"
}
```

**常见错误码：**
| HTTP状态码 | 说明 |
|------------|------|
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 八、数据格式

### 基础数据格式

```json
{
  "id": 1,
  "word": "machine learning",
  "text": "machine learning is a fundamental concept in 人工智能.",
  "category": "人工智能",
  "source": "clean",
  "confidence": 0.95,
  "timestamp": "2025-06-15T10:30:00",
  "user_id": "user_12345",
  "verified": true
}
```

### 行为序列数据格式

```json
{
  "global_id": 1,
  "user_id": "user_00001",
  "session_id": "abc123",
  "sequence_id": 1,
  "behavior": "浏览",
  "timestamp": "2025-06-15T10:30:00",
  "domain": "电商",
  "lifecycle_stage": "活跃"
}
```

---

## 九、使用流程

```
1. 调用 POST /generate 或 POST /generate_sequence 创建任务
   ↓
2. 获取返回的 task_id
   ↓
3. 调用 GET /task/{task_id} 查询任务状态
   ↓
4. 等待 status 变为 completed
   ↓
5. 使用 download_url 下载文件
```

---

## 十、SDK示例

### Python

```python
import urllib.request
import json
import time

# 创建任务
data = json.dumps({"domain": "人工智能", "count": 100}).encode()
req = urllib.request.Request(
    "http://localhost:8000/generate",
    data=data,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req)
task_id = json.loads(resp.read())["task_id"]

# 等待完成
while True:
    task_resp = urllib.request.urlopen(f"http://localhost:8000/task/{task_id}")
    task = json.loads(task_resp.read())
    if task["status"] == "completed":
        break
    time.sleep(1)

# 下载数据
download_url = f"http://localhost:8000{task['download_url']}"
urllib.request.urlretrieve(download_url, "output.json")
```

### JavaScript

```javascript
// 创建任务
const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({domain: '人工智能', count: 100})
});
const {task_id} = await response.json();

// 等待完成
let task;
do {
  await new Promise(r => setTimeout(r, 1000));
  const taskResp = await fetch(`http://localhost:8000/task/${task_id}`);
  task = await taskResp.json();
} while (task.status !== 'completed');

// 下载数据
window.location.href = `http://localhost:8000${task.download_url}`;
```
