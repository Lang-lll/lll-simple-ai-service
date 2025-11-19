from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from ..utils.prompt_template import PromptTemplate
from ..utils.extract import (
    MODALITY_TYPES,
    default_extract_strings,
    default_extract_fields_to_string,
    modality_type_to_name,
    event_entity_to_name,
    understood_data_get_main_content,
)


class EpisodicMemoriesGenerateModels(BaseModel):
    id: str = Field(
        ...,
        description="唯一标识符",
    )
    content: str = Field(
        default="",
        description="用一句话清晰概括记忆的核心内容，要简洁具体",
    )
    importance: int = Field(default=0, description="当前记忆的重要程度分数(0-100)")
    keywords: List[str] = Field(
        default_factory=list,
        description="从记忆内容中提取的具体名词或核心概念，用于精确匹配查询",
    )
    associations: List[str] = Field(
        default_factory=list,
        description="与记忆相关的抽象概念、类别或场景，用于语义联想查询",
    )


class EpisodicMemoriesModels(EpisodicMemoriesGenerateModels):
    timestamp: datetime
    entities: List[str]
    source: str


extract_memories_system_template = """请你对原始的历史记忆进行**提炼、概括和结构化**，生成清晰易用的记忆条目。

## 重要规则
1. **ID保持不变**：你必须原样使用每个记忆条目中提供的id，绝对不能修改或生成新的id
2. **内容可以优化**：你可以重新组织语言让content更清晰，但不能改变原意
3. **可以合并**：你可以将多个相关记忆合并为一个
4. **可以舍弃**：你可以舍弃不重要的记忆

## 合并记忆时的ID处理
- 如果合并多个记忆，保留最重要的那个记忆的id
- 被合并的其他记忆在输出中删除

【当前情境】
{{current_situation}}

【需要你整理的原始记忆】(每个记忆已包含ID)
{{recent_events}}

【你正在做的事情】
{{active_goals}}"""

extract_memories_template = f"""
<|im_start|>system
{extract_memories_system_template}
<|im_end|>
<|im_start|>assistant
"""

extract_memories_output_json_template = PromptTemplate(
    template="""请严格按照以下JSON格式输出。

# 输出要求
你必须输出一个JSON**数组**，数组中的每个对象代表一个提炼后的记忆条目，包含以下字段：

- `id`: 字符串。**必须原样使用**原始记忆中提供的唯一标识符。

- `content`: 字符串。用**一句话**清晰概括记忆的核心内容，要简洁具体。可以优化表达但不能改变原意。

- `importance`: 整数，范围0-100。评估当前记忆的重要程度分数。

- `keywords`: 数组，包含字符串。从记忆内容中提取的**具体名词或核心概念**，用于精确匹配查询。

- `associations`: 数组，包含字符串。与记忆相关的**抽象概念、类别或场景**，用于语义联想查询（如"环境控制"、"用户习惯"、"日常行为"）。

# 输出示例
```json
{examples}""",
    variables={
        "examples": """[
  {
    "id": "mem_12345",
    "content": "用户在晚上进入客厅后要求打开灯光",
    "importance": 40,
    "keywords": ["客厅", "灯光", "用户", "晚上"],
    "associations": ["环境控制", "用户习惯"]
  }
]"""
    },
)


def extract_memories_task_format_inputs(inputs):
    return {
        "current_situation": inputs.get("current_situation", "未知"),
        "recent_events": default_extract_fields_to_string(
            data_list=inputs.get("recent_events", []),
            field_configs=[
                {"key": "event_id", "display": "ID", "default": "未知"},
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
        "active_goals": default_extract_strings(
            inputs.get("active_goals", []), "description"
        ),
    }
