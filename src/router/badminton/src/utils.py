def normalize_time(time_str: str) -> str:
    """
    将时间字符串转换为 24 小时制，格式为 HH:MM
    """
    hour, minute = time_str.split(":")
    hour = int(hour)
    return f"{hour:02d}:{minute}"
