import fitz
import time
from typing import Dict, List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
from .model_loader import ModelLoader

def find_summary_table(pdf_path: str) -> Optional[Dict]:
    """
    在PDF文档中定位"Summary of project findings and ratings"相关的表格
    """
    total_start_time = time.time()
    result = None

    try:
        # 目标表格名
        target_text = "Summary of project findings and ratings"
        
        # 获取目标文本的编码
        target_embedding = ModelLoader.encode_text(target_text)
        
        # 使用 with 语句管理 PDF 文档
        pdf_start_time = time.time()
        logger.debug("打开PDF文档...")
        with fitz.open(pdf_path) as doc:
            logger.debug(f"PDF总页数: {len(doc)}, 打开耗时: {time.time() - pdf_start_time:.2f}秒")
            
            for page_num in range(len(doc)):
                page_start_time = time.time()
                logger.debug(f"处理第 {page_num + 1} 页")
                
                try:
                    page = doc[page_num]
                    
                    # 尝试获取页面文本，检查页面是否可解析
                    try:
                        test_text = page.get_text("text")
                        if not test_text.strip():
                            logger.debug(f"第 {page_num + 1} 页是空白页或无法提取文本")
                            continue
                    except Exception as e:
                        logger.debug(f"第 {page_num + 1} 页文本提取失败: {str(e)}")
                        continue
                    
                    # 提取表格
                    try:
                        table_finder = page.find_tables()
                        tables = table_finder.tables
                        # After using table_finder, explicitly delete it
                        del table_finder
                    except Exception as e:
                        logger.debug(f"第 {page_num + 1} 页表格提取失败: {str(e)}")
                        continue
                    
                    logger.debug(f"在第 {page_num + 1} 页找到 {len(tables)} 个表格，表格提取耗时: {time.time() - page_start_time:.2f}秒")
                    
                    if not tables:
                        continue
                        
                    for table_idx, table in enumerate(tables):
                        table_start_time = time.time()
                        logger.debug(f"分析第 {page_num + 1} 页的第 {table_idx + 1} 个表格")
                        
                        try:
                            # 获取表格上方的文本作为可能的表格标题
                            table_bbox = table.bbox
                            above_area = fitz.Rect(
                                table_bbox[0],
                                max(0, table_bbox[1] - 50),
                                table_bbox[2],
                                table_bbox[1]
                            )
                            
                            # 提取可能的表格标题文本
                            title_text = page.get_text("text", clip=above_area).strip()
                            
                            if not title_text:
                                logger.debug("未找到表格标题，跳过")
                                continue
                            
                            logger.debug(f"找到表格标题: {title_text}")
                                
                            # 计算语义相似度
                            title_embedding = ModelLoader.encode_text(title_text)
                            similarity = cosine_similarity(
                                [target_embedding], 
                                [title_embedding]
                            )[0][0]
                            
                            logger.debug(f"标题相似度: {similarity}, 单个表格处理耗时: {time.time() - table_start_time:.2f}秒")
                            
                            # 如果相似度超过阈值
                            if similarity > 0.8:
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
                                break
                                
                        except Exception as e:
                            logger.warning(f"处理第 {page_num + 1} 页第 {table_idx + 1} 个表格时发生错误: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"处理第 {page_num + 1} 页时发生错误: {str(e)}")
                    continue
            
            return result
        
    except Exception as e:
        logger.error(f"处理PDF时发生错误: {str(e)}", exc_info=True)
        return result
    finally:
        return result
    