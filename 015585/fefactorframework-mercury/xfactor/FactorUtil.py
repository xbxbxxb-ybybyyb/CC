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


def check_xdb_tick_1s_full(factor_class): # 包括cancel和1m数据都是从2017开始
    if factor_class is None:
        return False
    if not factor_class.xdb_data:
        return False
    for data_dict in factor_class.xdb_data:
        if data_dict["name"] in ["xdb_tickfull", "xdb_tick1s", 'xdb_tickfulladdorder', 'xdb_cancel', 'xdb_tick1m', 'xdb_order1m',
                                 'xdb_cancel_cs', 'xdb_tick1m_cs', 'xdb_order1m_cs']:
            return True

    return False


def check_pure_cs_factor(factor_class):
    if factor_class is None:
        return False

    for data_dict in factor_class.xdb_data:
        if "_cs" not in data_dict["name"]:
            return False

    for data_name in factor_class.t_day_data:
        if "_cs" not in data_name:
            return False

    for data_dict in factor_class.other_t_day_data:
        if "_cs" not in data_dict["name"]:
            return False
    return True


def check_tday_tick1s_full(factor_class):
    if not factor_class.t_day_data:
        return False
    for data_name in factor_class.t_day_data:
        if data_name in ['TTickfull', 'TTickfulladdorder', 'TTick1s', 'TCancel', 'TCancelprice',
                         'T1mTickfull', 'T1mTickfulladdorder', 'T1mTick1s', 'T1mCancel', 'T1mTickfull_cs',
                         'T1mTick1s_cs', 'T1mCancel_cs', 'T1mTickfulladdorder_cs',
                         'Next1mTickfull', 'Next1mTickfulladdorder', 'Next1mTick1s', 'Next1mCancel',
                         'Next1mTickfull_cs', 'Next1mTickfulladdorder_cs', 'Next1mTick1s_cs', 'Next1mCancel_cs',
                         'TTickfull_MetisAll', 'TTickfulladdorder_MetisAll', 'TTick1s_MetisAll', 'TCancel_MetisAll',
                         'TCancelprice_MetisAll']:
            return True
    return False

def split_calc_factor_into_group(strategy, factor_class_list):
    group = {
        "t_day_factor": [],
        "pure_t_1_factor": [],
        "combined_t_1_factor": [],
        "xdb_tick": [],
        "non_xdb_tick": []
    }
    tickfull_list = []
    tickfulladdorder_list = []
    tick1s_list = []

    for factor in factor_class_list:
        if strategy not in factor.strategy_name:
            logger.warning(
                '[SKIP] factor={}, factor_strategy={}, setting_strategy={},因子代码中策略名称与设置不匹配'.format(factor.factor_name,
                                                                                                   factor.strategy_name,
                                                                                                   strategy))
            continue

        day_factor_data = False
        h5_data = False

        if factor.t_1_factor_data:
            h5_data = True

        if factor.t_day_data or factor.xdb_data:
            day_factor_data = True

        dic = {"factor": factor, "xdb_tickfull": 0, "xdb_tick1s": 0, "xdb_tickfulladdorder": 0}

        if factor.xdb_data:
            xdb_elements = []
            tickfull_related = []
            for item in factor.xdb_data:
                if item["name"] in xdb_elements:
                    logger.warning(
                        '[SKIP] factor={}, factor_strategy={}, duplicate_xdb_element={},因子代码中存在重复xdb数据'.format(
                            factor.factor_name, factor.strategy_name, item["name"]))
                    continue
                else:
                    xdb_elements.append(item["name"])

                if item["name"] in ["xdb_tickfull", "xdb_tickfulladdorder"]:
                    dic[item["name"]] = item["lag"]
                    if item["name"] not in tickfull_related:
                        tickfull_related.append(item["name"])
                elif item["name"] in ["xdb_tick1s"]:
                    dic[item["name"]] = item["lag"]

            if len(tickfull_related) > 1:
                logger.warning('[SKIP] factor={}, factor_strategy={}, 因子代码中存在重复xdb_tickfull数据'.format(
                    factor.factor_name, factor.strategy_name))
                continue

            if dic["xdb_tickfull"] == 0 and dic["xdb_tick1s"] == 0 and dic["xdb_tickfulladdorder"] == 0:
                group["non_xdb_tick"].append(dic)
            elif dic["xdb_tickfull"] != 0:
                tickfull_list.append(dic)
            elif dic["xdb_tickfulladdorder"] != 0:
                tickfulladdorder_list.append(dic)
            else:
                tick1s_list.append(dic)
        else:
            group["non_xdb_tick"].append(dic)

        if factor.other_t_day_data:
            day_factor_data = True

        if h5_data and not day_factor_data:
            group["pure_t_1_factor"].append(factor)
        elif not h5_data and day_factor_data:
            group["t_day_factor"].append(factor)
        elif h5_data and day_factor_data:
            group["combined_t_1_factor"].append(factor)

    tickfull_list.sort(key=lambda k: (k['xdb_tickfull'], k["xdb_tick1s"]), reverse=True)
    tickfulladdorder_list.sort(key=lambda k: (k["xdb_tickfulladdorder"], k["xdb_tick1s"]), reverse=True)
    tick1s_list.sort(key=lambda k: k["xdb_tick1s"], reverse=True)

    group["xdb_tick"] = tickfull_list + tickfulladdorder_list + tick1s_list
    return group
