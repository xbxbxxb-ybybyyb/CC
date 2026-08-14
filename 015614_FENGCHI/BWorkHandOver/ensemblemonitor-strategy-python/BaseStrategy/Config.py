import time
import os
import json

BASE_DIR = "/data/group/800002/realtime/alpha"

# 实时数据地址
REALTIME_DATA_PATH = os.path.join(BASE_DIR, "market_data")
# 因子计算结果地址
FACTOR_SAVE_PATH = os.path.join(BASE_DIR, "x_day_lib")
# 分钟数据日期
TODAY_DATE = time.strftime('%Y%m%d', time.localtime(time.time()))

# 因子计算时间点
TIMETABLE_LIST = [
    "1000",
    "1030",
    "1100",
    "1300",
    "1330",
    "1400",
    "1430"
]


# 因子计算日期
def get_today_date():
    return TODAY_DATE


def get_timetable_list():
    return TIMETABLE_LIST


def get_realtime_data_path():
    return REALTIME_DATA_PATH


def get_factor_save_path():
    return FACTOR_SAVE_PATH
