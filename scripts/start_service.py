from pydantic import BaseModel, Field
from typing import Literal
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai_service import create_app, AIConfig


def main():
    # 自定义配置
    config = AIConfig()
    config.local_model_path = "./models/Qwen2-0.5B-Instruct"
    config.use_local_model = True
    config.port = 5000  # 修改端口

    # 创建应用
    app, ai_engine = create_app(config)

    class SpeechParameters(BaseModel):
        action: Literal["speak", "pause", "emphasize"] = Field(
            ..., description="语音动作类型：speak(说话)、pause(暂停)、emphasize(强调)"
        )
        text: str = Field(..., description="要说的具体文本内容")
        emotion: str = "neutral"
        voice_type: str = "default"
        speed: float = Field(default=1.0, description="语速0.5-2.0")

    # 添加自定义任务
    class BehaviorPlan(BaseModel):
        speech: SpeechParameters

    behavior_template = """
<|im_start|>system
基于以下情境生成语音、动作行为计划：

当前情境：{{current_situation}}
工作记忆：{{recent_events}}
联想记忆：{{active_memories}}
当前目标：{{active_goals}}
用户关系：{{relationship_context}}
社交规范：{{social_norms}}<|im_end|>
<|im_start|>assistant
"""

    """
用户情感：{{user_emotion}}
你的情感：{{robot_emotion}}"""

    def behavior_task_format_inputs(inputs):
        def extract_strings(data_list, field=None):
            """从对象列表中提取字符串"""
            if not data_list:
                return "无"

            strings = []
            for item in data_list[:5]:  # 最多取5个
                if field and hasattr(item, field):
                    # 对象字段提取
                    value = getattr(item, field, "")
                elif field and isinstance(item, dict):
                    # 字典字段提取
                    value = item.get(field, "")
                else:
                    # 直接使用字符串
                    value = str(item)

                if value and value not in strings:
                    strings.append(str(value))

            return "、".join(strings) if strings else "无"

        return {
            "current_situation": inputs.get("current_situation", "未知"),
            "recent_events": extract_strings(
                inputs.get("recent_events", []), "understood_data"
            ),
            "active_memories": extract_strings(inputs.get("active_memories", [])),
            "active_goals": extract_strings(
                inputs.get("active_goals", []), "description"
            ),
            "relationship_context": extract_strings(
                inputs.get("relationship_context", [])
            ),
            "social_norms": extract_strings(inputs.get("social_norms", [])),
        }

    ai_engine.add_custom_task(
        "generate_behavior",
        BehaviorPlan,
        behavior_template,
        behavior_task_format_inputs,
    )

    print(f"启动AI服务，端口: {config.port}")
    print(f"可用任务: {ai_engine.get_available_tasks()}")

    app.run(
        host=config.host,
        port=config.port,
    )


if __name__ == "__main__":
    main()

"""
{
        "type": "object",
        "properties": {
            "behavior_plan": {
                "type": "object",
                "properties": {
                    "speech": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "emotion": {"type": "string"},
                                    "voice_type": {"type": "string"},
                                    "speed": {
                                        "type": "number",
                                        "minimum": 0.5,
                                        "maximum": 2.0,
                                    },
                                },
                                "required": ["text"],
                            },
                        },
                        "required": ["action", "parameters"],
                    },
                },
                "additionalProperties": False,  # 不允许其他属性
            },
            "expected_outcomes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "probability": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                },
            },
            "social_appropriateness": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["behavior_plan"],
    }

"motion": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "animation_type": {"type": "string"},
                                    "context_variations": {
                                        "type": "object",
                                        "properties": {
                                            "intensity": {
                                                "type": "number",
                                                "minimum": 0,
                                                "maximum": 1,
                                            },
                                            "speed": {
                                                "type": "number",
                                                "minimum": 0.5,
                                                "maximum": 3.0,
                                            },
                                            "style": {"type": "string"},
                                            "emotional_tone": {"type": "string"},
                                            "target_audience": {"type": "string"},
                                        },
                                    },
                                    "spatial_context": {
                                        "type": "object",
                                        "properties": {
                                            "user_distance": {"type": "number"},
                                            "environment": {"type": "string"},
                                        },
                                    },
                                },
                                "required": ["animation_type"],
                            },
                        },
                        "required": ["action", "parameters"],
                    },
                    """
