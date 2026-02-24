#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗领域专精化模块
医学专业术语、诊断逻辑、治疗方案
"""

from .base_specialist import DomainSpecialist
from typing import Dict, List, Any, Optional
import random

class MedicalSpecialist(DomainSpecialist):
    """医疗领域专精生成器"""
    
    domain_name = "medical"
    domain_display_name = "医疗"
    
    def _load_entities(self) -> Dict[str, List[str]]:
        return {
            "departments": [
                "内科", "外科", "儿科", "妇产科", "骨科", "神经内科",
                "心血管内科", "呼吸内科", "消化内科", "内分泌科",
                "皮肤科", "眼科", "耳鼻喉科", "口腔科", "精神科",
                "肿瘤科", "急诊科", "麻醉科", "放射科", "病理科"
            ],
            "symptoms": [
                "发热", "咳嗽", "头痛", "腹痛", "胸痛", "乏力",
                "恶心呕吐", "腹泻", "便秘", "失眠", "头晕",
                "心悸", "呼吸困难", "水肿", "皮疹", "关节疼痛"
            ],
            "diseases": [
                "高血压", "糖尿病", "冠心病", "脑卒中", "肺炎",
                "胃炎", "肝炎", "肾炎", "贫血", "甲状腺功能亢进",
                "支气管炎", "哮喘", "胃溃疡", "肠炎", "颈椎病",
                "腰椎间盘突出", "骨折", "关节炎", "抑郁症", "焦虑症"
            ],
            "examinations": [
                "血常规", "尿常规", "肝功能", "肾功能", "血糖",
                "血脂", "心电图", "胸部X光", "CT扫描", "MRI检查",
                "B超", "胃镜", "肠镜", "支气管镜", "穿刺活检"
            ],
            "treatments": [
                "药物治疗", "手术治疗", "放射治疗", "化学治疗",
                "物理治疗", "康复训练", "心理治疗", "中医治疗",
                "介入治疗", "免疫治疗", "靶向治疗", "透析治疗"
            ],
            "medicines": [
                "抗生素", "降压药", "降糖药", "止痛药", "抗凝药",
                "激素类药物", "抗肿瘤药", "抗抑郁药", "镇静催眠药",
                "胃药", "心血管药物", "呼吸系统药物", "维生素类"
            ],
            "vital_signs": [
                "体温", "脉搏", "呼吸频率", "血压", "血氧饱和度"
            ],
            "body_parts": [
                "头部", "胸部", "腹部", "四肢", "脊柱", "关节",
                "心脏", "肺部", "肝脏", "肾脏", "胃", "肠道"
            ],
            "patient_types": [
                "门诊患者", "住院患者", "急诊患者", "手术患者",
                "复诊患者", "慢性病患者", "老年患者", "儿童患者"
            ],
            "medical_staff": [
                "主治医师", "副主任医师", "主任医师", "住院医师",
                "护士", "护师", "主管护师", "药师", "技师"
            ]
        }
    
    def _load_relations(self) -> Dict[str, List[str]]:
        return {
            "symptom_indicates_disease": ["提示", "可能为", "考虑"],
            "disease_requires_examination": ["需要", "应进行", "建议"],
            "examination_confirms_diagnosis": ["确诊", "排除", "支持"],
            "disease_treated_by_treatment": ["采用", "进行", "接受"],
            "allowed": ["伴有", "合并", "继发于", "导致"]
        }
    
    def _load_constraints(self) -> Dict[str, Any]:
        return {
            "temperature": {"type": "range", "min": 35.0, "max": 42.0},
            "heart_rate": {"type": "range", "min": 40, "max": 200},
            "blood_pressure_systolic": {"type": "range", "min": 60, "max": 250},
            "blood_pressure_diastolic": {"type": "range", "min": 40, "max": 150},
            "dosage_frequency": {"type": "enum", "values": ["每日一次", "每日两次", "每日三次", "每8小时一次"]}
        }
    
    def _load_templates(self) -> Dict[str, List[str]]:
        return {
            "symptom_description": [
                "患者主诉{symptom}{duration}，伴有{accompanying_symptom}。",
                "{patient_type}因{symptom}就诊，病史{history}。",
                "患者{symptom}{severity}，{onset_time}起病。"
            ],
            "diagnosis_process": [
                "根据患者{symptom}症状，结合{examination}检查结果，诊断为{disease}。",
                "患者{symptom}{duration}，{examination}显示{finding}，确诊为{disease}。",
                "经{department}会诊，结合临床表现和辅助检查，诊断为{disease}。"
            ],
            "examination_result": [
                "{examination}检查显示{finding}，{significance}。",
                "患者行{examination}检查，结果提示{finding}。",
                "{examination}结果：{finding}，建议{recommendation}。"
            ],
            "treatment_plan": [
                "诊断为{disease}，给予{treatment}治疗，方案为{regimen}。",
                "患者确诊{disease}，采用{treatment}，疗程{duration}。",
                "根据{disease}诊断结果，制定{treatment}方案，{medicine}{dosage}。"
            ],
            "medication_order": [
                "{medicine}{dosage}，{frequency}，{route}给药。",
                "处方：{medicine}，用法：{dosage}，{frequency}，共{days}天。",
                "医嘱：{medicine}{dosage}，{frequency}，注意{precaution}。"
            ],
            "vital_signs": [
                "患者生命体征：体温{temp}℃，脉搏{pulse}次/分，呼吸{resp}次/分，血压{bp}mmHg。",
                "查体：T {temp}℃，P {pulse}次/分，R {resp}次/分，BP {bp}mmHg，SpO2 {spo2}%。",
                "入院时生命体征：体温{temp}℃，心率{pulse}次/分，血压{bp}mmHg。"
            ],
            "discharge_summary": [
                "患者因{disease}入院，经{treatment}治疗后，病情好转出院。",
                "出院诊断：{disease}。出院医嘱：{discharge_advice}。",
                "患者住院{days}天，好转出院，门诊随访。"
            ],
            "medical_record": [
                "患者{age}岁，{gender}，因{symptom}于{date}入院。",
                "主诉：{symptom}{duration}。现病史：{history}。",
                "既往史：{past_history}。过敏史：{allergy}。"
            ]
        }
    
    def _load_knowledge(self) -> Dict[str, Any]:
        return {
            "normal_ranges": {
                "体温": "36.0-37.3℃",
                "脉搏": "60-100次/分",
                "呼吸": "16-20次/分",
                "血压": "90-139/60-89mmHg",
                "血氧饱和度": "95-100%"
            },
            "disease_symptoms": {
                "高血压": ["头痛", "头晕", "心悸"],
                "糖尿病": ["多饮", "多食", "多尿", "体重下降"],
                "肺炎": ["发热", "咳嗽", "咳痰", "胸痛"],
                "胃炎": ["上腹痛", "恶心", "呕吐", "食欲不振"]
            },
            "treatment_durations": {
                "感冒": "5-7天",
                "肺炎": "7-14天",
                "高血压": "长期服药",
                "糖尿病": "终身治疗"
            }
        }
    
    def _generate_single(self, index: int, quality: str) -> Optional[Dict]:
        template_type = random.choice(list(self.templates.keys()))
        template = random.choice(self.templates[template_type])
        
        try:
            if template_type == "symptom_description":
                symptom = random.choice(self.entities["symptoms"])
                content = template.format(
                    symptom=symptom,
                    duration=f"{random.randint(1,14)}天",
                    accompanying_symptom=random.choice(self.entities["symptoms"]),
                    patient_type=random.choice(self.entities["patient_types"]),
                    history="既往体健" if random.random() > 0.5 else "有慢性病史",
                    severity="明显" if random.random() > 0.5 else "轻微",
                    onset_time=f"{random.randint(1,72)}小时前"
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "症状描述",
                    "symptom": symptom,
                    "content": content
                }
            
            elif template_type == "diagnosis_process":
                disease = random.choice(self.entities["diseases"])
                content = template.format(
                    symptom=random.choice(self.entities["symptoms"]),
                    examination=random.choice(self.entities["examinations"]),
                    disease=disease,
                    duration=f"{random.randint(3,30)}天",
                    finding="异常" if random.random() > 0.3 else "未见明显异常",
                    department=random.choice(self.entities["departments"])
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "诊断过程",
                    "disease": disease,
                    "content": content
                }
            
            elif template_type == "examination_result":
                exam = random.choice(self.entities["examinations"])
                content = template.format(
                    examination=exam,
                    finding="结果正常" if random.random() > 0.5 else "发现异常",
                    significance="临床意义明确",
                    recommendation="进一步检查" if random.random() > 0.5 else "定期复查"
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "检查结果",
                    "examination": exam,
                    "content": content
                }
            
            elif template_type == "treatment_plan":
                disease = random.choice(self.entities["diseases"])
                treatment = random.choice(self.entities["treatments"])
                medicine = random.choice(self.entities["medicines"])
                content = template.format(
                    disease=disease,
                    treatment=treatment,
                    regimen="规范治疗",
                    duration=f"{random.randint(7,30)}天",
                    medicine=medicine,
                    dosage=f"{random.randint(1,3)}片/次"
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "治疗方案",
                    "disease": disease,
                    "content": content
                }
            
            elif template_type == "medication_order":
                medicine = random.choice(self.entities["medicines"])
                content = template.format(
                    medicine=medicine,
                    dosage=f"{random.randint(1,3)}片",
                    frequency=random.choice(self.constraints["dosage_frequency"]["values"]),
                    route="口服",
                    days=random.randint(3,14),
                    precaution="饭后服用" if random.random() > 0.5 else "餐前服用"
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "用药医嘱",
                    "medicine": medicine,
                    "content": content
                }
            
            elif template_type == "vital_signs":
                temp = round(random.uniform(36.0, 38.5), 1)
                pulse = random.randint(60, 100)
                resp = random.randint(16, 20)
                bp_sys = random.randint(90, 140)
                bp_dia = random.randint(60, 90)
                spo2 = random.randint(95, 100)
                content = template.format(
                    temp=temp,
                    pulse=pulse,
                    resp=resp,
                    bp=f"{bp_sys}/{bp_dia}",
                    spo2=spo2
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "生命体征",
                    "content": content
                }
            
            elif template_type == "discharge_summary":
                disease = random.choice(self.entities["diseases"])
                content = template.format(
                    disease=disease,
                    treatment=random.choice(self.entities["treatments"]),
                    days=random.randint(3,21),
                    discharge_advice="继续服药，定期复查"
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "出院小结",
                    "disease": disease,
                    "content": content
                }
            
            elif template_type == "medical_record":
                content = template.format(
                    age=random.randint(18, 80),
                    gender=random.choice(["男", "女"]),
                    symptom=random.choice(self.entities["symptoms"]),
                    date=f"2024年{random.randint(1,12)}月{random.randint(1,28)}日",
                    duration=f"{random.randint(1,30)}天",
                    history="患者于入院前出现上述症状",
                    past_history="否认高血压、糖尿病病史" if random.random() > 0.5 else "有慢性病史",
                    allergy="否认药物过敏史" if random.random() > 0.5 else "有青霉素过敏史"
                )
                return {
                    "id": index,
                    "domain": "医疗",
                    "type": "病历记录",
                    "content": content
                }
            
        except Exception as e:
            return None
        
        return None
