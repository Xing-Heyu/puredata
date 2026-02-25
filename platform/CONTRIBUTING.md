# 贡献指南

感谢您考虑为 PureData 做出贡献！

## 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请：

1. 检查是否已有相关issue
2. 创建新issue，包含：
   - 问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息

### 提交代码

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

#### Python 代码

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 函数和变量使用 snake_case
- 类使用 PascalCase
- 添加必要的文档字符串

#### JavaScript 代码

- 使用 2 空格缩进
- 使用 const/let 而非 var
- 函数使用 camelCase

### 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例**:
```
feat(api): 添加批量生成接口

- 支持一次生成10000条数据
- 添加进度查询接口
- 支持断点续传

Closes #123
```

### 测试

提交前请确保：

1. 所有测试通过
```bash
cd platform/backend
python -m pytest test/
```

2. 代码风格检查
```bash
flake8 --max-line-length=120
```

### 目录结构

```
platform/
├── backend/           # 后端代码
│   ├── routes/        # API路由
│   ├── core/          # 核心模块
│   ├── datagenpro/    # 数据生成模块
│   └── test/          # 测试文件
├── frontend/          # 前端代码
├── nginx/             # Nginx配置
└── docker-compose.yml
```

## 开发环境

### 后端

```bash
cd platform/backend
pip install -r requirements.txt
python simple_main.py
```

### 前端

```bash
cd platform/frontend
# 直接用浏览器打开 index.html
```

## 许可证

提交代码即表示您同意您的贡献将根据项目许可证进行授权。
