from pprint import pprint

from src.beike.query import query_beike_badminton
from src.tsinghua.query import TsinghuaBadmintonGym, query_tsinghua_badminton


if __name__ == "__main__":
    date = "2024-10-16"
    pprint(query_beike_badminton(date))
    pprint(query_tsinghua_badminton(date, TsinghuaBadmintonGym.清华大学综体羽毛球场))
    pprint(query_tsinghua_badminton(date, TsinghuaBadmintonGym.清华大学西体羽毛球场))
    pprint(query_tsinghua_badminton(date, TsinghuaBadmintonGym.清华大学气膜馆羽毛球场))