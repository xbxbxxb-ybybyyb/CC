import importlib
from xquant.factordata import FactorData
from enum import Enum, unique
import pandas as pd
import numpy as np
from loguru import logger

import settings


@unique
class FactorType(Enum):
    PREPARE = 0,
    T_DAY_FACTOR = 1,
    T_1_FACTOR = 2,
    COMBINED_FACTOR = 3

factor_data = FactorData()

valid_dates = pd.read_pickle(settings.xdb_valid_dates_path)

def get_class(kls):
    parts = kls.split(".")
    module = ".".join(parts[:-1])
    if check_module(module):
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    else:
        raise Exception("No factor module:" + module)


def check_module(module_name):
    """检查模块时候能被导入而不用实际的导入模块"""
    return importlib.util.find_spec(module_name)


def get_factor_module(factor_name):
    if check_module(".".join(["factor", factor_name])):
        return "factor"
    else:
        return None


def get_factor_class(factor_name):
    module_name = get_factor_module(factor_name)
    if module_name:
        return get_class(".".join([module_name, factor_name, factor_name]))
    else:
        raise Exception("No factor found:" + factor_name)


def get_factor_class_list(factor_name_list):
    return [get_factor_class(factor_name) for factor_name in factor_name_list]


def is_same_freq_factor(factor_class_list):
    freq_set = set()
    for factor in factor_class_list:
        freq_set.add(factor.factor_type)
    return len(freq_set) == 1


def create_factor_instance(factor_class):
    factor_instance = factor_class()

    return factor_instance


def get_max_xdb_lag(factor_class_list):
    max_lag = -1
    for factor in factor_class_list:
        if factor.xdb_data:
            for data_dict in factor.xdb_data:
                max_lag = max(data_dict["lag"], max_lag)

    return max_lag


def check_xdb_tick_1s_full(factor_class):
    if not factor_class.xdb_data:
        return False
    for data_dict in factor_class.xdb_data:
        if data_dict["name"] == "xdb_tickfull" or data_dict["name"] == "xdb_tick1s":
            return True

    return False


def split_calc_factor_into_group(strategy, factor_class_list):
    group = {
        "t_day_factor": [],
        "pure_t_1_factor": [],
        "combined_t_1_factor": []
    }

    for factor in factor_class_list:
        if strategy not in factor.strategy_name:
            logger.warning('factor = {},factor_strategy={},setting_strategy={},因子代码中策略名称与设置不匹配'.format(factor.factor_name, factor.strategy_name, strategy))
            continue

        day_factor_data = False
        h5_data = False

        if factor.t_1_factor_data:
            h5_data = True

        if factor.t_day_data or factor.xdb_data:
            day_factor_data = True

        if factor.other_t_day_data:
            day_factor_data = True

        if h5_data and not day_factor_data:
            group["pure_t_1_factor"].append(factor)
        elif not h5_data and day_factor_data:
            group["t_day_factor"].append(factor)
        elif h5_data and day_factor_data:
            group["combined_t_1_factor"].append(factor)

    return group

def fun_append_next_tradingday(factor_df):
    # 实盘中需要在T日开盘之前取到T-1日的因子，为了shift之后能有T日的时间戳，所以先把T日的时间戳加上去，取历史数据则没有该问题
    factor_df_unstack = factor_df.unstack()
    last_timestamp = factor_df_unstack.index[-1]
    break_flag = True
    counter = 0
    date = ""
    while break_flag:
        if counter > 5:
            raise RuntimeError("tradingday接口调用失败超过5次！")

        try:
            date = factor_data.tradingday(last_timestamp.strftime('%Y%m%d'), 2)[-1]
            break_flag = False
        except Exception as e:
            logger.warning("tradingday接口调用失败！重试...")
            counter += 1

    next_tradingday_timestamp = pd.Timestamp(date)
    next_tradingday_df = pd.DataFrame(np.zeros((1, factor_df_unstack.shape[1])), columns=factor_df_unstack.columns,
                                      index=[next_tradingday_timestamp])
    factor_df = (factor_df_unstack.append(next_tradingday_df)).stack()
    factor_df.index.names = ['dt', 'Ticker']
    return factor_df
