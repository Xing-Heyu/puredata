import json
with open('ai_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print('category:', data[0]['category'])
print('word_zh:', data[0].get('word_zh', 'N/A'))