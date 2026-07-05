#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据生成系统 CLI v6.0
命令行接口 + 四层数据来源 + 无限生成

用法:
    generate --type 人工智能 --count 1000 --format json
    generate --type 劳动合同 --count 500 --format csv --output data.csv
    generate --list-types
    generate --stats
"""

import argparse
import json
import os
import sys
import sqlite3
import hashlib
import random
import urllib.request
import urllib.parse
import time
import re
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============

CONFIG = {
    "cache_db": "cache.db",
    "dedup_db": "dedup.db",
    "output_dir": "./output",
    "default_format": "json"
}

# ============ 领域配置 ============

DOMAINS = {
    "人工智能": {
        "keywords": [
            "machine learning", "deep learning", "neural network", "artificial intelligence",
            "computer vision", "reinforcement learning", "transformer", "NLP", "CNN", "RNN",
            "GAN", "autoencoder", "gradient descent", "backpropagation", "overfitting",
            "underfitting", "feature extraction", "classification", "regression", "clustering",
            "supervised learning", "unsupervised learning", "transfer learning", "attention mechanism",
            "embedding", "BERT", "GPT", "language model", "tokenization", "word2vec"
        ],
        "templates": [
            "{word} means {definition}.",
            "The term {word} refers to {definition}.",
            "In AI, {word} is defined as {definition}.",
            "{word}: {definition} - a key concept in artificial intelligence.",
            "Understanding {word}: {definition}."
        ]
    },
    "劳动合同": {
        "keywords": [
            "劳动合同", "试用期", "工资", "社保", "公积金", "加班", "年假",
            "解除合同", "经济补偿", "违约金", "保密协议", "竞业限制",
            "工作时间", "休息休假", "劳动保护", "职业培训", "工伤认定"
        ],
        "templates": [
            "{word}是指{definition}。",
            "关于{word}的规定：{definition}",
            "劳动合同中{word}的含义为{definition}。",
            "{word}：{definition}（劳动法相关）。",
            "在劳动关系中，{word}表示{definition}。"
        ]
    },
    "医疗": {
        "keywords": [
            "disease", "symptom", "treatment", "medicine", "diagnosis",
            "surgery", "hospital", "doctor", "patient", "therapy",
            "vaccine", "infection", "chronic", "acute", "prognosis"
        ],
        "templates": [
            "{word} means {definition}.",
            "In medical terms, {word} refers to {definition}.",
            "{word}: {definition} - a medical concept.",
            "The medical definition of {word} is {definition}.",
            "Healthcare professionals define {word} as {definition}."
        ]
    },
    "金融": {
        "keywords": [
            "stock", "bond", "investment", "banking", "finance",
            "trading", "asset", "portfolio", "dividend", "interest",
            "cryptocurrency", "blockchain", "IPO", "volatility", "inflation"
        ],
        "templates": [
            "{word} means {definition}.",
            "In finance, {word} refers to {definition}.",
            "{word}: {definition} - a financial term.",
            "The financial definition of {word} is {definition}.",
            "Investors should understand {word} as {definition}."
        ]
    }
}

# ============ 四层数据来源 ============

# 第一层：免费公开数据API
FREE_APIS = [
    {
        "name": "Free Dictionary",
        "url": "https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
        "type": "en_dict",
        "cost": 0
    },
    {
        "name": "Wiktionary EN",
        "url": "https://en.wiktionary.org/w/api.php?action=query&titles={word}&prop=extracts&exintro=1&format=json",
        "type": "wiki",
        "cost": 0
    },
    {
        "name": "Wiktionary ZH",
        "url": "https://zh.wiktionary.org/w/api.php?action=query&titles={word}&prop=extracts&exintro=1&format=json",
        "type": "wiki",
        "cost": 0
    }
]

# 第二层：LLM API（可选，需自行配置 API Key）
# 第三层：本地生成器
# 第四层：智能体辅助（在运行时调用）

# ============ 数据库管理 ============

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(CONFIG["cache_db"])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        data TEXT,
        source TEXT,
        created_at DATETIME
    )''')
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect(CONFIG["dedup_db"])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dedup (
        hash TEXT PRIMARY KEY,
        created_at DATETIME
    )''')
    conn.commit()
    conn.close()

def get_cache(key):
    conn = sqlite3.connect(CONFIG["cache_db"])
    c = conn.cursor()
    c.execute('SELECT data FROM cache WHERE key=?', (key,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def set_cache(key, data, source):
    conn = sqlite3.connect(CONFIG["cache_db"])
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?)',
              (key, json.dumps(data, ensure_ascii=False), source, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def is_duplicate(text):
    h = hashlib.md5(text.encode('utf-8')).hexdigest()
    conn = sqlite3.connect(CONFIG["dedup_db"])
    c = conn.cursor()
    c.execute('SELECT 1 FROM dedup WHERE hash=?', (h,))
    exists = c.fetchone() is not None
    if not exists:
        c.execute('INSERT INTO dedup VALUES (?, ?)', (h, datetime.now().isoformat()))
        conn.commit()
    conn.close()
    return exists

# ============ 第一层：免费API ============

def call_free_api(word, api_info):
    """调用免费API"""
    try:
        url = api_info["url"].replace("{word}", urllib.parse.quote(word))
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        if api_info["type"] == "en_dict":
            if isinstance(data, list):
                for entry in data:
                    if 'meanings' in entry:
                        for m in entry['meanings']:
                            for d in m.get('definitions', []):
                                return d.get('definition', '')
        elif api_info["type"] == "wiki":
            pages = data.get('query', {}).get('pages', {})
            for page_id, page in pages.items():
                if 'extract' in page:
                    extract = re.sub(r'<[^>]+>', '', page['extract'])
                    return extract[:200]
    except:
        pass
    return None

# ============ 第二层：LLM API（可选，需自行配置 API Key）============

LLM_CONFIG = {
    "model": "qwen-plus",
    "api_key_env": "LLM_API_KEY",
    "base_url_env": "LLM_BASE_URL",
    "base_url_default": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
}

def _load_json_config(config_path="config.json"):
    """从 config.json 加载 LLM 配置（覆盖默认值）"""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            llm_cfg = cfg.get("llm", {})
            if llm_cfg.get("model"):
                LLM_CONFIG["model"] = llm_cfg["model"]
            if llm_cfg.get("api_key_env"):
                LLM_CONFIG["api_key_env"] = llm_cfg["api_key_env"]
            if llm_cfg.get("base_url_env"):
                LLM_CONFIG["base_url_env"] = llm_cfg["base_url_env"]
            if llm_cfg.get("base_url_default"):
                LLM_CONFIG["base_url_default"] = llm_cfg["base_url_default"]
    except:
        pass

_load_json_config()

def call_llm_api(word, domain):
    """调用 LLM API（仅当用户配置了 API Key 时才生效）"""
    api_key = os.environ.get(LLM_CONFIG["api_key_env"], '')
    if not api_key:
        return None
    
    base_url = os.environ.get(LLM_CONFIG["base_url_env"], LLM_CONFIG["base_url_default"])
    model = LLM_CONFIG["model"]
    
    try:
        prompt = f"请用一句话解释{domain}领域中'{word}'的含义，不超过50字。只输出解释内容。"
        data = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            base_url,
            data=data,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except:
        pass
    return None

# ============ 第三层：本地生成器 ============

def local_generator(word, domain):
    """本地生成器"""
    templates = [
        f"{word} is an important concept in {domain}.",
        f"In the field of {domain}, {word} plays a key role.",
        f"{word} refers to a fundamental principle in {domain}.",
        f"Understanding {word} is essential for {domain}.",
        f"{word} is widely used in {domain} applications."
    ]
    return random.choice(templates)

# ============ 第三层：智能体辅助 ============

def agent_assisted_generation(word, domain):
    """智能体辅助生成（预留接口）"""
    # 这里可以调用外部智能体服务
    # 目前返回None，使用其他层
    return None

# ============ 并行获取接口 ============

import concurrent.futures

def get_definition_parallel(words, domain, max_workers=10):
    """并行获取多个定义（提速5-10倍）"""
    results = {}
    
    def fetch_one(word):
        return word, get_definition(word, domain)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, w): w for w in words}
        for future in concurrent.futures.as_completed(futures):
            word, (definition, source) = future.result()
            results[word] = (definition, source)
    
    return results

def get_definition(word, domain):
    """四层获取定义"""
    # 查缓存
    cached = get_cache(word)
    if cached:
        return cached["definition"], "cache"
    
    # 第一层：免费API
    for api in FREE_APIS:
        definition = call_free_api(word, api)
        if definition and len(definition) > 10:
            set_cache(word, {"definition": definition}, api["name"])
            return definition, api["name"]
    
    # 第二层：LLM API（可选，需自行配 Key）
    definition = call_llm_api(word, domain)
    if definition:
        set_cache(word, {"definition": definition}, "llm")
        return definition, "llm"
    
    # 第三层：智能体辅助
    definition = agent_assisted_generation(word, domain)
    if definition:
        set_cache(word, {"definition": definition}, "agent")
        return definition, "agent"
    
    # 第四层：本地生成器
    definition = local_generator(word, domain)
    set_cache(word, {"definition": definition}, "local")
    return definition, "local"

# ============ 生成器 ============

def generate_data(domain, count, format_type="json"):
    """生成数据（并行优化版）"""
    if domain not in DOMAINS:
        print(f"错误: 未知领域 '{domain}'")
        print(f"可用领域: {', '.join(DOMAINS.keys())}")
        return None
    
    domain_config = DOMAINS[domain]
    keywords = domain_config["keywords"]
    templates = domain_config["templates"]
    
    print(f"\n生成数据: {domain}")
    print(f"目标数量: {count}")
    print(f"关键词数: {len(keywords)}")
    print(f"模板数: {len(templates)}")
    print("-" * 40)
    
    # 并行获取所有定义
    print("正在并行获取定义...")
    definitions = get_definition_parallel(keywords, domain, max_workers=10)
    
    stats = {"free_api": 0, "local": 0, "cache": 0}
    
    data = []
    per_keyword = max(1, count // len(keywords))
    
    for keyword in keywords:
        definition, source = definitions.get(keyword, (local_generator(keyword, domain), "local"))
        stats[source] = stats.get(source, 0) + 1
        
        # 生成变体
        for _ in range(per_keyword):
            template = random.choice(templates)
            text = template.format(word=keyword, definition=definition, domain=domain)
            
            if not is_duplicate(text):
                data.append({
                    "id": len(data),
                    "word": keyword,
                    "text": text,
                    "category": domain,
                    "source": source,
                    "generated_at": datetime.now().isoformat()
                })
        
        if len(data) >= count:
            break
    
    print(f"\n完成! 生成 {len(data)} 条数据")
    print(f"来源统计: {stats}")
    
    return data

# ============ 输出格式化 ============

def format_output(data, format_type, output_file=None):
    """格式化输出"""
    if format_type == "json":
        content = json.dumps(data, ensure_ascii=False, indent=2)
    elif format_type == "csv":
        if not data:
            return ""
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        for item in data:
            lines.append(",".join([str(item.get(h, "")) for h in headers]))
        content = "\n".join(lines)
    elif format_type == "txt":
        content = "\n".join([f"[{d['id']}] {d['text']}" for d in data])
    else:
        content = json.dumps(data, ensure_ascii=False, indent=2)
    
    if output_file:
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"输出文件: {output_file}")
    
    return content

# ============ CLI接口 ============

def main():
    parser = argparse.ArgumentParser(
        description="垂直领域训练数据生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  generate --type 人工智能 --count 1000 --format json
  generate --type 劳动合同 --count 500 --output data.json
  generate --list-types
  generate --stats
        """
    )
    
    parser.add_argument("--type", "-t", help="领域类型")
    parser.add_argument("--count", "-c", type=int, default=100, help="生成数量 (默认: 100)")
    parser.add_argument("--format", "-f", choices=["json", "csv", "txt"], default="json", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--list-types", action="store_true", help="列出所有领域类型")
    parser.add_argument("--stats", action="store_true", help="显示系统统计")
    
    args = parser.parse_args()
    
    # 初始化
    init_db()
    
    if args.list_types:
        print("\n可用领域类型:")
        for name, config in DOMAINS.items():
            print(f"  - {name}: {len(config['keywords'])} 个关键词")
        return
    
    if args.stats:
        conn = sqlite3.connect(CONFIG["cache_db"])
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM cache')
        cache_count = c.fetchone()[0]
        conn.close()
        
        conn = sqlite3.connect(CONFIG["dedup_db"])
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM dedup')
        dedup_count = c.fetchone()[0]
        conn.close()
        
        print(f"\n系统统计:")
        print(f"  缓存条目: {cache_count}")
        print(f"  去重记录: {dedup_count}")
        print(f"  可用领域: {len(DOMAINS)}")
        print(f"  免费API: {len(FREE_APIS)} 个")
        print(f"  LLM API: {'已配置' if os.environ.get(LLM_CONFIG['api_key_env']) else '未配置 (可选)'}")
        return
    
    if not args.type:
        parser.print_help()
        return
    
    # 生成数据
    data = generate_data(args.type, args.count, args.format)
    
    if data:
        output_file = args.output
        if not output_file:
            output_file = f"{args.type}_{args.count}.{args.format}"
        
        format_output(data, args.format, output_file)

if __name__ == '__main__':
    main()