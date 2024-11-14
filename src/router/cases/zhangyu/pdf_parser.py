import fitz
import numpy as np
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

def find_summary_table(pdf_path: str) -> Optional[Dict]:
    """
    在PDF文档中定位"Summary of project findings and ratings"相关的表格
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        Dict: {
            'page_num': 页码(从0开始),
            'bbox': [x0, y0, x1, y1], # 表格边界框坐标
            'table_name': 表格标题,
            'confidence': 相似度置信度
        }
    """
    logger.info(f"开始处理PDF文件: {pdf_path}")
    
    # 目标表格名
    target_text = "Summary of project findings and ratings"
    
    # 加载语义相似度模型
    logger.info("加载语义相似度模型...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    target_embedding = model.encode([target_text])[0]
    logger.debug("目标文本编码完成")
    
    try:
        # 打开PDF文档
        logger.info("打开PDF文档...")
        doc = fitz.open(pdf_path)
        logger.info(f"PDF总页数: {len(doc)}")
        
        for page_num in range(len(doc)):
            logger.debug(f"处理第 {page_num + 1} 页")
            page = doc[page_num]
            
            # 提取表格
            table_finder = page.find_tables()
            tables = table_finder.tables  # 获取表格列表
            logger.debug(f"在第 {page_num + 1} 页找到 {len(tables)} 个表格")
            
            if not tables:
                continue
                
            for table_idx, table in enumerate(tables):
                logger.debug(f"分析第 {page_num + 1} 页的第 {table_idx + 1} 个表格")
                # 获取表格上方的文本作为可能的表格标题
                table_bbox = table.bbox
                above_area = fitz.Rect(
                    table_bbox[0],  # x0
                    max(0, table_bbox[1] - 50),  # y0: 向上搜索50个单位
                    table_bbox[2],  # x2
                    table_bbox[1]   # y1
                )
                
                # 提取可能的表格标题文本
                title_text = page.get_text("text", clip=above_area).strip()
                
                if not title_text:
                    logger.debug("未找到表格标题，跳过")
                    continue
                
                logger.debug(f"找到表格标题: {title_text}")
                    
                # 计算语义相似度
                title_embedding = model.encode([title_text])[0]
                similarity = cosine_similarity(
                    [target_embedding], 
                    [title_embedding]
                )[0][0]
                
                logger.debug(f"标题相似度: {similarity}")
                
                # 如果相似度超过阈值
                if similarity > 0.8:
                    logger.info(f"找到目标表格! 页码: {page_num + 1}, 相似度: {similarity}")
                    result = {
                        'page_num': page_num,
                        'bbox': [
                            table_bbox[0],
                            table_bbox[1],
                            table_bbox[2],
                            table_bbox[3]
                        ],
                        'table_name': title_text,
                        'confidence': float(similarity)
                    }
                    logger.debug(f"返回结果: {result}")
                    return result
        
        logger.warning("未找到目标表格")
        return None
        
    except Exception as e:
        logger.error(f"处理PDF时发生错误: {str(e)}")
        return None
    
    finally:
        if 'doc' in locals():
            doc.close()
            logger.debug("PDF文档已关闭")

if __name__ == '__main__':
    # 配置日志级别
    logger.add("pdf_parser.log", rotation="500 MB", level="DEBUG")
    
    result = find_summary_table('/Users/mark/Documents/Terminal evaluation report/1.10321_2024_ValTR_unep_gef_msp.pdf')
    if result:
        logger.info(f"找到表格在第 {result['page_num'] + 1} 页")
        logger.info(f"表格坐标: {result['bbox']}")
        logger.info(f"表格标题: {result['table_name']}")
        logger.info(f"匹配置信度: {result['confidence']}")
    else:
        logger.warning("未找到目标表格") 