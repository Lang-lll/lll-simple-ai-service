from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TrainingConfig:
    """通用训练配置"""

    model_name: str = "../models/Qwen3-4B-Instruct-2507"
    output_dir: str = "./trained_models"

    # LoRA配置
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: Optional[list] = None

    # 训练参数
    learning_rate: float = 1e-4
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4

    # 其他
    custom_system_prompts: List[str] = []

    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
