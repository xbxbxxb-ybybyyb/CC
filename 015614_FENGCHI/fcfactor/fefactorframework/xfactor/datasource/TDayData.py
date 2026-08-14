import os
import pandas as pd
from settings import path_dict
from loguru import logger

# 获取T日数据
def get_data(path):
    df = pd.read_pickle(path)
    return df

# TODO remove this while testing
def get_basic_data(strategy):
    return get_data(path_dict[strategy]["Basic"])


def get_t_data_path(strategy_type, data_type, date):
    strategy_type = strategy_type.lower()

    tmp_path = path_dict[strategy_type].get(data_type, "")

    if tmp_path == "":
        logger.error("File path not found! strategy_type={}, data_type={}".format(strategy_type, data_type))
        raise RuntimeError("File Path Error")

    return os.path.join(tmp_path, str(date) + ".pkl")
