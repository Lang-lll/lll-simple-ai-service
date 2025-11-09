# AI Service

A structured AI service with Outlines support for guaranteed JSON output.

## 安装

```bash
pip install lll-simple-ai-service
```

## 使用

```python
from lll_simple_ai_service import create_app, AIConfig

def main():
    config = AIConfig()
    app, ai_engine = create_app(config)

    ai_engine.add_custom_task(
        "understand_event",
        UnderstoodData,
        understand_template,
        understand_task_format_inputs,
    )

    app.run(
        host=config.host,
        port=config.port,
    )
```
