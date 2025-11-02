from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseTrainer(ABC):
    """抽象基础训练器"""

    def __init__(self):
        pass

    @abstractmethod
    def prepare_model(self):
        """准备模型 - 子类实现"""
        pass

    @abstractmethod
    def train(self, training_data: List[Dict[str, Any]]):
        """训练方法 - 子类实现"""
        pass

    def save_model(self, save_path: str):
        """保存训练好的模型"""
        # 通用保存逻辑
        pass
