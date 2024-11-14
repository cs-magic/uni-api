from loguru import logger
from src.pdf_parser import find_summary_table
from src.model_loader import ModelLoader
import sys
import os
import pandas as pd
from pathlib import Path
import concurrent.futures
import re

def extract_number(filename):
    """从文件名中提取序号"""
    match = re.match(r'^(\d+)', filename)
    return int(match.group(1)) if match else float('inf')

def process_single_pdf(pdf_path):
    """处理单个PDF文件并返回结果"""
    try:
        # 添加更详细的日志记录
        logger.debug(f"开始处理文件: {pdf_path.name}")
        result = find_summary_table(str(pdf_path))
        
        if result:
            logger.debug(f"成功从文件 {pdf_path.name} 提取表格信息")
            return {
                'file_name': pdf_path.name,
                'status': 'success',
                'page_number': result['page_num'] + 1,
                'table_name': result['table_name'],
                'confidence': result['confidence'],
                'bbox': str(result['bbox'])
            }
        else:
            return {
                'file_name': pdf_path.name,
                'status': 'not_found',
                'page_number': None,
                'table_name': None,
                'confidence': None,
                'bbox': None,
                'error_msg': '未找到目标表格'
            }
    except Exception as e:
        error_msg = str(e)
        if "not a textpage" in error_msg.lower():
            logger.warning(f"文件 {pdf_path.name} 包含无法解析为文本的页面: {error_msg}")
            return {
                'file_name': pdf_path.name,
                'status': 'parse_error',
                'page_number': None,
                'table_name': None,
                'confidence': None,
                'bbox': None,
                'error_msg': '页面无法解析为文本'
            }
        else:
            logger.error(f"处理文件 {pdf_path.name} 时发生错误: {error_msg}", exc_info=True)
            return {
                'file_name': pdf_path.name,
                'status': 'error',
                'page_number': None,
                'table_name': None,
                'confidence': None,
                'bbox': None,
                'error_msg': error_msg
            }

def process_pdf_files(folder_path, max_workers=None):
    """并发处理文件夹中的所有PDF文件并返回结果列表"""
    pdf_files = list(Path(folder_path).glob('**/*.pdf'))
    # 按文件名中的序号排序
    pdf_files.sort(key=lambda x: extract_number(x.name))
    total_files = len(pdf_files)
    
    logger.info(f"找到 {total_files} 个PDF文件待处理")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pdf = {executor.submit(process_single_pdf, pdf_path): pdf_path 
                        for pdf_path in pdf_files}
        
        for index, future in enumerate(concurrent.futures.as_completed(future_to_pdf), 1):
            pdf_path = future_to_pdf[future]
            result = future.result()
            # 精简的日志输出格式
            status_msg = {
                'success': f"找到表格(页码:{result['page_number']}, 相似度:{result['confidence']:.2f})",
                'not_found': "未找到表格",
                'parse_error': "解析错误",
                'error': f"错误: {result['error_msg']}"
            }.get(result['status'])
            
            logger.info(f"[{index}/{total_files}] {pdf_path.name} - {status_msg}")
            results.append(result)
    
    results.sort(key=lambda x: extract_number(x['file_name']))
    return results

def save_statistics(results, output_path):
    """将结果保存为Excel统计表"""
    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False)
    logger.info(f"统计结果已保存至: {output_path}")
    
    # 输出详细统计信息
    total = len(results)
    success = len([r for r in results if r['status'] == 'success'])
    not_found = len([r for r in results if r['status'] == 'not_found'])
    parse_error = len([r for r in results if r['status'] == 'parse_error'])
    error = len([r for r in results if r['status'] == 'error'])
    
    logger.info(f"""处理统计:
    总文件数: {total}
    成功处理: {success}
    未找到表格: {not_found}
    页面解析错误: {parse_error}
    其他错误: {error}""")

def main():
    # 移除默认的 stderr 处理器
    logger.remove()
    
    # 添加文件处理器，设置 DEBUG 级别
    logger.add("pdf_parser.log", rotation="500 MB", level="DEBUG")
    # 添加控制台处理器，设置 INFO 级别
    logger.add(sys.stderr, level="INFO")
    
    # 预热模型
    logger.info("预热模型...")
    ModelLoader.get_model()
    
    # 设置PDF文件夹路径和输出文件路径
    pdf_folder = '/Users/mark/Documents/Terminal evaluation report'  # 替换为实际的PDF文件夹路径
    output_file = 'pdf_processing_results.xlsx'
    
    # 处理所有PDF文件，设置并发数为CPU核心数的2倍
    max_workers = os.cpu_count() * 2
    # max_workers = 4 # 太慢了
    results = process_pdf_files(pdf_folder, max_workers=max_workers)
    
    # 保存统计结果
    save_statistics(results, output_file)

if __name__ == '__main__':
    main() 