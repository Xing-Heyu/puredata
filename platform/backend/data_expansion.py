#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据扩展系统 - 接近无上限的数据生成
基于学术方法：关键词扩展、模板变体、组合爆炸
"""

import random
import hashlib
from typing import List, Dict, Any, Set
from collections import defaultdict

class KeywordExpander:
    """关键词扩展器 - 从基础词扩展到海量词"""
    
    BASE_KEYWORDS = {
        "人工智能": [
            "machine learning", "deep learning", "neural network", "AI", "transformer",
            "NLP", "computer vision", "reinforcement learning", "GPT", "BERT",
            "CNN", "RNN", "LSTM", "attention mechanism", "embedding",
            "gradient descent", "backpropagation", "overfitting", "regularization", "optimization",
            "feature extraction", "classification", "regression", "clustering", "dimensionality reduction",
            "supervised learning", "unsupervised learning", "semi-supervised learning", "transfer learning", "fine-tuning",
            "data augmentation", "model architecture", "hyperparameter", "training loop", "inference",
            "convolution", "pooling", "activation function", "loss function", "optimizer",
            "batch normalization", "dropout", "weight decay", "learning rate", "momentum",
            "cross-validation", "train-test split", "feature engineering", "model selection", "ensemble learning",
            "random forest", "decision tree", "support vector machine", "naive bayes", "k-nearest neighbors",
            "generative model", "discriminative model", "autoencoder", "variational autoencoder", "GAN",
            "diffusion model", "language model", "sequence-to-sequence", "beam search", "tokenization",
            "word embedding", "positional encoding", "multi-head attention", "feed-forward network", "layer normalization",
            "residual connection", "encoder-decoder", "self-attention", "cross-attention", "masking",
            "pre-training", "prompt engineering", "few-shot learning", "zero-shot learning", "chain-of-thought",
            "RAG", "knowledge distillation", "model compression", "quantization", "pruning",
            "edge AI", "on-device inference", "model serving", "MLOps", "experiment tracking",
            "data pipeline", "feature store", "model registry", "A/B testing", "model monitoring",
            "bias detection", "fairness", "explainability", "interpretability", "adversarial robustness",
            "federated learning", "differential privacy", "secure computation", "homomorphic encryption", "trusted AI",
            "multimodal learning", "vision-language model", "speech recognition", "text-to-speech", "image generation",
            "object detection", "semantic segmentation", "instance segmentation", "pose estimation", "face recognition",
            "OCR", "document understanding", "table extraction", "layout analysis", "form recognition",
            "sentiment analysis", "named entity recognition", "relation extraction", "coreference resolution", "dependency parsing",
            "machine translation", "summarization", "question answering", "dialogue system", "chatbot",
            "recommendation system", "collaborative filtering", "content-based filtering", "knowledge graph", "graph neural network",
            "time series forecasting", "anomaly detection", "fraud detection", "predictive maintenance", "demand forecasting",
            "robotics", "autonomous driving", "reinforcement learning from human feedback", "imitation learning", "world model",
        ],
        "劳动合同": [
            "劳动合同", "试用期", "工资", "社保", "公积金", "加班", "年假",
            "解除合同", "经济补偿", "违约金", "保密协议", "竞业限制",
            "工作时间", "休息休假", "劳动保护", "职业培训", "工伤认定",
            "劳动仲裁", "劳动合同法", "劳动关系", "用工形式", "劳务派遣",
            "劳动合同期限", "无固定期限", "固定期限", "试用期工资", "解除条件",
            "劳动合同续签", "劳动合同变更", "劳动合同终止", "劳动合同解除", "劳动合同无效",
            "用人单位", "劳动者", "雇主", "雇员", "职工",
            "工资支付", "工资标准", "最低工资", "加班工资", "绩效工资",
            "社会保险", "养老保险", "医疗保险", "失业保险", "工伤保险", "生育保险",
            "住房公积金", "住房补贴", "交通补贴", "餐补", "通讯补贴",
            "带薪年假", "法定节假日", "婚假", "产假", "陪产假", "丧假", "病假",
            "工伤赔偿", "职业病", "劳动能力鉴定", "伤残等级", "医疗期",
            "劳动争议", "劳动调解", "劳动仲裁", "劳动诉讼", "劳动监察",
            "劳动合同纠纷", "工资纠纷", "工伤纠纷", "社保纠纷", "解除合同纠纷",
            "试用期解除", "严重违纪", "不能胜任工作", "客观情况变化", "经济性裁员",
            "双倍工资", "经济补偿金", "赔偿金", "代通知金", "竞业限制补偿",
            "保密义务", "竞业禁止", "知识产权归属", "职务发明", "商业秘密",
            "劳动合同备案", "劳动用工登记", "社保登记", "公积金缴存", "个税代扣",
            "劳务外包", "劳务派遣工", "派遣单位", "用工单位", "派遣期限",
            "非全日制用工", "兼职", "临时工", "实习生", "退休返聘",
            "女职工保护", "未成年工保护", "特殊工种", "高温津贴", "夜班津贴",
            "劳动合同文本", "合同条款", "合同附件", "规章制度", "员工手册",
            "绩效考核", "岗位调整", "薪资调整", "晋升", "降职",
            "离职证明", "档案转移", "社保转移", "公积金提取", "失业登记",
            "劳动标准", "工时制度", "计件工资", "综合工时", "不定时工时",
            "劳动合同法实施条例", "劳动争议调解仲裁法", "社会保险法", "工伤保险条例", "失业保险条例",
        ],
        "医疗": [
            "disease", "symptom", "treatment", "medicine", "diagnosis",
            "surgery", "hospital", "doctor", "patient", "therapy",
            "vaccine", "infection", "chronic", "acute", "prognosis",
            "prescription", "dosage", "side effect", "clinical trial", "medical record",
            "radiology", "pathology", "oncology", "cardiology", "neurology",
            "pediatrics", "obstetrics", "gynecology", "orthopedics", "dermatology",
            "psychiatry", "psychology", "anesthesiology", "emergency medicine", "family medicine",
            "internal medicine", "surgery", "urology", "ophthalmology", "otolaryngology",
            "gastroenterology", "endocrinology", "nephrology", "pulmonology", "rheumatology",
            "hematology", "immunology", "infectious disease", "genetics", "metabolism",
            "blood pressure", "heart rate", "temperature", "respiratory rate", "oxygen saturation",
            "blood test", "urine test", "X-ray", "CT scan", "MRI", "ultrasound", "biopsy",
            "antibiotic", "antiviral", "antifungal", "anti-inflammatory", "painkiller",
            "chemotherapy", "radiation therapy", "immunotherapy", "targeted therapy", "gene therapy",
            "vaccination", "immunization", "booster shot", "flu shot", "COVID-19 vaccine",
            "diabetes", "hypertension", "heart disease", "cancer", "stroke",
            "Alzheimer", "Parkinson", "arthritis", "asthma", "allergy",
            "depression", "anxiety", "bipolar disorder", "schizophrenia", "PTSD",
            "obesity", "malnutrition", "eating disorder", "vitamin deficiency", "anemia",
            "fracture", "sprain", "strain", "dislocation", "tendonitis",
            "infection", "inflammation", "tumor", "cyst", "abscess",
            "wound", "burn", "cut", "bruise", "scar",
            "rehabilitation", "physical therapy", "occupational therapy", "speech therapy", "counseling",
            "preventive care", "health screening", "annual checkup", "wellness visit", "health education",
            "medical insurance", "healthcare system", "primary care", "specialist", "referral",
            "telemedicine", "remote consultation", "online diagnosis", "digital health", "health app",
            "electronic health record", "medical imaging", "laboratory test", "diagnostic code", "ICD-10",
            "informed consent", "patient rights", "medical ethics", "privacy protection", "HIPAA",
            "drug interaction", "contraindication", "allergic reaction", "adverse event", "medication error",
            "surgical procedure", "minimally invasive", "laparoscopy", "endoscopy", "robotic surgery",
            "organ transplant", "blood transfusion", "dialysis", "life support", "CPR",
            "palliative care", "hospice", "end-of-life care", "advance directive", "living will",
            "public health", "epidemiology", "disease outbreak", "pandemic", "quarantine",
        ],
        "金融": [
            "stock", "bond", "investment", "banking", "finance",
            "trading", "asset", "portfolio", "dividend", "interest",
            "cryptocurrency", "blockchain", "IPO", "volatility", "inflation",
            "hedge fund", "mutual fund", "ETF", "derivatives", "options",
            "futures", "forex", "market cap", "liquidity", "risk management",
            "equity", "debt", "credit", "loan", "mortgage",
            "interest rate", "yield", "return", "profit", "loss",
            "bull market", "bear market", "recession", "depression", "economic cycle",
            "GDP", "unemployment rate", "consumer price index", "inflation rate", "monetary policy",
            "fiscal policy", "central bank", "Federal Reserve", "interest rate hike", "quantitative easing",
            "capital gain", "dividend yield", "price-to-earnings ratio", "earnings per share", "book value",
            "market order", "limit order", "stop loss", "margin trading", "short selling",
            "blue chip", "penny stock", "growth stock", "value stock", "income stock",
            "treasury bond", "corporate bond", "municipal bond", "junk bond", "convertible bond",
            "call option", "put option", "strike price", "expiration date", "option premium",
            "forward contract", "futures contract", "swap", "collateral", "margin call",
            "Bitcoin", "Ethereum", "stablecoin", "DeFi", "NFT",
            "wallet", "exchange", "mining", "staking", "yield farming",
            "asset allocation", "diversification", "rebalancing", "dollar-cost averaging", "value averaging",
            "technical analysis", "fundamental analysis", "chart pattern", "moving average", "RSI",
            "support level", "resistance level", "trend line", "candlestick", "volume",
            "risk tolerance", "risk capacity", "investment horizon", "financial goal", "retirement planning",
            "401k", "IRA", "pension", "social security", "annuity",
            "insurance", "life insurance", "health insurance", "property insurance", "liability insurance",
            "tax planning", "tax deduction", "tax credit", "capital gains tax", "estate tax",
            "financial statement", "balance sheet", "income statement", "cash flow", "financial ratio",
            "credit score", "credit report", "debt-to-income ratio", "loan-to-value ratio", "collateral value",
            "financial advisor", "wealth management", "private banking", "family office", "robo-advisor",
            "ESG investing", "sustainable finance", "impact investing", "green bond", "carbon credit",
            "financial regulation", "SEC", "FINRA", "compliance", "anti-money laundering",
            "market crash", "flash crash", "circuit breaker", "trading halt", "market manipulation",
        ],
        "电商": [
            "电商", "网购", "在线购物", "电子商务", "网上商城",
            "商品", "库存", "价格", "折扣", "促销",
            "优惠券", "满减", "秒杀", "团购", "预售",
            "物流", "快递", "配送", "仓储", "发货",
            "退货", "退款", "换货", "售后", "客服",
            "评价", "评分", "评论", "晒单", "买家秀",
            "店铺", "商家", "卖家", "买家", "消费者",
            "购物车", "订单", "支付", "结算", "收货地址",
            "直播带货", "短视频营销", "内容电商", "社交电商", "社区团购",
            "跨境电商", "进口商品", "海外购", "保税仓", "直邮",
            "品牌", "旗舰店", "专卖店", "自营", "第三方卖家",
            "会员", "积分", "等级", "权益", "专属优惠",
            "搜索", "推荐", "个性化", "猜你喜欢", "热销榜单",
            "新品", "爆款", "限量", "独家", "联名款",
            "比价", "历史价格", "降价提醒", "价格保护", "保价",
            "假货", "正品", "防伪", "溯源", "质量保证",
            "包装", "礼盒", "定制", "刻字", "贺卡",
            "发票", "电子发票", "增值税", "报销", "企业采购",
            "大促", "双11", "618", "年货节", "女王节",
            "品类", "分类", "筛选", "排序", "导航",
            "详情页", "主图", "详情图", "视频", "3D展示",
            "SKU", "规格", "颜色", "尺码", "版本",
            "库存预警", "补货", "预售", "缺货", "到货通知",
            "运费", "包邮", "满包邮", "运费险", "偏远地区",
            "签收", "验货", "拒收", "代收", "自提",
            "投诉", "维权", "举报", "纠纷", "仲裁",
        ],
        "法律": [
            "法律", "法规", "条例", "规定", "办法",
            "合同", "协议", "契约", "条款", "约定",
            "诉讼", "起诉", "应诉", "上诉", "申诉",
            "判决", "裁定", "调解", "仲裁", "和解",
            "律师", "法官", "检察官", "公证员", "法律顾问",
            "原告", "被告", "第三人", "代理人", "辩护人",
            "证据", "举证", "质证", "认证", "鉴定",
            "民事", "刑事", "行政", "经济", "知识产权",
            "侵权", "违约", "犯罪", "违法", "违规",
            "赔偿", "补偿", "罚款", "罚金", "没收",
            "拘留", "逮捕", "取保候审", "监视居住", "缓刑",
            "有期徒刑", "无期徒刑", "死刑", "剥夺政治权利", "驱逐出境",
            "民事诉讼", "刑事诉讼", "行政诉讼", "公益诉讼", "集团诉讼",
            "一审", "二审", "再审", "执行", "强制执行",
            "管辖", "管辖权", "移送", "指定管辖", "专属管辖",
            "时效", "诉讼时效", "除斥期间", "期限", "期间",
            "送达", "公告送达", "邮寄送达", "直接送达", "留置送达",
            "财产保全", "证据保全", "行为保全", "先予执行", "诉前禁令",
            "破产", "清算", "重组", "和解", "重整",
            "商标", "专利", "著作权", "版权", "商业秘密",
            "公司", "股东", "董事", "监事", "法定代表人",
            "股权转让", "增资", "减资", "合并", "分立",
            "劳动合同", "劳务合同", "承揽合同", "租赁合同", "买卖合同",
            "借贷", "担保", "抵押", "质押", "保证",
            "继承", "遗嘱", "遗赠", "法定继承", "代位继承",
            "婚姻", "离婚", "抚养", "赡养", "扶养",
            "房产", "土地", "物权", "所有权", "使用权",
            "行政处罚", "行政许可", "行政强制", "行政复议", "行政诉讼",
        ],
        "教育": [
            "教育", "教学", "学习", "培训", "课程",
            "学校", "大学", "中学", "小学", "幼儿园",
            "教师", "学生", "家长", "校长", "教务",
            "考试", "测验", "作业", "论文", "答辩",
            "成绩", "分数", "排名", "学分", "学位",
            "本科", "硕士", "博士", "研究生", "博士后",
            "专业", "学科", "科目", "选修", "必修",
            "教材", "教案", "课件", "习题", "试卷",
            "课堂", "讲座", "实验", "实习", "实践",
            "在线教育", "远程教学", "网课", "直播课", "录播课",
            "素质教育", "应试教育", "职业教育", "终身学习", "继续教育",
            "招生", "录取", "报名", "注册", "入学",
            "毕业", "结业", "肄业", "休学", "退学",
            "奖学金", "助学金", "贷款", "减免", "补助",
            "教师资格", "职称", "评优", "考核", "晋升",
            "教育改革", "双减", "课改", "素质教育", "创新教育",
            "早教", "启蒙", "幼小衔接", "小升初", "中考", "高考",
            "考研", "考公", "考证", "雅思", "托福", "GRE",
            "留学", "交换生", "访学", "联合培养", "双学位",
            "图书馆", "实验室", "体育馆", "宿舍", "食堂",
            "校园", "校服", "校规", "校历", "校训",
            "班主任", "辅导员", "导师", "师兄", "师姐",
            "班级", "年级", "院系", "学院", "校区",
            "学籍", "档案", "证书", "文凭", "学历",
            "补习", "辅导", "培优", "补差", "一对一",
            "兴趣班", "特长", "竞赛", "奥数", "科创",
            "阅读", "写作", "口语", "听力", "翻译",
        ],
        "科技": [
            "科技", "技术", "创新", "研发", "专利",
            "芯片", "半导体", "处理器", "存储", "内存",
            "操作系统", "软件", "硬件", "固件", "驱动",
            "云计算", "大数据", "人工智能", "物联网", "5G",
            "区块链", "量子计算", "边缘计算", "分布式", "并行计算",
            "网络安全", "数据安全", "隐私保护", "加密", "认证",
            "虚拟现实", "增强现实", "元宇宙", "数字孪生", "仿真",
            "机器人", "无人机", "自动驾驶", "智能制造", "工业4.0",
            "新能源", "电池", "充电", "储能", "光伏",
            "航天", "卫星", "火箭", "空间站", "深空探测",
            "生物技术", "基因编辑", "新药研发", "精准医疗", "脑机接口",
            "材料科学", "纳米技术", "超导", "复合材料", "智能材料",
            "显示技术", "OLED", "MicroLED", "全息", "柔性屏",
            "传感器", "摄像头", "雷达", "激光雷达", "超声波",
            "通信", "信号", "频谱", "基站", "天线",
            "数据中心", "服务器", "存储阵列", "网络设备", "机房",
            "开发", "编程", "代码", "算法", "架构",
            "测试", "调试", "部署", "运维", "监控",
            "版本控制", "持续集成", "持续部署", "敏捷开发", "DevOps",
            "开源", "闭源", "许可证", "知识产权", "商业秘密",
            "科技巨头", "独角兽", "创业公司", "孵化器", "加速器",
            "技术转移", "成果转化", "产学研", "协同创新", "联合实验室",
            "技术标准", "行业标准", "国际标准", "标准化", "互操作性",
            "技术路线", "技术栈", "技术选型", "技术债务", "技术升级",
            "产品迭代", "版本更新", "功能扩展", "性能优化", "用户体验",
            "技术文档", "API文档", "用户手册", "技术支持", "售后服务",
        ],
        "旅游": [
            "旅游", "旅行", "度假", "出行", "游玩",
            "景点", "景区", "名胜古迹", "自然风光", "人文景观",
            "酒店", "民宿", "客栈", "青年旅舍", "度假村",
            "机票", "火车票", "汽车票", "船票", "签证",
            "跟团游", "自由行", "半自助游", "定制游", "私家团",
            "导游", "领队", "司机", "翻译", "地陪",
            "行程", "路线", "攻略", "游记", "点评",
            "预订", "下单", "支付", "确认", "取消",
            "入住", "退房", "房态", "房型", "房价",
            "接机", "送机", "接送", "包车", "租车",
            "早餐", "午餐", "晚餐", "特色美食", "当地小吃",
            "购物", "免税店", "特产", "纪念品", "手信",
            "保险", "意外险", "行程取消险", "医疗险", "救援险",
            "签证", "护照", "入境", "出境", "海关",
            "时差", "汇率", "货币兑换", "小费", "消费水平",
            "天气", "季节", "最佳时间", "穿衣指南", "防晒",
            "语言", "翻译软件", "当地语言", "英语", "中文服务",
            "网络", "WiFi", "电话卡", "漫游", "流量",
            "紧急联系", "大使馆", "领事馆", "报警", "急救",
            "拍照", "摄影", "航拍", "打卡", "网红景点",
            "亲子游", "蜜月游", "老年游", "毕业旅行", "公司团建",
            "海滩", "海岛", "山区", "草原", "沙漠",
            "古镇", "古城", "博物馆", "展览", "演出",
            "温泉", "滑雪", "潜水", "徒步", "攀岩",
            "邮轮", "游艇", "帆船", "皮划艇", "漂流",
            "主题公园", "游乐园", "动物园", "水族馆", "植物园",
        ],
        "餐饮": [
            "餐饮", "美食", "餐厅", "饭店", "小吃店",
            "菜品", "菜单", "招牌菜", "特色菜", "推荐菜",
            "早餐", "午餐", "晚餐", "夜宵", "下午茶",
            "中餐", "西餐", "日料", "韩餐", "东南亚菜",
            "火锅", "烧烤", "自助餐", "快餐", "外卖",
            "预订", "排队", "等位", "取号", "叫号",
            "点餐", "下单", "上菜", "加菜", "退菜",
            "口味", "味道", "咸淡", "辣度", "甜度",
            "食材", "原料", "新鲜", "有机", "进口",
            "厨师", "服务员", "店长", "收银", "配菜",
            "厨房", "后厨", "明厨", "包间", "大厅",
            "卫生", "环境", "装修", "氛围", "格调",
            "价格", "人均", "性价比", "优惠", "折扣",
            "评价", "评分", "点评", "推荐", "避雷",
            "网红店", "老字号", "连锁店", "旗舰店", "概念店",
            "米其林", "黑珍珠", "必吃榜", "人气榜", "新店",
            "堂食", "外带", "打包", "配送", "自提",
            "酒水", "饮料", "茶水", "果汁", "咖啡",
            "甜点", "蛋糕", "冰淇淋", "水果", "零食",
            "素食", "清真", "低卡", "健身餐", "轻食",
            "节日套餐", "商务宴请", "家庭聚餐", "朋友聚会", "约会",
            "开业", "周年庆", "会员日", "限时活动", "新品",
            "食材采购", "供应链", "中央厨房", "预制菜", "标准化",
            "食品安全", "卫生许可证", "健康证", "添加剂", "保质期",
            "餐饮创业", "加盟", "连锁", "品牌", "选址",
        ],
    }
    
    SYNONYM_MAP = {
        "人工智能": {
            "machine learning": ["ML", "机器学习", "自动学习"],
            "deep learning": ["DL", "深度学习", "深层学习"],
            "neural network": ["神经网络", "人工神经网络", "ANN"],
            "AI": ["人工智能", "artificial intelligence", "智能系统"],
            "transformer": ["变换器", "注意力模型", "自注意力"],
            "NLP": ["自然语言处理", "natural language processing", "语言理解"],
            "computer vision": ["CV", "计算机视觉", "视觉识别"],
            "reinforcement learning": ["RL", "强化学习", "奖励学习"],
        },
        "劳动合同": {
            "劳动合同": ["聘用合同", "雇佣合同", "工作合同"],
            "试用期": ["考察期", "试用期间", "实习期"],
            "工资": ["薪资", "薪酬", "报酬", "薪水"],
            "社保": ["社会保险", "五险", "社会保障"],
            "加班": ["加班工作", "超时工作", "额外工作"],
        },
        "医疗": {
            "disease": ["illness", "condition", "disorder", "疾病"],
            "symptom": ["sign", "manifestation", "症状"],
            "treatment": ["therapy", "intervention", "治疗"],
            "medicine": ["medication", "drug", "药物"],
            "diagnosis": ["detection", "identification", "诊断"],
        },
        "金融": {
            "stock": ["share", "equity", "股票", "股份"],
            "investment": ["investing", "投资", "理财"],
            "bond": ["debt security", "债券", "债务证券"],
            "trading": ["exchange", "交易", "买卖"],
            "portfolio": ["holdings", "投资组合", "资产组合"],
        },
    }
    
    RELATED_WORDS = {
        "人工智能": {
            "model": ["architecture", "parameter", "weight", "layer", "neuron"],
            "training": ["learning", "optimization", "convergence", "epoch", "iteration"],
            "data": ["dataset", "sample", "feature", "label", "annotation"],
            "performance": ["accuracy", "precision", "recall", "F1", "AUC"],
        },
        "劳动合同": {
            "合同": ["协议", "约定", "条款", "期限", "条件"],
            "工资": ["薪资", "奖金", "津贴", "补贴", "福利"],
            "休假": ["年假", "病假", "事假", "婚假", "产假"],
        },
        "医疗": {
            "治疗": ["手术", "药物", "康复", "护理", "预防"],
            "检查": ["化验", "影像", "体检", "筛查", "诊断"],
        },
        "金融": {
            "投资": ["股票", "债券", "基金", "期货", "期权"],
            "风险": ["波动", "损失", "对冲", "保险", "分散"],
        },
    }
    
    def __init__(self):
        self.expanded_cache = {}
    
    def expand_keywords(self, domain: str, count: int = 500) -> List[str]:
        if domain in self.expanded_cache and len(self.expanded_cache[domain]) >= count:
            return self.expanded_cache[domain][:count]
        
        base_keywords = self.BASE_KEYWORDS.get(domain, [])
        expanded = list(base_keywords)
        
        synonym_map = self.SYNONYM_MAP.get(domain, {})
        for word, synonyms in synonym_map.items():
            if word in expanded:
                for syn in synonyms:
                    if syn not in expanded:
                        expanded.append(syn)
        
        related_words = self.RELATED_WORDS.get(domain, {})
        for category, words in related_words.items():
            for word in words:
                if word not in expanded:
                    expanded.append(word)
        
        prefixes = ["advanced", "modern", "traditional", "hybrid", "distributed", "scalable", "efficient", "robust"]
        suffixes = ["system", "method", "approach", "technique", "framework", "model", "algorithm"]
        
        for base in base_keywords[:50]:
            for prefix in prefixes[:3]:
                new_word = f"{prefix} {base}"
                if new_word not in expanded:
                    expanded.append(new_word)
            for suffix in suffixes[:3]:
                new_word = f"{base} {suffix}"
                if new_word not in expanded:
                    expanded.append(new_word)
        
        random.shuffle(expanded)
        self.expanded_cache[domain] = expanded
        
        return expanded[:count]
    
    def get_keyword_variations(self, keyword: str) -> List[str]:
        variations = [keyword]
        
        if " " in keyword:
            parts = keyword.split()
            if len(parts) == 2:
                variations.append(f"{parts[1]} {parts[0]}")
        
        if keyword.islower():
            variations.append(keyword.title())
            variations.append(keyword.upper())
        elif keyword.istitle():
            variations.append(keyword.lower())
        
        return list(set(variations))


class TemplateExpander:
    """模板扩展器 - 从基础模板生成海量变体"""
    
    BASE_TEMPLATES = {
        "人工智能": [
            "{word} is a fundamental concept in {domain}.",
            "{word} refers to a key technique in {domain}.",
            "In {domain}, {word} plays a critical role in modern applications.",
            "{word} is widely applied in {domain} systems, enabling smarter solutions.",
            "The concept of {word} is essential for {domain} practitioners to master.",
            "{word} represents an important paradigm in {domain}, transforming how we solve problems.",
            "Understanding {word} is crucial for {domain} practitioners, as it forms the basis of many advanced techniques.",
            "{word} forms the foundation of many {domain} algorithms, from basic classification to complex reasoning systems.",
            "In the field of {domain}, {word} enables breakthrough innovations that were previously impossible.",
            "{word} has revolutionized how we approach {domain} problems, making solutions more efficient and accurate.",
        ],
        "劳动合同": [
            "{word}是劳动法中的重要概念。",
            "{word}指的是劳动关系中的关键条款。",
            "在劳动合同中，{word}具有重要意义，直接关系到双方权益。",
            "{word}是保障劳动者权益的重要内容，用人单位必须严格遵守。",
            "关于{word}的规定是劳动合同的核心条款，双方签字即具有法律效力。",
            "{word}涉及劳动者的基本权利和义务，是劳动关系的基础性内容。",
            "理解{word}对于维护劳动关系至关重要，很多纠纷都源于对此理解不清。",
            "{word}是劳动合同法明确规定的条款，任何违反都可能承担法律责任。",
            "在劳动关系中，{word}需要双方共同遵守，这是建立和谐劳动关系的基础。",
            "{word}是劳动争议中常见的问题，处理不当可能引发仲裁或诉讼。",
        ],
        "医疗": [
            "{word} is a critical aspect of modern healthcare.",
            "{word} plays a vital role in patient diagnosis and treatment.",
            "In medical practice, {word} requires careful consideration by healthcare professionals.",
            "{word} has significant implications for patient outcomes and quality of care.",
            "Understanding {word} is essential for healthcare providers in clinical settings.",
            "{word} represents an important advancement in medical science and patient care.",
            "The study of {word} has led to breakthrough treatments and improved patient outcomes.",
            "{word} is a key factor in determining appropriate treatment protocols for patients.",
            "Medical professionals must stay updated on {word} to provide optimal patient care.",
            "{word} has transformed how healthcare providers approach patient management.",
        ],
        "金融": [
            "{word} is a fundamental concept in financial markets.",
            "{word} plays a crucial role in investment decision-making.",
            "In the financial industry, {word} is essential for risk management and portfolio optimization.",
            "{word} has significant implications for market dynamics and investor behavior.",
            "Understanding {word} is critical for financial professionals and investors alike.",
            "{word} represents a key component of modern financial systems and markets.",
            "The analysis of {word} provides valuable insights for investment strategies.",
            "{word} is a major factor influencing market trends and economic conditions.",
            "Financial institutions rely on {word} for strategic planning and risk assessment.",
            "{word} has transformed the landscape of modern finance and investment.",
        ],
        "电商": [
            "{word}是电商运营中的核心要素。",
            "{word}直接影响消费者的购买决策和用户体验。",
            "在电商平台上，{word}是提升转化率的关键因素。",
            "{word}对于电商企业的运营效率和盈利能力至关重要。",
            "理解{word}对于电商从业者来说是必备的专业知识。",
            "{word}是电商平台差异化竞争的重要手段。",
            "优化{word}能够显著提升用户满意度和复购率。",
            "{word}是电商行业持续创新和发展的驱动力。",
            "电商企业需要重视{word}以保持市场竞争力。",
            "{word}已成为电商运营不可或缺的重要组成部分。",
        ],
        "法律": [
            "{word}是法律体系中的重要概念。",
            "{word}在司法实践中具有关键作用。",
            "在法律框架下，{word}是维护当事人权益的重要保障。",
            "{word}对于法律从业者来说是必须掌握的专业知识。",
            "理解{word}对于正确适用法律具有重要意义。",
            "{word}是法律制度中不可或缺的组成部分。",
            "{word}的规定体现了法律对公平正义的追求。",
            "在法律实务中，{word}是常见的争议焦点。",
            "{word}的正确理解和适用对于案件结果至关重要。",
            "{word}是法律体系不断完善和发展的重要领域。",
        ],
        "教育": [
            "{word}是教育领域的重要概念。",
            "{word}对于学生的学习和发展具有深远影响。",
            "在教育实践中，{word}是提高教学质量的关键因素。",
            "{word}是教育改革和创新的重要方向。",
            "理解{word}对于教育工作者来说是必备的专业素养。",
            "{word}是构建现代教育体系的重要组成部分。",
            "{word}的有效实施能够显著提升教育效果。",
            "教育机构需要重视{word}以适应时代发展需求。",
            "{word}是培养创新人才的重要途径。",
            "{word}已成为教育领域研究的热点话题。",
        ],
        "科技": [
            "{word}是科技发展的核心驱动力。",
            "{word}正在深刻改变我们的生活方式和工作模式。",
            "在科技领域，{word}代表着前沿的发展方向。",
            "{word}对于推动产业升级具有关键作用。",
            "理解{word}对于把握科技发展趋势至关重要。",
            "{word}是科技创新的重要突破口。",
            "{word}的发展将带来巨大的社会和经济价值。",
            "科技企业需要持续投入{word}的研发和创新。",
            "{word}是构建未来智能社会的重要基础。",
            "{word}已成为全球科技竞争的焦点领域。",
        ],
        "旅游": [
            "{word}是旅游体验的重要组成部分。",
            "{word}对于提升旅游品质具有关键作用。",
            "在旅游行业中，{word}是吸引游客的重要因素。",
            "{word}是旅游目的地核心竞争力的重要体现。",
            "理解{word}对于旅游从业者来说是必备知识。",
            "{word}是旅游消费升级的重要方向。",
            "{word}的优化能够显著提升游客满意度。",
            "旅游企业需要重视{word}以满足市场需求。",
            "{word}是旅游业可持续发展的重要保障。",
            "{word}已成为旅游行业创新发展的热点。",
        ],
        "餐饮": [
            "{word}是餐饮行业的核心要素。",
            "{word}直接影响顾客的用餐体验和满意度。",
            "在餐饮经营中，{word}是提升竞争力的关键。",
            "{word}对于餐饮企业的品牌建设至关重要。",
            "理解{word}对于餐饮从业者来说是必备技能。",
            "{word}是餐饮差异化经营的重要手段。",
            "{word}的优化能够显著提升经营效益。",
            "餐饮企业需要重视{word}以适应市场变化。",
            "{word}是餐饮行业持续发展的动力源泉。",
            "{word}已成为餐饮消费升级的重要方向。",
        ],
    }
    
    SENTENCE_STARTERS = [
        "", "First,", "Moreover,", "Furthermore,", "Additionally,",
        "In particular,", "Specifically,", "Notably,", "Importantly,",
        "Interestingly,", "Significantly,", "Remarkably,",
    ]
    
    SENTENCE_ENDINGS = [
        "", " This is particularly relevant in today's context.",
        " Understanding this concept is essential for practitioners.",
        " This has significant practical implications.",
        " Further research in this area is ongoing.",
        " This represents an important area of study.",
    ]
    
    INTENSIFIERS = [
        "", "very ", "highly ", "extremely ", "particularly ",
        "especially ", "remarkably ", "significantly ", "crucially ",
    ]
    
    CONNECTORS = [
        "", " and", " as well as", " along with", " combined with",
    ]
    
    def __init__(self):
        self.template_cache = {}
    
    def expand_templates(self, domain: str, count: int = 100) -> List[str]:
        cache_key = f"{domain}_{count}"
        if cache_key in self.template_cache:
            return self.template_cache[cache_key]
        
        base_templates = self.BASE_TEMPLATES.get(domain, self.BASE_TEMPLATES["人工智能"])
        expanded = list(base_templates)
        
        for template in base_templates[:20]:
            for starter in self.SENTENCE_STARTERS[:5]:
                if starter:
                    new_template = f"{starter} {template}"
                    expanded.append(new_template)
            
            for ending in self.SENTENCE_ENDINGS[:5]:
                if ending:
                    new_template = f"{template.rstrip('.')} {ending}"
                    expanded.append(new_template)
        
        expanded = list(set(expanded))
        random.shuffle(expanded)
        self.template_cache[cache_key] = expanded[:count]
        
        return expanded[:count]
    
    def generate_dynamic_template(self, domain: str, keyword: str) -> str:
        patterns = [
            "Let me explain {word}: it's one of the key concepts in {domain}.",
            "When we talk about {word} in {domain}, we're discussing something transformative.",
            "Have you heard about {word}? It's changing the landscape of {domain}.",
            "{word} - this might sound technical, but it's actually quite intuitive in {domain}.",
            "From a {domain} perspective, {word} can be understood as a powerful methodology.",
            "What makes {word} so special in {domain}? Let me break it down.",
            "The beauty of {word} lies in its simplicity and power within {domain}.",
            "Researchers in {domain} have been fascinated by {word} for years.",
            "{word} isn't just a buzzword in {domain} - it's a game-changer.",
            "If you're studying {domain}, you'll definitely encounter {word}.",
        ]
        
        return random.choice(patterns).format(word=keyword, domain=domain)


class DataExpansionEngine:
    """数据扩展引擎 - 统一入口"""
    
    def __init__(self):
        self.keyword_expander = KeywordExpander()
        self.template_expander = TemplateExpander()
        self.generation_stats = defaultdict(int)
    
    def get_expansion_capacity(self, domain: str) -> Dict[str, int]:
        keywords = self.keyword_expander.expand_keywords(domain, 500)
        templates = self.template_expander.expand_templates(domain, 100)
        
        base_capacity = len(keywords) * len(templates)
        
        noise_levels = 5
        quality_tiers = 4
        human_variations = 10
        
        extended_capacity = base_capacity * noise_levels * quality_tiers * human_variations
        
        return {
            "keywords": len(keywords),
            "templates": len(templates),
            "base_combinations": base_capacity,
            "extended_capacity": extended_capacity,
            "domains_available": len(KeywordExpander.BASE_KEYWORDS)
        }
    
    def generate_expanded_data(self, domain: str, count: int, 
                               noise_level: int = 2,
                               quality_tier: str = "high") -> List[Dict[str, Any]]:
        keywords = self.keyword_expander.expand_keywords(domain, min(count // 2 + 100, 500))
        templates = self.template_expander.expand_templates(domain, 100)
        
        data = []
        seen_hashes = set()
        
        attempts = 0
        max_attempts = count * 3
        
        while len(data) < count and attempts < max_attempts:
            attempts += 1
            
            keyword = random.choice(keywords)
            template = random.choice(templates)
            
            try:
                text = template.format(word=keyword, domain=domain)
            except:
                text = self.template_expander.generate_dynamic_template(domain, keyword)
            
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            if text_hash in seen_hashes:
                continue
            seen_hashes.add(text_hash)
            
            item = {
                "id": len(data) + 1,
                "word": keyword,
                "text": text,
                "category": domain,
                "source": "expanded",
                "quality_tier": quality_tier,
                "noise_level": noise_level,
            }
            
            data.append(item)
        
        self.generation_stats[domain] += len(data)
        
        return data
    
    def get_available_domains(self) -> List[str]:
        return list(KeywordExpander.BASE_KEYWORDS.keys())
    
    def get_total_capacity(self) -> Dict[str, Any]:
        total_keywords = 0
        total_templates = 0
        total_base = 0
        
        for domain in self.get_available_domains():
            capacity = self.get_expansion_capacity(domain)
            total_keywords += capacity["keywords"]
            total_templates += capacity["templates"]
            total_base += capacity["base_combinations"]
        
        return {
            "total_keywords": total_keywords,
            "total_templates": total_templates,
            "total_base_combinations": total_base,
            "total_extended": total_base * 5 * 4 * 10,
            "domains": len(self.get_available_domains())
        }


data_expansion_engine = DataExpansionEngine()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("数据扩展系统测试")
    print("="*70)
    
    print("\n[1] 扩展能力分析")
    print("-"*70)
    
    total = data_expansion_engine.get_total_capacity()
    print(f"可用领域: {total['domains']}个")
    print(f"关键词总数: {total['total_keywords']}个")
    print(f"模板总数: {total['total_templates']}个")
    print(f"基础组合: {total['total_base_combinations']:,}条")
    print(f"扩展后容量: {total['total_extended']:,}条")
    
    print("\n[2] 各领域容量")
    print("-"*70)
    
    for domain in data_expansion_engine.get_available_domains():
        cap = data_expansion_engine.get_expansion_capacity(domain)
        print(f"\n【{domain}】")
        print(f"  关键词: {cap['keywords']}个")
        print(f"  模板: {cap['templates']}个")
        print(f"  基础组合: {cap['base_combinations']:,}条")
        print(f"  扩展容量: {cap['extended_capacity']:,}条")
    
    print("\n[3] 生成测试")
    print("-"*70)
    
    for domain in ["人工智能", "劳动合同", "电商"]:
        data = data_expansion_engine.generate_expanded_data(domain, 5)
        print(f"\n【{domain}】生成5条数据:")
        for item in data[:3]:
            print(f"  - {item['word']}: {item['text'][:50]}...")
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)
