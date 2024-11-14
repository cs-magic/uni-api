import fitz
import time
from typing import Dict, List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
from .model_loader import ModelLoader
from .config import TARGET_TABLE_CONFIG

def find_summary_text(pdf_path: str, page_callback=None) -> Optional[Dict]:
    """
    在PDF文档中查找目标文字（通常是表格标题）
    返回相似度最高的匹配结果，包含文字位置信息和下方表格的位置

    Args:
        pdf_path: PDF文件路径
        page_callback: 页面处理进度回调函数，接收当前页码和总页数作为参数
    Returns:
        dict: 包含匹配结果的字典，如果未找到则返回 None
    """
    total_start_time = time.time()
    best_match = {
        'confidence': -1,
        'page_num': None,
        'text_bbox': None,  # 匹配文字的位置
        'table_bbox': None,  # 文字下方表格的位置
        'matched_text': None
    }

    try:
        # 获取目标文本的编码
        target_text = TARGET_TABLE_CONFIG['name']
        target_embedding = ModelLoader.encode_text(target_text)
        
        pdf_start_time = time.time()
        logger.debug("打开PDF文档...")
        with fitz.open(pdf_path) as doc:
            logger.debug(f"PDF总页数: {len(doc)}, 打开耗时: {time.time() - pdf_start_time:.2f}秒")
            
            total_pages = len(doc)
            for page_num in range(total_pages):
                page_start_time = time.time()
                logger.debug(f"处理第 {page_num + 1} 页")
                
                # 调用回调函数报告当前进度
                if page_callback:
                    page_callback(page_num, total_pages)
                
                try:
                    page = doc[page_num]
                    
                    # 获取页面上的所有文本块
                    blocks = page.get_text("dict")["blocks"]
                    
                    for block in blocks:
                        if "lines" not in block:
                            continue
                            
                        # 获取文本块的内容
                        text = " ".join([span["text"] for line in block["lines"] 
                                       for span in line["spans"]]).strip()
                        
                        if not text:
                            continue
                            
                        # 计算语义相似度
                        text_embedding = ModelLoader.encode_text(text)
                        similarity = cosine_similarity(
                            [target_embedding], 
                            [text_embedding]
                        )[0][0]
                        
                        if similarity > best_match['confidence']:
                            # 获取文本块的位置
                            text_bbox = block["bbox"]
                            
                            # 查找文本块下方的表格
                            table_bbox = None
                            try:
                                table_finder = page.find_tables()
                                for table in table_finder.tables:
                                    # 检查表格是否在文本块下方
                                    if (table.bbox[1] > text_bbox[3] and  # 表格在文本下方
                                        table.bbox[0] >= text_bbox[0] - 50 and  # 表格与文本水平位置接近
                                        table.bbox[2] <= text_bbox[2] + 50 and
                                        table.bbox[1] - text_bbox[3] < 50):  # 表格与文本垂直距离不太远
                                        table_bbox = table.bbox
                                        break
                                del table_finder
                            except Exception as e:
                                logger.debug(f"表格检测失败: {str(e)}")
                            
                            best_match = {
                                'page_num': page_num,
                                'text_bbox': [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]],
                                'table_bbox': ([table_bbox[0], table_bbox[1], table_bbox[2], table_bbox[3]] 
                                             if table_bbox else None),
                                'matched_text': text,
                                'confidence': float(similarity)
                            }
                            
                except Exception as e:
                    logger.warning(f"处理第 {page_num + 1} 页时发生错误: {str(e)}")
                    continue
            
            # 返回最佳匹配结果
            return best_match if best_match['confidence'] > -1 else None
        
    except Exception as e:
        logger.error(f"处理PDF时发生错误: {str(e)}", exc_info=True)
        return None
    