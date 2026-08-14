import os
import pandas as pd
import settings
from loguru import logger

# 获取T日数据
def get_data(path):
    if any([s in path for s in ['/dfs/group/800463/data/projectZZmkt_prod/everyday_Data_931/',
                                '/dfs/group/800463/data/projectZZ1000_prod/',
                                '/dfs/group/800463/public/projectZZmkt_prod/everyday_Data_931/',
                                '/dfs/group/800463/public/projectZZ1000_prod/']]):
        df = pd.read_pickle(path, compression='gzip')
    else:
        df = pd.read_pickle(path)
    return df

# TODO remove this while testing
def get_basic_data(strategy):
    return get_data(settings.path_dict[strategy]["Basic"])

# TODO full basic path, change if file is .h5
def get_full_basic_df(strategy):
    return get_data(settings.path_dict[strategy]["FullBasic"])

def get_t_data_path(strategy_type, data_type, date):
    strategy_type = strategy_type.lower()

    tmp_path = settings.path_dict[strategy_type].get(data_type, "")

    if tmp_path == "":
        logger.error("File path not found! strategy_type={}, data_type={}".format(strategy_type, data_type))
        raise RuntimeError("File Path Error")

    return os.path.join(tmp_path, str(date) + ".pkl")