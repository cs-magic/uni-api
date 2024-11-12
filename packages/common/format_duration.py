def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f'{seconds:.2f}s'
    minutes = seconds / 60
    if minutes < 60:
        return f'{minutes:.2f}m'
    hours = minutes / 60
    if hours < 24:
        return f'{hours:.2f}h'
    days = hours / 24
    return f'{days:.2f}d'
