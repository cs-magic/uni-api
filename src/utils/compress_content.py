from typing import List

from loguru import logger


def compress_content(content: str, target_len=6e3) -> str:
    """
    压缩字符串到指定的长度内
    """
    
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
    
    seq = 0
    while len(content) >= target_len:
        seq += 1
        if seq > 10:
            raise Exception("failed to compress...")
        
        lines = content.splitlines()
        charsBefore = len(content)
        content = "\n".join(compress_lines(lines))
        charsAfter = len(content)
        logger.debug(f"compressed content ({len(lines)} lines): {charsBefore} --> {charsAfter}, ratio: {charsAfter / charsBefore * 100:.2f}%")
    return content
