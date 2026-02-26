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
    image_style: str = "realistic"
    voice_id: str = "Cherry"
    image_size: str = "1024*1024"
    audio_rate: float = 1.0


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


class MultimodalConverter:
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or {}
        self.prompt_converter = ImagePromptConverter()
        self._init_generators()
    
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
        
        results = []
        for item in data:
            converted_item = item.copy()
            
            if config.output_type in [OutputType.IMAGE, OutputType.MULTIMODAL]:
                image_result = await self._generate_image(item, config)
                converted_item.update(image_result)
            
            if config.output_type in [OutputType.AUDIO, OutputType.MULTIMODAL]:
                audio_result = await self._generate_audio(item, config)
                converted_item.update(audio_result)
            
            results.append(converted_item)
        
        return results
    
    async def _generate_image(self, item: Dict, config: MultimodalConfig) -> Dict:
        prompt_data = self.prompt_converter.convert(
            text=item.get("text", ""),
            word=item.get("word", ""),
            category=item.get("category", "人工智能"),
            style=config.image_style
        )
        
        generator = self.image_generators.get(config.image_provider)
        if not generator:
            return {"image_error": f"Image provider {config.image_provider.value} not configured"}
        
        try:
            if config.image_provider == ImageProvider.WANXIANG:
                result = await generator.generate(
                    prompt=prompt_data["prompt"],
                    negative_prompt=prompt_data["negative_prompt"],
                    size=config.image_size.replace("x", "*"),
                    style=config.image_style
                )
            else:
                result = await generator.generate(
                    prompt=prompt_data["prompt"],
                    negative_prompt=prompt_data["negative_prompt"],
                    size=config.image_size
                )
            return {
                "image_url": result.get("image_url"),
                "image_prompt": prompt_data["prompt"],
                "image_model": result.get("model"),
                "image_size": config.image_size
            }
        except Exception as e:
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
    """通义万相图片生成器 - 使用wan2.6-t2i模型"""
    
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
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    async def generate(self, prompt: str, negative_prompt: str = None,
                       size: str = "1024*1024", style: str = "realistic",
                       n: int = 1) -> dict:
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        style_desc = self.STYLE_MAP.get(style, "")
        full_prompt = f"{style_desc}，{prompt}" if style_desc else prompt
        
        payload = {
            "model": "wan2.6-t2i",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "negative_prompt": negative_prompt or "",
                "prompt_extend": True,
                "watermark": False,
                "n": n,
                "size": size
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            result = response.json()
            
            if "output" in result and "choices" in result["output"]:
                choices = result["output"]["choices"]
                if choices and "message" in choices[0]:
                    content = choices[0]["message"].get("content", [])
                    if content and len(content) > 0:
                        image_url = content[0].get("image", "")
                        return {
                            "image_url": image_url,
                            "model": "wan2.6-t2i",
                            "size": size
                        }
            
            if "code" in result and result["code"] != "Success":
                raise Exception(f"通义万相API错误: {result.get('message', result)}")
            
            raise Exception(f"通义万相API返回格式异常: {result}")


class QwenTTSGenerator:
    """阿里云千问TTS生成器 - 使用qwen3-tts-flash模型"""
    
    VOICES = {
        "Cherry": "Cherry（女声，活泼可爱）",
        "Ethan": "Ethan（男声，沉稳大气）",
        "Luna": "Luna（女声，温柔甜美）",
        "Marcus": "Marcus（男声，磁性低沉）",
        "Serena": "Serena（女声，知性优雅）",
        "Thea": "Thea（女声，清新自然）",
        "Alex": "Alex（男声，阳光活力）",
        "Bella": "Bella（女声，俏皮灵动）",
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate(self, text: str, voice_id: str = "Cherry") -> dict:
        try:
            import dashscope
            from dashscope.audio.qwen_tts import SpeechSynthesizer
        except ImportError:
            raise Exception("dashscope SDK未安装，请运行: pip install dashscope>=1.23.1")
        
        dashscope.api_key = self.api_key
        
        response = SpeechSynthesizer.call(
            model="qwen3-tts-flash",
            api_key=self.api_key,
            text=text,
            voice=voice_id
        )
        
        if response.status_code == 200:
            audio_data = response.output_audio
            
            return {
                "audio_data": audio_data,
                "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
                "duration": round(len(text) / 150 * 60, 2),
                "voice_id": voice_id,
                "voice_name": self.VOICES.get(voice_id, voice_id),
                "model": "qwen3-tts-flash",
                "format": "mp3"
            }
        else:
            raise Exception(f"千问TTS错误: {response.message}")


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
                                image_style: str = "realistic",
                                voice_id: str = "zh-CN-XiaoxiaoNeural",
                                config: Dict = None) -> List[Dict]:
    converter = get_multimodal_converter(config)
    mm_config = MultimodalConfig(
        output_type=OutputType(output_type),
        image_style=image_style,
        voice_id=voice_id
    )
    return await converter.convert(data, mm_config)
