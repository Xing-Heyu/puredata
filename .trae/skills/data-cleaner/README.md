# 垂直领域训练数据生成系统

开箱即用的训练数据生成工具，帮你快速产出高质量的领域训练语料。

## 做什么的？

一句话：**输入一个领域名称，输出几百上千条结构化的训练数据。**

比如你说"人工智能"，它就自动从免费词典 API 查到 "machine learning"、"deep learning" 等术语的定义，然后套上模板生成各种句式变体：

```json
{ "word": "machine learning", "text": "Machine learning is a subset of AI that enables systems to learn from experience." }
{ "word": "machine learning", "text": "The term machine learning refers to a subset of AI that enables systems to learn from experience." }
{ "word": "deep learning", "text": "Deep learning means a class of ML algorithms using multiple layers to extract features." }
```

## 哪些场景用得上？

| 场景 | 用法 |
|------|------|
| **SFT / 指令微调** | 批量生成领域术语的解释语料，喂给模型做微调 |
| **知识图谱构建** | 按领域生成 `{实体, 定义, 来源}` 三元组 |
| **RAG 知识库** | 快速搭建垂直领域的 FAQ / 词典库 |
| **教育教学** | 生成学科术语表、概念解释卡片 |
| **数据增强** | 已有少量数据时，生成同义变体扩充数据集 |

## 怎么用？

### 1. 列出可用的领域

```bash
python generate.py --list-types
```

输出：
```
可用领域类型:
  - 人工智能: 28 个关键词
  - 劳动合同: 17 个关键词
  - 医疗: 15 个关键词
  - 金融: 15 个关键词
```

### 2. 生成数据

```bash
# 生成 100 条人工智能领域数据，JSON 格式
python generate.py --type 人工智能 --count 100

# 指定输出文件
python generate.py --type 金融 --count 500 --format csv --output finance_data.csv

# 生成文本格式
python generate.py --type 劳动合同 --count 50 --format txt
```

### 3. 查看系统状态

```bash
python generate.py --stats
```

## 工作原理

四层数据来源，自动降级兜底：

```
第一层：免费词典 API（Free Dictionary / Wiktionary）
   ↓ 失败
第二层：LLM API（可选，需自行配 Key，支持千问/DeepSeek/OpenAI 等）
   ↓ 失败或未配置
第三层：智能体辅助（预留扩展接口）
   ↓ 失败
第四层：本地模板生成（100% 可用）
```

- **缓存机制**：查过的定义存入 SQLite，30 天内无需重复请求
- **去重**：MD5 哈希去重，不会产出重复数据
- **并行获取**：ThreadPoolExecutor 并发请求，10 倍加速

> **关于 LLM API**：如果不配置，英文领域靠免费词典已经够用；中文领域建议配一个 Key（千问/DeepSeek 都行），数据质量会明显更好。配置方法见下方"配置 LLM API"。

## 配置 LLM API（可选）

如果你有千问、DeepSeek 或 OpenAI 的 API Key，配一下就能让中文数据质量翻倍。不配也能用，零影响。

### 方式一：环境变量（推荐）

```bash
# Linux / Mac
export LLM_API_KEY="你的Key"
export LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# Windows PowerShell
$env:LLM_API_KEY="你的Key"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
```

### 方式二：.env 文件

```bash
cp .env.example .env
# 编辑 .env，填入你的 Key
```

### 支持的接口

任何 OpenAI 兼容 API 都可以，只需设置 `LLM_BASE_URL`：

| 服务 | base_url |
|------|----------|
| 阿里百炼（千问） | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` |
| OpenAI | `https://api.openai.com/v1/chat/completions` |
| 本地 Ollama | `http://localhost:11434/v1/chat/completions` |

模型名可在 [config.json](config.json) 的 `llm.model` 中修改。

## 自定义领域

打开 [generate.py](generate.py)，找到 `DOMAINS` 字典，按格式添加你的领域：

```python
DOMAINS = {
    "你的领域": {
        "keywords": ["术语1", "术语2", "术语3"],
        "templates": [
            "{word}是指{definition}。",
            "关于{word}，你可以理解为{definition}。",
            "{word}：{definition}"
        ]
    }
}
```

模板变量：`{word}` = 关键词，`{definition}` = 查到的定义，`{domain}` = 领域名。

## 批量生成

批量处理多个领域：

```bash
python batch_generator.py --domains 人工智能,医疗,金融 --count 200
```

或通过配置文件：

```bash
python batch_generator.py --config batch_config.json
```

## 附加功能：数据清洗

`main.py` + `utils/` 提供数据清洗工具，支持去重、去空格、空值处理、日期标准化：

```bash
python main.py -i example.csv -o cleaned.csv -f csv -d -t -n -nd
```

## 依赖

- Python 3.6+
- 纯标准库，零额外依赖
- 免费 API 需要网络连接（失败会自动降级到本地生成）

## 项目结构

```
├── generate.py           # 核心：训练数据生成 CLI
├── main.py               # 数据清洗工具
├── main_v5.py            # v5.0 增强版（模板管理 + 毒性检测）
├── batch_generator.py    # 批量生成器
├── batch_config.json     # 批量生成配置示例
├── config.json           # 全局配置
├── batch_run.py          # 快速批量运行脚本
├── quick_test.py         # 快速测试
├── utils/                # 工具模块
│   ├── cleaner.py        # 数据清洗规则
│   ├── data_generator.py # 数据生成核心
│   ├── dictionary_api.py # 词典 API 封装
│   ├── domain_manager.py # 领域管理
│   ├── input_handler.py  # 输入格式处理
│   ├── output_handler.py # 输出格式处理
│   └── topic_generator.py
├── domains/              # 领域配置文件
├── dicts/                # 字典数据
├── templates/            # 模板文件
├── training_data.json    # 示例输出（5 条 demo）
├── example.csv           # 清洗示例输入
└── cleaned_example.csv   # 清洗示例输出
```

## 许可证

MIT License - 随便用，完全开源。
