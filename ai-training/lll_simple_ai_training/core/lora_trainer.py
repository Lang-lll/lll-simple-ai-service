import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
from .base_trainer import BaseTrainer
from .data_processor import DataProcessor
from ..config import TrainingConfig


class LoRATrainer(BaseTrainer):
    """LoRA训练器 - 不关心具体任务"""

    def __init__(self, config: TrainingConfig):
        super().__init__()
        self.config = config
        self.data_processor = DataProcessor(config.custom_system_prompts)

    def prepare_model(self):
        """准备模型和LoRA配置"""
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name, torch_dtype=torch.bfloat16, device_map="auto"
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)

        # LoRA配置
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.target_modules,
        )

        self.model = get_peft_model(self.model, lora_config)
        return self.model

    def train(self, training_data: List[Dict[str, Any]], **kwargs):
        """执行训练 - 只关心数据格式，不关心任务内容"""

        # 准备训练数据
        formatted_data = self.data_processor.format_training_data(
            training_data, self.tokenizer, **kwargs
        )

        # 训练参数
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            num_train_epochs=self.config.num_train_epochs,
            logging_dir="./logs",
            save_strategy="epoch",
            fp16=True,
            **kwargs
        )

        # 开始训练
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=formatted_data,
            data_collator=self.data_processor.get_data_collator(self.tokenizer),
        )

        trainer.train()
        return trainer
