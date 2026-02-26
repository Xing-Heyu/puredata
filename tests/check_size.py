import os
size = os.path.getsize(r'd:\skill\puredata-platform\platform\frontend\index.html')
print(f'前端文件大小: {size} 字节 ({size/1024:.1f} KB)')
