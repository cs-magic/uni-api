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
    
    while len(content) >= target_len:
        L1 = len(content)
        content = "\n".join(compress_lines(content.splitlines()))
        L2 = len(content)
        logger.debug(f"compressed content: {L1} --> {L2}, ratio: {L2 / L1 * 100:.2f}%")
    return content
