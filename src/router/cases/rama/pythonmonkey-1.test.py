import pythonmonkey


def replace_null_with_none(obj):
    if obj is pythonmonkey.null:
        return None
    elif isinstance(obj, dict):
        return {k: replace_null_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_null_with_none(item) for item in obj]
    else:
        return obj


# Example usage
test_data = {"a": 1, "b": pythonmonkey.null, "c": [pythonmonkey.null, {"d": pythonmonkey.null}, 2]}

result = replace_null_with_none(test_data)
print(result)

# To verify the conversion
print(f"Type of 'b': {type(result['b'])}")
print(f"Type of first item in 'c': {type(result['c'][0])}")
print(f"Type of 'd' in second item of 'c': {type(result['c'][1]['d'])}")
