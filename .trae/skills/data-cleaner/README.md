# 数据清洗Skill使用指南

本指南将帮助您使用「字典核心+合规清洗」数据清洗Skill，实现高效、合规的数据处理。

## 功能特点

- **极简、零难度**：以字典/字典列表为唯一数据载体，操作简单
- **多格式支持**：支持JSON、CSV、文本文件格式
- **核心清洗功能**：
  - 去重（移除重复记录）
  - 去空格（去除字符串前后空格）
  - 空值处理（统一处理空值）
  - 日期标准化（将不同格式日期转换为ISO 8601格式）
  - 字段筛选（只保留指定字段）
- **合规导向**：不复制原始数据，仅进行加工整理
- **自动运行**：支持命令行调用，可集成到自动化工作流

## 安装要求

- Python 3.6+
- 无额外依赖库，仅使用Python标准库

## 使用方法

### 基本用法

```bash
python main.py -i <输入文件> -o <输出文件> -f <格式> [选项]
```

### 命令行参数

| 参数 | 简写 | 说明 |
|------|------|------|
| --input | -i | 输入文件路径（必填） |
| --output | -o | 输出文件路径（必填） |
| --format | -f | 输入文件格式，可选值：json, csv, txt（必填） |
| --remove-duplicates | -d | 移除重复项 |
| --trim-spaces | -t | 去除空格 |
| --handle-null | -n | 处理空值 |
| --normalize-dates | -nd | 标准化日期格式 |
| --fields | -fs | 指定需要保留的字段列表 |

### 示例

#### 1. 清洗CSV文件（全功能）

```bash
python main.py -i example.csv -o cleaned_example.csv -f csv -d -t -n -nd
```

#### 2. 清洗JSON文件（仅去重和去空格）

```bash
python main.py -i data.json -o cleaned_data.json -f json -d -t
```

#### 3. 清洗文本文件（指定保留字段）

```bash
python main.py -i data.txt -o cleaned_data.txt -f txt -fs name email age
```

## 文件格式说明

### 1. JSON格式

支持标准JSON格式，可处理字典或字典列表：

```json
// 字典格式
{
  "name": "Alice",
  "age": "25",
  "email": "alice@example.com"
}

// 字典列表格式
[
  {
    "name": "Alice",
    "age": "25",
    "email": "alice@example.com"
  },
  {
    "name": "Bob",
    "age": "30",
    "email": "bob@example.com"
  }
]
```

### 2. CSV格式

标准CSV格式，第一行为表头：

```csv
name,age,email
Alice,25,alice@example.com
Bob,30,bob@example.com
```

### 3. 文本格式

每行一条记录，格式为`key1=value1,key2=value2`：

```txt
name=Alice,age=25,email=alice@example.com
name=Bob,age=30,email=bob@example.com
```

## 输出格式

- **JSON**：保持输入的JSON结构，添加`processed_at`字段
- **CSV**：保持CSV格式，添加`processed_at`列
- **文本**：保持文本格式，添加`processed_at=时间戳`字段

## 示例

### 输入示例（CSV）

```csv
name,age,email,date_joined
Alice, 25, alice@example.com,2023-01-01
Bob,30,bob@example.com,2023/02/01
Alice, 25, alice@example.com,2023-01-01
Charlie,,charlie@example.com,2023年03月01日
David,35, david@example.com,2023-04-01 10:30:00
```

### 输出示例（CSV）

```csv
age,date_joined,email,name,processed_at
25,2023-01-01T00:00:00,alice@example.com,Alice,2026-02-17T21:00:24.857137
30,2023-02-01T00:00:00,bob@example.com,Bob,2026-02-17T21:00:24.857475
,2023-03-01T00:00:00,charlie@example.com,Charlie,2026-02-17T21:00:24.857813
35,2023-04-01T10:30:00,david@example.com,David,2026-02-17T21:00:24.857980
```

## 合规说明

- **数据处理原则**：本工具仅对数据进行加工、整理、重构，不复制原始数据
- **保留内容**：仅保留核心字段与结构，输出全新结构化数据
- **适用场景**：符合大厂及各类项目的合规需求

## 集成与扩展

### 集成到自动化工作流

```bash
# 示例：在shell脚本中使用
python /path/to/data-cleaner/main.py -i input.csv -o output.csv -f csv -d -t -n -nd

# 示例：在Python代码中调用
from main import main
import sys

sys.argv = [
    'main.py',
    '-i', 'input.csv',
    '-o', 'output.csv',
    '-f', 'csv',
    '-d', '-t', '-n', '-nd'
]
main()
```

### 功能扩展

如需扩展功能，可修改以下文件：

- `utils/cleaner.py`：添加新的清洗规则
- `utils/input_handler.py`：支持新的输入格式
- `utils/output_handler.py`：支持新的输出格式

## 故障排除

### 常见问题

1. **文件不存在**：确保输入文件路径正确
2. **格式错误**：确保输入文件格式符合要求
3. **编码错误**：确保输入文件使用UTF-8编码

### 错误信息

- `不支持的数据类型`：输入数据不是字典或字典列表
- `不支持的文件格式`：指定的文件格式不受支持
- `文件不存在`：输入文件路径不存在

## 许可证

本项目采用MIT许可证，详见LICENSE文件。