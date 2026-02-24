# 测试文件目录

本目录包含开发和调试过程中创建的测试脚本和临时数据文件。

## 文件说明

### 测试脚本

| 文件 | 用途 |
|------|------|
| check_api.py | API接口检查 |
| check_data.py | 数据检查 |
| check_encoding.py | 编码检查 |
| check_files.py | 文件检查 |
| check_final.py | 最终检查 |
| check_result.py | 结果检查 |
| check_size.py | 大小检查 |
| check_v3.py | V3版本检查 |
| check_v4.py | V4版本检查 |
| test_all_domains.py | 全领域测试 |
| test_api.py | API测试 |
| test_download.py | 下载测试 |
| test_full_download.py | 完整下载测试 |
| test_full_version.py | 完整版本测试 |
| test_generate.py | 生成测试 |
| test_hash.py | 哈希测试 |
| test_keywords.py | 关键词测试 |
| test_login.py | 登录测试 |
| test_login_speed.py | 登录速度测试 |
| test_quality.py | 质量测试 |
| test_quick.py | 快速测试 |
| test_quota.py | 配额测试 |
| test_simple_login.py | 简单登录测试 |
| test_system.py | 系统测试 |
| verify_output.py | 输出验证 |

### 临时数据文件 (temp_files/)

| 文件 | 用途 |
|------|------|
| test_ai.json | AI测试数据 |
| test_download.json | 下载测试数据 |
| test_free.json | 免费测试数据 |
| test_output.json | 输出测试数据 |
| test_small.json | 小规模测试数据 |
| test_wiki.json | Wiki测试数据 |
| ai_fixed.json | AI修复数据 |
| ai_full.json | AI完整数据 |
| ai_test2.json | AI测试数据2 |
| ai_validated.json | AI验证数据 |
| downloaded_data.json | 下载数据 |
| medical.json | 医疗数据 |
| medical_test.json | 医疗测试数据 |
| medical_zh.json | 医疗中文数据 |
| 人工智能_100.json | 人工智能100条数据 |

## 使用方法

```bash
# 运行单个测试
python tests/test_login.py

# 运行快速测试
python tests/test_quick.py
```

## 注意事项

- 这些文件是开发调试过程中创建的临时文件
- 部分测试可能需要配置环境变量或API密钥
- 临时数据文件仅供参考，不应用于生产环境
