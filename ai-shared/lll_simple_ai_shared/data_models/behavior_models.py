from pydantic import BaseModel, Field
from typing import List, Literal, Union, Any
from ..utils.prompt_template import PromptTemplate
from ..utils.extract import (
    modality_type_to_name,
    event_entity_to_name,
    understood_data_get_main_content,
    default_extract_strings,
    default_extract_fields_to_string,
)
from ..utils.date import datetime_to_cn_format


class BaseAction(BaseModel):
    type: Literal["tts", "motion", "wait"] = Field(..., description="计划类型")


class TTSAction(BaseAction):
    type: str = "tts"
    data: str = Field(default="", description="要说的具体文本内容")
    emotion: str = "neutral"
    speed: float = Field(default=1.0, description="语速0.5-2.0")


class MotionAction(BaseAction):
    type: str = "motion"
    action_id: str = Field(..., description="动作ID，如 'walk_normal', 'happy_wave_01'")
    intensity: float = Field(default=1.0, description="动作强度 0.0-1.0")
    speed: float = Field(default=1.0, description="动作速度 0.5-2.0")


class WaitAction(BaseAction):
    type: str = "wait"
    duration: float = Field(..., description="等待时间（秒）")
    reason: str = Field(default="", description="等待的原因")


class BehaviorPlan(BaseModel):
    plan: List[Union[TTSAction, MotionAction, WaitAction]] = Field(
        default_factory=list, description="行为计划序列"
    )
    current_situation: str | Any = Field(
        default=None,
        description="根据你的行为计划，更新你对当前情境认知",
    )


behavior_system_template = """下面是当前的信息，请根据你的角色生成语音、动作行为计划：

【当前情境】
{{current_situation}}

【当前主要事件】
{{main_events}}

【刚才的对话和事件】
{{recent_events}}

【相关的历史记忆或总结】
{{episodic_memories}}

【可选动作】
{{actions}}"""


behavior_template = f"""
<|im_start|>system
{behavior_system_template}
<|im_end|>
<|im_start|>assistant
"""

behavior_output_json_template = PromptTemplate(
    template="""请严格按照指定的JSON格式输出。

# 输出要求
你必须输出一个JSON对象，包含以下字段：

- `current_situation`: 字符串。根据你制定的行为计划，更新对当前情境的认知和理解，说明为什么这样的行为序列适合当前情境。

- `plan`字段是动作对象数组，每个对象必须包含：
  - `type`: 字符串，动作类型：`"tts"`(语音)、`"motion"`(动作)、`"wait"`(等待)

  ## 根据type选择对应字段：

  ### 当 type = "tts" 时，包含：
  - `data`: 字符串，要说的具体文本
  - `emotion`: 字符串，情感类型，默认"neutral"
  - `speed`: 数字0.5-2.0，语速，默认1.0

  ### 当 type = "motion" 时，包含：
  - `action_id`: 动作ID，从动作列表中选择
  - `speed`: 数字0.5-2.0，动作速度，默认1.0

  ### 当 type = "wait" 时，包含：
  - `duration`: 数字，等待时间（秒）
  - `reason`: 字符串，等待的原因

# 输出示例
```json
{examples}""",
    variables={
        "examples": """{
  "plan": [
    {
      "type": "tts",
      "data": "我注意到您刚刚进入了客厅",
      "emotion": "neutral",
      "speed": 1.0
    }
  ],
  "current_situation": "用户刚进入昏暗环境，采用分步沟通策略：先告知观察结果，再停顿给予反应时间，这样既礼貌又有效"
}"""
    },
)


def behavior_task_format_inputs(inputs):
    episodic_memories = ""
    episodic_memories_text = inputs.get("episodic_memories_text", None)

    if episodic_memories_text:
        episodic_memories = episodic_memories_text
    else:
        episodic_memories = default_extract_fields_to_string(
            data_list=inputs.get("episodic_memories", []),
            field_configs=[
                {
                    "key": "timestamp",
                    "display": "时间",
                    "default": "未知",
                    "processor": datetime_to_cn_format,
                    "format_template": "{value}: ",
                },
                {
                    "key": "content",
                    "display": "内容",
                    "default": "未知",
                    "format_template": "{value}",
                },
            ],
            list_name="无",
            separator="",
        )

    return {
        "current_situation": inputs.get("current_situation", "未知"),
        "main_events": inputs.get("main_events", "无"),
        "recent_events": default_extract_fields_to_string(
            data_list=inputs.get("recent_events", []),
            field_configs=[
                {
                    "key": "modality_type",
                    "display": "类型",
                    "default": "未知",
                    "processor": modality_type_to_name,
                },
                {
                    "key": "understood_data",
                    "display": "来源",
                    "default": "未知",
                    "processor": event_entity_to_name,
                },
                {
                    "key": "understood_data",
                    "display": "内容",
                    "default": "未知",
                    "processor": understood_data_get_main_content,
                },
            ],
            list_name="无",
        ),
        "episodic_memories": episodic_memories,
        "active_goals": default_extract_strings(
            inputs.get("active_goals", []), "description"
        ),
        "social_norms": default_extract_strings(inputs.get("social_norms", [])),
        "actions": "无",
    }
