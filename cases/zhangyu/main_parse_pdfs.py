from loguru import logger
from src.pdf_parser import find_summary_text
from src.model_loader import ModelLoader
import sys
import os
import pandas as pd
from pathlib import Path
import concurrent.futures
import re
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich import box
from threading import Lock
from src.config import DEFAULT_CONFIG

# 添加状态表情映射
STATUS_EMOJI = {
    'pending': '⏳',
    'opening': '📂',
    'processing': '🔄',
    'processing_page': '📄',
    'success': '✅',
    'not_found': '❌',
    'parse_error': '⚠️',
    'error': '💔'
}

class ProgressTracker:
    def __init__(self, total_files):
        self.total_files = total_files
        self.results = {}
        self.lock = Lock()
        self.console = Console()
        
    def update_progress(self, file_name, status, details=None, best_match=None):
        with self.lock:
            # 如果是第一次更新这个文件的状态
            if file_name not in self.results:
                self.results[file_name] = {
                    'status': status,
                    'details': details,
                    'best_match': best_match
                }
            else:
                # 更新状态和详情
                self.results[file_name]['status'] = status
                self.results[file_name]['details'] = details
                # 只有当提供了新的最优匹配时才更新
                if best_match is not None:
                    self.results[file_name]['best_match'] = best_match
            
            logger.debug(f"{file_name}: {status} - {details} - Best match: {best_match}")
    
    def create_progress_table(self):
        table = Table(box=box.ROUNDED, expand=True, show_edge=True)
        table.add_column("序号", style="cyan", width=4)
        table.add_column("状态", width=2)
        table.add_column("文件名", style="blue", width=40, no_wrap=True)
        table.add_column("详情", style="green")
        table.add_column("最优匹配", style="yellow", width=60, no_wrap=True)
        
        sorted_items = sorted(self.results.items(), key=lambda x: extract_number(x[0]))
        for idx, (filename, info) in enumerate(sorted_items, 1):
            status = info['status']
            emoji = STATUS_EMOJI.get(status, '❓')
            details = info['details'] or ''
            best_match = info.get('best_match', '')
            
            # 如果文件名过长，截断并添加省略号
            if len(filename) > 27:  # 预留3个字符用于省略号
                truncated_filename = filename[:27] + "..."
            else:
                truncated_filename = filename
            
            table.add_row(
                str(idx),
                emoji,
                truncated_filename,
                str(details),
                str(best_match)
            )
        
        return table

def extract_number(filename):
    """从文件名中提取序号"""
    match = re.match(r'^(\d+)', filename)
    return int(match.group(1)) if match else float('inf')

def process_single_pdf(pdf_path, progress_tracker: ProgressTracker):
    """处理单个PDF文件并返回结果"""
    try:
        logger.debug(f"开始处理文件: {pdf_path.name}")
        progress_tracker.update_progress(pdf_path.name, 'opening', "正在打开文件...")
        
        def page_callback(page_num, total_pages, best_match=None):
            """页面处理进度回调"""
            details = f"正在处理第 {page_num + 1}/{total_pages} 页..."
            
            # 如果有最优匹配，格式化显示信息
            best_match_info = ""
            if best_match:
                best_match_info = (f"页码:{best_match['page_num'] + 1} "
                                 f"相似度:{best_match['confidence']:.2f} "
                                 f"文本:{best_match['matched_text'][:20]}...")
            
            logger.debug(f"{pdf_path.name}: {details}")
            progress_tracker.update_progress(
                pdf_path.name, 
                'processing_page', 
                details,
                best_match_info
            )
        
        logger.debug(f"{pdf_path.name}: 准备调用 find_summary_text...")
        progress_tracker.update_progress(pdf_path.name, 'processing', "开始处理文件内容...")
        
        # 设置超时时间
        try:
            result = find_summary_text(str(pdf_path), page_callback=page_callback)
            logger.debug(f"{pdf_path.name}: find_summary_text 调用完成")
        except Exception as e:
            logger.debug(f"{pdf_path.name}: find_summary_text 执行出错: {str(e)}")
            raise
        
        if result:
            details = f"找到目标! 页码:{result['page_num'] + 1}, 相似度:{result['confidence']:.2f}"
            logger.debug(f"{pdf_path.name}: {details}")
            progress_tracker.update_progress(pdf_path.name, 'success', details)
            return {
                'file_name': pdf_path.name,
                'status': 'success',
                'page_number': result['page_num'] + 1,
                'matched_text': result['matched_text'],
                'confidence': result['confidence'],
                'text_bbox': str(result['text_bbox']),
                'table_bbox': str(result['table_bbox']) if result['table_bbox'] else None
            }
        else:
            progress_tracker.update_progress(pdf_path.name, 'not_found', "搜索完成，未找到目标文字")
            return {
                'file_name': pdf_path.name,
                'status': 'not_found',
                'page_number': None,
                'matched_text': None,
                'confidence': None,
                'text_bbox': None,
                'table_bbox': None,
                'error_msg': '未找到目标文字'
            }
    except Exception as e:
        error_msg = str(e)
        if "not a textpage" in error_msg.lower():
            progress_tracker.update_progress(pdf_path.name, 'parse_error', "页面无法解析为文本")
            return {
                'file_name': pdf_path.name,
                'status': 'parse_error',
                'page_number': None,
                'matched_text': None,
                'confidence': None,
                'text_bbox': None,
                'table_bbox': None,
                'error_msg': '页面无法解析为文本'
            }
        else:
            progress_tracker.update_progress(pdf_path.name, 'error', f"错误: {error_msg[:50]}...")
            return {
                'file_name': pdf_path.name,
                'status': 'error',
                'page_number': None,
                'matched_text': None,
                'confidence': None,
                'text_bbox': None,
                'table_bbox': None,
                'error_msg': error_msg
            }

def process_pdf_files(folder_path, max_workers=None):
    """并发处理文件夹中的所有PDF文件并返回结果列表"""
    pdf_files = list(Path(folder_path).glob('**/*.pdf'))
    pdf_files.sort(key=lambda x: extract_number(x.name))
    pdf_files = pdf_files[:20]
    total_files = len(pdf_files)
    
    logger.info(f"找到 {total_files} 个PDF文件待处理")
    
    # if max_workers is None:
        # max_workers = 2  # 降低并发数，方便调试
    
    logger.info(f"设置最大并发数为: {max_workers}")
    
    progress_tracker = ProgressTracker(total_files)
    console = Console()
    
    # 初始化所有文件状态为pending
    for pdf_file in pdf_files:
        progress_tracker.update_progress(pdf_file.name, 'pending', "等待处理")
    
    results = []
    
    # 创建一个共享的Live对象，供回调函数使用
    live = None
    
    def update_display():
        """更新显示的辅助函数"""
        if live:
            live.update(progress_tracker.create_progress_table())
    
    # 包装progress_tracker，使其在更新状态时自动刷新显示
    class DisplayUpdatingTracker:
        def __init__(self, tracker):
            self.tracker = tracker
            
        def update_progress(self, *args, **kwargs):
            self.tracker.update_progress(*args, **kwargs)
            update_display()
    
    display_tracker = DisplayUpdatingTracker(progress_tracker)
    
    try:
        with Live(
            progress_tracker.create_progress_table(),
            console=console,
            refresh_per_second=4,
            transient=False,
            vertical_overflow="visible"
        ) as live_display:
            live = live_display  # 保存live对象的引用
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for pdf_path in pdf_files:
                    logger.debug(f"提交任务: {pdf_path.name}")
                    # 使用包装后的tracker
                    future = executor.submit(process_single_pdf, pdf_path, display_tracker)
                    futures.append((future, pdf_path))
                
                for future, pdf_path in futures:
                    try:
                        result = future.result(timeout=300)
                        results.append(result)
                    except concurrent.futures.TimeoutError:
                        logger.debug(f"处理文件超时: {pdf_path.name}")
                        display_tracker.update_progress(pdf_path.name, 'error', "处理超时")
                    except Exception as e:
                        logger.debug(f"处理文件出错: {pdf_path.name}, 错误: {str(e)}")
                        display_tracker.update_progress(pdf_path.name, 'error', f"错误: {str(e)[:50]}...")
    
    except KeyboardInterrupt:
        logger.warning("用户中断处理")
        return results
    
    return results

def save_statistics(results, output_path):
    """将结果保存为Excel统计表，并增加相似度分析"""
    df = pd.DataFrame(results)
    
    # 添加相似度分布分析
    successful_results = df[df['status'] == 'success']
    if not successful_results.empty:
        confidence_stats = successful_results['confidence'].describe()
        logger.info(f"""相似度统计:
        最小值: {confidence_stats['min']:.3f}
        最大值: {confidence_stats['max']:.3f}
        平均值: {confidence_stats['mean']:.3f}
        中位数: {confidence_stats['50%']:.3f}""")
    
    # 重新排列列的顺序，使其更有逻辑性
    columns_order = [
        'file_name', 
        'status', 
        'page_number',
        'matched_text',
        'confidence',
        'text_bbox',
        'table_bbox',
        'error_msg'
    ]
    
    # 确保所有列都存在，如果不存在则填充 None
    for col in columns_order:
        if col not in df.columns:
            df[col] = None
            
    # 按指定顺序重排列列
    df = df[columns_order]
    
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
    未找到目标文字: {not_found}
    页面解析错误: {parse_error}
    其他错误: {error}""")

def main():
    # 加载配置
    config = DEFAULT_CONFIG
    
    # 移除默认的 stderr 处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        level=config.log.console_level,
        format=config.log.console_format,
        colorize=True
    )
    
    # 添加文件处理器
    logger.add(
        str(config.log.log_file),
        level=config.log.file_level,
        format=config.log.log_format,
        rotation=config.log.rotation
    )
    
    # 打印配置信息
    logger.info("当前配置:")
    logger.info(config)
    
    try:
        # 预热模型
        logger.info("预热模型...")
        ModelLoader.get_model()
        
        # 处理所有PDF文件
        results = process_pdf_files(
            config.pdf.pdf_folder,
            max_workers=config.pdf.max_workers
        )
        
        # 保存统计结果
        if results:
            save_statistics(results, config.pdf.output_file)
        
    except Exception as e:
        logger.exception("处理过程中发生错误")
        raise

if __name__ == '__main__':
    main() 