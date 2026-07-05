#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态数据转换器 - 将文本数据转换为图片/音频
"""

import asyncio
import base64
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class OutputType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class ImageProvider(Enum):
    DALLE = "dalle"
    STABILITY = "stability"
    WANXIANG = "wanxiang"


class AudioProvider(Enum):
    QWEN = "qwen"
    AZURE = "azure"
    ELEVENLABS = "elevenlabs"


@dataclass
class MultimodalConfig:
    output_type: OutputType = OutputType.TEXT
    image_provider: ImageProvider = ImageProvider.WANXIANG
    audio_provider: AudioProvider = AudioProvider.QWEN
    image_style: str = ""
    voice_id: str = "Cherry"
    image_size: str = "1024*1024"
    audio_rate: float = 1.0
    custom_style: str = ""
    custom_requirement: str = ""


class ImagePromptConverter:
    
    STYLE_TEMPLATES = {
        "realistic": "photorealistic, highly detailed, 8k resolution, professional photography",
        "anime": "anime style, vibrant colors, detailed illustration",
        "oil_painting": "oil painting style, classical art, masterpiece",
        "watercolor": "watercolor painting, soft colors, artistic",
        "3d_render": "3D render, octane render, highly detailed",
        "minimalist": "minimalist design, clean lines, simple composition",
        "cyberpunk": "cyberpunk style, neon lights, futuristic",
        "fantasy": "fantasy art, magical, ethereal"
    }
    
    DOMAIN_ENHANCEMENTS = {
        "人工智能": "futuristic technology, AI concept art",
        "医疗健康": "medical illustration, healthcare visualization",
        "金融财经": "financial charts, business visualization",
        "教育培训": "educational illustration, clear diagram",
        "法律法务": "legal concept, professional setting",
        "科技互联网": "technology concept, digital innovation",
        "文化艺术": "artistic visualization, cultural elements"
    }
    
    NEGATIVE_PROMPT = "blurry, low quality, distorted, watermark, text overlay"
    
    def convert(self, text: str, word: str, category: str, style: str = "realistic") -> Dict[str, str]:
        key_concepts = self._extract_key_concepts(text, word)
        base_prompt = f"{word}, {key_concepts}"
        style_prompt = self.STYLE_TEMPLATES.get(style, self.STYLE_TEMPLATES["realistic"])
        domain_prompt = self.DOMAIN_ENHANCEMENTS.get(category, "")
        final_prompt = f"{base_prompt}, {style_prompt}, {domain_prompt}"
        
        return {
            "prompt": final_prompt[:1000],
            "negative_prompt": self.NEGATIVE_PROMPT,
            "word": word,
            "style": style,
            "category": category
        }
    
    def _extract_key_concepts(self, text: str, word: str) -> str:
        sentences = text.replace('\n', ' ').split('。')[:2]
        return ' '.join(sentences).strip()[:300]


class PromptEnhancer:
    """LLM提示词增强器 - 用AI把文本转成精准图片提示词"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._qwen_api = None
    
    def _get_qwen_api(self):
        if self._qwen_api is None and self.api_key:
            try:
                from 千问API集成 import QwenAPI
                self._qwen_api = QwenAPI(self.api_key)
            except ImportError:
                pass
        return self._qwen_api
    
    async def enhance(self, text: str, word: str, category: str = None, style: str = "realistic") -> str:
        """
        用LLM把文本转成精准的图片生成提示词
        
        Args:
            text: 原始文本描述
            word: 关键词
            category: 领域（可选）
            style: 风格
        
        Returns:
            增强后的英文提示词
        """
        qwen_api = self._get_qwen_api()
        
        if not qwen_api:
            return self._fallback_prompt(text, word, style)
        
        prompt = f"""你是AI图片生成提示词专家。请把以下内容转换成精准的英文图片生成提示词。

原始文本：{text}
关键词：{word}
领域：{category or '通用'}
风格：{style}

要求：
1. 输出详细的英文提示词，用于AI图片生成
2. 包含：主体描述、视角、光线、细节、风格、质量要求
3. 如果是医疗/科技等专业领域，使用专业术语
4. 只输出提示词，不要任何解释

示例输出格式：
A detailed [subject], [view/angle], [lighting], [style], [quality], professional, high resolution"""

        try:
            result = qwen_api.call(prompt, max_tokens=300)
            enhanced = result.get("response", "")
            if enhanced and len(enhanced) > 10:
                return enhanced.strip()
        except Exception as e:
            print(f"[提示词增强] LLM调用失败: {e}")
        
        return self._fallback_prompt(text, word, style)
    
    def _fallback_prompt(self, text: str, word: str, style: str) -> str:
        """LLM不可用时的兜底方案"""
        style_map = {
            "realistic": "photorealistic, highly detailed, 8k resolution",
            "anime": "anime style, vibrant colors, detailed illustration",
            "oil_painting": "oil painting style, classical art",
            "watercolor": "watercolor painting, soft colors",
            "3d_render": "3D render, octane render, highly detailed",
            "cyberpunk": "cyberpunk style, neon lights, futuristic",
            "fantasy": "fantasy art, magical, ethereal"
        }
        style_desc = style_map.get(style, style_map["realistic"])
        return f"{word}, {text[:200]}, {style_desc}, professional, high quality"


class MultimodalConverter:
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or {}
        self.prompt_converter = ImagePromptConverter()
        self._init_generators()
        self._init_enhancer()
    
    def _init_enhancer(self):
        """初始化提示词增强器"""
        api_key = self.config.get("dashscope_api_key") or self.config.get("qianwen_api_key")
        self.prompt_enhancer = PromptEnhancer(api_key) if api_key else None
        self.use_llm_enhance = self.config.get("use_llm_enhance", True)
    
    def _init_generators(self):
        self.image_generators = {}
        self.audio_generators = {}
        
        dashscope_key = self.config.get("dashscope_api_key") or self.config.get("qianwen_api_key")
        if dashscope_key:
            self.image_generators[ImageProvider.WANXIANG] = WanxiangImageGenerator(dashscope_key)
            self.audio_generators[AudioProvider.QWEN] = QwenTTSGenerator(dashscope_key)
        
        if self.config.get("openai_api_key"):
            self.image_generators[ImageProvider.DALLE] = DALLEImageGenerator(self.config["openai_api_key"])
        
        if self.config.get("azure_speech_key"):
            self.audio_generators[AudioProvider.AZURE] = AzureTTSGenerator(
                self.config["azure_speech_key"],
                self.config.get("azure_speech_region", "eastasia")
            )
        
        if self.config.get("elevenlabs_api_key"):
            self.audio_generators[AudioProvider.ELEVENLABS] = ElevenLabsTTSGenerator(self.config["elevenlabs_api_key"])
    
    async def convert(self, data: List[Dict], config: MultimodalConfig) -> List[Dict]:
        if config.output_type == OutputType.TEXT:
            return data
        
        import asyncio
        
        async def process_item(item: Dict, index: int) -> Dict:
            converted_item = item.copy()
            
            if config.output_type in [OutputType.IMAGE, OutputType.MULTIMODAL]:
                image_result = await self._generate_image(item, config)
                converted_item.update(image_result)
            
            if config.output_type in [OutputType.AUDIO, OutputType.MULTIMODAL]:
                audio_result = await self._generate_audio(item, config)
                converted_item.update(audio_result)
            
            return converted_item
        
        tasks = [process_item(item, i) for i, item in enumerate(data)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({**data[i], "error": str(result)})
            else:
                final_results.append(result)
        
        return final_results
    
    async def _generate_image(self, item: Dict, config: MultimodalConfig) -> Dict:
        text = item.get("text", "")
        word = item.get("word", "")
        category = item.get("category", "人工智能")
        
        custom_style = getattr(config, 'custom_style', '') or ''
        custom_requirement = getattr(config, 'custom_requirement', '') or ''
        
        if custom_style or custom_requirement:
            prompt_parts = []
            
            if custom_style:
                prompt_parts.append(f"风格：{custom_style}")
            
            if custom_requirement:
                prompt_parts.append(f"具体需求：{custom_requirement}")
            
            if text:
                prompt_parts.append(f"内容：{text}")
            
            prompt = "\n".join(prompt_parts)
            prompt_data = {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted, watermark, text overlay, ugly, deformed"
            }
        elif self.use_llm_enhance and self.prompt_enhancer:
            enhanced_prompt = await self.prompt_enhancer.enhance(
                text=text,
                word=word,
                category=category,
                style=config.image_style
            )
            prompt_data = {
                "prompt": enhanced_prompt,
                "negative_prompt": "blurry, low quality, distorted, watermark, text overlay"
            }
        else:
            prompt_data = self.prompt_converter.convert(
                text=text,
                word=word,
                category=category,
                style=config.image_style
            )
        
        generator = self.image_generators.get(config.image_provider)
        if not generator:
            return {"image_error": f"Image provider {config.image_provider.value} not configured"}
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if config.image_provider == ImageProvider.WANXIANG:
                    result = await generator.generate(
                        prompt=prompt_data["prompt"],
                        negative_prompt=prompt_data["negative_prompt"],
                        size=config.image_size.replace("x", "*"),
                        style=custom_style or config.image_style
                    )
                else:
                    result = await generator.generate(
                        prompt=prompt_data["prompt"],
                        negative_prompt=prompt_data["negative_prompt"],
                        size=config.image_size
                    )
                
                image_url = result.get("image_url")
                if not image_url:
                    return {"image_error": "未获取到图片URL"}
                
                # === 图片验证 ===
                validator = ImageValidator()
                validation = await validator.validate(
                    image_url=image_url,
                    prompt=prompt_data["prompt"],
                    context=text
                )
                
                print(f"[图片验证] 尝试{attempt+1}/{max_retries}, 分数={validation['score']:.2f}, 原因={validation['reason']}")
                
                if validation["is_valid"]:
                    return {
                        "image_url": image_url,
                        "image_prompt": prompt_data["prompt"],
                        "image_prompt_enhanced": self.use_llm_enhance and self.prompt_enhancer is not None,
                        "image_model": result.get("model"),
                        "image_size": config.image_size,
                        "validation": validation
                    }
                else:
                    print(f"[图片验证] 不符合实际，尝试重新生成...")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    else:
                        return {
                            "image_url": image_url,
                            "image_prompt": prompt_data["prompt"],
                            "image_prompt_enhanced": self.use_llm_enhance and self.prompt_enhancer is not None,
                            "image_model": result.get("model"),
                            "image_size": config.image_size,
                            "validation": validation,
                            "image_warning": f"图片可能不符合实际: {validation['reason']}"
                        }
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[图片生成] 尝试{attempt+1}失败: {e}，重试...")
                    await asyncio.sleep(1)
                    continue
                return {"image_error": str(e)}
    
    async def _generate_audio(self, item: Dict, config: MultimodalConfig) -> Dict:
        generator = self.audio_generators.get(config.audio_provider)
        if not generator:
            return {"audio_error": f"Audio provider {config.audio_provider.value} not configured"}
        
        try:
            result = await generator.generate(
                text=item.get("text", ""),
                voice_id=config.voice_id,
                rate=config.audio_rate
            )
            return {
                "audio_base64": result.get("audio_base64"),
                "audio_duration": result.get("duration"),
                "audio_voice": result.get("voice_name", config.voice_id),
                "audio_model": result.get("model"),
                "audio_format": result.get("format", "mp3")
            }
        except Exception as e:
            return {"audio_error": str(e)}


class DALLEImageGenerator:
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/images/generations"
    
    async def generate(self, prompt: str, negative_prompt: str = None,
                       size: str = "1024x1024", quality: str = "standard") -> dict:
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "response_format": "url"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            result = response.json()
        
        return {
            "image_url": result["data"][0]["url"],
            "revised_prompt": result["data"][0].get("revised_prompt", prompt),
            "model": "dall-e-3",
            "size": size
        }


class WanxiangImageGenerator:
    """通义万相图片生成器 - 安全调用模式"""
    
    STYLE_MAP = {
        "realistic": "写实风格，高清摄影",
        "anime": "动漫风格，二次元",
        "oil_painting": "油画风格，艺术画作",
        "watercolor": "水彩风格，淡雅清新",
        "3d_render": "3D渲染，立体效果",
        "minimalist": "极简风格，简洁设计",
        "cyberpunk": "赛博朋克风格，霓虹灯光",
        "fantasy": "奇幻风格，梦幻场景"
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._semaphore = asyncio.Semaphore(5)
        self._request_interval = 4.0
    
    async def generate(self, prompt: str, negative_prompt: str = None,
                       size: str = "1024*1024", style: str = "realistic",
                       n: int = 1) -> dict:
        async with self._semaphore:
            await asyncio.sleep(self._request_interval)
            
            try:
                import dashscope
                from dashscope import ImageSynthesis
            except ImportError:
                raise Exception("dashscope SDK未安装，请运行: pip install dashscope>=1.23.1")
            
            dashscope.api_key = self.api_key
            
            style_desc = self.STYLE_MAP.get(style, "")
            full_prompt = f"{style_desc}，{prompt}" if style_desc else prompt
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ImageSynthesis.call(
                    model="wanx-v1",
                    prompt=full_prompt,
                    n=n,
                    size=size
                )
            )
            
            if response.status_code == 200:
                results = response.output.get("results", [])
                if results:
                    image_url = results[0].get("url", "")
                    return {
                        "image_url": image_url,
                        "model": "wanx-v1",
                        "size": size
                    }
            
            raise Exception(f"通义万相API错误: {response.message if hasattr(response, 'message') else '未知错误'}")


class QwenTTSGenerator:
    """阿里云千问TTS生成器 - 安全调用模式"""
    
    VOICES = {
        "zhichu": "zhichu（女声，知性）",
        "zhiyan": "zhiyan（女声，温柔）",
        "zhida": "zhida（男声，大气）",
        "zhiwei": "zhiwei（男声，温暖）",
        "Cherry": "Cherry（女声，活泼可爱）",
        "Ethan": "Ethan（男声，沉稳大气）",
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._semaphore = asyncio.Semaphore(10)
        self._request_interval = 2.0
    
    async def generate(self, text: str, voice_id: str = "zhichu", rate: float = 1.0) -> dict:
        async with self._semaphore:
            await asyncio.sleep(self._request_interval)
            
            try:
                import dashscope
                from dashscope.audio.tts import SpeechSynthesizer
            except ImportError:
                raise Exception("dashscope SDK未安装，请运行: pip install dashscope>=1.23.1")
            
            dashscope.api_key = self.api_key
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: SpeechSynthesizer.call(
                    model="sambert-zhichu-v1",
                    text=text,
                    voice=voice_id,
                    format="mp3"
                )
            )
            
            if hasattr(result, 'output_audio') and result.output_audio:
                audio_data = result.output_audio
                return {
                    "audio_data": audio_data,
                    "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
                    "duration": round(len(text) / 150 * 60, 2),
                    "voice_id": voice_id,
                    "voice_name": self.VOICES.get(voice_id, voice_id),
                    "model": "sambert-zhichu-v1",
                    "format": "mp3"
                }
            
            raise Exception("千问TTS错误: 无法生成音频")


class AzureTTSGenerator:
    
    VOICES = {
        "zh-CN-XiaoxiaoNeural": "晓晓",
        "zh-CN-YunxiNeural": "云希",
        "zh-CN-YunyangNeural": "云扬",
        "zh-CN-XiaoyiNeural": "晓伊",
        "zh-CN-YunjianNeural": "云健",
    }
    
    def __init__(self, subscription_key: str, region: str = "eastasia"):
        self.subscription_key = subscription_key
        self.region = region
        self.base_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    async def generate(self, text: str, voice_id: str = "zh-CN-XiaoxiaoNeural",
                       rate: float = 1.0) -> dict:
        import httpx
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
        }
        
        ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
            <voice name='{voice_id}'><prosody rate='{rate}'>{text}</prosody></voice>
        </speak>"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.base_url, headers=headers, content=ssml.encode('utf-8'))
            audio_data = response.content
        
        duration = len(text) / 150 * 60 / rate
        
        return {
            "audio_data": audio_data,
            "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
            "duration": round(duration, 2),
            "voice_id": voice_id,
            "voice_name": self.VOICES.get(voice_id, voice_id),
            "format": "mp3"
        }


class ElevenLabsTTSGenerator:
    
    VOICES = {
        "Rachel": "21m00Tcm4TlvDq8ikWAM",
        "Domi": "AZnzlk1XvdvUeBnXmlld",
        "Bella": "EXAVITQu4vr4xnSDxMaL",
        "Antoni": "ErXwobaYiN019PkySvjV",
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
    
    async def generate(self, text: str, voice_id: str = "Rachel", stability: float = 0.5) -> dict:
        import httpx
        
        voice_uuid = self.VOICES.get(voice_id, voice_id)
        url = f"{self.base_url}/{voice_uuid}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": stability, "similarity_boost": 0.75}
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            audio_data = response.content
        
        duration = len(text) / 150 * 60
        
        return {
            "audio_data": audio_data,
            "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
            "duration": round(duration, 2),
            "voice_id": voice_id,
            "model": "eleven_multilingual_v2",
            "format": "mp3"
        }


def get_multimodal_converter(config: Dict = None) -> MultimodalConverter:
    if config is None:
        config = {
            "dashscope_api_key": os.getenv("DASHSCOPE_API_KEY") or os.getenv("QIANWEN_API_KEY"),
            "qianwen_api_key": os.getenv("QIANWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "azure_speech_key": os.getenv("AZURE_SPEECH_KEY"),
            "azure_speech_region": os.getenv("AZURE_SPEECH_REGION", "eastasia"),
            "elevenlabs_api_key": os.getenv("ELEVENLABS_API_KEY")
        }
    return MultimodalConverter(config)


async def convert_to_multimodal(data: List[Dict], output_type: str = "text",
                                image_style: str = "",
                                voice_id: str = "zh-CN-XiaoxiaoNeural",
                                image_requirement: str = "",
                                config: Dict = None) -> List[Dict]:
    converter = get_multimodal_converter(config)
    mm_config = MultimodalConfig(
        output_type=OutputType(output_type),
        image_style=image_style,
        voice_id=voice_id
    )
    mm_config.custom_style = image_style
    mm_config.custom_requirement = image_requirement
    return await converter.convert(data, mm_config)


class ImageValidator:
    """图片验证器 - 使用千问API验证图片是否符合实际"""
    
    UNREALISTIC_KEYWORDS = [
        "漂浮", "悬浮", "违反物理", "不可能", "超现实", "幻觉",
        "变形", "扭曲", "怪物", "外星", "魔法", "奇幻",
        "卡通", "动漫", "二次元", "虚构", "想象"
    ]
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self._qwen_vl = None
    
    def _get_qwen_vl(self):
        if self._qwen_vl is None and self.api_key:
            try:
                import dashscope
                from dashscope import MultiModalConversation
                self._qwen_vl = MultiModalConversation
            except ImportError:
                pass
        return self._qwen_vl
    
    async def validate(self, image_url: str, prompt: str, context: str = "") -> dict:
        """
        验证图片是否符合实际
        
        Args:
            image_url: 图片URL
            prompt: 生成图片时使用的提示词
            context: 上下文（原始文本）
        
        Returns:
            {
                "is_valid": bool,
                "reason": str,
                "score": float  # 0-1, 越高越符合实际
            }
        """
        qwen_vl = self._get_qwen_vl()
        
        if not qwen_vl:
            return {"is_valid": True, "reason": "验证器未配置，默认通过", "score": 1.0}
        
        validation_prompt = f"""请判断这张图片是否符合实际、是否真实可信。

原始需求：{prompt}
上下文：{context}

请检查：
1. 图片内容是否符合物理规律？
2. 图片是否存在明显的变形、扭曲或不可能的结构？
3. 图片是否与原始需求匹配？

请用JSON格式回答：
{{
    "is_realistic": true/false,
    "score": 0-100,
    "reason": "简要说明原因"
}}

只输出JSON，不要其他内容。"""

        try:
            import dashscope
            dashscope.api_key = self.api_key
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": image_url},
                        {"text": validation_prompt}
                    ]
                }
            ]
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: qwen_vl.call(
                    model="qwen-vl-max",
                    messages=messages
                )
            )
            
            if response.status_code == 200:
                result_text = response.output.choices[0].message.content
                
                import json
                try:
                    if isinstance(result_text, (list, dict)):
                        result = result_text
                    else:
                        result = json.loads(result_text)
                    
                    if isinstance(result, dict):
                        score = result.get("score", 50) / 100
                        is_valid = result.get("is_realistic", True) and score >= 0.5
                    else:
                        is_valid = True
                        score = 0.6
                        result = {"reason": "解析结果格式异常"}
                    
                    return {
                        "is_valid": is_valid,
                        "reason": result.get("reason", ""),
                        "score": score
                    }
                except (json.JSONDecodeError, TypeError) as e:
                    is_valid = "true" in str(result_text).lower() and "false" not in str(result_text).lower()
                    return {
                        "is_valid": is_valid,
                        "reason": f"解析失败: {str(e)[:50]}",
                        "score": 0.6 if is_valid else 0.3
                    }
            
            return {"is_valid": True, "reason": f"API调用失败: {response.code}", "score": 0.5}
            
        except Exception as e:
            print(f"[图片验证] 错误: {e}")
            return {"is_valid": True, "reason": f"验证异常: {str(e)}", "score": 0.5}
