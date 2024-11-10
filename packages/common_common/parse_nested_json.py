import json
from typing import Union, Dict, List, Any, Optional


def _match_field_path(current_path: str, field_paths: List[str]) -> bool:
    """
    检查当前路径是否匹配任何目标解析路径

    Args:
        current_path: 当前字段的完整路径（如 'publish_page.publish_list.publish_info'）
        field_paths: 要解析的字段路径列表

    Returns:
        bool: 是否匹配
    """
    if not field_paths:
        return True

    return any(
        current_path == path or
        current_path.startswith(path + '.') or
        path.startswith(current_path + '.')
        for path in field_paths
    )


def parse_nested_json(
    data: Union[Dict, List],
    fields_to_parse: Optional[List[str]] = None,
    current_path: str = ""
) -> Union[Dict, List]:
    """
    递归解析嵌套的 JSON 字符串，支持通过点号分隔的路径指定字段

    Args:
        data: 要解析的数据，可以是字典或列表
        fields_to_parse: 需要解析的字段路径列表。例如 ['publish_page', 'publish_page.publish_list.publish_info']
        current_path: 当前处理的字段路径（内部使用）

    Returns:
        解析后的数据结构
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # 构建当前字段的完整路径
            new_path = f"{current_path}.{key}" if current_path else key

            # 检查是否需要解析这个字段
            should_parse = _match_field_path(new_path, fields_to_parse)

            if should_parse and isinstance(value, str):
                try:
                    # 尝试解析 JSON 字符串
                    parsed_value = json.loads(value)
                    result[key] = parse_nested_json(parsed_value, fields_to_parse, new_path)
                except json.JSONDecodeError:
                    # 如果解析失败，保持原值
                    result[key] = value
            elif isinstance(value, (dict, list)):
                # 递归处理嵌套的字典或列表
                result[key] = parse_nested_json(value, fields_to_parse, new_path)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        # 对于列表，保持当前路径不变，因为列表索引不计入路径
        return [parse_nested_json(item, fields_to_parse, current_path) for item in data]
    else:
        return data