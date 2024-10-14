import json
from pprint import pprint
import requests

from ..utils import normalize_time

def query_beike_badminton(date):

    print({date, "北科大体育馆"})

    url = f"http://32901.koksoft.com/GuestGetForm.aspx?datatype=viewchangdi4weixinvguest&pagesize=0&pagenum=0&searchparam=orderdate%3D{date}%7Clxbh%3DY&wxkey=E7E7EB4C8EC1A817B3858271B986FBBA0ECE35796DD6B28992DAB943C20CC2235734D8DD36E20AB6425DAE0E30E8080E00B5149C31AAF8D018D123A07C6050749A515AAC19DB70160859E9EE5FF6DEAE9B334F09023BE6F6304947D8C4F3AD01D6E55D9973F8617E29C4C1EF6778D8A1"
    response = requests.get(url)

    data = response.json()[1]
    data = json.loads(data)['rows']
    result = []
    for item in data:
        # print(item['id'], item['timemc'], item['endtimemc'])
        # 'lxbh1': 'Y', 'cdbh1': '1', 'cdmc1': '羽1', 'c1': 'u', 'price1': '', 'packageid1': '',
        available = sum([1 for k, v in item.items() if k.startswith("lxbh") and v != "Y"])
        result.append({"start_time": normalize_time(item['timemc']), "end_time": normalize_time(item['endtimemc']), "available": available})
    # print(data)
    return result


if __name__ == "__main__":
    pprint(query_beike_badminton("2024-10-18"))
