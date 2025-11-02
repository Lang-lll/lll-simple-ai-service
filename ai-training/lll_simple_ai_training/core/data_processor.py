from typing import List


class DataProcessor:
    def __init__(self, system_prompts: List[str] | None = None):
        self.system_prompts = system_prompts or self._get_default_system_prompts()

    def _get_default_system_prompts(self):
        """默认系统提示词"""
        return []

    def add_system_prompt(self, text):
        """添加固定的系统提示词前缀"""
        system_part = "".join([f"{prompt}\n" for prompt in self.system_prompts])
        return f"<|im_start|>system\n{system_part}<|im_end|>\n{text}"

    def format_training_data(
        self, training_data, tokenizer, format_func=None, **kwargs
    ):
        formatted = []
        for example in training_data:
            if format_func:
                text = format_func(example, **kwargs)
            else:
                text = self._default_format(example)

            # 添加系统提示词到训练数据
            text_with_system = self.add_system_prompt(text)
            formatted.append({"text": text_with_system})

        return formatted
