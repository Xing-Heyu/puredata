#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                    PureData 系统使用指南
================================================================================

本文档是 PureData AI训练数据生成平台的完整使用指南。
适用于系统运维人员、管理员和后续接手项目的开发者。

================================================================================
目录
================================================================================

一、系统概述
二、快速启动指南
三、用户管理系统
四、企业用户管理
五、支付与订单管理
六、数据生成操作
七、大规模数据生成指南
八、管理员后台操作
九、API接口文档
十、常见问题处理
十一、添加新领域指南
十二、添加新领域详细指南（开发者专用）
十三、系统维护

================================================================================
"""

"""
================================================================================
一、系统概述
================================================================================

1.1 系统简介
------------
PureData是一个专业的AI训练数据生成平台，主要功能：
- 多领域合成数据生成（人工智能、医疗、金融、劳动合同等）
- 高质量数据审计与过滤
- 用户权限与配额管理
- 企业级用户支持
- 支付与发票管理
- 大规模数据生成（支持百万级，最大1000万条）

1.2 系统架构
------------
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端层                                          │
│  frontend/index.html - 单页应用，包含所有用户界面                            │
│  支持最大1000万条数据生成，自动切换流式下载模式                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              后端服务层                                       │
│  simple_main.py - HTTP服务器入口                                             │
│  routes/ - 路由模块（admin_routes, user_routes, payment_routes等）           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              业务逻辑层                                       │
│  user_system.py - 用户管理、权限控制、配额管理                                │
│  payment_manager.py - 订单管理、支付确认、退款、发票                          │
│  api_key_manager.py - API密钥管理                                            │
│  tenant_manager.py - 多租户管理                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据生成层                                       │
│  high_quality_generator.py - 高质量数据生成器                                │
│  data_quality_pipeline.py - 数据质量流水线（7阶段+学术模块）                  │
│  domain_specialists/ - 领域专精生成器                                        │
│  千问API集成.py - LLM API调用                                                │
│  llm_data_auditor.py - 数据审计系统                                          │
└─────────────────────────────────────────────────────────────────────────────┘

1.3 核心文件清单
----------------
| 文件路径 | 功能说明 |
|----------|----------|
| simple_main.py | 主服务入口，启动HTTP服务器，包含流式生成逻辑 |
| user_system.py | 用户注册、登录、权限、配额管理 |
| payment_manager.py | 订单、支付、退款、发票管理 |
| 管理员认证.py | 管理员登录认证系统 |
| routes/admin_routes.py | 管理员API路由 |
| routes/user_routes.py | 用户API路由 |
| routes/payment_routes.py | 支付相关API路由 |
| routes/generate_routes.py | 数据生成API路由 |
| high_quality_generator.py | 高质量数据生成核心 |
| data_quality_pipeline.py | 数据质量流水线，7阶段处理+学术模块 |
| llm_data_auditor.py | 数据质量审计系统 |

1.4 数据存储文件
----------------
| 文件路径 | 内容说明 |
|----------|----------|
| users.json | 用户数据（账号、配额、权限等） |
| sessions.json | 用户登录会话 |
| orders.json | 订单记录 |
| invoices.json | 发票申请记录 |
| outputs/ | 生成的数据文件存放目录 |
| *.checkpoint | 流式生成断点续传文件 |

================================================================================
二、快速启动指南
================================================================================

2.1 环境要求
------------
- Python 3.9+
- pip 包管理器
- 网络连接（用于LLM API调用）

2.2 安装依赖
------------
cd d:\\skill\\puredata-platform\\platform\\backend
pip install -r requirements.txt

重要依赖：
- bcrypt: 密码加密（必须）
- fastapi/uvicorn: Web框架
- numpy/pandas: 数据处理
- dashscope: 通义千问API

2.3 启动服务器
--------------
方式一：使用启动脚本（Windows）
双击运行 start.bat

方式二：命令行启动
cd d:\\skill\\skill3\\platform\\backend
python simple_main.py

方式三：指定端口启动
python simple_main.py --port 8080

2.4 默认账号
------------
管理员账号：
- 用户名: admin
- 密码: PureData@2026
- 权限: 完全管理权限

首次启动时会自动创建管理员账号。

2.5 访问系统
------------
- 前端界面: http://localhost:8000/
- API文档: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/swagger

================================================================================
三、用户管理系统
================================================================================

3.1 用户角色体系
----------------
系统支持5种用户角色，权限从高到低：

| 角色 | 英文标识 | 日配额 | 月配额 | 可用功能 |
|------|----------|--------|--------|----------|
| 管理员/开发者 | ADMIN/DEVELOPER | 100万 | 1000万 | 全部功能 |
| 专业版 | PREMIUM | 10万 | 100万 | 生成、API、高质量数据 |
| 基础版 | STANDARD | 1万 | 10万 | 生成、API、普通质量 |
| 体验版 | FREE | 100条 | 1000条 | 基础生成、免费质量 |

注：管理员和开发者权限相同，仅名称不同。

3.2 用户注册流程
----------------
1. 用户访问前端注册页面
2. 填写用户名、邮箱、密码
3. 密码要求：至少8位，包含大小写字母和数字
4. 系统自动分配FREE角色
5. 赠送1000条免费配额
6. 可使用邀请码获得额外500条配额

3.3 用户登录流程
----------------
API: POST /api/user/login
请求体: {"username": "xxx", "password": "xxx"}
成功响应: {"success": true, "token": "xxx", "user": {...}}

安全机制：
- 连续5次密码错误，账户锁定30分钟
- 会话有效期1小时
- 使用bcrypt加密存储密码

3.4 配额管理
------------
免费用户：
- 使用free_quota字段记录总配额
- 配额用尽后需升级或购买

付费用户：
- 日配额（daily）和月配额（monthly）独立计算
- 每日0点重置日配额
- 每月1日重置月配额

查看配额状态：
API: GET /api/user/quota
响应: {
    "daily": {"used": 100, "limit": 100000, "remaining": 99900},
    "monthly": {"used": 1000, "limit": 1000000, "remaining": 999000},
    "warning_level": "normal"
}

3.5 邀请奖励机制
----------------
- 每个用户有唯一邀请码
- 被邀请人注册后双方各得500条配额
- 每个用户最多邀请10人

================================================================================
四、企业用户管理
================================================================================

4.1 企业用户套餐
----------------
| 套餐类型 | plan_type | 年配额 | 适用场景 |
|----------|-----------|--------|----------|
| 专业版年付 | pro_yearly | 250万条 | 中型团队 |
| 企业版年付 | enterprise_yearly | 100万条 | 中型企业 |
| 旗舰版年付 | flagship_yearly | 200万条 | 大型企业 |

4.2 创建企业用户（管理员操作）
------------------------------
方式一：通过API创建
POST /api/admin/enterprise/create
请求体: {
    "username": "company_user",
    "password": "Company@123",
    "email": "contact@company.com",
    "company_name": "示例公司",
    "contact_person": "张三",
    "contact_phone": "13800138000",
    "plan_type": "enterprise",  // 或 "flagship" 或 "custom"
    "custom_quota": 1000000,    // 仅custom时需要
    "contract_end": "2026-12-31"
}

方式二：直接修改users.json（不推荐）
在users.json中添加企业用户记录。

4.3 企业用户信息结构
--------------------
{
    "username": "company_user",
    "role": "enterprise",
    "paid_quota": 800000,
    "enterprise_info": {
        "plan_type": "enterprise",
        "plan_name": "企业版",
        "company_name": "示例公司",
        "contact_person": "张三",
        "contact_phone": "13800138000",
        "annual_quota": 800000,
        "contract_end": "2026-12-31"
    }
}

4.4 企业用户业务流程
--------------------
1. 客户通过前端"联系企业版"提交需求
2. 运营人员与客户沟通确认套餐
3. 管理员在后台创建企业用户账号
4. 将账号信息发送给客户
5. 客户登录使用，配额按年度计算

================================================================================
五、支付与订单管理
================================================================================

5.1 套餐定价
------------
| 套餐ID | 名称 | 价格(元) | 配额 | 有效期 |
|--------|------|----------|------|--------|
| starter_monthly | 入门版月付 | 2,999 | 1万 | 30天 |
| basic_monthly | 基础版月付 | 19,999 | 5万 | 30天 |
| pro_monthly | 专业版月付 | 49,999 | 20万 | 30天 |
| pro_yearly | 专业版年付 | 499,990 | 250万 | 365天 |
| enterprise_yearly | 企业版年付 | 799,990 | 100万 | 365天 |
| flagship_yearly | 旗舰版年付 | 1,199,990 | 200万 | 365天 |

按需付费包：
| 包ID | 配额 | 价格(元) | 单价 |
|------|------|----------|------|
| 10k | 1万条 | 3,999 | ¥0.40/条 |
| 50k | 5万条 | 14,999 | ¥0.30/条 |
| 200k | 20万条 | 49,999 | ¥0.25/条 |
| 500k | 50万条 | 99,999 | ¥0.20/条 |
| 800k | 80万条 | 159,999 | ¥0.20/条 |
| 1m | 100万条 | 179,999 | ¥0.18/条 |
| 3m | 300万条 | 499,999 | ¥0.17/条 |

5.2 订单创建流程
----------------
API: POST /api/payment/order
请求体: {
    "plan_id": "pro_monthly",
    "payment_method": "wechat"  // 或 "alipay"
}
响应: {
    "success": true,
    "order_id": "ORD20260224XXXXXX",
    "amount": 49999,
    "payment_url": "/pay/ORD20260224XXXXXX"
}

5.3 支付确认（管理员操作）
--------------------------
当用户完成支付后，管理员需要确认支付：

API: POST /api/admin/payment/confirm
请求体: {
    "order_id": "ORD20260224XXXXXX",
    "transaction_id": "微信/支付宝交易号"
}

确认后系统会：
1. 更新订单状态为"paid"
2. 自动为用户添加配额
3. 可能自动升级用户角色

5.4 退款规则（合成数据特殊规则）
--------------------------------
合成数据服务的特殊性：
- 数据一旦生成下载即视为交付
- 数据可无限复制，无法真正"退货"

退款条件：
- 支付后7天内可申请退款
- 未使用配额：可全额退款
- 使用0-50%配额：按比例退款
- 使用超过50%配额：不支持自助退款，需联系客服

申请退款：
API: POST /api/payment/refund
请求体: {
    "order_id": "ORD20260224XXXXXX",
    "reason": "退款原因"
}

5.5 发票管理
------------
用户申请发票：
API: POST /api/invoice/apply
请求体: {
    "order_id": "ORD20260224XXXXXX",
    "title": "公司名称",
    "tax_id": "税号",
    "address": "地址",
    "phone": "电话",
    "bank": "开户行",
    "bank_account": "账号",
    "email": "接收邮箱"
}

管理员审核发票：
- 查看待审核发票: GET /api/admin/invoices/pending
- 通过审核: POST /api/admin/invoice/approve
- 驳回: POST /api/admin/invoice/reject
- 开具: POST /api/admin/invoice/issue

================================================================================
六、数据生成操作
================================================================================

6.1 支持的领域
--------------
- 人工智能 (ai)
- 医疗 (medical)
- 金融 (finance)
- 劳动合同 (labor)

6.2 数据质量等级
----------------
| 质量等级 | 标识 | 分数范围 | 可用角色 |
|----------|------|----------|----------|
| 高质量 | high_quality | ≥0.85 | 管理员、企业、开发者、高级用户 |
| 免费试用质量 | free_quality | 0.80-0.85 | 所有用户 |
| 普通质量 | medium_quality | 0.75-0.80 | 管理员、企业、开发者、高级、标准用户 |
| 鲁棒性测试质量 | robustness_quality | <0.75 | 管理员、企业、开发者、高级用户 |

6.3 生成数据API（小规模，≤50万条）
----------------------------------
API: POST /api/generate
请求体: {
    "domain": "人工智能",
    "count": 1000,
    "quality_mode": "standard",
    "format": "json"
}

响应: {
    "success": true,
    "task_id": "task_xxxxx",
    "estimated_time": 30,
    "message": "任务已创建"
}

查询任务状态：
API: GET /api/task/{task_id}
响应: {
    "status": "completed",
    "progress": 100,
    "download_url": "/download/xxxxx.json"
}

6.4 大规模生成API（>50万条）
---------------------------
API: POST /api/generate/download
请求体: {
    "domain": "人工智能",
    "count": 1000000,
    "quality_mode": "standard",
    "format": "jsonl"
}

响应: {
    "success": true,
    "task_id": "task_xxxxx",
    "message": "已开始生成 1000000 条数据，完成后可直接下载"
}

特点：
- 流式生成，边生成边写入文件
- 支持断点续传（检查点机制）
- 后台异步处理，不阻塞其他请求
- 自动使用完整质量流水线

6.5 数据格式
------------
支持格式：
- JSON: 标准JSON格式，适合程序处理
- CSV: 表格格式，适合Excel查看
- JSONL: 每行一个JSON，适合大数据处理

6.6 数据下载
------------
API: GET /download/{filename}
响应: 文件下载

数据保留：
- 生成的数据文件保留90天
- 超过90天自动清理

================================================================================
七、大规模数据生成指南
================================================================================

7.1 概述
--------
系统支持百万级数据生成，最大支持1000万条。大规模生成采用流式处理架构，
确保内存占用可控、支持断点续传、保证数据质量。

7.2 流式生成流程
----------------
用户请求 → /api/generate/download → generate_data_streaming()
    → DataQualityPipeline (7阶段处理)
    → HighQualityGenerator (高质量生成)
    → 领域专精器 (专业验证)
    → 数据血缘追踪 (来源记录)
    → 断点续传检查点
    → 流式写入文件

7.3 质量保证模块
----------------
流式生成集成以下质量模块：

| 模块名称 | 功能说明 | 触发条件 |
|----------|----------|----------|
| T²框架 | Team Then Trim质量控制 | 始终启用 |
| 专业验证 | 解决"逻辑通但专业错"问题 | 始终启用 |
| 去重系统 | MinHash LSH去重 | 始终启用 |
| 多样性增强 | GECE长尾检测(ACL2024) | 始终启用 |
| 质量门控 | 四级质量分类 | 始终启用 |
| LLM审计 | 9维度评估(arXiv:2601.17717) | 始终启用 |
| 异常检测 | 基于国家标准 | 始终启用 |
| 数据血缘 | 来源追踪与记录 | 始终启用 |

7.4 学术模块（高级质量模式）
----------------------------
以下模块在quality_mode为"high"或"ultra"时启用：

| 模块名称 | 功能说明 | 触发条件 |
|----------|----------|----------|
| CADS | 对抗合成数据增强 | quality_mode=ultra |
| DASGen | 分布对齐生成 | quality_mode=ultra |
| FAC | 特征覆盖合成 | quality_mode=ultra |
| Failure Recovery | 失败数据回收 | quality_mode=high/ultra |
| Smart Diversity | 智能多样性增强 | quality_mode=high/ultra |
| Calibrated Enhance | 校准增强 | quality_mode=ultra |

7.5 断点续传机制
----------------
流式生成支持断点续传：
- 每批处理完成后自动保存检查点（*.checkpoint文件）
- 任务中断后重启会自动从检查点恢复
- 检查点记录：已生成数量、当前批次、统计信息

7.6 内存优化
------------
流式生成的内存优化策略：
- 分批处理：默认每批1000条
- 边生成边写入：不累积全部数据
- Bloom Filter去重：内存高效
- 及时释放：每批处理完立即释放内存

7.7 性能建议
------------
大规模生成性能建议：
- 单次生成建议不超过500万条
- 超大规模建议分多次生成
- 高质量模式生成速度较慢，建议提前规划时间
- 生成期间避免服务器重启

================================================================================
八、管理员后台操作
================================================================================

8.1 管理员登录
--------------
API: POST /api/admin/login
请求体: {"username": "admin", "password": "PureData@2026"}

管理员使用独立的管理员认证系统，与普通用户分离。

8.2 用户管理
------------
查看所有用户：
GET /api/admin/users

更新用户信息：
POST /api/admin/users/update
请求体: {
    "username": "target_user",
    "updates": {
        "role": "premium",
        "free_quota": 5000
    }
}

删除用户：
POST /api/admin/users/delete
请求体: {"username": "target_user"}

8.3 企业用户管理
----------------
查看企业用户列表：
GET /api/admin/enterprise/list

更新企业用户：
POST /api/admin/enterprise/update
请求体: {
    "username": "company_user",
    "updates": {
        "company_name": "新公司名",
        "contact_person": "李四",
        "contract_end": "2027-12-31"
    }
}

8.4 订单管理
------------
查看所有订单：
GET /api/admin/orders

确认支付：
POST /api/admin/payment/confirm

处理退款申请：
GET /api/admin/refunds/pending
POST /api/admin/refund/approve
POST /api/admin/refund/reject

8.5 系统监控
------------
查看操作日志：
GET /api/admin/logs

查看系统状态：
GET /api/admin/status

================================================================================
九、API接口文档
================================================================================

9.1 认证方式
------------
所有需要认证的API使用Bearer Token方式：
Header: Authorization: Bearer {token}

Token获取：
- 用户登录后从响应中获取
- Token有效期1小时

9.2 通用响应格式
----------------
成功响应：
{
    "success": true,
    "data": {...},
    "message": "操作成功"
}

失败响应：
{
    "success": false,
    "error": "错误描述"
}

9.3 主要API端点
---------------
用户相关：
- POST /api/user/register - 注册
- POST /api/user/login - 登录
- POST /api/user/logout - 登出
- GET /api/user/info - 获取用户信息
- GET /api/user/quota - 获取配额状态
- POST /api/user/change_password - 修改密码

数据生成：
- POST /api/generate - 创建生成任务（≤50万条）
- POST /api/generate/download - 创建大规模生成任务（>50万条）
- GET /api/task/{task_id} - 查询任务状态
- GET /download/{filename} - 下载数据

支付相关：
- POST /api/payment/order - 创建订单
- GET /api/payment/orders - 查看我的订单
- POST /api/payment/refund - 申请退款
- POST /api/invoice/apply - 申请发票

管理员：
- POST /api/admin/login - 管理员登录
- GET /api/admin/users - 用户列表
- POST /api/admin/enterprise/create - 创建企业用户
- GET /api/admin/invoices/pending - 待审核发票

================================================================================
十、常见问题处理
================================================================================

10.1 用户无法登录
-----------------
检查步骤：
1. 确认用户名和密码正确
2. 检查账户是否被锁定（连续5次密码错误）
3. 查看sessions.json是否有残留会话

解锁账户：
管理员调用 POST /api/admin/unlock
{"username": "locked_user"}

10.2 配额显示异常
-----------------
检查步骤：
1. 查看users.json中用户的quota_used字段
2. 检查quota_reset时间是否正确
3. 手动重置配额（修改quota_reset为当前时间）

10.3 数据生成失败
-----------------
可能原因：
1. LLM API调用失败（检查API密钥和网络）
2. 领域配置文件缺失
3. 配额不足

排查方法：
1. 查看服务器日志输出
2. 检查千问API集成.py中的API配置
3. 确认keywords/和domain_configs/目录下有对应领域的配置

10.4 大规模生成中断
-------------------
可能原因：
1. 服务器重启
2. 内存不足
3. 网络超时

处理方法：
1. 检查是否存在.checkpoint文件
2. 重新提交相同请求，系统会自动从检查点恢复
3. 如需重新生成，删除.checkpoint文件后重新提交

10.5 支付确认后配额未增加
-------------------------
检查步骤：
1. 确认订单状态已变为"paid"
2. 检查orders.json中订单的quota_added字段
3. 查看用户记录中的paid_quota字段

手动添加配额：
修改users.json中用户的paid_quota字段

10.6 服务器启动失败
-------------------
常见错误：
1. 端口被占用 - 更换端口或关闭占用进程
2. 依赖缺失 - 运行 pip install -r requirements.txt
3. bcrypt未安装 - pip install bcrypt

================================================================================
十一、添加新领域指南
================================================================================

11.1 必须创建的文件
-------------------
1. keywords/新领域.json
   格式：
   新领域关键词库 - 500个
   关键词1,关键词2,关键词3,关键词4,关键词5
   ...

2. domain_configs/新领域.json
   包含：领域知识、边界定义、术语库

3. domain_templates/新领域.json
   包含：模板、变体、知识映射

11.2 必须修改的文件
-------------------
1. config/templates_config.py
   添加TEMPLATES["新领域"] = [...]
   添加VARIATIONS["新领域"] = [...]
   添加STRUCTURES["新领域"] = [...]

2. domain_validator.py
   添加DOMAIN_TERM_LIBRARIES["新领域"] = {...}

3. config/extended_knowledge_base.py
   添加EXTENDED_KNOWLEDGE["新领域"] = {...}

11.3 可选的高级定制
-------------------
创建领域专精生成器：
domain_specialists/new_domain_specialist.py

================================================================================
十二、添加新领域详细指南（开发者专用）
================================================================================

本文档说明如何为系统添加新的数据生成领域。

当前支持领域：人工智能、医疗、金融、劳动合同、交通驾驶

================================================================================
一、数据生成完整链路
================================================================================

用户请求 → HTTP Handler → generate_data_clean() → 领域配置加载 → 关键词获取 
    → 模板选择 → 数据生成 → 质量过滤 → 去重处理 → 审计系统 → 最终输出

详细调用关系:

┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户请求入口                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  命令行: main.py::main()                                                    │
│      └── simple_main.py::generate_data_clean()                              │
│                                                                             │
│  HTTP: simple_main.py::Handler                                              │
│      └── handlers/generation_handler.py::GenerationHandler                  │
│              └── simple_main.py::generate_data_clean()                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              配置加载层                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  config/domains_config.py::get_keywords()                                   │
│      └── keywords/*.json                                                    │
│                                                                             │
│  domain_config_loader.py::DomainConfigLoader                                │
│      └── domain_configs/*.json                                              │
│                                                                             │
│  domain_templates/__init__.py                                               │
│      └── domain_templates/*.json                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据生成层                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  high_quality_generator.py::HighQualityGenerator                            │
│      ├── KnowledgeBase (内置知识)                                           │
│      ├── 千问API集成.py::QwenAPI                                            │
│      └── 模板兜底                                                           │
│                                                                             │
│  simple_main.py::TopologyGenerator                                          │
│  simple_main.py::RealismEnhancer                                            │
│  simple_main.py::CopulaGenerator                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              质量审计层                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  domain_validator.py::DomainValidator                                       │
│                                                                             │
│  llm_data_auditor.py::LLMDataAuditor                                        │
│      ├── CompletenessEvaluator (完整性)                                     │
│      ├── ConsistencyEvaluator (一致性)                                      │
│      ├── AccuracyEvaluator (准确性)                                         │
│      ├── DiversityEvaluator (多样性)                                        │
│      ├── AuthenticityEvaluator (真实性)                                     │
│      ├── PrivacyEvaluator (隐私安全)                                        │
│      ├── FairnessEvaluator (公平性)                                         │
│      ├── RobustnessEvaluator (鲁棒性)                                       │
│      └── ExplainabilityEvaluator (可解释性)                                 │
│                                                                             │
│  filters/quality_gate.py::QualityGateController                             │
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
二、核心文件清单
================================================================================

按重要性排序:

| 文件 | 功能 | 重要性 |
|------|------|--------|
| simple_main.py | 主入口，核心生成逻辑 | 极高 |
| high_quality_generator.py | 高质量数据生成器，三层知识来源 | 高 |
| 千问API集成.py | API调用和成本控制 | 高 |
| llm_data_auditor.py | 完整审计系统 | 高 |
| domain_config_loader.py | 领域配置加载器 | 高 |
| domain_validator.py | 领域验证器 | 高 |
| filters/quality_gate.py | 质量门控系统 | 中 |
| config/templates_config.py | 模板配置 | 中 |
| domain_templates/__init__.py | 模板系统入口 | 中 |

================================================================================
三、文件结构概览（2026年2月更新）
================================================================================

添加新领域需要修改/创建以下文件：

├── backend/
│   │
│   │  【第一层：核心配置文件 - 必须】
│   ├── keywords/                    # 关键词文件
│   │   └── 新领域.json              ← 必须新建
│   │
│   ├── domain_configs/              # 领域配置
│   │   └── 新领域.json              ← 必须新建
│   │
│   ├── domain_templates/            # 领域模板
│   │   └── 新领域.json              ← 必须新建
│   │
│   │  【第二层：配置入口文件 - 必须】
│   ├── config/
│   │   ├── domains_config.py        ← 必须修改（默认关键词+领域列表）
│   │   ├── templates_config.py      ← 必须修改（添加模板）
│   │   └── extended_knowledge_base.py ← 必须修改（添加知识）
│   │
│   │  【第三层：验证器 - 必须】
│   ├── domain_validator.py          ← 必须修改（添加术语库）
│   ├── filters/
│   │   └── professional_validator.py ← 必须修改（专业知识库）
│   │
│   │  【第四层：生成器 - 必须】
│   ├── simple_main.py               ← 必须修改（模板+关键词+声明）
│   ├── high_quality_generator.py    ← 必须修改（知识定义）
│   │
│   │  【第五层：增强器 - 推荐】
│   ├── generators/
│   │   └── realism_enhancer.py      ← 推荐（语法错误）
│   ├── noise_generator.py           ← 推荐（噪音配置）
│   ├── human_like_generator.py      ← 推荐（拟人化）
│   ├── data_expansion.py            ← 推荐（实体扩展）
│   │
│   │  【第六层：审计器 - 高风险领域必须】
│   ├── multi_angle_auditor.py       ← 高风险必须（审计配置）
│   ├── ai_safety_auditor.py         ← 高风险必须（安全审计）
│   │
│   │  【第七层：专精生成器 - 可选】
│   ├── domain_specialists/
│   │   ├── __init__.py              ← 可选修改
│   │   └── 新领域_specialist.py     ← 可选新建

================================================================================
四、必须修改的文件（10个核心文件）
================================================================================

# ------------------------------------------------------------------------------
# 文件1: keywords/新领域.json
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\keywords\\新领域.json

格式示例:
新领域关键词库 - 500个
关键词1,关键词2,关键词3,关键词4,关键词5
关键词6,关键词7,关键词8,关键词9,关键词10
...

说明:
- 第一行是标题，格式为"领域名关键词库 - N个"
- 从第二行开始，每行5个关键词，用英文逗号分隔
- 建议每个领域准备100-500个关键词

# ------------------------------------------------------------------------------
# 文件2: domain_configs/新领域.json
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\domain_configs\\新领域.json

格式示例:
{
    "domain": "新领域",
    "version": "v1.0",
    "last_update": "2026-02-23",
    "description": "新领域知识库 - 结构化分层配置",
    
    "knowledge": {
        "核心概念": {
            "关键词1": {
                "correct_rules": [
                    "正确规则描述1",
                    "正确规则描述2"
                ],
                "common_errors": {
                    "light": ["轻微错误示例"],
                    "medium": ["中度错误示例"],
                    "severe": ["严重错误示例"]
                },
                "fusion_templates": [
                    "基于{word}的应用场景包括..."
                ]
            }
        }
    },
    
    "domain_border": {
        "core_domain": ["子领域1", "子领域2"],
        "related_domain": ["相关领域1"],
        "irrelevant_domain": ["无关领域1"],
        "border_examples": [
            {
                "keyword": "示例关键词",
                "belongs_to": ["属于场景"],
                "not_belongs_to": ["不属于场景"]
            }
        ]
    },
    
    "term_library": {
        "core_terms": ["核心术语1", "核心术语2"],
        "forbidden_pairs": [
            ["禁止词A", "禁止词B"]
        ]
    }
}

说明:
- knowledge: 领域知识库，按分类组织
- domain_border: 领域边界定义
- term_library: 核心术语和禁止词对
- forbidden_pairs: 防止生成逻辑通但专业错误的内容

# ------------------------------------------------------------------------------
# 文件3: domain_templates/新领域.json
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\domain_templates\\新领域.json

格式示例:
{
    "domain": "新领域",
    "templates": [
        "{word}是新领域的核心技术，应用广泛。",
        "基于{word}的创新方案正在重塑行业。",
        "{word}技术发展迅速，应用场景不断扩展。"
    ],
    "variations": [
        "【新领域知识】{text}",
        "📌 {text}",
        "→ {text}"
    ],
    "structures": [
        "【新领域知识】{base}",
        "Q: 什么是{keyword}? A: {base}"
    ],
    "knowledge": {
        "关键词1": "关键词1的详细定义和说明...",
        "关键词2": "关键词2的详细定义和说明..."
    },
    "keywords": ["关键词1", "关键词2", "关键词3"]
}

占位符说明:
- {word} - 关键词（必须使用！系统只传入word参数）
- {text} - 生成的文本
- {base} - 基础内容
- {keyword} - 关键词
- {index} - 序号

⚠️ 重要警告：
模板必须使用 {word} 占位符！
系统生成数据时调用 template.format(word=keyword)
如果模板使用其他变量名（如{location}、{event}等），格式化会失败并回退到默认模板！

正确示例：
"{word}是智能驾驶系统的重要检测场景。"  ✅

错误示例：
"在{location}行驶时，{event}发生"  ❌ （缺少{word}）

# ------------------------------------------------------------------------------
# 文件4: config/templates_config.py
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\config\\templates_config.py

需要修改的位置:

1. TEMPLATES 字典（约第30行）:
TEMPLATES = {
    # ... 现有领域 ...
    
    "新领域": [
        "{word}是新领域的核心技术，应用广泛。",
        "基于{word}的创新方案正在重塑行业。",
        "{word}技术发展迅速，应用场景不断扩展。",
        "在{word}领域，创新是推动发展的关键动力。",
        "{word}的应用已经渗透到各个行业。",
    ],
}

2. VARIATIONS 字典（约第80行）:
VARIATIONS = {
    # ... 现有领域 ...
    
    "新领域": [
        "【新领域知识】{text}",
        "📌 {text}",
        "→ {text}",
    ] + _DEFAULT_VARIATION_TEMPLATES,
}

3. STRUCTURES 字典（约第130行）:
STRUCTURES = {
    # ... 现有领域 ...
    
    "新领域": [
        "【新领域知识】{base}",
        "Q: 什么是{keyword}? A: {base}",
    ] + _DEFAULT_STRUCTURE_TEMPLATES,
}

# ------------------------------------------------------------------------------
# 文件5: domain_validator.py
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\domain_validator.py

需要修改的位置: DOMAIN_TERM_LIBRARIES 字典（约第20行）

DOMAIN_TERM_LIBRARIES = {
    # ... 现有领域 ...
    
    "新领域": {
        "core_terms": [
            "核心术语1",
            "核心术语2",
            "核心术语3",
        ],
        "forbidden_pairs": [
            ("禁止词A", "禁止词B"),
            ("错误搭配1", "错误搭配2"),
        ],
        "required_density": 0.025
    }
}

说明:
- core_terms: 领域核心术语列表
- forbidden_pairs: 禁止同时出现的词对
- required_density: 核心术语密度要求

# ------------------------------------------------------------------------------
# 文件6: config/extended_knowledge_base.py
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\config\\extended_knowledge_base.py

需要修改的位置: EXTENDED_KNOWLEDGE 字典（约第20行）

EXTENDED_KNOWLEDGE = {
    # ... 现有领域 ...
    
    "新领域": {
        "关键词1": "关键词1的详细定义和说明，可以包含应用场景、技术特点等...",
        "关键词2": "关键词2的详细定义和说明...",
        "关键词3": "关键词3的详细定义和说明...",
        # ... 更多关键词
    }
}

说明:
- 这里的知识会被用于生成更准确的内容
- 每个关键词对应一段详细说明

# ------------------------------------------------------------------------------
# 文件7: filters/professional_validator.py（必须）
# ------------------------------------------------------------------------------
路径: d:\\skill\\puredata-platform\\platform\\backend\\filters\\professional_validator.py

需要修改的位置: 添加领域专业知识库

class DomainKnowledgeBase:
    # 添加新领域的知识库
    NEW_DOMAIN_KNOWLEDGE = {
        "disease_symptom_mapping": {
            "疾病1": ["症状1", "症状2", "症状3"],
            "疾病2": ["症状A", "症状B", "症状C"],
        },
        "forbidden_pairs": [
            ("错误搭配A", "错误搭配B", "原因说明"),
        ],
        "body_part_relations": {
            "部位A": ["相关部位1", "相关部位2"],
        },
        "normal_ranges": {
            "指标1": (最小值, 最大值),
            "指标2": (最小值, 最大值),
        }
    }
    
    @classmethod
    def get_knowledge(cls, domain: str) -> Dict:
        knowledge_map = {
            "医疗": cls.MEDICAL_KNOWLEDGE,
            "金融": cls.FINANCE_KNOWLEDGE,
            "新领域": cls.NEW_DOMAIN_KNOWLEDGE,  # 添加这行
        }
        return knowledge_map.get(domain, {})

说明:
- 用于专业验证，防止生成逻辑通但专业错误的内容
- forbidden_pairs 防止错误搭配（如"感冒"和"手术"同时出现）
- normal_ranges 用于验证数值合理性

# ------------------------------------------------------------------------------
# 文件8: simple_main.py（必须）
# ------------------------------------------------------------------------------
路径: d:\\skill\\puredata-platform\\platform\\backend\\simple_main.py

需要修改的位置:

1. DOMAINS 字典（约第627行）- 添加默认关键词:
default_keywords = {
    # ... 现有领域 ...
    "新领域": ["关键词1", "关键词2", "关键词3", "关键词4"],
}

2. TEMPLATES 字典（约第767行）- 添加生成模板:
TEMPLATES = {
    # ... 现有领域 ...
    "新领域": [
        "{word}是新领域的核心技术，应用广泛。",
        "基于{word}的创新方案正在重塑行业。",
    ],
}

3. VARIATIONS 字典（约第817行）- 添加变体模板:
VARIATIONS = {
    # ... 现有领域 ...
    "新领域": ["【新领域知识】{text}", "📌 {text}"],
}

4. STRUCTURES 字典（约第831行）- 添加结构模板:
STRUCTURES = {
    # ... 现有领域 ...
    "新领域": ["【新领域知识】{base}", "Q: 什么是{keyword}? A: {base}"],
}

5. create_provenance() 函数（约第196行）- 添加领域声明:
domain_disclaimers = {
    # ... 现有领域 ...
    "新领域": "This text is synthetically generated by AI...",
}

# ------------------------------------------------------------------------------
# 文件9: high_quality_generator.py（必须）
# ------------------------------------------------------------------------------
路径: d:\\skill\\puredata-platform\\platform\\backend\\high_quality_generator.py

需要修改的位置: KnowledgeBase.KNOWLEDGE 字典（约第247行）

class KnowledgeBase:
    KNOWLEDGE = {
        # ... 现有领域 ...
        "新领域": {
            "关键词1": "关键词1的详细定义和说明...",
            "关键词2": "关键词2的详细定义和说明...",
            # ... 更多关键词
        }
    }

说明:
- 这是高质量生成器的核心知识库
- 每个关键词需要有详细的定义说明

# ------------------------------------------------------------------------------
# 文件10: config/domains_config.py（必须）
# ------------------------------------------------------------------------------
路径: d:\\skill\\puredata-platform\\platform\\backend\\config\\domains_config.py

需要修改的位置:

1. default_keywords 字典（约第31行）:
default_keywords = {
    # ... 现有领域 ...
    "新领域": ["关键词1", "关键词2", "关键词3"],
}

2. get_available_domains() 函数（约第39行）:
def get_available_domains():
    # ... 或者在返回列表中添加
    return ["人工智能", "劳动合同", "医疗", "金融", "新领域"]

说明:
- 这是关键词懒加载的入口
- 当 keywords/新领域.json 文件不存在时，会使用这里的默认关键词

================================================================================
五、推荐修改的文件（增强功能）
================================================================================

# ------------------------------------------------------------------------------
# 文件11: multi_angle_auditor.py（高风险领域必须）
# ------------------------------------------------------------------------------
路径: d:\\skill\\puredata-platform\\platform\\backend\\multi_angle_auditor.py

需要修改的位置:

1. AUDIT_CONFIGS 字典（约第26行）:
AUDIT_CONFIGS = {
    # ... 现有领域 ...
    "新领域": {
        "prompt_template": "你是一位新领域专家。请审核以下内容...",
        "audit_dimensions": ["safety", "accuracy", "applicability"],
        "risk_level": "high",  # 或 "medium", "low"
    }
}

2. 如果是高风险领域，添加到 HIGH_RISK_DOMAINS（如医疗/金融/法律）

# ------------------------------------------------------------------------------
# 文件12: ai_safety_auditor.py（高风险领域必须）
# ------------------------------------------------------------------------------
路径: d:\\skill\\puredata-platform\\platform\\backend\\ai_safety_auditor.py

需要修改的位置: AUDIT_CONFIGS 字典

AUDIT_CONFIGS = {
    # ... 现有领域 ...
    "新领域": {
        "audit_prompt": "你是一位新领域安全审核专家...",
        "check_items": ["安全风险", "专业准确性", "适用性"],
    }
}

# ------------------------------------------------------------------------------
# 文件13-16: 增强器文件（推荐）
# ------------------------------------------------------------------------------

generators/realism_enhancer.py - GRAMMAR_ERRORS 字典
noise_generator.py - DOMAIN_NOISE_CONFIG 字典
human_like_generator.py - DOMAIN_PREFIXES/DOMAIN_STYLES 字典
data_expansion.py - DOMAIN_ENTITIES/DOMAIN_RELATIONS 字典

================================================================================
六、专精生成器（可选）
================================================================================

# ------------------------------------------------------------------------------
# 文件7: domain_specialists/new_domain_specialist.py（可选）
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\domain_specialists\\new_domain_specialist.py

用途: 创建领域专精生成器，实现更复杂的生成逻辑

模板:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"新领域专精化模块\"\"\"

from .base_specialist import DomainSpecialist
from typing import Dict, List, Any, Optional
import random

class NewDomainSpecialist(DomainSpecialist):
    \"\"\"新领域专精生成器\"\"\"
    
    domain_name = "new_domain"
    domain_display_name = "新领域"
    
    def _load_entities(self) -> Dict[str, List[str]]:
        \"\"\"加载领域实体\"\"\"
        return {
            "实体类型1": ["实体1", "实体2", "实体3"],
            "实体类型2": ["实体A", "实体B", "实体C"],
        }
    
    def _load_relations(self) -> Dict[str, List[str]]:
        \"\"\"加载实体关系\"\"\"
        return {
            "关系类型1": ["关系动词1", "关系动词2"],
            "allowed": ["适用于", "用于", "包含"]
        }
    
    def _load_constraints(self) -> Dict[str, Any]:
        \"\"\"加载约束规则\"\"\"
        return {
            "字段1": {"type": "range", "min": 0, "max": 100},
            "字段2": {"type": "enum", "values": ["值1", "值2"]}
        }
    
    def _load_templates(self) -> Dict[str, List[str]]:
        \"\"\"加载专精模板\"\"\"
        return {
            "模板类型1": [
                "{entity1}与{entity2}的关系描述。",
            ]
        }
    
    def _load_knowledge(self) -> Dict[str, Any]:
        \"\"\"加载领域知识\"\"\"
        return {
            "知识分类": {
                "项目": "描述"
            }
        }
    
    def _generate_single(self, index: int, quality: str) -> Optional[Dict]:
        \"\"\"生成单条数据 - 实现具体生成逻辑\"\"\"
        template = self.templates.get(quality, self.templates.get('default', {}))
        entity = random.choice(self.entities.get('main_entities', ['实体A', '实体B']))
        return {
            "id": f"{self.domain_name}_{index:06d}",
            "domain": self.domain_name,
            "content": f"{entity}相关的{quality}质量数据内容",
            "quality": quality,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "template_used": template.get('name', 'default')
            }
        }
```

# ------------------------------------------------------------------------------
# 文件8: domain_specialists/__init__.py（可选）
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\domain_specialists\\__init__.py

需要添加:
from .new_domain_specialist import NewDomainSpecialist

SPECIALISTS = {
    # ... 现有领域 ...
    "新领域": NewDomainSpecialist,
    "new_domain": NewDomainSpecialist,
}

def list_domains() -> list:
    return ["人工智能", "医疗", "金融", "劳动合同", "新领域"]

# ------------------------------------------------------------------------------
# 文件9: domain/__init__.py（可选）
# ------------------------------------------------------------------------------
路径: d:\\skill\\skill3\\platform\\backend\\domain\\__init__.py

需要添加:
_lazy_modules = {
    # ... 现有领域 ...
    'NewDomainSpecialist': ('.new_domain', 'NewDomainSpecialist'),
}

def get_specialist(domain: str):
    specialists = {
        # ... 现有领域 ...
        "新领域": ".new_domain",
    }

def list_domains():
    return ["人工智能", "医疗", "金融", "劳动合同", "新领域"]

================================================================================
六、快速添加清单（2026年2月更新）
================================================================================

📌 说明：
  【新领域】= 开新领域时必须做
  【改内核】= 变更原有领域内容时需要做（换知识库/模板/验证规则）
  【高风险】= 仅医疗/金融/法律等高风险领域需要

================================================================================

【第一层：核心配置文件 - 必须】
-----------------------------------
□ 1. 创建 keywords/新领域.json              【新领域】
       - 关键词文件，100-500个关键词
       - 改内核时：修改 keywords/原领域.json

□ 2. 创建 domain_configs/新领域.json        【新领域】【改内核】
       - 领域配置：知识、边界、术语
       - 改内核时：修改此文件更换领域知识

□ 3. 创建 domain_templates/新领域.json      【新领域】【改内核】
       - 领域模板
       - 改内核时：修改此文件更换生成模板

【第二层：配置入口文件 - 必须】
-----------------------------------
□ 4. 修改 config/domains_config.py          【新领域】
       - 在 default_keywords 字典中添加新领域的默认关键词
       - 在 get_available_domains() 返回列表中添加领域名
       - 改内核时：不需要修改

□ 5. 修改 config/templates_config.py        【新领域】【改内核】
       - TEMPLATES 字典：添加生成模板
       - VARIATIONS 字典：添加变体模板
       - STRUCTURES 字典：添加结构模板
       - 改内核时：修改对应领域的模板

□ 6. 修改 config/extended_knowledge_base.py 【新领域】【改内核】
       - EXTENDED_KNOWLEDGE 字典：添加领域知识库
       - 改内核时：修改此文件更换核心知识内容

【第三层：验证器 - 必须】
-----------------------------------
□ 7. 修改 domain_validator.py               【新领域】
       - DOMAIN_TERM_LIBRARIES 字典：添加核心术语和禁止词对
       - 改内核时：修改对应领域的术语库

□ 8. 修改 filters/professional_validator.py 【新领域】【改内核】
       - 添加领域专业知识库（如 MEDICAL_KNOWLEDGE、FINANCE_KNOWLEDGE）
       - 在 get_knowledge() 方法中添加领域映射
       - 包含：疾病症状映射、禁止词对、正常值范围等
       - 改内核时：修改对应领域的知识库

【第四层：生成器 - 必须】
-----------------------------------
□ 9. 修改 simple_main.py                    【新领域】【改内核】
       - DOMAINS 字典（约第627行）：添加默认关键词
       - TEMPLATES 字典（约第767行）：添加生成模板
       - VARIATIONS 字典（约第817行）：添加变体模板
       - STRUCTURES 字典（约第831行）：添加结构模板
       - create_provenance() 函数（约第196行）：添加领域定制声明
       - 改内核时：修改对应领域的模板和声明

□ 10. 修改 high_quality_generator.py        【新领域】【改内核】
       - KnowledgeBase.KNOWLEDGE 字典（约第247行）：添加领域知识定义
       - 改内核时：修改此文件更换高质量生成的知识内容

【第五层：增强器 - 推荐】
-----------------------------------
□ 11. 修改 generators/realism_enhancer.py   【可选】
       - GRAMMAR_ERRORS 字典：添加领域特定语法错误

□ 12. 修改 noise_generator.py               【可选】
       - DOMAIN_NOISE_CONFIG 字典：添加领域噪音配置
       - DOMAIN_NOISE_PATTERNS 字典：添加领域噪音模式

□ 13. 修改 human_like_generator.py          【可选】
       - DOMAIN_PREFIXES 字典：添加领域前缀
       - DOMAIN_STYLES 字典：添加领域风格

□ 14. 修改 data_expansion.py                【可选】
       - DOMAIN_ENTITIES 字典：添加领域实体
       - DOMAIN_RELATIONS 字典：添加领域关系

【第六层：审计器 - 高风险领域必须】
-----------------------------------
□ 15. 修改 multi_angle_auditor.py           【新领域】【高风险】
       - AUDIT_CONFIGS 字典：添加审计配置
       - HIGH_RISK_DOMAINS 列表：如医疗/金融/法律需添加

□ 16. 修改 ai_safety_auditor.py             【新领域】【高风险】
       - AUDIT_CONFIGS 字典：添加AI安全审计配置

【第七层：专精生成器 - 可选】
-----------------------------------
□ 17. 创建 domain_specialists/新领域_specialist.py  【可选】
□ 18. 修改 domain_specialists/__init__.py           【可选】

================================================================================
七、场景对照表
================================================================================

场景                          | 需要修改的文件
------------------------------|--------------------------------------------------
开全新领域                    | 第一层~第四层全部 + 第六层（高风险）
变更原有领域的知识内容        | 第2、3、6、8、10项（知识库文件）
变更原有领域的生成模板        | 第3、5、9项（模板文件）
变更原有领域的验证规则        | 第7、8项（验证器文件）
添加高风险领域                | 第一层~第四层 + 第六层
只做简单领域（非高风险）      | 第一层~第四层即可

================================================================================
七、验证方法
================================================================================

def test_new_domain():
    \"\"\"测试新领域是否添加成功\"\"\"
    from domain_specialists import get_specialist, list_domains
    
    print("可用领域:", list_domains())
    
    specialist = get_specialist("新领域")
    if specialist:
        print(f"领域信息: {specialist.get_domain_info()}")
        data = specialist.generate(count=5)
        print(f"生成数据示例: {data[:2]}")
    else:
        print("领域专精器未找到，使用基础生成...")

================================================================================
八、注意事项
================================================================================

1. 领域名称一致性
   - 所有文件中的领域名称必须完全一致
   - 如"人工智能"不要写成"AI"或"ai"

2. 关键词数量
   - 建议每个领域准备100-500个关键词
   - 关键词质量直接影响生成内容质量

3. 禁止词对（forbidden_pairs）
   - 用于防止生成逻辑通但专业错误的内容
   - 例如医疗领域禁止"感冒"和"手术"同时出现

4. 模板占位符
   - {word} - 关键词
   - {text} - 生成的文本
   - {base} - 基础内容
   - {keyword} - 关键词
   - {index} - 序号

5. 热加载支持
   - DomainConfigLoader 支持配置热加载
   - 修改JSON后可调用 reload_config() 方法

6. 高风险领域
   - 医疗、金融、劳动合同、政治 被标记为高风险领域
   - 高风险领域会经过3轮AI审计（安全、准确、适用性）
   - 如需添加新的高风险领域，修改 multi_angle_auditor.py 中的 HIGH_RISK_DOMAINS

================================================================================
九、现有领域参考
================================================================================

可参考现有领域的配置文件:
- 人工智能: keywords/人工智能.json, domain_configs/人工智能.json
- 医疗: keywords/医疗.json, domain_configs/医疗.json
- 金融: keywords/金融.json, domain_configs/金融.json
- 劳动合同: keywords/劳动合同.json, domain_configs/劳动合同.json

================================================================================

================================================================================
十三、2026年2月更新日志
================================================================================

13.1 高级噪音配置功能
--------------------
新增功能：高级订阅用户可自定义噪音参数

文件变更：
- noise_generator.py: 支持 advanced_config 参数
- generate_routes.py: 接收 advanced_noise 参数
- simple_main.py: 传递 advanced_noise 参数
- index.html: 添加高级噪音配置UI面板

功能说明：
- 总体噪音强度：0-100% 滑块调整
- 噪音类型选择：OCR/ASR/拼写/格式/口语化/标点
- 各类型比例微调：单独调整每种噪音占比
- 权限控制：仅 premium/developer/admin 可用

13.2 定时清理功能
----------------
新增功能：每24小时自动清理过期数据

文件变更：
- simple_main.py: 添加 schedule_daily_cleanup() 函数

功能说明：
- 使用 threading.Timer 实现定时清理
- 每24小时执行一次 clean_expired_data()
- 守护线程，不阻塞主程序退出

13.3 缓存优化（2026-02-27更新）
-----------------------------
重要变更：禁用数据缓存，每次生成全新数据

原因：
- 缓存导致相同参数返回相同数据
- 用户期望每次生成都是新数据
- 生成速度已经很快，不需要缓存

文件变更：
- simple_main.py: 删除缓存读取/写入逻辑
- data_cache.py: Lock() 改为 RLock() 修复死锁问题

13.4 多模态数据生成
------------------
新增功能：支持图片和音频生成

新增文件：
- multimodal_converter.py: 多模态转换器

文件变更：
- simple_main.py: 添加 output_type/image_style/voice_id 参数
- index.html: 添加图片/音频生成Tab页面

功能说明：
- 图片生成：支持8种风格（写实/动漫/油画/水彩/3D/极简/赛博朋克/奇幻）
- 音频生成：支持8种中文声线（Cherry/Ethan/Luna/Marcus/Serena/Thea/Alex/Bella）
- 文本来源：缓存优先 > 历史文件 > 临时生成
- 权限控制：free用户不可用

API配置：
- 图片/音频使用 DASHSCOPE_API_KEY（阿里云百炼）
- 配置文件：platform/.env

13.5 多模态数据分开下载（2026-02-27新增）
---------------------------------------
新增功能：生成多模态数据时自动分开保存

文件变更：
- simple_main.py: 添加多文件保存逻辑
- index.html: 显示多个下载按钮

生成文件：
- xxx_人工智能_100.jsonl - 完整数据（含图片/音频URL）
- xxx_人工智能_100_text.jsonl - 纯文本数据
- xxx_images.zip - 图片包（所有图片打包）
- xxx_audio.zip - 音频包（所有音频打包）

前端显示：
- 下载数据 (99条) - 主下载按钮
- 📄 下载纯文本 - 纯文本数据
- 🖼️ 下载图片包 - 图片ZIP包
- 🎵 下载音频包 - 音频ZIP包

13.6 下载功能修复（2026-02-27）
-----------------------------
问题修复：修复多个下载相关问题

修复内容：
1. 死锁问题：data_cache.py 中 Lock() 改为 RLock()
2. 下载无反应：前端改用 fetch + blob 携带 token
3. URL解码不一致：添加解码比较逻辑
4. save_data_in_format 返回值：添加 return filepath
5. _serve_file 缺少 Content-Length：添加 header
6. 历史记录下载：使用 download_url 字段

13.7 历史记录修复（2026-02-27）
-----------------------------
问题修复：历史记录不显示

原因：user_routes.py 返回的是 user.get('tasks_completed', [])
而不是从 tasks 字典获取

修复：修改 user_routes.py 从 tasks 字典获取用户任务

13.8 环境变量加载（2026-02-27新增）
---------------------------------
新增功能：启动时自动加载 .env 文件

文件变更：
- simple_main.py: 添加 .env 文件加载逻辑
- platform/.env: 新建环境变量配置文件

配置内容：
- DASHSCOPE_API_KEY: 阿里云百炼API密钥
- QIANWEN_API_KEY: 千问API密钥
- QIANWEN_MODEL: 模型选择
- SECRET_KEY: JWT密钥

13.9 数据包购买模式
------------------
新增功能：按数据包量计费

文件变更：
- index.html: 添加图片/音频生成界面，显示费用计算

定价：
- 图片：¥1.99/张
- 音频：¥0.19/条

13.10 多模态安全调用（2026-02-27新增）
------------------------------------
重要更新：采用安全调用模式，避免触发风控

文件变更：
- multimodal_converter.py: 添加并发限制和请求间隔
- DashScope安全调用指南.md: 新增安全调用文档

安全配置：
- 图片生成：最大并发3，请求间隔2秒
- 音频生成：最大并发5，请求间隔1秒

风控避免措施：
1. 控制并发数（图片≤3，音频≤5）
2. 请求间隔（图片2秒，音频1秒）
3. 分批处理（每批5-10条）
4. 错误重试（指数退避）
5. 避免高频轮询

详见：DashScope安全调用指南.md

13.11 新增交通驾驶领域（2026-02-27新增）
---------------------------------------
新增功能：交通驾驶场景数据生成

新增文件：
- keywords/交通驾驶.json: 200个驾驶场景关键词
- domain_configs/交通驾驶.json: 领域配置和知识库
- domain_templates/交通驾驶.json: 模板和变体

修改文件：
- config/templates_config.py: 添加交通驾驶模板
- simple_main.py: 添加默认领域

支持场景：
- 突发场景：鬼探头、紧急刹车、山洪泥石流
- 驾驶场景：城市道路、高速公路、山区道路
- 车辆系统：ADAS功能、自动驾驶
- 特殊天气：雨天、雪天、雾天、夜间

使用方式：
1. 选择"交通驾驶"领域
2. 输入关键词（如：鬼探头、紧急刹车）
3. 生成驾驶场景训练数据

================================================================================
十四、API调用文件清单
================================================================================

14.1 外部API调用文件
-------------------
| 文件 | 调用的API | 用途 |
|------|----------|------|
| multimodal_converter.py | OpenAI DALL-E 3 | 图片生成 |
| multimodal_converter.py | Stability AI | 图片生成 |
| multimodal_converter.py | Azure Speech | 音频合成 |
| multimodal_converter.py | ElevenLabs | 声优声线音频 |
| 千问API集成.py | 阿里千问 | 关键词扩展、内容生成 |
| api_key_manager.py | 多个API | API密钥管理 |

14.2 内部API路由文件
-------------------
| 文件 | 路由 | 用途 |
|------|------|------|
| simple_main.py | /generate | 数据生成 |
| simple_main.py | /download/* | 文件下载 |
| simple_main.py | /api/user/* | 用户信息 |
| routes/generate_routes.py | /generate | 生成路由（备用） |
| routes/analytics_routes.py | /api/analytics/* | 数据分析 |
| routes/auth_routes.py | /api/auth/* | 认证相关 |

================================================================================
十五、推荐API提供商（性价比排行）
================================================================================

15.1 图片生成API性价比排行
-------------------------
| 排名 | 提供商 | 单价 | 质量 | 速度 | 推荐指数 |
|------|--------|------|------|------|----------|
| 1 | Stability AI | $0.002/张 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 2 | 阿里通义万相 | ¥0.08/张 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 3 | OpenAI DALL-E 3 | $0.04/张 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 4 | 百度文心一格 | ¥0.1/张 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

推荐理由：
- Stability AI：性价比最高，支持负面提示词，适合批量生成
- 通义万相：国内服务，中文理解好，速度快
- DALL-E 3：质量最高，适合高端需求

15.2 音频生成API性价比排行
-------------------------
| 排名 | 提供商 | 单价 | 声线数 | 质量 | 推荐指数 |
|------|--------|------|--------|------|----------|
| 1 | Azure Speech | $4/100万字符 | 18+中文 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 2 | 讯飞语音 | ¥20/100万字符 | 10+中文 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 3 | ElevenLabs | $5/100万字符 | 声优克隆 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 4 | 火山引擎TTS | ¥15/100万字符 | 8+中文 | ⭐⭐⭐ | ⭐⭐⭐ |

推荐理由：
- Azure Speech：性价比最高，声线丰富，稳定可靠
- 讯飞语音：国内服务，中文效果好
- ElevenLabs：声优声线，适合高端需求

15.3 文本生成API性价比排行
-------------------------
| 排名 | 提供商 | 单价 | 质量 | 速度 | 推荐指数 |
|------|--------|------|------|------|----------|
| 1 | 阿里千问 | ¥0.008/千token | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 2 | 智谱GLM | ¥0.01/千token | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 3 | 百度文心 | ¥0.012/千token | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 4 | OpenAI GPT | $0.0015/千token | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

推荐理由：
- 千问：性价比最高，中文理解好，国内服务
- GLM：开源模型，可私有部署
- GPT：质量最高，但国内访问受限

15.4 官网链接
------------
图片生成：
- Stability AI: https://stability.ai
- OpenAI DALL-E: https://openai.com/dall-e-3
- 阿里通义万相: https://tongyi.aliyun.com/wanxiang
- 百度文心一格: https://yige.baidu.com

音频生成：
- Azure Speech: https://azure.microsoft.com/zh-cn/services/cognitive-services/speech-services
- ElevenLabs: https://elevenlabs.io
- 讯飞语音: https://www.xfyun.cn/services/online_tts
- 火山引擎TTS: https://www.volcengine.com/products/tts

文本生成：
- 阿里千问: https://tongyi.aliyun.com
- 智谱GLM: https://open.bigmodel.cn
- 百度文心: https://yiyan.baidu.com
- OpenAI: https://openai.com

================================================================================
十六、系统维护
================================================================================

12.1 日常维护任务
-----------------
- 每日检查服务器运行状态
- 每周清理过期数据文件（自动）
- 每月检查用户配额使用情况
- 定期备份users.json和orders.json

12.2 数据备份
-------------
重要文件需定期备份：
- users.json
- orders.json
- invoices.json
- sessions.json

备份命令示例：
copy users.json users_backup_20260224.json

12.3 日志查看
-------------
服务器日志输出到控制台，建议：
- 使用重定向保存日志：python simple_main.py >> server.log 2>&1
- 定期查看日志排查问题

12.4 性能优化
-------------
- 大批量数据生成建议分批进行
- 定期清理outputs/目录下的旧文件
- 高并发场景考虑使用Redis缓存

12.5 安全建议
-------------
- 定期更换管理员密码
- 不要将users.json暴露在公网
- API密钥不要提交到代码仓库
- 生产环境使用HTTPS

================================================================================
联系方式
================================================================================

如有问题，请联系系统开发者。

================================================================================
"""

if __name__ == "__main__":
    print(__doc__)
