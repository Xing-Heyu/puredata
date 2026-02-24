# 支付接口对接文档

## 一、支付宝当面付

### 1. 申请流程
1. 登录 [支付宝开放平台](https://open.alipay.com/)
2. 创建应用，选择"当面付"
3. 配置应用公钥
4. 提交审核（约1-3天）

### 2. Python代码

```python
from alipay import AliPay

# 初始化
alipay = AliPay(
    appid="你的APPID",
    app_notify_url="http://你的域名/api/payment/callback",
    app_private_key_string="你的应用私钥",
    alipay_public_key_string="支付宝公钥",
    sign_type="RSA2",
    debug=False  # True为沙箱环境
)

# 创建订单
def create_alipay_order(order_id, amount, subject):
    order_string = alipay.api_alipay_trade_precreate(
        out_trade_no=order_id,
        total_amount=str(amount),
        subject=subject
    )
    
    # 返回二维码链接
    qr_url = "https://qr.alipay.com/" + order_string.get('qr_code')
    return qr_url

# 查询订单
def query_order(order_id):
    result = alipay.api_alipay_trade_query(out_trade_no=order_id)
    return result.get('trade_status')  # TRADE_SUCCESS 表示支付成功
```

### 3. 回调处理

```python
@app.post("/payment/callback")
async def alipay_callback(request: Request):
    # 获取回调数据
    form = await request.form()
    data = dict(form)
    
    # 验证签名
    if not alipay.verify(data, data.pop('sign'), data.pop('sign_type')):
        return "fail"
    
    # 处理支付成功
    order_id = data.get('out_trade_no')
    trade_status = data.get('trade_status')
    
    if trade_status == 'TRADE_SUCCESS':
        # 更新订单状态，解锁下载
        pass
    
    return "success"
```

---

## 二、微信支付Native

### 1. 申请流程
1. 登录 [微信支付商户平台](https://pay.weixin.qq.com/)
2. 申请Native支付
3. 配置API密钥
4. 提交审核（约1-3天）

### 2. Python代码

```python
import requests
import hashlib
import time
import xml.etree.ElementTree as ET

# 配置
WECHAT_CONFIG = {
    "appid": "你的APPID",
    "mch_id": "你的商户号",
    "api_key": "你的API密钥",
    "notify_url": "http://你的域名/api/payment/wechat/callback"
}

def create_wechat_order(order_id, amount, body):
    """创建微信支付订单"""
    params = {
        "appid": WECHAT_CONFIG["appid"],
        "mch_id": WECHAT_CONFIG["mch_id"],
        "nonce_str": hashlib.md5(str(time.time()).encode()).hexdigest(),
        "body": body,
        "out_trade_no": order_id,
        "total_fee": int(amount * 100),  # 单位：分
        "spbill_create_ip": "127.0.0.1",
        "notify_url": WECHAT_CONFIG["notify_url"],
        "trade_type": "NATIVE"
    }
    
    # 生成签名
    sign = generate_sign(params)
    params["sign"] = sign
    
    # 发送请求
    xml = dict_to_xml(params)
    response = requests.post(
        "https://api.mch.weixin.qq.com/pay/unifiedorder",
        data=xml,
        headers={"Content-Type": "application/xml"}
    )
    
    # 解析响应
    result = xml_to_dict(response.content)
    if result.get("return_code") == "SUCCESS":
        return result.get("code_url")  # 二维码链接
    
    return None

def generate_sign(params):
    """生成签名"""
    sorted_params = sorted(params.items())
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    sign_str += f"&key={WECHAT_CONFIG['api_key']}"
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

def dict_to_xml(data):
    """字典转XML"""
    xml = "<xml>"
    for k, v in data.items():
        xml += f"<{k}>{v}</{k}>"
    xml += "</xml>"
    return xml.encode()

def xml_to_dict(xml_str):
    """XML转字典"""
    root = ET.fromstring(xml_str)
    return {child.tag: child.text for child in root}
```

---

## 三、简化方案（推荐初期使用）

### 使用第三方聚合支付

| 平台 | 特点 | 费率 |
|------|------|------|
| 易支付 | 个人可用，接入简单 | 1-2% |
| 虎皮椒 | 个人可用，支持支付宝/微信 | 1% |
| XorPay | 个人可用，即时到账 | 1% |

### 易支付对接示例

```python
import requests

YIPAY_CONFIG = {
    "api_url": "https://你的易支付域名/submit.php",
    "pid": "你的商户ID",
    "key": "你的商户密钥"
}

def create_yipay_order(order_id, amount, name):
    """创建易支付订单"""
    params = {
        "pid": YIPAY_CONFIG["pid"],
        "type": "alipay",  # alipay或wxpay
        "out_trade_no": order_id,
        "notify_url": "http://你的域名/api/payment/callback",
        "return_url": "http://你的域名/success",
        "name": name,
        "money": str(amount)
    }
    
    # 生成签名
    sign_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    sign_str += YIPAY_CONFIG["key"]
    params["sign"] = hashlib.md5(sign_str.encode()).hexdigest()
    params["sign_type"] = "MD5"
    
    # 返回支付链接
    return YIPAY_CONFIG["api_url"] + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
```

---

## 四、初期建议

### 最简方案：手动发卡

1. 用户扫码付款（个人收款码）
2. 用户截图发给客服
3. 客服手动发送下载链接

**优点**：
- 无需对接API
- 无手续费
- 快速上线

**缺点**：
- 人工成本
- 无法自动化

---

## 五、定价建议

| 数量 | 价格 | 成本 | 利润 |
|------|------|------|------|
| 100条 | 免费 | ¥0 | 获客 |
| 500条 | ¥9.9 | ¥0.02 | ¥9.88 |
| 1000条 | ¥19.9 | ¥0.04 | ¥19.86 |
| 5000条 | ¥49.9 | ¥0.2 | ¥49.7 |
| 10000条 | ¥99.9 | ¥0.4 | ¥99.5 |

**说明**：成本主要是千问API，约¥0.0004/条