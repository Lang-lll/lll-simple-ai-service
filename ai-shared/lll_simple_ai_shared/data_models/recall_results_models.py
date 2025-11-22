from pydantic import BaseModel, Field
from ..utils.prompt_template import PromptTemplate
from ..utils.extract import (
    modality_type_to_name,
    event_entity_to_name,
    understood_data_get_main_content,
    default_extract_strings,
    default_extract_fields_to_string,
)
from ..utils.date import datetime_to_cn_format


class RecallResultsModels(BaseModel):
    recalled_episode: str = Field(
        default="",
        description="针对当前主要事件，从历史记忆中找出与主要事件相关的经验或模式。应该具体描述相关记忆，不要过度总结",
    )
    current_situation: str = Field(
        default="",
        description="在结合历史经验和上下文后，对**当前情境的深化理解和分析**。说明历史经验如何影响对现状的理解",
    )


associative_recall_system_template = """关注**当前主要事件**，将**当前情境**、**刚才的对话和事件**与**历史记忆**进行智能关联，找出有用的经验和模式，更好地理解主要事件。

【当前情境】
{{current_situation}}

【当前主要事件】
{{main_events}}

【刚才的对话和事件】
{{recent_events}}

【相关的历史记忆】
{{episodic_memories}}
{% if query_too_many_results %}
**注意: 记忆查询结果过多，已过滤部分信息，当前查询结果不完整**
{% endif %}"""


associative_recall_template = f"""
<|im_start|>system
{associative_recall_system_template}
<|im_end|>
<|im_start|>assistant
"""

associative_recall_output_json_template = PromptTemplate(
    template="""请严格按照指定的JSON格式输出。

# 输出要求
你必须输出一个JSON对象，包含以下字段：

- `recalled_episode`: 字符串。针对当前主要事件，从历史记忆中找出与主要事件相关的经验或模式。应该具体描述相关记忆，不要过度总结。

- `current_situation`: 字符串。在结合历史经验和上下文后，对**当前情境的深化理解和分析**。说明历史经验如何影响对现状的理解。

# 输出示例
```json
{examples}""",
    variables={
        "examples": """{
  "recalled_episode": "上周用户同样在晚上进入客厅后说'有点暗'，随后要求打开了灯光",
  "current_situation": "用户现在再次在晚间进入客厅，结合历史行为模式，他很可能需要照明但尚未明确表达开灯指令"
}"""
    },
)


def associative_recall_task_format_inputs(inputs):
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
        "episodic_memories": default_extract_fields_to_string(
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
        ),
        "query_too_many_results": inputs.get("query_too_many_results", False),
        "active_goals": default_extract_strings(
            inputs.get("active_goals", []), "description"
        ),
    }
