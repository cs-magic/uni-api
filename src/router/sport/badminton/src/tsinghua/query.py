from enum import Enum
from pprint import pprint
import requests
import re
from collections import defaultdict

from ..types import BadmintonCourtStatus


class TsinghuaBadmintonSport(int, Enum  ):
    # 羽毛球 = 4045681
    羽毛球 = 4836196

class TsinghuaBadmintonGym(int, Enum):
    清华大学气膜馆羽毛球场 = 3998000
    清华大学综体羽毛球场 = 4797914
    清华大学西体羽毛球场 = 4836273


tsinghua_badminton_gym_id_to_item_id = {
    TsinghuaBadmintonGym.清华大学气膜馆羽毛球场: 4045681,
    TsinghuaBadmintonGym.清华大学综体羽毛球场: 4797899,
    TsinghuaBadmintonGym.清华大学西体羽毛球场: 4836196,
}


def query_tsinghua_badminton(date, place: TsinghuaBadmintonGym) -> list[BadmintonCourtStatus]:
    """


    从 ./data/2024-10-15-西体羽毛球.html 中查询 date 和 place 的场地状态
    1、从 `resourceArray.push({id:'5500077',time_session:'7:00-8:00',field_name:'Óð1',overlaySize:'2',can_net_book:'1'});` 这样的格式中提取 id、时间，这些代表候选场地
    2、从 `markStatusColor('5500077','Ñ§Éú','1','');` 这样的格式中提取 id，表示该 id 的场地已经被预定

    最终返回一个列表，列表中包含每个时间段的统计信息，包括时间、可预定的数量。
    列表按时间升序排序。
    """


    # # 读取HTML文件
    # with open(f'./data/{date}-{place}羽毛球.html', 'r', encoding='utf-8') as file:
    #     content = file.read()

    print({date, place.name})

    item_id = tsinghua_badminton_gym_id_to_item_id[place]


    url = f"https://50.tsinghua.edu.cn/gymsite/cacheAction.do?ms=viewBook&time_date={date}&userType="

    payload = {}
    headers = {
    'Cookie': 'serverid=1425456'
    }

    query = {
        "gymnasium_id": place.value,
        "item_id": item_id
    }

    response = requests.request("GET", url, headers=headers, params=query, data=payload)

    content = response.text


    # 提取候选场地信息
    candidate_pattern = r"resourceArray\.push\(\{id:'(\d+)',time_session:'(\d+:\d+)-(\d+:\d+)',.*?\}\);"
    candidates = re.findall(candidate_pattern, content)
    
    # 统一时间格式为 HH:MM
    formatted_candidates = []
    for court_id, start_time, end_time in candidates:
        start_time = start_time.zfill(5)  # 确保格式为 HH:MM
        end_time = end_time.zfill(5)  # 确保格式为 HH:MM
        formatted_candidates.append((court_id, start_time, end_time))
    candidates = formatted_candidates

    # 提取已预定场地信息
    booked_pattern = r"markStatusColor\('(\d+)',.*?\);"
    booked = set(re.findall(booked_pattern, content))

    # 统计可用场地
    available_courts = defaultdict(int)
    for court_id, start_time, end_time in candidates:
        available_courts[(start_time, end_time)] += court_id not in booked

    # 格式化结果
    result = [
        BadmintonCourtStatus(
            start_time=start_time,
            end_time=end_time,
            available_count=available_count
        )
        for (start_time, end_time), available_count in available_courts.items()
    ]

    return sorted(result, key=lambda x: x.start_time)



