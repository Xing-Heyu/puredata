# PureData - AI训练数据生成平台

一键生成高质量AI训练数据，支持多领域、多格式、多质量模式。

## 快速开始

### 启动服务

```bash
cd platform/backend
python simple_main.py
```

访问地址：
- 前台：http://localhost:8000
- 后台：http://localhost:8000/admin
- API文档：http://localhost:8000/docs

### 管理员账号

首次启动时，系统会自动创建管理员账户并打印登录信息到控制台。

**安全提示**：生产环境请立即修改默认密码。

---

## 功能特性

### 核心功能
- 多领域数据生成（人工智能、劳动合同、医疗、金融）
- 多质量模式（纯净/混乱/噪音/混合）
- 多输出格式（JSON/CSV/TXT/JSONL/Parquet）
- 批量生成支持（10000+条）
- 实时进度显示

### 用户系统
- 手机/邮箱注册登录
- 邀请码奖励机制
- 免费额度管理
- 多角色权限控制

### 商业化功能
- 租户隔离系统
- 套餐购买支付
- API密钥管理
- 使用量统计

### 安全防护
- API限流保护
- 反滥用系统
- 操作日志审计
- 数据加密存储

---

## 系统架构

```
platform/
├── backend/
│   ├── simple_main.py      # 主服务入口
│   ├── user_system.py      # 用户系统
│   ├── tenant_manager.py   # 租户管理
│   ├── payment_manager.py  # 支付管理
│   ├── generators/         # 数据生成器
│   ├── filters/            # 数据过滤器
│   ├── handlers/           # 请求处理器
│   └── config/             # 配置管理
└── frontend/
    ├── index.html          # 前台页面
    └── admin.html          # 后台页面
```

---

## API接口

### 用户认证

```
POST /api/register     # 注册
POST /api/login        # 登录
POST /api/logout       # 登出
GET  /api/user/info    # 用户信息
```

### 数据生成

```
POST /api/generate     # 生成数据
GET  /api/progress     # 查询进度
GET  /api/download     # 下载数据
```

### 管理后台

```
POST /api/admin/login  # 管理员登录
GET  /api/admin/users  # 用户列表
GET  /api/admin/stats  # 系统统计
```

---

## 配置说明

### 环境变量

创建 `.env` 文件：

```
# 千问API（可选）
QIANWEN_API_KEY=sk-xxx

# Redis缓存（可选）
REDIS_URL=redis://localhost:6379
```

### 依赖安装

```bash
pip install -r requirements.txt
```

---

## 模块测试

运行完整模块测试：

```bash
python test_minimal.py
```

测试覆盖：
- 58个模块通过
- 1个模块跳过（psutil可选依赖）

---

## 更新日志

### v3.13 (2026-02-21)
- 完成全部模块测试（58个模块）
- 修复anti_abuse变量引用问题
- 修复Unicode编码问题
- 清理冗余测试文件

### v3.8 (2026-02-20)
- 新增手机/邮箱验证注册流程
- 优化用户注册体验
- 添加邀请码奖励机制

### v3.7 (2026-02-19)
- 租户隔离系统
- OTP验证码提供商接口

---

## 技术栈

- **后端**: Python 3.10+, HTTPServer
- **前端**: Vue 3, Axios
- **数据库**: SQLite
- **缓存**: Redis (可选)

---

## 许可证

MIT License
