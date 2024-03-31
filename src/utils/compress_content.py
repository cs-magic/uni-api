from typing import List

from loguru import logger


def compress_content(content: str, target_len=6e3) -> str:
    """
    压缩字符串到指定的长度内
    """
    
    def horizontal_compress():
        nonlocal content

        def compress_line(line: str, ratio=.9) -> str:
            """
            压缩单行，按照比例将中间的变成省略号，两头保留
            """
            if len(line) < 20:
                return line
            
            n = len(line)
            return line[: int(n * ratio / 2)] + "……" + line[int(n * (1 - ratio / 2)):]
        
        def compress_lines(lines: List[str]) -> List[str]:
            """
            压缩多行，V 型，中间多压，两头少压 (.9 --> .4 --> .9)
            """
            n = max(len(lines) - 1, 1)
            return [compress_line(line, .4 + abs(i / n - .5)) for (i, line) in enumerate(lines)]
        
        logger.debug("horizontal compressing...")
        for i in range(1, 11):
            if len(content) <= target_len: return
            lines = content.splitlines()
            chars1 = len(content)
            content = "\n".join(compress_lines(lines))
            chars2 = len(content)
            logger.debug(f"[{i}] {len(lines)} lines, {chars1} --> {chars2}, ratio: {chars2 / chars1 * 100:.2f}%")
    
    def vertical_compress():
        nonlocal content

        logger.debug("vertical compressing...")
        i = 0
        while len(content) > target_len:
            lines = content.splitlines()
            k = len(lines) >> 1
            lines.pop(k)
            content = "\n".join(lines)
            i += 1
            logger.debug(f"[{i}] {len(lines)} lines, dropped {k}th line, current chars: {len(content)}")
    
    horizontal_compress()
    vertical_compress()
    return content
