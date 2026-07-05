#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataGen Pro - 主入口（精简版）
统一入口，按需加载各层模块

使用方式：
    python main.py --domain 人工智能 --count 100 --quality high
    python main.py --server --port 8000
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import config, DOMAINS

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PureData - AI训练数据生成器')
    parser.add_argument('--domain', '-d', type=str, default='人工智能',
                        choices=list(DOMAINS.keys()), help='领域')
    parser.add_argument('--count', '-c', type=int, default=100, help='生成数量')
    parser.add_argument('--quality', '-q', type=str, default='standard',
                        choices=['ultra', 'high', 'standard', 'mixed'], help='质量模式')
    parser.add_argument('--output', '-o', type=str, default='outputs/', help='输出目录')
    parser.add_argument('--port', '-p', type=int, default=8000, help='服务端口')
    parser.add_argument('--server', '-s', action='store_true', help='启动HTTP服务')
    
    args = parser.parse_args()
    
    if args.server:
        print(f"[PureData] 启动HTTP服务: http://0.0.0.0:{args.port}")
        import simple_main
        simple_main.main()
    else:
        from simple_main import generate_data_clean
        import json
        from datetime import datetime
        
        print(f"[PureData] 开始生成数据")
        print(f"  领域: {args.domain}")
        print(f"  数量: {args.count}")
        print(f"  质量: {args.quality}")
        
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        result = generate_data_clean(args.domain, args.count, task_id, args.quality)
        
        if result:
            os.makedirs(args.output, exist_ok=True)
            output_file = os.path.join(args.output, f"{args.domain}_{task_id}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"[PureData] 生成完成: {len(result)}条数据")
            print(f"[PureData] 输出文件: {output_file}")
        else:
            print("[PureData] 生成失败")

if __name__ == "__main__":
    main()
