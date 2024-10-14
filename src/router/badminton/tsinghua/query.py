from pprint import pprint


def query_tsinghua_badminton(date, place):
    """
    从 ./data/2024-10-15-西体羽毛球.html 中查询 date 和 place 的场地状态

    1、从 `resourceArray.push({id:'5500077',time_session:'7:00-8:00',field_name:'Óð1',overlaySize:'2',can_net_book:'1'});` 这样的格式中提取 id、时间，这些代表候选场地
    2、从 `markStatusColor('5500077','Ñ§Éú','1','');` 这样的格式中提取 id，表示该 id 的场地已经被预定

    最终返回一个列表，列表中包含每个时间段的统计信息，包括时间、可预定的数量。
    列表按时间升序排序。
    """
    import re
    from collections import defaultdict

    # 读取HTML文件
    with open(f'./data/{date}-{place}羽毛球.html', 'r', encoding='utf-8') as file:
        content = file.read()

    # 提取候选场地信息
    candidate_pattern = r"resourceArray\.push\(\{id:'(\d+)',time_session:'(\d+:\d+)-(\d+:\d+)',.*?\}\);"
    candidates = re.findall(candidate_pattern, content)
    
    # 统一时间格式为 HH:MM
    formatted_candidates = []
    for court_id, start_time, end_time in candidates:
        start_time = start_time.zfill(5)  # 确保格式为 HH:MM
        end_time = end_time.zfill(5)  # 确保格式为 HH:MM
        formatted_candidates.append((court_id, f"{start_time}-{end_time}"))
    candidates = formatted_candidates

    # 提取已预定场地信息
    booked_pattern = r"markStatusColor\('(\d+)',.*?\);"
    booked = set(re.findall(booked_pattern, content))

    # 统计可用场地
    available_courts = defaultdict(int)
    for court_id, time_slot in candidates:
        available_courts[time_slot] += court_id not in booked

    # 格式化结果
    result = [{"时间": time, "可供预定的场地数量": count} for time, count in available_courts.items()]

    return sorted(result, key=lambda x: x["时间"])


if __name__ == "__main__":
    pprint(query_tsinghua_badminton("2024-10-15", "西体"))
