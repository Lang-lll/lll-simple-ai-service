from pydantic import BaseModel, Field
from ..utils.prompt_template import PromptTemplate
from ..utils.extract import (
    default_extract_fields_to_string,
)
from ..utils.date import datetime_to_cn_format


class MorningSituationModels(BaseModel):
    current_situation: str = Field(
        default="",
        description="基于近期记忆生成的睡醒情境认知，要自然、个性化，像刚睡醒时想起事情的感觉",
    )


morning_situation_system_template = """请根据你的角色、基于近期的记忆生成睡醒时的情境认知。

【近期的记忆】
{{episodic_memories}}
{% if query_too_many_results %}
**注意: 记忆查询结果过多，已过滤部分信息，当前查询结果不完整**
{% endif %}"""


morning_situation_template = f"""
<|im_start|>system
{morning_situation_system_template}
<|im_end|>
<|im_start|>assistant
"""

morning_situation_output_json_template = PromptTemplate(
    template="""请严格按照指定的JSON格式输出。

# 输出要求
你必须输出一个JSON对象，包含以下字段：

- `current_situation`: 字符串。基于近期记忆生成的睡醒情境认知，要自然、个性化，像刚睡醒时想起事情的感觉。

# 输出示例
```json
{examples}""",
    variables={
        "examples": """{
  "current_situation": "刚刚醒来，想起用户今天要接待客人，得提醒一下。"
}"""
    },
)


def morning_situation_task_format_inputs(inputs):
    return {
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
    }
