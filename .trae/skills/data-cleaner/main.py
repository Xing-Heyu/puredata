#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
垂直领域训练数据生成系统 v4.0
多词典API + 大规模生成支持
"""

import json
import os
import sys
import sqlite3
import hashlib
import random
import urllib.request
import urllib.parse
import time
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ 多词典API配置（全部免费） ============

DICT_APIS = {
    # 英文词典
    "free_dictionary": {
        "name": "Free Dictionary",
        "url": "https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
        "parse": "free_dict",
        "lang": "en",
        "enabled": True
    },
    "wiktionary_en": {
        "name": "Wiktionary英文",
        "url": "https://en.wiktionary.org/w/api.php?action=query&titles={word}&prop=extracts&exintro=1&format=json",
        "parse": "wiktionary",
        "lang": "en",
        "enabled": True
    },
    "owlbot": {
        "name": "OwlBot Dictionary",
        "url": "https://owlbot.info/api/v4/dictionary/{word}",
        "parse": "owlbot",
        "lang": "en",
        "enabled": True,
        "headers": {"Authorization": "Token "}  # 可选，无token也能用
    },
    "wordnik": {
        "name": "Wordnik",
        "url": "https://api.wordnik.com/v4/word.json/{word}/definitions?limit=1&includeRelated=false&useCanonical=false&includeTags=false&api_key=",
        "parse": "wordnik",
        "lang": "en",
        "enabled": False  # 需要免费API Key
    },
    # 中文词典
    "wiktionary_zh": {
        "name": "维基词典中文",
        "url": "https://zh.wiktionary.org/w/api.php?action=query&titles={word}&prop=extracts&exintro=1&format=json",
        "parse": "wiktionary",
        "lang": "zh",
        "enabled": True
    },
    "zdic": {
        "name": "汉典",
        "url": "https://www.zdic.net/hans/{word}",
        "parse": "zdic",
        "lang": "zh",
        "enabled": True
    }
}

# 千问API配置
QIANWEN_API = {
    "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "model": "qwen-plus",
    "env_key": "QIANWEN_API_KEY",
    "enabled": True
}

# ============ 配置 ============

CONFIG = {
    "output_file": "training_data.json",
    "cache_db": "cache.db",
    "dedup_db": "dedup.db",
    "cache_expire_days": 30,
    "incremental": True,
    
    # 单领域大规模生成示例
    "tasks": [
        {"topic": "人工智能", "keywords": [], "count": 1000, "use_wordlist": True},
    ],
    
    # 模板库（15个基础模板 + 动态变化）
    "templates": [
        "{word} means {definition}.",
        "The word \"{word}\" refers to {definition}.",
        "What does {word} mean? It means {definition}.",
        "In the context of {domain}, {word} is defined as {definition}.",
        "{word}: {definition}.",
        "The term {word} can be understood as {definition}.",
        "Simply put, {word} means {definition}.",
        "{word} is best described as {definition}.",
        "To understand {word}, know that it means {definition}.",
        "The definition of {word} is: {definition}.",
        "When we talk about {word}, we mean {definition}.",
        "{word} can be defined as {definition}.",
        "In simple terms, {word} refers to {definition}.",
        "The concept of {word} means {definition}.",
        "As a technical term, {word} denotes {definition}.",
    ],
    
    # 动态前缀（增加变化）
    "prefixes": [
        "", "Interestingly, ", "Notably, ", "In practice, ", 
        "Fundamentally, ", "Essentially, ", "Technically, ",
        "Broadly speaking, ", "In essence, ", "To elaborate, "
    ],
    
    # 动态后缀（增加变化）
    "suffixes": [
        "", " This is widely used in the field.", " This concept is fundamental.",
        " Understanding this is essential.", " This is a key concept.",
        " Professionals use this term frequently.", " This term appears often in literature.",
        " Mastery of this concept is important.", " This is commonly discussed in research.",
        " This has practical applications."
    ],
    
    # 同义词替换表（增加变化）
    "word_synonyms": {
        "means": ["means", "signifies", "denotes", "indicates", "represents", "implies", "suggests", "refers to"],
        "definition": ["definition", "meaning", "explanation", "description", "interpretation", "understanding"],
        "concept": ["concept", "idea", "notion", "term", "principle", "theory"],
        "understand": ["understand", "comprehend", "grasp", "know", "learn", "recognize"],
        "important": ["important", "significant", "crucial", "essential", "key", "fundamental", "vital"],
        "used": ["used", "utilized", "applied", "employed", "implemented", "adopted"],
    },
    
    # AI领域词汇表（500+词汇）
    "wordlists": {
        "人工智能": [
            # 基础概念
            "artificial intelligence", "machine learning", "deep learning", "neural network",
            "algorithm", "model", "training", "inference", "prediction", "classification",
            "regression", "clustering", "supervised learning", "unsupervised learning",
            "reinforcement learning", "transfer learning", "feature extraction", "feature engineering",
            "data preprocessing", "normalization", "standardization", "regularization",
            # 神经网络
            "convolutional neural network", "recurrent neural network", "LSTM", "GRU",
            "transformer", "attention mechanism", "self-attention", "encoder", "decoder",
            "embedding", "hidden layer", "activation function", "ReLU", "sigmoid",
            "softmax", "dropout", "batch normalization", "weight initialization",
            # 优化
            "gradient descent", "stochastic gradient descent", "Adam", "learning rate",
            "loss function", "cross-entropy", "mean squared error", "backpropagation",
            "epoch", "batch size", "iteration", "convergence", "overfitting", "underfitting",
            "bias", "variance", "hyperparameter tuning", "grid search", "random search",
            # NLP
            "natural language processing", "tokenization", "word embedding", "word2vec",
            "GloVe", "BERT", "GPT", "language model", "text classification", "sentiment analysis",
            "named entity recognition", "machine translation", "text generation", "summarization",
            "question answering", "speech recognition", "text-to-speech", "chatbot",
            # 计算机视觉
            "computer vision", "image classification", "object detection", "semantic segmentation",
            "instance segmentation", "face recognition", "image generation", "GAN",
            "style transfer", "image augmentation", "convolution", "pooling", "feature map",
            # 其他
            "autoencoder", "variational autoencoder", "generative model", "discriminator",
            "generator", "adversarial training", "data augmentation", "ensemble learning",
            "random forest", "decision tree", "support vector machine", "k-nearest neighbors",
            "naive bayes", "logistic regression", "linear regression", "principal component analysis",
            "dimensionality reduction", "feature selection", "cross-validation", "confusion matrix",
            "precision", "recall", "F1 score", "accuracy", "AUC", "ROC curve",
            "false positive", "false negative", "true positive", "true negative",
            "bias-variance tradeoff", "model selection", "hyperparameter", "parameter",
            "weight", "gradient", "loss", "optimizer", "activation", "neuron", "layer",
            "input", "output", "target", "label", "feature", "sample", "dataset",
            "training set", "validation set", "test set", "batch", "epoch", "iteration",
            "inference", "deployment", "serving", "API", "endpoint", "model serving",
            "MLOps", "model versioning", "experiment tracking", "pipeline", "workflow",
            "data pipeline", "feature store", "model registry", "monitoring", "logging",
        ]
    }
}

# ============ 统计 ============

class Stats:
    def __init__(self):
        self.sources = {}
        self.api_calls = {"dict": 0, "qianwen": 0}
        self.start_time = time.time()
    
    def add(self, source):
        self.sources[source] = self.sources.get(source, 0) + 1
        if source == 'qianwen_api':
            self.api_calls["qianwen"] += 1
        elif source not in ['cache', 'local_dict', 'generated']:
            self.api_calls["dict"] += 1
    
    def report(self):
        elapsed = time.time() - self.start_time
        return {
            "sources": self.sources,
            "api_calls": self.api_calls,
            "elapsed_time": f"{elapsed:.1f}s"
        }

stats = Stats()

# ============ 数据库管理 ============

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and not os.environ.get(key):
                        os.environ[key] = value

load_env()

def init_databases(db_path, dedup_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        data TEXT,
        source TEXT,
        created_at DATETIME,
        expire_at DATETIME
    )''')
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect(dedup_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dedup (
        hash TEXT PRIMARY KEY,
        text TEXT,
        created_at DATETIME
    )''')
    conn.commit()
    conn.close()

def get_cache(db_path, key):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT data FROM cache WHERE key=? AND expire_at>?', 
              (key, datetime.now().isoformat()))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def set_cache(db_path, key, data, source):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    expire = (datetime.now() + timedelta(days=CONFIG["cache_expire_days"])).isoformat()
    c.execute('INSERT OR REPLACE INTO cache (key, data, source, created_at, expire_at) VALUES (?, ?, ?, ?, ?)',
              (key, json.dumps(data, ensure_ascii=False), source, datetime.now().isoformat(), expire))
    conn.commit()
    conn.close()

def is_duplicate(dedup_path, text):
    h = hashlib.md5(text.encode('utf-8')).hexdigest()
    conn = sqlite3.connect(dedup_path)
    c = conn.cursor()
    c.execute('SELECT 1 FROM dedup WHERE hash=?', (h,))
    exists = c.fetchone() is not None
    if not exists:
        c.execute('INSERT INTO dedup (hash, text, created_at) VALUES (?, ?, ?)',
                  (h, text, datetime.now().isoformat()))
        conn.commit()
    conn.close()
    return exists

# ============ 多词典API调用 ============

def call_free_dict_api(word):
    """Free Dictionary API"""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if isinstance(data, list):
            for entry in data:
                if 'meanings' in entry:
                    for m in entry['meanings']:
                        for d in m.get('definitions', []):
                            return {
                                "word": word,
                                "definition": d.get('definition', ''),
                                "synonyms": m.get('synonyms', [])[:3],
                                "source": "free_dictionary"
                            }
    except:
        pass
    return None

def call_wiktionary_api(word, lang='en'):
    """Wiktionary API"""
    try:
        base_url = f"https://{lang}.wiktionary.org/w/api.php"
        url = f"{base_url}?action=query&titles={urllib.parse.quote(word)}&prop=extracts&exintro=1&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        pages = data.get('query', {}).get('pages', {})
        for page_id, page in pages.items():
            if 'extract' in page:
                extract = page['extract']
                # 清理HTML标签
                import re
                extract = re.sub(r'<[^>]+>', '', extract)
                if extract and len(extract) > 20:
                    return {
                        "word": word,
                        "definition": extract[:300],
                        "synonyms": [],
                        "source": f"wiktionary_{lang}"
                    }
    except:
        pass
    return None

def call_owlbot_api(word):
    """OwlBot Dictionary API"""
    try:
        url = f"https://owlbot.info/api/v4/dictionary/{urllib.parse.quote(word)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        if 'definitions' in data and data['definitions']:
            d = data['definitions'][0]
            return {
                "word": word,
                "definition": d.get('definition', ''),
                "synonyms": [],
                "source": "owlbot"
            }
    except:
        pass
    return None

def call_qianwen_api(word, topic):
    """千问API"""
    api_key = os.environ.get(QIANWEN_API["env_key"], '')
    if not api_key:
        return None
    
    model = os.environ.get('QIANWEN_MODEL', QIANWEN_API["model"])
    
    try:
        prompt = f"请用一句话解释{topic}领域中'{word}'的含义，不超过50字。只输出解释内容。"
        data = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            QIANWEN_API["url"],
            data=data,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            definition = result['choices'][0]['message']['content']
            return {
                "word": word,
                "definition": definition,
                "synonyms": [],
                "source": "qianwen_api"
            }
    except:
        pass
    return None

def get_word_data(word, topic, db_path):
    """多词典API轮询获取"""
    # 查缓存
    cached = get_cache(db_path, word)
    if cached:
        cached["source"] = "cache"
        return cached
    
    # 1. Free Dictionary API
    data = call_free_dict_api(word)
    if data and len(data.get('definition', '')) > 10:
        set_cache(db_path, word, data, "free_dictionary")
        return data
    
    # 2. Wiktionary英文
    data = call_wiktionary_api(word, 'en')
    if data and len(data.get('definition', '')) > 20:
        set_cache(db_path, word, data, "wiktionary_en")
        return data
    
    # 3. OwlBot
    data = call_owlbot_api(word)
    if data and len(data.get('definition', '')) > 10:
        set_cache(db_path, word, data, "owlbot")
        return data
    
    # 4. Wiktionary中文
    data = call_wiktionary_api(word, 'zh')
    if data and len(data.get('definition', '')) > 20:
        set_cache(db_path, word, data, "wiktionary_zh")
        return data
    
    # 5. 千问API
    if QIANWEN_API["enabled"]:
        data = call_qianwen_api(word, topic)
        if data:
            set_cache(db_path, word, data, "qianwen_api")
            return data
    
    # 兜底
    return {
        "word": word,
        "definition": f"{word} is an important concept in {topic}.",
        "synonyms": [],
        "source": "generated"
    }

# ============ 生成器 ============

def generate_variants(word_data, count, topic, dedup_path):
    """生成变体（支持大规模生成，无上限）"""
    results = []
    word = word_data["word"]
    definition = word_data.get("definition", "")
    synonyms = word_data.get("synonyms", [])
    
    templates = CONFIG["templates"]
    prefixes = CONFIG["prefixes"]
    suffixes = CONFIG["suffixes"]
    word_synonyms = CONFIG["word_synonyms"]
    
    attempts = 0
    max_attempts = count * 20  # 增加尝试次数
    
    while len(results) < count and attempts < max_attempts:
        attempts += 1
        
        # 选择模板
        template = random.choice(templates)
        
        # 动态前缀
        prefix = random.choice(prefixes)
        
        # 动态后缀
        suffix = random.choice(suffixes)
        
        # 同义词替换
        text = template.format(
            word=word,
            definition=definition,
            domain=topic,
            antonym=random.choice(["opposite", "different", "contrary"])
        )
        
        # 添加前缀后缀
        text = prefix + text + suffix
        
        # 随机同义词替换（增加变化）
        if random.random() < 0.3:
            for key, syns in word_synonyms.items():
                if key in text.lower():
                    text = text.replace(key, random.choice(syns), 1)
                    break
        
        if is_duplicate(dedup_path, text):
            continue
        
        results.append({
            "word": word,
            "text": text,
            "template": template[:30] + "...",
            "source": word_data["source"],
            "category": topic
        })
    
    for syn in synonyms[:3]:  # 增加同义词数量
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        text = f"{prefix}{syn.capitalize()} is similar to {word}, meaning {definition}{suffix}"
        if not is_duplicate(dedup_path, text):
            results.append({
                "word": syn,
                "text": text,
                "template": "synonym_sentence",
                "source": "synonym",
                "category": topic
            })
    
    return results

# ============ 主程序 ============

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, CONFIG["cache_db"])
    dedup_path = os.path.join(script_dir, CONFIG["dedup_db"])
    output_path = os.path.join(script_dir, CONFIG["output_file"])
    
    init_databases(db_path, dedup_path)
    
    print(f'\n{"="*60}')
    print(f'垂直领域训练数据生成系统 v4.0')
    print(f'多词典API支持 | 时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'{"="*60}\n')
    
    # 增量模式
    all_data = []
    if CONFIG["incremental"] and os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        print(f'增量模式: 已加载 {len(all_data)} 条历史数据\n')
    
    for i, task in enumerate(CONFIG["tasks"], 1):
        topic = task["topic"]
        count = task["count"]
        
        # 获取词汇列表
        if task.get("use_wordlist") and topic in CONFIG["wordlists"]:
            keywords = CONFIG["wordlists"][topic]
        else:
            keywords = task.get("keywords", [topic])
        
        print(f'[{i}/{len(CONFIG["tasks"])}] {topic}')
        print(f'  词汇数: {len(keywords)} | 目标: {count}条')
        
        per_word = max(1, count // len(keywords))
        
        for j, kw in enumerate(keywords):
            if j % 50 == 0 and j > 0:
                print(f'  处理中: {j}/{len(keywords)} | 累计: {len(all_data)}条')
            
            word_data = get_word_data(kw, topic, db_path)
            stats.add(word_data["source"])
            
            variants = generate_variants(word_data, per_word, topic, dedup_path)
            
            for v in variants:
                v["id"] = len(all_data)
                v["generated_at"] = datetime.now().isoformat()
                all_data.append(v)
        
        print(f'  ✓ 完成: {len(all_data)} 条\n')
    
    # 保存
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    report = stats.report()
    
    print(f'{"="*60}')
    print(f'完成! 总计 {len(all_data)} 条数据')
    print(f'{"="*60}')
    print(f'数据来源:')
    for k, v in sorted(report["sources"].items(), key=lambda x: -x[1]):
        print(f'  {k}: {v}')
    print(f'\nAPI调用:')
    print(f'  词典API: {report["api_calls"]["dict"]} 次')
    print(f'  千问API: {report["api_calls"]["qianwen"]} 次')
    print(f'  耗时: {report["elapsed_time"]}')
    print(f'\n输出: {output_path}')
    print(f'{"="*60}\n')

if __name__ == '__main__':
    main()