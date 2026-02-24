#!/usr/bin/env python3
"""
政策更新脚本 - 每月自动更新政策发现页面
使用方法: python update_policy.py
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

POLICY_FILE = os.path.join(os.path.dirname(__file__), 'policy_data.json')

DEFAULT_POLICIES = {
    "last_update": datetime.now().strftime("%Y年%m月"),
    "categories": {
        "subsidy": {
            "name": "补贴政策",
            "icon": "💰",
            "color": "var(--success)",
            "policies": [
                {
                    "title": "数据要素市场化配置改革",
                    "desc": "支持企业开展数据资产评估、数据交易等业务，符合条件的可申请专项资金补贴。",
                    "url": "https://www.gov.cn/zhengce/"
                },
                {
                    "title": "人工智能产业发展专项资金",
                    "desc": "对AI训练数据集建设、数据标注等项目给予资金支持，最高可达500万元。",
                    "url": "https://www.miit.gov.cn/"
                },
                {
                    "title": "数字经济创新发展试验区",
                    "desc": "试验区企业可享受数据要素市场建设相关补贴和税收优惠。",
                    "url": "https://www.ndrc.gov.cn/"
                }
            ]
        },
        "tax": {
            "name": "税收优惠",
            "icon": "📊",
            "color": "var(--primary)",
            "policies": [
                {
                    "title": "高新技术企业认定",
                    "desc": "数据服务企业可申请高新技术企业认定，享受15%企业所得税优惠税率。",
                    "url": "https://fuwu.most.gov.cn/"
                },
                {
                    "title": "研发费用加计扣除",
                    "desc": "AI数据训练相关研发费用可享受100%加计扣除政策。",
                    "url": "https://www.chinatax.gov.cn/chinatax/c102061/c102072/c102077/index.html"
                },
                {
                    "title": "软件企业税收优惠",
                    "desc": "符合条件的软件企业可享受\"两免三减半\"企业所得税优惠。",
                    "url": "https://www.chinatax.gov.cn/chinatax/n810341/n810765/n812191/n812199/c1188025/content.html"
                }
            ]
        },
        "certification": {
            "name": "资质认证",
            "icon": "🏛️",
            "color": "var(--warning)",
            "policies": [
                {
                    "title": "数据管理能力成熟度(DCMM)",
                    "desc": "通过DCMM认证的企业可获得地方补贴，最高50万元。",
                    "url": "https://www.dcmm-cfeii.com/"
                },
                {
                    "title": "信息安全等级保护",
                    "desc": "数据安全合规认证，部分行业必备资质，可申请认证补贴。",
                    "url": "https://www.djbh.net/"
                },
                {
                    "title": "ISO 27001认证",
                    "desc": "信息安全管理体系认证，提升企业数据安全信誉度。",
                    "url": "https://www.iso.org/isoiec-27001-information-security.html"
                }
            ]
        },
        "industry": {
            "name": "产业政策",
            "icon": "📈",
            "color": "var(--danger)",
            "policies": [
                {
                    "title": "\"数据要素×\"三年行动计划",
                    "desc": "国家数据局发布，重点支持工业、金融、医疗等12个行业数据应用。",
                    "url": "https://www.ndrc.gov.cn/"
                },
                {
                    "title": "人工智能+行动",
                    "desc": "推动AI与实体经济深度融合，支持AI训练数据集建设。",
                    "url": "https://www.gov.cn/"
                },
                {
                    "title": "数字中国建设整体布局规划",
                    "desc": "国家级战略规划，数据要素市场建设是重点任务。",
                    "url": "https://www.gov.cn/"
                }
            ]
        }
    },
    "resources": [
        {"name": "国务院政策文件", "desc": "中央政策发布", "url": "https://www.gov.cn/zhengce/", "icon": "🏛️"},
        {"name": "国家发改委", "desc": "产业政策制定", "url": "https://www.ndrc.gov.cn/", "icon": "📊"},
        {"name": "工信部", "desc": "数字经济政策", "url": "https://www.miit.gov.cn/", "icon": "🏭"},
        {"name": "国家税务总局", "desc": "税收优惠政策", "url": "https://www.chinatax.gov.cn/", "icon": "💰"}
    ]
}

def load_policies():
    if os.path.exists(POLICY_FILE):
        with open(POLICY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_POLICIES

def save_policies(policies):
    policies["last_update"] = datetime.now().strftime("%Y年%m月")
    with open(POLICY_FILE, 'w', encoding='utf-8') as f:
        json.dump(policies, f, ensure_ascii=False, indent=2)
    print(f"✅ 政策数据已保存，更新时间: {policies['last_update']}")

def check_url(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return True
        return False
    except Exception as e:
        return False

def audit_links():
    policies = load_policies()
    print("\n🔍 开始审查链接...\n")
    
    broken_links = []
    total_links = 0
    ok_links = 0
    
    for cat_key, cat in policies["categories"].items():
        print(f"检查 {cat['icon']} {cat['name']}...")
        for p in cat["policies"]:
            total_links += 1
            url = p["url"]
            title = p["title"]
            
            if check_url(url):
                ok_links += 1
                print(f"  ✅ {title}")
            else:
                broken_links.append((cat_key, title, url))
                print(f"  ❌ {title} - {url}")
    
    print(f"\n检查资源链接...")
    for r in policies["resources"]:
        total_links += 1
        if check_url(r["url"]):
            ok_links += 1
            print(f"  ✅ {r['name']}")
        else:
            broken_links.append(("resources", r["name"], r["url"]))
            print(f"  ❌ {r['name']} - {r['url']}")
    
    print(f"\n" + "="*50)
    print(f"📊 审查结果:")
    print(f"   总链接数: {total_links}")
    print(f"   正常: {ok_links}")
    print(f"   失效: {len(broken_links)}")
    
    if broken_links:
        print(f"\n❌ 失效链接列表:")
        for cat, title, url in broken_links:
            print(f"   [{cat}] {title}: {url}")
        return False
    else:
        print(f"\n✅ 所有链接正常!")
        return True

def fix_broken_links():
    policies = load_policies()
    fixed = 0
    
    known_fixes = {
        "https://www.dcmma.org.cn/": "https://www.dcmm-cfeii.com/",
        "https://www.dcmm.org.cn/": "https://www.dcmm-cfeii.com/",
        "https://www.iso.org/": "https://www.iso.org/isoiec-27001-information-security.html",
        "https://www.innocom.gov.cn/": "https://fuwu.most.gov.cn/",
        "https://www.chinatorch.gov.cn/": "https://fuwu.most.gov.cn/",
        "https://hjrz.chinatorch.org.cn/": "https://fuwu.most.gov.cn/",
    }
    
    for cat_key, cat in policies["categories"].items():
        for p in cat["policies"]:
            old_url = p["url"]
            if old_url in known_fixes:
                p["url"] = known_fixes[old_url]
                print(f"🔧 修复: {p['title']}")
                print(f"   旧: {old_url}")
                print(f"   新: {p['url']}")
                fixed += 1
    
    for r in policies["resources"]:
        old_url = r["url"]
        if old_url in known_fixes:
            r["url"] = known_fixes[old_url]
            print(f"🔧 修复: {r['name']}")
            fixed += 1
    
    if fixed > 0:
        save_policies(policies)
        print(f"\n✅ 共修复 {fixed} 个链接")
    else:
        print("没有需要修复的链接")
    
    return fixed

def add_policy(category_key, title, desc, url):
    policies = load_policies()
    if category_key in policies["categories"]:
        policies["categories"][category_key]["policies"].append({
            "title": title,
            "desc": desc,
            "url": url
        })
        save_policies(policies)
        print(f"✅ 已添加政策: {title}")
    else:
        print(f"❌ 分类不存在: {category_key}")

def remove_policy(category_key, title):
    policies = load_policies()
    if category_key in policies["categories"]:
        original_count = len(policies["categories"][category_key]["policies"])
        policies["categories"][category_key]["policies"] = [
            p for p in policies["categories"][category_key]["policies"] 
            if p["title"] != title
        ]
        if len(policies["categories"][category_key]["policies"]) < original_count:
            save_policies(policies)
            print(f"✅ 已删除政策: {title}")
        else:
            print(f"❌ 未找到政策: {title}")
    else:
        print(f"❌ 分类不存在: {category_key}")

def update_last_update():
    policies = load_policies()
    policies["last_update"] = datetime.now().strftime("%Y年%m月")
    save_policies(policies)
    print(f"✅ 更新时间已更新: {policies['last_update']}")

def list_policies():
    policies = load_policies()
    print(f"\n📋 政策列表 (最后更新: {policies['last_update']})\n")
    for key, cat in policies["categories"].items():
        print(f"{cat['icon']} {cat['name']}:")
        for p in cat["policies"]:
            print(f"   - {p['title']}")
            print(f"     {p['desc'][:50]}...")
            print(f"     🔗 {p['url']}")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python update_policy.py list              # 列出所有政策")
        print("  python update_policy.py update            # 更新时间戳")
        print("  python update_policy.py audit             # 审查链接可用性")
        print("  python update_policy.py fix               # 自动修复已知失效链接")
        print("  python update_policy.py add <分类> <标题> <描述> <链接>  # 添加政策")
        print("  python update_policy.py remove <分类> <标题>  # 删除政策")
        print("\n分类: subsidy(补贴), tax(税收), certification(资质), industry(产业)")
        list_policies()
    else:
        cmd = sys.argv[1]
        
        if cmd == "list":
            list_policies()
        elif cmd == "update":
            update_last_update()
        elif cmd == "audit":
            audit_links()
        elif cmd == "fix":
            fix_broken_links()
        elif cmd == "add" and len(sys.argv) >= 6:
            add_policy(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        elif cmd == "remove" and len(sys.argv) >= 4:
            remove_policy(sys.argv[2], sys.argv[3])
        else:
            print("❌ 参数错误")
