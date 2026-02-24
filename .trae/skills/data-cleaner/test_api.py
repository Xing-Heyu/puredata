try:
    import requests
    print('requests OK')
    
    # 测试免费字典API
    resp = requests.get('https://api.dictionaryapi.dev/api/v2/entries/en/AI', timeout=10)
    print(f'API状态: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'API返回: {data}')
except Exception as e:
    print(f'错误: {e}')