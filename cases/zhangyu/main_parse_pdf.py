from loguru import logger
from src.pdf_parser import find_summary_table
from src.model_loader import ModelLoader
import sys

def main():
    # 移除默认的 stderr 处理器
    logger.remove()
    
    # 添加文件处理器，设置 INFO 级别
    logger.add("pdf_parser.log", rotation="500 MB", level="DEBUG")
    # 如果需要控制台输出，也添加一个 stderr 处理器，同样设置 INFO 级别
    logger.add(sys.stderr, level="INFO")
    
    # 预热模型
    logger.info("预热模型...")
    ModelLoader.get_model()
    
    # 设置PDF文件路径
    pdf_path = '/Users/mark/Documents/Terminal evaluation report/1.10321_2024_ValTR_unep_gef_msp.pdf'
    
    result = find_summary_table(pdf_path)
    if result:
        logger.info(f"找到表格在第 {result['page_num'] + 1} 页")
        logger.info(f"表格坐标: {result['bbox']}")
        logger.info(f"表格标题: {result['table_name']}")
        logger.info(f"匹配置信度: {result['confidence']}")
    else:
        logger.warning("未找到目标表格")

if __name__ == '__main__':
    main() 