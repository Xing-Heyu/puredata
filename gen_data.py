import json
from datetime import datetime
import random

keywords = [
    '劳动合同', '试用期', '工资', '加班费', '社保', '五险一金', '年假', '病假',
    '产假', '婚假', '解除合同', '经济补偿', '赔偿金', '违约金', '竞业限制',
    '保密协议', '培训协议', '服务期', '工伤', '职业病', '劳动仲裁', '劳动争议',
    '调解', '诉讼', '举证', '合同期限', '工作内容', '工作地点', '工作时间',
    '休息休假', '劳动保护', '劳动条件', '用人单位', '劳动者', '薪酬', '福利'
]

templates_clean = [
    '{keyword}是劳动法中的重要概念。根据《劳动合同法》规定，{keyword}应当明确约定，保障劳动者合法权益。',
    '关于{keyword}的问题，用人单位与劳动者应当在劳动合同中明确约定，避免产生劳动争议。',
    '{keyword}涉及劳动者的切身利益，企业应当依法执行相关规定，保障员工权益。',
    '在处理{keyword}相关事宜时，应当遵循合法、公平、平等自愿的原则。',
    '{keyword}的约定应当符合法律规定，不得违反强制性规定，否则约定无效。',
]

templates_mixed = [
    '{keyword}这个事情，一般来说企业会按规定来处理，员工也要配合。',
    '关于{keyword}，建议双方协商解决，实在不行可以申请仲裁。',
    '{keyword}方面的问题，要看具体情况，不同企业可能有不同做法。',
    '遇到{keyword}相关的问题，最好先了解清楚相关法律规定。',
    '{keyword}这个，其实很多企业都在做，关键是要合法合规。',
]

templates_noisy = [
    '{keyword}...这个怎么说呢...反正就是那样吧。',
    '{keyword}，嗯，对，就是这样。',
    '关于{keyword}的事情，嗯嗯嗯嗯嗯。',
    '{keyword}，好的好的好的好的。',
    '{keyword}...重复重复重复...',
]

def generate_item(keyword, quality, idx):
    if quality == 'clean':
        text = random.choice(templates_clean).format(keyword=keyword)
        score = round(random.uniform(0.85, 0.98), 2)
        tier = 'high'
    elif quality == 'mixed':
        text = random.choice(templates_mixed).format(keyword=keyword)
        score = round(random.uniform(0.60, 0.80), 2)
        tier = 'medium'
    else:
        text = random.choice(templates_noisy).format(keyword=keyword)
        score = round(random.uniform(0.35, 0.55), 2)
        tier = 'low'
    
    return {
        'id': idx,
        'word': keyword,
        'text': text,
        'category': '劳动合同',
        'quality_score': score,
        'quality_tier': tier,
        'source': 'synthetic',
        'timestamp': datetime.now().isoformat()
    }

data = []
idx = 1

for i in range(30):
    kw = keywords[i % len(keywords)]
    data.append(generate_item(kw, 'clean', idx))
    idx += 1

for i in range(40):
    kw = keywords[(i + 30) % len(keywords)]
    data.append(generate_item(kw, 'mixed', idx))
    idx += 1

for i in range(30):
    kw = keywords[(i + 70) % len(keywords)]
    data.append(generate_item(kw, 'noisy', idx))
    idx += 1

print(json.dumps(data, ensure_ascii=False, indent=2))
