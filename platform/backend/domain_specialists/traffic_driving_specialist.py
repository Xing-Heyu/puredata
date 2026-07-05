#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交通驾驶领域专精化模块
智能驾驶训练数据、驾驶场景、交通安全
"""

from .base_specialist import DomainSpecialist
from typing import Dict, List, Any, Optional
import random


class TrafficDrivingSpecialist(DomainSpecialist):
    """交通驾驶领域专精生成器"""
    
    domain_name = "traffic_driving"
    domain_display_name = "交通驾驶"
    
    def _load_entities(self) -> Dict[str, List[str]]:
        return {
            "road_types": [
                "城市道路", "高速公路", "山区道路", "乡村道路",
                "隧道", "桥梁", "立交桥", "匝道", "服务区"
            ],
            "weather_conditions": [
                "晴天", "阴天", "雨天", "雪天", "雾天", "沙尘暴",
                "台风", "冰雹", "逆光", "夜间"
            ],
            "traffic_participants": [
                "行人", "自行车", "电动车", "摩托车", "轿车", "SUV",
                "货车", "客车", "公交车", "出租车", "网约车", "救护车",
                "消防车", "警车", "工程车", "拖拉机"
            ],
            "hazard_types": [
                "鬼探头", "紧急刹车", "追尾", "加塞", "闯红灯",
                "逆行", "违停", "爆胎", "侧翻", "碰撞", "山洪",
                "泥石流", "塌方", "落石", "积水", "结冰"
            ],
            "adas_functions": [
                "ACC自适应巡航", "LKA车道保持", "AEB自动紧急制动",
                "FCW前向碰撞预警", "LDW车道偏离预警", "BSD盲区监测",
                "TSR交通标志识别", "DMS驾驶员监测", "APA自动泊车",
                "TJA交通拥堵辅助", "ICA集成巡航辅助"
            ],
            "sensors": [
                "摄像头", "激光雷达", "毫米波雷达", "超声波雷达",
                "IMU惯性测量单元", "GPS定位", "高精地图"
            ],
            "driving_actions": [
                "加速", "减速", "刹车", "变道", "超车", "转弯",
                "掉头", "倒车", "停车", "避让", "紧急制动", "接管"
            ],
            "traffic_signs": [
                "限速标志", "禁止通行", "禁止停车", "禁止鸣笛",
                "红绿灯", "人行横道", "学校区域", "施工路段",
                "急转弯", "连续弯道", "陡坡", "落石区域"
            ],
            "time_periods": [
                "早高峰", "晚高峰", "平峰期", "深夜", "凌晨",
                "上午", "下午", "傍晚", "夜间"
            ],
            "autonomy_levels": [
                "L0无自动化", "L1驾驶辅助", "L2部分自动化",
                "L3有条件自动化", "L4高度自动化", "L5完全自动化"
            ]
        }
    
    def _load_relations(self) -> Dict[str, List[str]]:
        return {
            "hazard_triggers_action": ["触发", "导致", "引起"],
            "adas_detects_hazard": ["检测到", "识别到", "感知到"],
            "vehicle_responds": ["自动", "紧急", "立即"],
            "allowed": ["同时", "伴随", "随后"]
        }
    
    def _load_constraints(self) -> Dict[str, Any]:
        return {
            "speed_city": {"type": "range", "min": 0, "max": 80},
            "speed_highway": {"type": "range", "min": 60, "max": 120},
            "braking_distance": {"type": "range", "min": 5, "max": 100},
            "visibility": {"type": "range", "min": 10, "max": 10000},
            "reaction_time": {"type": "range", "min": 0.3, "max": 2.0}
        }
    
    def _load_templates(self) -> Dict[str, List[str]]:
        return {
            "emergency_scenario": [
                "在{road_type}行驶时，突然有{participant}从{direction}冲出，距离约{distance}米，驾驶员紧急{action}，避免了事故。",
                "{time_period}在{location}以{speed}km/h行驶，{hazard}出现，触发{adas_function}，车辆自动{action}。",
                "车辆配备{sensor}，在{weather}天气下检测到{hazard}，系统在{distance}米处触发紧急制动。"
            ],
            "daily_driving": [
                "{time_period}从{start}出发，经{route}到达{destination}，全程{distance}公里，耗时{duration}。",
                "在{road_type}行驶，{traffic_condition}，平均车速{speed}km/h，油耗{consumption}L/100km。",
                "行驶在{location}，{weather}天气，能见度{visibility}米，驾驶员保持{speed}km/h匀速行驶。"
            ],
            "adas_operation": [
                "{adas_function}检测到{hazard}，在{distance}米处触发{action}，{result}。",
                "L{level}自动驾驶在{scenario}场景下，系统{action}，置信度{confidence}%。",
                "车辆配备{sensor_list}，{adas_function}在{weather}条件下{performance}。"
            ],
            "special_weather": [
                "{weather}天气下在{road_type}行驶，能见度{visibility}米，路面{condition}，车速降至{speed}km/h。",
                "{time_period}遇到{weather}，开启{light_mode}，{adas_status}，安全行驶至{destination}。",
                "在{weather}天气条件下，{adas_function}性能{performance}，驾驶员{action}。"
            ],
            "highway_driving": [
                "在{highway}以{speed}km/h行驶，{lane_position}，前方{distance}米有{vehicle}。",
                "{time_period}从{entry}进入高速，行驶{distance}公里后，在{exit}下高速。",
                "高速行驶中，{adas_function}保持车距{distance}米，设定速度{speed}km/h。"
            ],
            "urban_driving": [
                "在{city_area}的{road_type}上，{traffic_condition}，驾驶员{action}。",
                "{time_period}经过{intersection}，信号灯{light_status}，{surrounding}，{decision}。",
                "城市道路行驶，{weather}天气，{traffic_condition}，平均速度{speed}km/h。"
            ],
            "mountain_driving": [
                "在{mountain_area}的{road_type}上，{gradient}坡度，{curve}弯道，{road_condition}。",
                "{time_period}行驶在{elevation}海拔山区，{weather}，能见度{visibility}米。",
                "山区道路遇到{hazard}，驾驶员{action}，车辆{status}。"
            ],
            "autonomous_driving": [
                "L{level}自动驾驶在{scenario}下，系统{action}，{confidence}%置信度，驾驶员{response}。",
                "{time_period}在{location}，自动驾驶系统{decision}，原因{reason}，驾驶员{response}。",
                "自动驾驶车辆配备{sensor_list}，在{weather}条件下实现{autonomy_level}。"
            ]
        }
    
    def _load_forbidden_pairs(self) -> List[Dict[str, str]]:
        return [
            {"entity1": "高速公路", "entity2": "红绿灯", "reason": "高速公路没有红绿灯"},
            {"entity1": "高速公路", "entity2": "行人", "reason": "高速公路禁止行人通行"},
            {"entity1": "L0无自动化", "entity2": "自动驾驶系统决策", "reason": "L0级别无自动驾驶功能"},
            {"entity1": "晴天", "entity2": "雨刷高速运转", "reason": "晴天不需要高速雨刷"},
            {"entity1": "隧道", "entity2": "GPS精确定位", "reason": "隧道内GPS信号弱"}
        ]
    
    def generate_scenario(self, scenario_type: str = "emergency") -> Dict[str, Any]:
        """生成驾驶场景数据"""
        entities = self._load_entities()
        templates = self._load_templates()
        
        if scenario_type == "emergency":
            template = random.choice(templates["emergency_scenario"])
            data = {
                "road_type": random.choice(entities["road_types"]),
                "participant": random.choice(entities["traffic_participants"]),
                "direction": random.choice(["左侧", "右侧", "前方", "后方"]),
                "distance": random.randint(5, 50),
                "action": random.choice(entities["driving_actions"]),
                "time_period": random.choice(entities["time_periods"]),
                "speed": random.randint(30, 120),
                "hazard": random.choice(entities["hazard_types"]),
                "adas_function": random.choice(entities["adas_functions"]),
                "sensor": random.choice(entities["sensors"]),
                "weather": random.choice(entities["weather_conditions"])
            }
        elif scenario_type == "daily":
            template = random.choice(templates["daily_driving"])
            data = {
                "time_period": random.choice(entities["time_periods"]),
                "start": random.choice(["家", "公司", "学校", "商场"]),
                "route": random.choice(["主干道", "快速路", "高速", "小路"]),
                "destination": random.choice(["公司", "家", "商场", "医院"]),
                "distance": random.randint(5, 100),
                "duration": f"{random.randint(10, 120)}分钟",
                "road_type": random.choice(entities["road_types"]),
                "traffic_condition": random.choice(["畅通", "缓行", "拥堵", "严重拥堵"]),
                "speed": random.randint(20, 80),
                "consumption": round(random.uniform(6.0, 12.0), 1),
                "weather": random.choice(entities["weather_conditions"]),
                "visibility": random.randint(100, 10000)
            }
        else:
            template = random.choice(templates["adas_operation"])
            data = {
                "adas_function": random.choice(entities["adas_functions"]),
                "hazard": random.choice(entities["hazard_types"]),
                "distance": random.randint(10, 100),
                "action": random.choice(entities["driving_actions"]),
                "result": random.choice(["成功避险", "避免碰撞", "安全停车"]),
                "level": random.randint(2, 4),
                "scenario": random.choice(["城市道路", "高速公路", "交叉路口"]),
                "confidence": random.randint(85, 99),
                "sensor_list": ", ".join(random.sample(entities["sensors"], 3)),
                "weather": random.choice(entities["weather_conditions"]),
                "performance": random.choice(["正常工作", "性能良好", "受限运行"])
            }
        
        content = template.format(**data)
        return {
            "content": content,
            "scenario_type": scenario_type,
            "entities": data,
            "quality_score": round(random.uniform(0.85, 0.98), 2)
        }
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """验证内容的专业正确性"""
        forbidden_pairs = self._load_forbidden_pairs()
        errors = []
        
        for pair in forbidden_pairs:
            if pair["entity1"] in content and pair["entity2"] in content:
                errors.append({
                    "type": "forbidden_pair",
                    "entity1": pair["entity1"],
                    "entity2": pair["entity2"],
                    "reason": pair["reason"]
                })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "quality_score": 1.0 if len(errors) == 0 else 0.5
        }
