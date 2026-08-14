import os
from h5data.IO import IO
from settings import path_dict
from loguru import logger

# 获取T-1Factor数据
def get_data(path, start_time, end_time, columns):
    if columns:
        return IO.read_data([start_time, end_time], columns=columns, alt=path)
    else:
        return IO.read_data([start_time, end_time], alt=path)

def get_t_1_factor_path(data_name):
    tmp_path = path_dict["t_1_factor"].get(data_name, "")
    if tmp_path == "":
        logger.error("File path not found! data_name={}".format(data_name))
        raise RuntimeError("File Path Error")
    return tmp_path

def get_industry_data(start_date, end_date):
    df = IO.read_data([start_date, end_date], columns=['Industry'],
                        alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')

    return df
