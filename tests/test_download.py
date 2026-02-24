import urllib.request
from urllib.parse import quote

print("测试下载API...")

# 测试下载第一个文件（URL编码中文）
filename = '028f2900_人工智能_100.json'
encoded_filename = quote(filename, safe='')
url = f'http://localhost:8000/download/{encoded_filename}'
print(f"URL: {url}")

req = urllib.request.Request(url)

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        print(f"状态码: {response.status}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
        content = response.read()
        print(f"文件大小: {len(content)} bytes")
        
        # 保存到测试位置
        with open('d:/skill/skill3/test_download.json', 'wb') as f:
            f.write(content)
        print("✅ 下载成功，已保存到 test_download.json")
except Exception as e:
    print(f"错误: {e}")
