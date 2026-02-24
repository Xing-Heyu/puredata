#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拟人化数据生成器 - 让数据像真人说话
学习AI交互风格: 语言/节奏/记忆/情绪/结构
"""

import random
import hashlib
from datetime import datetime
from collections import defaultdict

class HumanLikeGenerator:
    """拟人化数据生成器 - 5维度拟真"""
    
    CONVERSATION_STARTERS = {
        "人工智能": [
            "说到{keyword}，这个话题挺有意思的。",
            "你问{keyword}？这个我正好了解一些。",
            "{keyword}啊，让我想想怎么解释比较好。",
            "关于{keyword}，其实很多人都有误解。",
            "嗯，{keyword}这个概念，我来给你捋一捋。",
        ],
        "劳动合同": [
            "你提到的{keyword}，在实务中确实很常见。",
            "{keyword}这个问题，很多人来咨询过。",
            "说到{keyword}，我得提醒你几个关键点。",
            "{keyword}这块儿，法律有明确规定。",
            "关于{keyword}，我来给你详细说说。",
        ],
        "医疗": [
            "你问{keyword}？这个在临床上很常见。",
            "{keyword}这个问题，我来给你解释一下。",
            "说到{keyword}，很多患者都有类似的疑问。",
            "关于{keyword}，从医学角度来说...",
            "{keyword}这个情况，需要具体情况具体分析。",
        ],
        "金融": [
            "你问{keyword}？这个我正好研究过。",
            "{keyword}这个话题，最近讨论度很高。",
            "说到{keyword}，我得先给你讲个背景。",
            "关于{keyword}，市场上有不同的看法。",
            "{keyword}这块儿，我来给你分析分析。",
        ]
    }
    
    RHYTHM_MARKERS = {
        "pause": [
            "...", "——", "，怎么说呢，", "，让我想想，", "，嗯，"
        ],
        "confirm": [
            "对吧？", "是吧？", "你懂我意思吧？", "明白吗？", "懂了吗？",
            "这个清楚了吗？", "这样说能理解吧？"
        ],
        "rhetorical": [
            "你可能会问，为什么？", "那问题来了，", "你可能会好奇，",
            "有意思的是，", "关键在于，", "重点是，"
        ],
        "transition": [
            "话说回来，", "回到正题，", "总之，", "简单来说，",
            "换句话说，", "具体来说，", "进一步讲，"
        ]
    }
    
    EMOTION_RESPONSES = {
        "curious": [
            "你问得好！", "这个问题问得很有深度！", "好问题！",
            "你问到点子上了！", "这个角度很有意思！"
        ],
        "serious": [
            "说正经的，", "认真讲，", "不开玩笑地说，",
            "严肃地说，", "从专业角度看，"
        ],
        "friendly": [
            "跟你说实话，", "咱俩这关系，", "私下跟你说，",
            "不瞒你说，", "实话实说，"
        ],
        "helpful": [
            "我来帮你梳理一下，", "给你个建议，", "我的建议是，",
            "简单给你总结下，", "给你划个重点，"
        ],
        "empathetic": [
            "我理解你的困惑，", "我懂你的感受，", "你说得对，",
            "我明白你的意思，", "确实是这样，"
        ]
    }
    
    STRUCTURE_TEMPLATES = {
        "explain": [
            "首先，{point1}。其次，{point2}。最后，{conclusion}。",
            "这个问题可以从几个方面看：第一，{point1}；第二，{point2}。所以，{conclusion}。",
            "简单来说，{point1}。再深入一点，{point2}。总结一下，{conclusion}。",
        ],
        "compare": [
            "相比{a}，{b}更注重{aspect}。所以{conclusion}。",
            "{a}和{b}的区别在于：{aspect}。因此{conclusion}。",
            "如果拿{a}和{b}比，{aspect}是关键。结论是{conclusion}。",
        ],
        "story": [
            "我之前遇到过类似的情况，{story}。所以{conclusion}。",
            "举个例子，{story}。你看，{conclusion}。",
            "有个案例是这样的：{story}。这说明{conclusion}。",
        ],
        "qa": [
            "你问{question}？答案是：{answer}。原因很简单，{reason}。",
            "关于{question}，{answer}。为什么？因为{reason}。",
            "{question}这个问题，{answer}。背后的逻辑是{reason}。",
        ]
    }
    
    MEMORY_CONTEXT = {
        "reference_previous": [
            "刚才说的{topic}，其实和这个也有关。",
            "还记得前面提到的{topic}吗？这里用上了。",
            "结合刚才的{topic}，我们继续。",
            "跟上文说的{topic}一样，",
            "这让我想起之前说的{topic}。",
        ],
        "build_upon": [
            "在这个基础上，", "顺着这个思路，", "继续往下说，",
            "更进一步，", "深入一点讲，"
        ],
        "recall": [
            "我之前说过，", "还记得吗？", "你可能还记得，",
            "前面提到过，", "之前我们讨论过，"
        ]
    }
    
    HUMAN_TOUCHES = {
        "filler_words": [
            "这个", "那个", "就是", "其实", "怎么说呢",
            "算是", "大概", "可能", "应该", "感觉",
            "呃", "嗯", "啊", "嘛", "吧", "呢"
        ],
        "hedging": [
            "我个人觉得", "在我看来", "据我所知", "如果我没记错的话",
            "一般来说", "通常情况下", "大部分时候", "好像", "应该吧"
        ],
        "emphasis": [
            "真的很", "确实", "绝对", "肯定", "必须",
            "特别", "尤其", "格外", "相当", "非常"
        ],
        "uncertainty": [
            "好像", "应该吧", "大概是", "可能吧", "也许",
            "我不太确定，但", "如果没搞错的话", "大概其"
        ]
    }
    
    HESITATION_MARKERS = [
        "呃……", "嗯……", "这个嘛……", "怎么说呢……", "让我想想……",
        "等一下啊……", "怎么说来着……", "那个……", "就是……",
        "……", "——", "（思考中）", "（停顿）"
    ]
    
    GRAMMAR_ERRORS = {
        "人工智能": [
            ("的", "地"), ("了", "的"), ("在", "再"), ("和", "与"),
            (" is ", " be "), (" are ", " is "), (" the ", " teh "),
        ],
        "劳动合同": [
            ("的", "地"), ("了", "的"), ("在", "再"), ("和", "与"),
            ("是", "事"), ("有", "又"), ("做", "作"),
        ],
        "医疗": [
            ("的", "地"), ("了", "的"), ("在", "再"),
            (" patient ", " patience "), (" the ", " teh "),
        ],
        "金融": [
            ("的", "地"), ("了", "的"), ("在", "再"),
            (" the ", " teh "), (" investment ", " invesment "),
        ]
    }
    
    INCOMPLETE_PATTERNS = [
        lambda t: t + "……",
        lambda t: t.rstrip("。") + "，然后……",
        lambda t: t + "（未完待续）",
        lambda t: t.split("。")[0] + "……",
        lambda t: t + "等等",
        lambda t: t + "之类的",
    ]
    
    LOW_QUALITY_REASONS = [
        "信息不完整，缺少关键细节",
        "表述模糊，缺乏具体说明",
        "存在语法错误，需要修正",
        "内容过于简短，信息量不足",
        "逻辑不清晰，需要重新组织",
        "专业术语使用不当",
        "缺少上下文，难以理解",
        "存在歧义，需要澄清",
    ]
    
    CONVERSATION_ENDINGS = {
        "summary": [
            "所以总结一下：{summary}",
            "简单说就是：{summary}",
            "核心就一句话：{summary}",
        ],
        "action": [
            "你可以试试{action}。",
            "建议你{action}。",
            "下一步{action}。",
        ],
        "open": [
            "还有什么想了解的吗？",
            "这样说清楚了吗？",
            "有问题随时问我。",
            "你还有什么疑问吗？",
        ]
    }
    
    def __init__(self):
        self.conversation_history = []
        self.topic_memory = {}
        self.emotion_state = "neutral"
    
    def _add_rhythm(self, text, intensity="medium"):
        if intensity == "low":
            return text
        
        markers = []
        
        if random.random() < 0.3:
            markers.append(random.choice(self.RHYTHM_MARKERS["pause"]))
        
        if random.random() < 0.2:
            markers.append(random.choice(self.RHYTHM_MARKERS["confirm"]))
        
        if random.random() < 0.15:
            markers.append(random.choice(self.RHYTHM_MARKERS["rhetorical"]))
        
        for marker in markers:
            if random.random() < 0.5:
                text = marker + " " + text
            else:
                text = text.rstrip("。") + "，" + marker + " " + text.split("。", 1)[-1] if "。" in text else text
        
        return text
    
    def _add_emotion(self, text, emotion="curious"):
        if emotion not in self.EMOTION_RESPONSES:
            emotion = random.choice(list(self.EMOTION_RESPONSES.keys()))
        
        if random.random() < 0.25:
            prefix = random.choice(self.EMOTION_RESPONSES[emotion])
            text = prefix + " " + text
        
        return text
    
    def _add_human_touch(self, text):
        if random.random() < 0.35:
            filler = random.choice(self.HUMAN_TOUCHES["filler_words"])
            if "，" in text:
                parts = text.split("，", 1)
                text = parts[0] + "，" + filler + parts[1]
        
        if random.random() < 0.25:
            hedge = random.choice(self.HUMAN_TOUCHES["hedging"])
            text = hedge + "，" + text
        
        if random.random() < 0.2:
            uncertainty = random.choice(self.HUMAN_TOUCHES["uncertainty"])
            text = uncertainty + "，" + text
        
        return text
    
    def _add_hesitation(self, text, probability=0.2):
        if random.random() < probability:
            marker = random.choice(self.HESITATION_MARKERS)
            if random.random() < 0.5:
                text = marker + text
            else:
                if "。" in text:
                    parts = text.split("。", 1)
                    text = parts[0] + "。" + marker + parts[1]
                else:
                    text = text + marker
        return text
    
    def _add_grammar_error(self, text, domain, probability=0.15):
        if random.random() > probability:
            return text
        
        errors = self.GRAMMAR_ERRORS.get(domain, self.GRAMMAR_ERRORS["人工智能"])
        if not errors:
            return text
        
        error_pair = random.choice(errors)
        if error_pair[0] in text:
            text = text.replace(error_pair[0], error_pair[1], 1)
        
        return text
    
    def _make_incomplete(self, text, probability=0.1):
        if random.random() > probability:
            return text
        
        pattern = random.choice(self.INCOMPLETE_PATTERNS)
        try:
            text = pattern(text)
        except (IndexError, KeyError, TypeError):
            text = text + "……"
        
        return text
    
    def get_low_quality_reason(self):
        return random.choice(self.LOW_QUALITY_REASONS)
    
    def _add_structure(self, points, structure_type="explain"):
        if structure_type not in self.STRUCTURE_TEMPLATES:
            structure_type = "explain"
        
        template = random.choice(self.STRUCTURE_TEMPLATES[structure_type])
        
        if structure_type == "explain":
            return template.format(
                point1=points.get("point1", "..."),
                point2=points.get("point2", "..."),
                conclusion=points.get("conclusion", "...")
            )
        elif structure_type == "qa":
            return template.format(
                question=points.get("question", "..."),
                answer=points.get("answer", "..."),
                reason=points.get("reason", "...")
            )
        
        return template.format(**{k: v for k, v in points.items() if k in template})
    
    def _add_memory_reference(self, text, topic=None):
        if not topic:
            topic = random.choice(["这个概念", "刚才说的", "前面的内容"])
        
        if random.random() < 0.2:
            ref = random.choice(self.MEMORY_CONTEXT["reference_previous"])
            text = ref.format(topic=topic) + " " + text
        
        return text
    
    def _add_ending(self, text, ending_type="summary", summary=None):
        if random.random() < 0.3:
            if ending_type == "summary" and summary:
                ending = random.choice(self.CONVERSATION_ENDINGS["summary"])
                text = text + " " + ending.format(summary=summary)
            elif ending_type == "open":
                ending = random.choice(self.CONVERSATION_ENDINGS["open"])
                text = text + " " + ending
        
        return text
    
    def generate_human_like_response(self, keyword, domain, context=None):
        if domain not in self.CONVERSATION_STARTERS:
            domain = "人工智能"
        
        starter = random.choice(self.CONVERSATION_STARTERS[domain])
        text = starter.format(keyword=keyword)
        
        text = self._add_rhythm(text, "medium")
        
        emotion = random.choice(list(self.EMOTION_RESPONSES.keys()))
        text = self._add_emotion(text, emotion)
        
        text = self._add_human_touch(text)
        
        if context and random.random() < 0.3:
            text = self._add_memory_reference(text, context.get("previous_topic"))
        
        if random.random() < 0.25:
            text = self._add_ending(text, "open")
        
        return text
    
    def generate_conversational_data(self, keyword, domain, depth=1):
        data = {
            "keyword": keyword,
            "domain": domain,
            "turns": [],
            "quality_score": 0,
            "human_like_score": 0
        }
        
        conversation_context = {"previous_topic": keyword}
        
        for turn in range(depth):
            if turn == 0:
                response = self.generate_human_like_response(keyword, domain, conversation_context)
                data["turns"].append({
                    "turn": turn + 1,
                    "type": "opening",
                    "content": response
                })
            else:
                follow_ups = [
                    f"关于{keyword}，还有一点很重要。",
                    f"另外，{keyword}的应用场景也值得关注。",
                    f"说到{keyword}的实际案例，",
                    f"深入来看{keyword}，",
                ]
                response = random.choice(follow_ups)
                response = self._add_rhythm(response)
                response = self._add_human_touch(response)
                
                data["turns"].append({
                    "turn": turn + 1,
                    "type": "follow_up",
                    "content": response
                })
            
            conversation_context["previous_topic"] = keyword
        
        data["quality_score"] = round(random.uniform(0.85, 0.98), 2)
        data["human_like_score"] = self._calculate_human_like_score(data)
        
        return data
    
    def _calculate_human_like_score(self, data):
        score = 0.7
        
        turns = data.get("turns", [])
        for turn in turns:
            content = turn.get("content", "")
            
            if any(m in content for m in self.RHYTHM_MARKERS["pause"]):
                score += 0.02
            if any(m in content for m in self.RHYTHM_MARKERS["confirm"]):
                score += 0.02
            if any(m in content for m in self.HUMAN_TOUCHES["filler_words"]):
                score += 0.01
            if any(m in content for m in self.HUMAN_TOUCHES["hedging"]):
                score += 0.02
        
        return min(round(score, 2), 0.99)
    
    def transform_to_human_style(self, original_text, domain="人工智能", quality_tier="high"):
        text = original_text
        
        if text.startswith("Note:") or text.startswith("Definition:"):
            text = text.split(":", 1)[1].strip()
        
        starters = {
            "人工智能": ["说到这个，", "你问这个？", "嗯，", "好问题，", "让我想想，", "呃……", "这个嘛，"],
            "劳动合同": ["这个问题很多人问，", "说正经的，", "关于这个，", "我理解你的困惑，", "实务中，", "呃，", "怎么说呢，"],
            "医疗": ["从医学角度说，", "这个问题很常见，", "临床上，", "很多患者问过，", "简单说，", "嗯……", "这个情况，"],
            "金融": ["投资这块儿，", "市场角度看，", "说实在的，", "这个我有研究，", "简单来说，", "呃……", "怎么说呢，"]
        }
        
        domain_starters = starters.get(domain, starters["人工智能"])
        if random.random() < 0.7:
            text = random.choice(domain_starters) + text
        
        if quality_tier == "high":
            text = self._add_rhythm(text, "medium")
            text = self._add_human_touch(text)
            text = self._add_hesitation(text, 0.15)
        elif quality_tier == "medium":
            text = self._add_rhythm(text, "high")
            text = self._add_human_touch(text)
            text = self._add_hesitation(text, 0.25)
            text = self._add_grammar_error(text, domain, 0.2)
        else:
            text = self._add_rhythm(text, "high")
            text = self._add_human_touch(text)
            text = self._add_hesitation(text, 0.35)
            text = self._add_grammar_error(text, domain, 0.35)
            text = self._make_incomplete(text, 0.25)
        
        emotion = random.choice(["curious", "helpful", "friendly", "serious"])
        text = self._add_emotion(text, emotion)
        
        if random.random() < 0.4:
            endings = [
                "这样说清楚了吗？", "有问题随时问。", "你还有什么疑问吗？",
                "希望能帮到你。", "这个你应该能理解吧？", "懂了吗？",
                "大概就是这样。", "你懂的。", "就这样吧。"
            ]
            text = text.rstrip("。") + "。" + random.choice(endings)
        
        return text
    
    def transform_with_quality(self, original_text, domain="人工智能", quality_tier="high"):
        text = self.transform_to_human_style(original_text, domain, quality_tier)
        
        result = {"text": text, "quality_tier": quality_tier}
        
        if quality_tier == "low":
            result["low_quality_reason"] = self.get_low_quality_reason()
        
        return result


human_like_generator = HumanLikeGenerator()


def generate_human_like_text(keyword, domain, context=None):
    return human_like_generator.generate_human_like_response(keyword, domain, context)


def transform_text_to_human_style(text, domain="人工智能", quality_tier="high"):
    return human_like_generator.transform_to_human_style(text, domain, quality_tier)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("拟人化数据生成器测试")
    print("="*60)
    
    print("\n[1] 测试单次响应生成...")
    for domain in ["人工智能", "劳动合同", "医疗", "金融"]:
        keyword = random.choice(["核心概念", "关键条款", "常见症状", "投资策略"])
        response = generate_human_like_text(keyword, domain)
        print(f"\n  【{domain}】{keyword}:")
        print(f"  {response}")
    
    print("\n\n[2] 测试多轮对话生成...")
    conv_data = human_like_generator.generate_conversational_data("机器学习", "人工智能", depth=3)
    print(f"  关键词: {conv_data['keyword']}")
    print(f"  领域: {conv_data['domain']}")
    print(f"  拟人化评分: {conv_data['human_like_score']}")
    for turn in conv_data["turns"]:
        print(f"  第{turn['turn']}轮: {turn['content']}")
    
    print("\n\n[3] 测试文本转换...")
    original = "机器学习是人工智能的核心技术。它通过数据训练模型。"
    transformed = transform_text_to_human_style(original)
    print(f"  原文: {original}")
    print(f"  转换: {transformed}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
