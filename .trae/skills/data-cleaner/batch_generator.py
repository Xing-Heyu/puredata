#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量垂直领域数据生成脚本

本脚本支持从配置文件或命令行批量生成多个垂直领域的数据。
"""

import argparse
import json
import os
import sys
import concurrent.futures
from datetime import datetime

# 添加工具模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from domain_manager import DomainManager
from data_generator import DataGenerator


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='批量垂直领域数据生成脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 从命令行批量生成
  python batch_generator.py --domains medical,finance,education --output-dir ./output

  # 从配置文件批量生成
  python batch_generator.py --config batch_config.json

  # 并行生成
  python batch_generator.py --domains medical,finance,education --parallel 4
        """
    )
    
    parser.add_argument('--domains', '-d', type=str, help='领域列表（逗号分隔）')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--output-dir', '-o', type=str, default='./batch_output', help='输出目录')
    parser.add_argument('--format', '-f', type=str, default='json',
                       choices=['json', 'jsonl', 'csv', 'txt', 'dict'],
                       help='输出格式')
    parser.add_argument('--count', '-n', type=int, default=10, help='每个领域生成数量')
    parser.add_argument('--parallel', '-p', type=int, default=4, help='并行处理数量')
    
    return parser.parse_args()


def load_config(config_file):
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_domain_data(domain_name, output_dir, output_format, count, domain_manager, data_generator):
    """生成单个领域数据"""
    try:
        domain_config = domain_manager.get_domain(domain_name)
        
        data = data_generator.generate(domain_config, count)
        
        extension = {
            'json': '.json',
            'jsonl': '.jsonl',
            'csv': '.csv',
            'txt': '.txt',
            'dict': '.pkl'
        }.get(output_format, '.json')
        
        output_file = os.path.join(output_dir, f"{domain_name}_data{extension}")
        data_generator.save_to_file(data, output_file, output_format)
        
        return {
            'domain': domain_name,
            'success': True,
            'count': len(data),
            'file': output_file
        }
        
    except Exception as e:
        return {
            'domain': domain_name,
            'success': False,
            'error': str(e)
        }


def main():
    """主函数"""
    try:
        args = parse_arguments()
        
        # 初始化组件
        domain_manager = DomainManager()
        data_generator = DataGenerator()
        
        # 获取领域列表
        domains = []
        config = None
        
        if args.config:
            config = load_config(args.config)
            domains = config.get('domains', [])
            output_dir = config.get('output_dir', args.output_dir)
            output_format = config.get('format', args.format)
            count = config.get('count', args.count)
            parallel = config.get('parallel', args.parallel)
        else:
            if not args.domains:
                print("错误：请指定领域列表 (--domains) 或配置文件 (--config)")
                return
            
            domains = [d.strip() for d in args.domains.split(',')]
            output_dir = args.output_dir
            output_format = args.format
            count = args.count
            parallel = args.parallel
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n开始批量生成数据...")
        print(f"领域数量: {len(domains)}")
        print(f"每个领域数量: {count}")
        print(f"输出格式: {output_format}")
        print(f"并行处理数: {parallel}")
        print("=" * 60)
        
        # 并行生成
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_domain = {
                executor.submit(
                    generate_domain_data,
                    domain,
                    output_dir,
                    output_format,
                    count,
                    domain_manager,
                    data_generator
                ): domain
                for domain in domains
            }
            
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        print(f"✓ {result['domain']}: {result['count']} 条数据 -> {result['file']}")
                    else:
                        print(f"✗ {result['domain']}: {result['error']}")
                        
                except Exception as e:
                    print(f"✗ {domain}: {str(e)}")
                    results.append({
                        'domain': domain,
                        'success': False,
                        'error': str(e)
                    })
        
        # 输出统计
        print("\n" + "=" * 60)
        print("批量生成结果统计：")
        print(f"总领域数: {len(results)}")
        print(f"成功数: {sum(1 for r in results if r['success'])}")
        print(f"失败数: {sum(1 for r in results if not r['success'])}")
        print(f"总数据量: {sum(r.get('count', 0) for r in results)}")
        
        # 保存生成报告
        report_file = os.path.join(output_dir, f"generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_domains': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'total_data_count': sum(r.get('count', 0) for r in results),
            'results': results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n生成报告已保存: {report_file}")
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()