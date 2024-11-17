import requests

import requests
from ..types import BadmintonCourtStatus
from ..utils import normalize_time
from typing import List
import time

def query_ruc_badminton_court_info(date_str: str) -> List[BadmintonCourtStatus]:
    """
    Query badminton court information for RUC (Renmin University of China) on a specific date.
    
    Args:
        date_str (str): The date to query in format 'YYYY-MM-DD'.
    
    Returns:
        List[BadmintonCourtStatus]: A list of BadmintonCourtStatus objects containing court availability information.
    """
    t = int(time.time() * 1000)
    t = 1728958011837
    url = f'https://cgyy.ruc.edu.cn/venue-server/api/reservation/day/info?venueSiteId=1&searchDate={date_str}&hasReserveInfo=1&nocache={t}'
    print("visit url: ", url)

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/en",
        "Referer": "https://cgyy.ruc.edu.cn/venue/venue-reservation/1",
        "Cookie": "JSESSIONID=A23F378211549E12D9C517F02B091778",
        "cgAuthorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyb2xlIjo2LCJuYW1lIjoi6YKi5YGlIiwibG9naW5DaGVja1N0YXR1cyI6MCwidXNlcklkIjozMzUzLCJ1c2VybmFtZSI6IjE3NzY2MDkxODU3IiwiaXNzIjoicmVzdGFwaXVzZXIiLCJhdWQiOiIwOThmNmJjZDQ2MjFkMzczY2FkZTRlODMyNjI3YjRmNiJ9.j2phR1qLLFPAkb4jLIXa1Ws32MNH39yFjQunh7iqUF4",
        "Accept": "application/json, text/plain, */*",
        "app-key": "8fceb735082b5a529312040b58ea780b",
        "timestamp": str(t),
        "sign": "0224200526c364872f9f2a8cd9105713",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    print("headers: ", headers)
    
    response = requests.get(url=url, headers=headers)
    data = response.json()

    print('data: ', data)
    
    if data['code'] != 200:
        raise Exception(f"Failed to fetch data: {data['message']}")
    
    court_statuses = []
    for time_slot in data['data']['timeList']:
        start_time = normalize_time(time_slot['startTime'])
        end_time = normalize_time(time_slot['endTime'])
        available_count = sum(1 for court in time_slot['siteList'] if court['status'] == 0)
        
        court_statuses.append(BadmintonCourtStatus(
            start_time=start_time,
            end_time=end_time,
            available_count=available_count
        ))
    
    return court_statuses