from sentence_transformers import SentenceTransformer
from loguru import logger
import time

class ModelLoader:
    _instance = None
    _model = None
    
    @classmethod
    def get_model(cls):
        """单例模式获取模型实例"""
        if cls._model is None:
            start_time = time.time()
            logger.info("加载语义相似度模型...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info(f"模型加载完成，耗时: {time.time() - start_time:.2f}秒")
        return cls._model

    @classmethod
    def encode_text(cls, text):
        """编码文本"""
        start_time = time.time()
        model = cls.get_model()
        embedding = model.encode([text])[0]
        logger.debug(f"文本编码完成，耗时: {time.time() - start_time:.2f}秒")
        return embedding 