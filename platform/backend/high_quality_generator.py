#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量数据生成器 - 完整版

核心功能:
1. 三层知识来源 (内置知识库 -> 千问API -> 模板兜底)
2. 成本控制 (预算限制 + 缓存 + 降级策略)
3. 专业验证 (领域约束 + 质量评分)
4. 质量流水线集成 (可选)

依赖:
- 千问API集成.py: QwenAPI, CostConfig, CostController, ResponseCache, HybridDataGenerator
"""

import os
import sys
import json
import time
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from quality import ProfessionalValidator, ProfessionalEnhancer
    from filters.professional_validator import professional_validator
    VALIDATOR_AVAILABLE = True
except ImportError:
    try:
        from filters.professional_validator import (
            ProfessionalValidator, ProfessionalEnhancer, professional_validator
        )
        VALIDATOR_AVAILABLE = True
    except ImportError:
        VALIDATOR_AVAILABLE = False

try:
    from quality import DataQualityPipeline, PipelineConfig
    PIPELINE_AVAILABLE = True
except ImportError:
    try:
        from data_quality_pipeline import DataQualityPipeline, PipelineConfig
        PIPELINE_AVAILABLE = True
    except ImportError:
        PIPELINE_AVAILABLE = False

try:
    from api.llm import QwenAPI, CostController, CostConfig
    QWEN_API_AVAILABLE = True
except ImportError:
    try:
        from 千问API集成 import QwenAPI, CostConfig, CostController, ResponseCache, HybridDataGenerator
        QWEN_API_AVAILABLE = True
    except ImportError:
        QWEN_API_AVAILABLE = False
        print("[警告] 千问API集成.py 不可用，API生成功能将禁用")


@dataclass
class GeneratedItem:
    """生成数据项"""
    id: int
    word: str
    text: str
    category: str
    quality_score: float
    source: str
    metadata: Dict


HIGH_QUALITY_EXAMPLES = {
    "医疗": """【高血压】定义与诊疗规范

高血压是指以体循环动脉血压持续升高为主要特征的临床综合征。诊断标准：收缩压≥140mmHg和/或舒张压≥90mmHg。

分类：
- 原发性高血压：病因不明，占95%以上
- 继发性高血压：由其他疾病引起

治疗原则：
1. 非药物治疗：生活方式干预（限盐、减重、运动）
2. 药物治疗：钙通道阻滞剂、ACEI/ARB、利尿剂等""",

    "金融": """【市盈率】估值指标分析

市盈率(PE) = 股价 / 每股收益，反映投资者为每1元净利润支付的价格。

计算方法：
- 静态PE：当前股价 / 上年度EPS
- 动态PE：当前股价 / 预测EPS

应用场景：
- PE<15：可能被低估
- PE 15-25：估值合理
- PE>25：可能被高估""",

    "法律": """【劳动合同解除】法律规范

劳动合同解除是指劳动合同当事人在合同期限届满前终止劳动合同关系的法律行为。

法定解除情形：
一、劳动者单方解除：提前30日书面通知
二、用人单位单方解除：过失性辞退、非过失性辞退、经济性裁员

经济补偿标准：每满一年支付一个月工资""",

    "人工智能": """【Transformer架构】技术解析

Transformer是一种基于自注意力机制的神经网络架构。

核心组件：
1. 自注意力机制：Query、Key、Value三个向量
2. 多头注意力：并行计算多组注意力
3. 位置编码：补充序列位置信息

优势：并行计算能力强、长距离依赖建模能力好""",

    "教育": """【建构主义学习理论】教育理论解析

建构主义学习理论认为学习是学习者主动建构知识的过程。

核心观点：
1. 学习是主动建构而非被动接受
2. 知识是个体经验的产物
3. 学习需要社会互动

教学应用：支架式教学、抛锚式教学、随机进入教学""",

    "电商": """【用户行为分析】电商数据分析

用户行为分析是电商运营的核心环节，用于理解用户需求和优化运营策略。

关键指标：
1. 转化率：访客转化为购买者的比例
2. 客单价：平均每笔订单金额
3. 复购率：重复购买用户比例

分析方法：漏斗分析、路径分析、RFM模型""",

    "科技": """【微服务架构】技术架构解析

微服务架构是一种将应用拆分为多个小型服务的架构风格。

核心特点：
1. 服务独立部署和扩展
2. 去中心化数据管理
3. 容错设计

优势：技术栈灵活、独立扩展、故障隔离""",

    "劳动合同": """【劳动合同期限】法律规范

劳动合同期限是劳动合同的必备条款，分为固定期限、无固定期限和以完成一定工作任务为期限。

类型：
1. 固定期限：约定明确的终止时间
2. 无固定期限：约定无确定终止时间
3. 任务期限：以完成工作任务为期限

试用期规定：合同期限3个月以上不满1年的，试用期不得超过1个月"""
}

DOMAIN_PROFESSIONAL_CONSTRAINTS = {
    "医疗": """
【专业约束 - 必须遵守】
1. 症状与疾病必须正确对应：
   - 高血压 → 头痛、头晕、心悸 ✓
   - 腰椎间盘突出 → 腰痛、下肢麻木 ✓
   - 腰椎间盘突出 → 头痛 ✗ (错误！)
2. 数值必须在正常范围内：
   - 体温：36.0-37.3℃
   - 脉搏：60-100次/分
   - 血压：90-139/60-89mmHg
3. 禁止跨界乱连不相关的疾病和症状""",
    
    "金融": """
【专业约束 - 必须遵守】
1. 概念不能混淆：
   - 股票 → 股息 ✓，存款利率 ✗
   - 债券 → 利息 ✓，股息 ✗
2. 风险等级要准确：
   - 国债：低风险
   - 股票基金：中高风险
   - 期货：高风险""",
    
    "人工智能": """
【专业约束 - 必须遵守】
1. 技术应用要准确：
   - CNN → 图像处理 ✓，时序预测 ✗
   - LSTM → 时序预测 ✓
   - K-means → 无监督聚类 ✓，标签预测 ✗
2. 概念关系要正确"""
}


class KnowledgeBase:
    """领域知识库 - 提供真实知识支撑"""
    
    KNOWLEDGE = {
        "金融": {
            "投资": "投资是指将资金投入到各种资产中，以期获得未来收益的经济行为。主要包括股票投资、债券投资、基金投资、房地产投资等形式。投资的核心在于风险与收益的平衡，投资者需要根据自身风险承受能力和投资目标选择合适的投资品种。",
            "理财": "理财是指对个人或家庭的财务进行科学管理，包括收入管理、支出规划、投资配置、风险保障等方面。现代理财强调资产配置的多元化，通过合理的财务规划实现财富保值增值。",
            "贷款": "贷款是金融机构向借款人提供资金，借款人按约定利率和期限偿还本金的信用行为。主要类型包括个人消费贷款、住房贷款、经营贷款等。贷款利率受市场利率、信用评级等因素影响。",
            "保险": "保险是一种风险转移机制，投保人支付保费，保险人承担约定风险造成的经济损失。主要类型有人寿保险、财产保险、健康保险等。保险是现代金融体系的重要组成部分。",
            "股票": "股票是股份公司发行的所有权凭证，代表股东对公司的部分所有权。股票投资具有高风险高收益特征，价格受公司业绩、市场环境、政策法规等多重因素影响。",
            "基金": "基金是一种集合投资工具，由专业管理人运作，投资者按份额享有收益。主要类型包括股票型基金、债券型基金、混合型基金、货币市场基金等。",
            "债券": "债券是政府、企业等发行的债务凭证，承诺按期支付利息并到期偿还本金。债券投资相对稳健，收益率通常低于股票但风险也较低。",
            "期货": "期货是标准化的远期合约，约定在未来特定时间以特定价格买卖特定资产。期货交易具有杠杆效应，风险较高，主要用于套期保值和投机交易。",
            "外汇": "外汇是指外国货币及以外币表示的支付手段。外汇交易是全球最大的金融市场，日均交易量超过6万亿美元。汇率受经济数据、政治事件、央行政策等影响。",
            "风控": "风控即风险控制，是金融机构识别、评估、监控和控制风险的过程。现代风控体系包括信用风险、市场风险、操作风险等多个维度，运用大数据和AI技术提升风控效率。",
            "征信": "征信是指依法收集、整理、保存、加工自然人、法人及其他组织的信用信息，并提供信用报告、信用评分等服务的活动。征信体系是现代金融基础设施的重要组成部分。",
            "支付": "支付是货币债权转移的过程，现代支付体系包括现金支付、银行卡支付、移动支付、数字货币等多种形式。支付清算系统是金融市场的核心基础设施。",
            "结算": "结算是交易双方完成资金转移的过程，包括实时全额结算、净额结算等方式。高效的结算系统对金融市场稳定运行至关重要。",
            "融资": "融资是企业或个人获取资金的行为，包括股权融资、债权融资、混合融资等方式。融资渠道的选择影响企业资本结构和经营成本。",
            "上市": "上市是指公司股票在证券交易所公开交易的过程。上市可以为企业筹集资金、提升知名度，但也需要履行信息披露等义务。",
            "并购": "并购是企业兼并和收购的统称，是企业扩张和重组的重要方式。并购交易需要考虑估值、融资、整合等多个环节。",
            "资产管理": "资产管理是专业机构受托管理客户资产，实现资产保值增值的业务。包括公募基金、私募基金、银行理财、信托等多种形式。",
            "量化交易": "量化交易是利用数学模型和计算机程序进行投资决策的交易方式。具有纪律性强、反应速度快、可回测验证等特点。",
            "区块链": "区块链是一种分布式账本技术，具有去中心化、不可篡改、可追溯等特点。在金融领域应用于数字货币、供应链金融、跨境支付等场景。",
            "数字货币": "数字货币是以数字形式存在的货币，包括央行数字货币和加密货币。具有交易便捷、可编程等特点，是金融科技发展的重要方向。",
        },
        "人工智能": {
            "机器学习": "机器学习是人工智能的核心分支，通过算法让计算机从数据中学习规律，无需显式编程即可完成预测和决策任务。主要方法包括监督学习、无监督学习和强化学习。",
            "深度学习": "深度学习是机器学习的子领域，使用多层神经网络学习数据的层次化表示。在图像识别、语音处理、自然语言理解等领域取得突破性进展。",
            "神经网络": "神经网络是模拟生物神经系统的计算模型，由大量互联的节点组成。深度神经网络能够学习复杂的非线性映射关系。",
            "自然语言处理": "自然语言处理是让计算机理解和生成人类语言的技术，包括文本分类、情感分析、机器翻译、问答系统等任务。大语言模型的出现带来革命性突破。",
            "计算机视觉": "计算机视觉是让计算机理解和处理图像视频的技术，包括图像分类、目标检测、图像分割、人脸识别等应用。深度学习极大提升了视觉任务性能。",
            "大模型": "大模型是参数规模巨大的深度学习模型，通常指参数量在数十亿以上的语言模型。具有强大的语言理解和生成能力，是当前AI发展的核心方向。",
            "GPT": "GPT(Generative Pre-trained Transformer)是一种基于Transformer的生成式预训练模型，通过大规模无监督学习获得语言能力，可应用于对话、写作、编程等多种任务。",
            "Transformer": "Transformer是一种基于自注意力机制的神经网络架构，具有并行计算能力强、长距离依赖建模能力好的特点，是现代大语言模型的基础架构。",
            "注意力机制": "注意力机制让模型能够关注输入的不同部分，是Transformer的核心创新。自注意力机制能够捕捉序列内部的依赖关系。",
            "强化学习": "强化学习是智能体通过与环境交互学习最优策略的机器学习方法。在游戏AI、机器人控制、推荐系统等领域有广泛应用。",
            "知识图谱": "知识图谱是以图结构表示知识的系统，由实体、关系和属性组成。能够支持知识推理和问答，是AI认知能力的重要基础。",
            "图像识别": "图像识别是让计算机识别图像中物体或场景的技术，基于卷积神经网络等方法实现。广泛应用于安防监控、医疗诊断、自动驾驶等领域。",
            "语音识别": "语音识别是将语音信号转换为文本的技术，是人机交互的重要方式。深度学习使语音识别准确率大幅提升。",
            "推荐系统": "推荐系统是根据用户偏好推荐物品的系统，广泛应用于电商、视频、音乐等平台。主要方法包括协同过滤、内容过滤和混合推荐。",
            "迁移学习": "迁移学习是将一个领域的知识迁移到另一个领域的学习方法，能够解决数据稀缺问题，提高模型训练效率。",
            "联邦学习": "联邦学习是一种分布式机器学习方法，数据不出本地，只交换模型参数。能够保护数据隐私，适用于金融、医疗等敏感领域。",
            "模型蒸馏": "模型蒸馏是将大型模型的知识迁移到小型模型的技术，能够在保持性能的同时降低模型复杂度，适合边缘部署。",
            "对抗训练": "对抗训练是通过对抗样本增强模型鲁棒性的训练方法，在图像分类、文本分类等任务中广泛应用。",
            "预训练": "预训练是在大规模数据上训练模型的过程，使模型获得通用知识。预训练模型可以通过微调适应下游任务。",
            "微调": "微调是在预训练模型基础上，使用特定任务数据进行训练的过程。能够使通用模型适应特定领域需求。",
        },
        "医疗": {
            "诊断": "诊断是医生根据患者症状、体征和检查结果判断疾病的过程。现代诊断技术包括影像诊断、实验室检验、基因检测等多种手段。",
            "治疗": "治疗是消除疾病、缓解症状、恢复健康的医疗行为。主要方式包括药物治疗、手术治疗、物理治疗、心理治疗等。",
            "药物": "药物是用于预防、治疗、诊断疾病的化学物质或生物制品。药物研发需要经过严格的临床前研究和临床试验。",
            "手术": "手术是外科治疗的主要手段，通过操作器械治疗疾病。现代手术技术包括微创手术、机器人手术等先进方法。",
            "康复": "康复是帮助患者恢复功能、提高生活质量的过程。包括物理治疗、作业治疗、言语治疗等多种手段。",
            "疫苗": "疫苗是预防传染病的生物制品，通过刺激机体产生免疫保护。疫苗研发需要严格的临床试验验证安全性和有效性。",
            "病历": "病历是记录患者诊疗过程的医疗文书，包括病史、检查、诊断、治疗等信息。电子病历系统提高了医疗信息化水平。",
            "处方": "处方是医生开具的用药指导，包括药品名称、剂量、用法等信息。合理用药是保障医疗安全的重要环节。",
            "影像": "医学影像是通过各种技术获取人体内部图像的诊断方法，包括X光、CT、MRI、超声等。影像诊断是现代医学的重要支柱。",
            "检验": "医学检验是通过实验室方法检测人体样本的过程，包括血液检验、生化检验、免疫检验等。检验结果为诊断提供客观依据。",
            "护理": "护理是协助患者康复、维护健康的医疗活动。护理工作包括病情观察、治疗配合、健康指导等内容。",
            "急诊": "急诊是处理急性疾病和创伤的医疗服务，要求快速诊断和及时治疗。急诊科是医院的重要科室。",
            "门诊": "门诊是医院提供非住院医疗服务的诊疗形式。门诊服务包括初诊、复诊、专科门诊等多种类型。",
            "住院": "住院是患者入住医院接受系统治疗的医疗形式。住院患者需要办理入院手续，接受全程医疗服务。",
            "医保": "医保是为参保人员提供医疗费用保障的社会保险制度。医保政策影响医疗服务可及性和医疗费用负担。",
        },
        "劳动合同": {
            "劳动合同": "劳动合同是劳动者与用人单位确立劳动关系、明确双方权利义务的协议。劳动合同应当以书面形式订立，包含工作内容、劳动报酬、工作时间等必备条款。",
            "试用期": "试用期是用人单位和劳动者相互考察的期限。试用期最长不得超过六个月，工资不得低于转正后工资的80%。",
            "工资": "工资是用人单位支付给劳动者的劳动报酬。工资应当以货币形式按月支付，不得克扣或无故拖欠。",
            "社保": "社保即社会保险，包括养老保险、医疗保险、失业保险、工伤保险和生育保险。用人单位和劳动者应当依法缴纳社会保险费。",
            "加班": "加班是劳动者在法定工作时间之外工作。用人单位安排加班应当支付加班费，平日加班支付150%工资，休息日加班支付200%工资。",
            "休假": "休假是劳动者依法享有的休息时间，包括法定节假日、年休假、婚假、产假等。劳动者在休假期间享有工资待遇。",
            "离职": "离职是劳动者与用人单位解除劳动关系的行为。劳动者提前三十日书面通知用人单位可以解除劳动合同。",
            "竞业协议": "竞业协议是劳动者承诺在离职后一定期限内不从事与原单位有竞争关系的工作。竞业限制期限不得超过两年，用人单位应当支付经济补偿。",
            "经济补偿": "经济补偿是用人单位依法向劳动者支付的补偿金。在特定情形下解除劳动合同，用人单位应当支付经济补偿。",
            "工伤": "工伤是劳动者在工作时间和工作场所内因工作原因受到的事故伤害。工伤认定后，劳动者享有工伤保险待遇。",
            "劳动仲裁": "劳动仲裁是解决劳动争议的法律程序。劳动争议发生后，当事人可以向劳动争议仲裁委员会申请仲裁。",
            "劳动合同解除": "劳动合同解除是提前终止劳动合同效力的行为。包括协商解除、劳动者单方解除、用人单位单方解除等情形。",
            "劳动合同终止": "劳动合同终止是劳动合同因法定事由而失效。包括合同期满、劳动者退休、用人单位主体资格消灭等情形。",
            "保密协议": "保密协议是劳动者承诺保守用人单位商业秘密的协议。劳动者违反保密协议应当承担违约责任。",
            "培训协议": "培训协议是用人单位为劳动者提供专项培训，劳动者承诺服务期限的协议。劳动者违反服务期约定应当支付违约金。",
        },
        "旅游": {
            "旅游": "旅游是人们离开常住地前往其他地方进行休闲、观光、度假等活动的总称。现代旅游业已成为重要的经济产业，涵盖交通、住宿、餐饮、景点等多个领域。",
            "景点": "景点是具有观赏价值或文化内涵的旅游目的地，包括自然景观和人文景观。优质景点是吸引游客的核心资源，需要合理开发和保护。",
            "酒店": "酒店是为旅客提供住宿服务的商业场所，按星级可分为一星至五星。现代酒店业注重服务品质和个性化体验，满足不同层次旅客需求。",
            "导游": "导游是为游客提供讲解、引导服务的专业人员。优秀导游需要具备丰富的知识储备、良好的沟通能力和服务意识。",
            "旅行社": "旅行社是为游客提供旅游服务的中介机构，负责行程安排、票务预订、签证办理等业务。选择正规旅行社是保障旅游质量的重要因素。",
            "签证": "签证是一国政府授权机关为外国人入境、过境签发的许可证明。签证类型包括旅游签证、商务签证、工作签证等，申请需提供相关材料。",
            "机票": "机票是旅客乘坐飞机的凭证，分为电子客票和纸质客票。机票价格受季节、舱位、提前预订时间等因素影响。",
            "民宿": "民宿是利用当地住宅资源为游客提供住宿服务的经营形式。民宿具有地方特色浓厚、价格亲民等特点，深受年轻游客喜爱。",
            "自驾游": "自驾游是游客自行驾驶车辆进行旅游的方式，具有灵活自由、可深入体验等特点。自驾游需要做好路线规划和安全准备。",
            "跟团游": "跟团游是参加旅行社组织的团队旅游活动，由导游统一带领。跟团游省心省力，适合缺乏旅游经验或时间紧张的游客。",
            "自由行": "自由行是游客自主安排行程的旅游方式，具有高度自主性。自由行需要游客具备一定的规划能力和目的地了解。",
            "旅游保险": "旅游保险是为游客提供旅途风险保障的保险产品，包括意外伤害、医疗费用、行李丢失等保障。购买旅游保险是出行的重要准备。",
            "旅游攻略": "旅游攻略是游客分享的旅游经验和建议，包括路线、住宿、美食、注意事项等内容。攻略是规划行程的重要参考。",
            "黄金周": "黄金周是指国庆、春节等长假期间，是旅游高峰期。黄金周期间景区游客众多，需要提前预订和合理规划。",
            "出境游": "出境游是前往国外或港澳台地区的旅游活动。出境游需要办理护照、签证等证件，了解目的地文化和法规。",
            "入境游": "入境游是外国游客来国内旅游的活动。发展入境游对于促进文化交流和经济增长具有重要意义。",
            "生态旅游": "生态旅游是以自然环境和生态资源为基础的旅游形式，强调环境保护和可持续发展。生态旅游是旅游业发展的重要方向。",
            "文化旅游": "文化旅游是以文化资源为核心的旅游活动，包括历史遗迹、民俗风情、艺术表演等内容。文化旅游能够促进文化传承和交流。",
            "度假村": "度假村是集住宿、餐饮、娱乐于一体的综合性旅游度假场所。度假村通常位于风景优美的地区，提供一站式休闲体验。",
            "景区门票": "景区门票是进入景点游览的凭证，价格因景区等级和淡旺季而异。部分景区实行预约制，需提前购票。",
        }
    }
    
    @classmethod
    def get_definition(cls, keyword: str, domain: str) -> Optional[str]:
        """获取关键词定义"""
        domain_knowledge = cls.KNOWLEDGE.get(domain, {})
        
        if keyword in domain_knowledge:
            return domain_knowledge[keyword]
        
        for k, v in domain_knowledge.items():
            if keyword in k or k in keyword:
                return v
        
        return None
    
    @classmethod
    def get_related_keywords(cls, keyword: str, domain: str, count: int = 3) -> List[str]:
        """获取相关关键词"""
        domain_knowledge = cls.KNOWLEDGE.get(domain, {})
        keywords = list(domain_knowledge.keys())
        
        if keyword in keywords:
            idx = keywords.index(keyword)
            related = []
            if idx > 0:
                related.append(keywords[idx - 1])
            if idx < len(keywords) - 1:
                related.append(keywords[idx + 1])
            return related[:count]
        
        return random.sample(keywords, min(count, len(keywords)))


class HighQualityGenerator:
    """高质量数据生成器 - 完整版
    
    使用千问API集成.py中的QwenAPI进行API调用
    """
    
    def __init__(self, use_api: bool = True, use_pipeline: bool = True, use_validator: bool = True,
                 api_config: CostConfig = None):
        self.use_api = use_api and QWEN_API_AVAILABLE
        self.api_config = api_config
        
        if self.use_api:
            self.api = QwenAPI(config=api_config or CostConfig())
        else:
            self.api = None
        
        self.use_pipeline = use_pipeline and PIPELINE_AVAILABLE
        self.use_validator = use_validator and VALIDATOR_AVAILABLE
        
        if self.use_validator:
            self.validator = professional_validator
        else:
            self.validator = None
        
        if self.use_pipeline:
            self.pipeline = DataQualityPipeline(PipelineConfig(verbose=False))
        else:
            self.pipeline = None
        
        self.stats = {
            "api_calls": 0,
            "cache_hits": 0,
            "knowledge_used": 0,
            "total_generated": 0,
            "total_passed": 0,
            "total_failed": 0,
            "fallback_used": 0,
        }
    
    def generate_single(self, keyword: str, domain: str, index: int) -> Optional[GeneratedItem]:
        """生成单条高质量数据"""
        
        definition = None
        source = "knowledge_base"
        
        definition = KnowledgeBase.get_definition(keyword, domain)
        
        if definition:
            self.stats["knowledge_used"] += 1
        
        if not definition and self.use_api and self.api:
            result = self.api.call(
                prompt=f"""请用专业、准确的语言解释{domain}领域中"{keyword}"的概念。

要求:
1. 定义准确，符合专业标准
2. 包含核心特征和关键要点
3. 字数控制在50-150字
4. 语言简洁流畅
5. 只输出解释内容，不要其他说明

解释:""",
                max_tokens=300
            )
            if result.get("success") and result.get("response"):
                definition = result["response"]
                source = "knowledge_base"
                self.stats["api_calls"] += 1
                if result.get("cached"):
                    self.stats["cache_hits"] += 1
        
        if not definition:
            definition = self._generate_fallback(keyword, domain)
            source = "template_fallback"
            self.stats["fallback_used"] += 1
        
        if not definition:
            return None
        
        text = self._enhance_text(definition, keyword, domain)
        
        quality_score = self._calculate_quality(text, keyword, domain)
        
        self.stats["total_generated"] += 1
        
        return GeneratedItem(
            id=index,
            word=keyword,
            text=text,
            category=domain,
            quality_score=quality_score,
            source=source,
            metadata={
                "definition_length": len(definition),
                "has_knowledge": source in ["knowledge_base"],
                "generated_at": datetime.now().isoformat()
            }
        )
    
    def generate_batch(self, keywords: List[str], domain: str, start_id: int = 1) -> List[GeneratedItem]:
        """批量生成数据"""
        results = []
        
        for i, keyword in enumerate(keywords):
            item = self.generate_single(keyword, domain, start_id + i)
            if item:
                results.append(item)
        
        return results
    
    def generate(self, domain: str, topic: str, count: int = 5, 
                 min_quality: float = 0.75) -> List[Dict]:
        """生成高质量数据（API批量模式）"""
        
        if self.use_api and self.api:
            example = HIGH_QUALITY_EXAMPLES.get(domain, HIGH_QUALITY_EXAMPLES.get("人工智能", ""))
            constraints = DOMAIN_PROFESSIONAL_CONSTRAINTS.get(domain, "")
            
            prompt = f"""你是一位{domain}领域的资深专家，请生成{count}条高质量的专业知识内容。

主题：{topic}

【质量要求 - 必须严格遵守】
1. 只生成标准定义和规范流程，不生成随机病例或案例
2. 禁止症状和诊断乱配对
3. 内容必须专业、准确、逻辑清晰
4. 结构统一：【术语】+ 定义 + 核心要点
5. 禁止口语化、语气词、语病
6. 每条内容100-300字
7. 不许重复内容
{constraints}
【高质量示例格式】
{example}

【输出格式】
每条内容用"---"分隔，格式如下：
【标题】
正文内容（包含定义、分类、要点等）

请生成{count}条关于"{topic}"的专业内容："""
            
            result = self.api.call(prompt, max_tokens=3000)
            
            if result.get("success") and result.get("response"):
                results = self._parse_response(result["response"], domain)
                results = self._quality_filter(results)
                results = self._validate_and_score(results, domain)
                results = [r for r in results if r.get("quality_score", 0) >= min_quality]
                
                self.stats["total_generated"] += len(results)
                self.stats["total_passed"] += len(results)
                
                return results
        
        keywords = [f"{topic}_{i}" for i in range(count)]
        items = self.generate_batch(keywords, domain)
        
        results = []
        for item in items:
            results.append({
                "id": item.id,
                "domain": domain,
                "title": item.word,
                "content": item.text,
                "text": item.text,
                "category": item.category,
                "source": item.source,
                "quality_score": item.quality_score,
            })
        
        return results
    
    def generate_with_pipeline(self, domain: str, topic: str, count: int = 5) -> List[Dict]:
        """生成数据并通过完整质量流水线"""
        raw_data = self.generate(domain, topic, count * 2)
        
        if self.pipeline:
            result = self.pipeline.process(raw_data, domain)
            return result.data[:count]
        
        return raw_data[:count]
    
    def _parse_response(self, response: str, domain: str) -> List[Dict]:
        """解析响应"""
        results = []
        items = response.split("---")
        
        for i, item in enumerate(items):
            item = item.strip()
            if not item or len(item) < 50:
                continue
            
            title = ""
            for line in item.split("\n"):
                if line.startswith("【") and "】" in line:
                    title = line.split("】")[0].replace("【", "")
                    break
            
            results.append({
                "id": i,
                "domain": domain,
                "title": title,
                "content": item,
                "text": item,
                "category": domain,
                "source": "api"
            })
        
        return results
    
    def _generate_fallback(self, keyword: str, domain: str) -> str:
        """兜底生成"""
        templates = [
            f"{keyword}是{domain}领域的核心概念，指代该领域中具有特定含义和应用价值的专业术语。",
            f"在{domain}领域中，{keyword}是一个重要概念，对于理解和实践该领域知识具有重要意义。",
            f"{keyword}作为{domain}领域的关键术语，涵盖了该领域的核心知识和实践经验。",
        ]
        return random.choice(templates)
    
    def _enhance_text(self, definition: str, keyword: str, domain: str) -> str:
        """增强文本"""
        related = KnowledgeBase.get_related_keywords(keyword, domain, 2)
        
        if related and random.random() < 0.3:
            related_str = "、".join(related)
            definition += f" 该概念与{related_str}密切相关。"
        
        return definition
    
    def _calculate_quality(self, text: str, keyword: str, domain: str) -> float:
        """计算质量分数"""
        score = 0.5
        
        if len(text) >= 50:
            score += 0.1
        if len(text) >= 100:
            score += 0.1
        if len(text) >= 150:
            score += 0.05
        
        if keyword in text:
            score += 0.1
        
        if domain in text or any(d in text for d in ["金融", "人工智能", "医疗", "劳动"]):
            score += 0.05
        
        import re
        sentences = re.split(r'[。！？]', text)
        if len(sentences) >= 2:
            score += 0.05
        
        return min(score, 0.99)
    
    def _quality_filter(self, data: List[Dict]) -> List[Dict]:
        """基础质量过滤"""
        filtered = []
        seen = set()
        
        for item in data:
            content = item.get("content", "")
            
            if len(content) < 50 or len(content) > 1000:
                continue
            
            h = hash(content[:100])
            if h in seen:
                continue
            seen.add(h)
            
            oral = ["嗯", "啊", "呃", "哦", "就是", "那个"]
            if sum(1 for w in oral if w in content) > 2:
                continue
            
            filtered.append(item)
        
        return filtered
    
    def _validate_and_score(self, data: List[Dict], domain: str) -> List[Dict]:
        """专业验证并计算质量分数"""
        if not self.validator:
            for item in data:
                item["quality_score"] = 0.80
                item["quality_level"] = "medium_quality"
            return data
        
        validated_data = []
        
        for item in data:
            content = item.get("content", "")
            
            val_result = self.validator.validate(content, domain)
            
            base_score = 0.80
            
            if val_result.is_valid:
                base_score = min(1.0, base_score + 0.10)
            else:
                error_penalty = sum(
                    0.15 if e.severity == "high" else 0.10 if e.severity == "medium" else 0.05
                    for e in val_result.errors
                )
                base_score = max(0.5, base_score - error_penalty)
            
            if len(content) >= 100 and len(content) <= 500:
                base_score = min(1.0, base_score + 0.05)
            
            has_structure = any(c in content for c in ["：", "。", "1.", "2.", "-", "•"])
            if has_structure:
                base_score = min(1.0, base_score + 0.03)
            
            item["quality_score"] = round(base_score, 3)
            
            if base_score >= 0.85:
                item["quality_level"] = "high_quality"
            elif base_score >= 0.80:
                item["quality_level"] = "free_quality"
            elif base_score >= 0.75:
                item["quality_level"] = "medium_quality"
            else:
                item["quality_level"] = "robustness_quality"
            
            item["_validation"] = {
                "is_valid": val_result.is_valid,
                "validated_aspects": val_result.validated_aspects,
                "error_count": len(val_result.errors),
            }
            
            if val_result.errors:
                item["_validation"]["errors"] = [
                    {"type": e.error_type, "description": e.description}
                    for e in val_result.errors
                ]
            
            validated_data.append(item)
        
        return validated_data
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        stats["pass_rate"] = (
            self.stats["total_passed"] / max(self.stats["total_generated"], 1)
        )
        
        if self.api:
            stats["api_cost_report"] = self.api.get_cost_report()
        
        return stats


high_quality_generator = HighQualityGenerator()


if __name__ == "__main__":
    print("=" * 70)
    print("高质量数据生成器 - 完整版测试")
    print("=" * 70)
    
    gen = HighQualityGenerator(use_api=True, use_pipeline=True, use_validator=True)
    
    print("\n[测试1] 单条生成 - 人工智能领域")
    print("-" * 60)
    item = gen.generate_single("深度学习", "人工智能", 1)
    if item:
        print(f"关键词: {item.word}")
        print(f"内容: {item.text[:100]}...")
        print(f"质量分数: {item.quality_score}")
        print(f"来源: {item.source}")
    
    print("\n[测试2] 批量生成 - 金融领域")
    print("-" * 60)
    data = gen.generate("金融", "资产配置策略", count=3)
    for item in data:
        print(f"\n【{item.get('title', '未知')}】")
        print(f"质量分数: {item.get('quality_score', 'N/A')}")
        print(f"质量等级: {item.get('quality_level', 'N/A')}")
    
    print("\n[测试3] 统计信息")
    print("-" * 60)
    print(gen.get_stats())
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)
