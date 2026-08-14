import importlib

from loguru import logger
from xquant.factordata import FactorData
from enum import Enum, unique
import pandas as pd
import numpy as np

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


def get_factor_module(module_dir, factor_name):
    if module_dir[0] == "/":
        module_dir = module_dir[1:]
    if module_dir[-1] == '/':
        module_dir = module_dir[:-1]

    module_dir = module_dir.replace("//", "/")
    li = module_dir.split('/')

    if check_module(".".join(li + [factor_name])):
        return li
    else:
        return None


def get_factor_class(module_path, factor_name):
    module_name = get_factor_module(module_path, factor_name)
    if module_name:
        return get_class(".".join(module_name + [factor_name, factor_name]))
    else:
        raise Exception("No factor found:" + factor_name)


def get_factor_class_list(factor_name_list):
    for factor_dict in factor_name_list:
        factor_dict["factor_class"] = get_factor_class(factor_dict["module_path"], factor_dict["factor_name"])
    return factor_name_list


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
    next_tradingday_df = pd.DataFrame(np.zeros((1,factor_df_unstack.shape[1])), columns=factor_df_unstack.columns,
                                      index=[next_tradingday_timestamp])
    factor_df = (factor_df_unstack.append(next_tradingday_df)).stack()
    factor_df.index.names = ['dt', 'Ticker']
    return factor_df

# 202508: 更完善的fillna
def fill_factor_na_values(result_df, factor_class, basic_file):
    fillna_value = factor_class.fill_na_value
    factor_name = factor_class.factor_name
    strategy = factor_class.strategy_name
    if type(fillna_value) == float or type(fillna_value) == int:
        result_df = result_df.fillna(fillna_value)
        return result_df
    elif strategy not in ['neptune', 'neptunelong']:
        print(f'!!! {factor_name}非 neptune/neptunelong 策略因子，无法使用非float和int的填充值')
        raise TypeError
    elif type(fillna_value) == tuple:
        if len(fillna_value) != 2:
            print(factor_name, 'fillna_value error, type == tuple and length != 2')
            raise TypeError
        elif fillna_value[0] == 'mean':
            result_df[factor_name] = result_df[factor_name].fillna(result_df.groupby(['dt'])[factor_name].transform('mean'))
            result_df[factor_name] = result_df[factor_name].fillna(fillna_value[1])
        elif fillna_value[0] == 'median':
            result_df[factor_name] = result_df[factor_name].fillna(result_df.groupby(['dt'])[factor_name].transform('median'))
            result_df[factor_name] = result_df[factor_name].fillna(fillna_value[1])
        elif fillna_value[0] == 'industry_mean':
            result_df['industry_code'] = basic_file['industry_code']
            result_df[factor_name] = result_df[factor_name].fillna(result_df.groupby(['dt','industry_code'])[factor_name].transform('mean'))
            result_df[factor_name] = result_df[factor_name].fillna(fillna_value[1])
            result_df = result_df[[factor_name]]
        elif fillna_value[0] == 'industry_median':
            result_df['industry_code'] = basic_file['industry_code']
            result_df[factor_name] = result_df[factor_name].fillna(result_df.groupby(['dt','industry_code'])[factor_name].transform('median'))
            result_df[factor_name] = result_df[factor_name].fillna(fillna_value[1])
            result_df = result_df[[factor_name]]
    return result_df

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

    for factor_dict in factor_class_list:
        factor = factor_dict["factor_class"]
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

def get_factor_type(factor_kls):
    type_list = []
    if factor_kls.t_1_factor_data:
        type_list.append("T-1_Factor")
    # for data_name in factor_kls.t_1_factor_data_types:
    #     type_list.append(data_name)

    for data_name in factor_kls.t_day_data:
        type_list.append(data_name)

    for data_dict in factor_kls.xdb_data:
        type_list.append(data_dict["name"])

    return type_list

def update_xlsx(strategy, factor_class_list, upload_date):
    if strategy == "jupiter" or strategy == 'europa':
        # jupiter europa 共用文件
        df = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="right_factor")
        df_left_factors = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="left_factor")
        df_emotion_factors = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="emotion_factor")
        df_t_emotion_factors = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="t_emotion_factor")
        new_factors = {
            "factor_name": [],
            "factor_type": [],
            "factor_owner": [],
            "factor_explain": [],
            "factor_date": [],
            "填充值": [],
            "是否针对注册制做调整": [],
            "T-1日类别": [],
            "逻辑类别": []
        }

        for kls in factor_class_list:
            new_factors['factor_name'].append(kls.factor_name)
            new_factors['factor_type'].append(get_factor_type(kls))
            new_factors['factor_owner'].append(kls.owner)
            new_factors['factor_explain'].append(kls.factor_explain)
            new_factors['factor_date'].append(int(upload_date))
            new_factors['填充值'].append(kls.fill_na_value)
            new_factors['是否针对注册制做调整'].append(kls.zcz_adjusted)
            new_factors['T-1日类别'].append(kls.t_1_type)
            new_factors['逻辑类别'].append(kls.logic_type)

        new_factors_df = pd.DataFrame(new_factors)
        df = pd.concat([df, new_factors_df])
        df = df[['factor_name', 'factor_type', 'factor_owner', 'factor_explain', 'factor_date', '填充值', '是否针对注册制做调整', 'T-1日类别', '逻辑类别']]

        with pd.ExcelWriter(settings.warehouse_settings_dict["europa"]["all_factors_list"], mode='w') as writer:
            df.to_excel(writer, sheet_name="right_factor", index=False)
            df_left_factors.to_excel(writer, sheet_name="left_factor", index=False)
            df_emotion_factors.to_excel(writer, sheet_name="emotion_factor", index=False)
            df_t_emotion_factors.to_excel(writer, sheet_name="t_emotion_factor", index=False)


    else:
        df = pd.read_excel(settings.warehouse_settings_dict[strategy]["all_factors_list"])
        if strategy == "metis":
            new_factors = {
                "factor_name": [],
                "factor_type": [],
                "factor_owner": [],
                "factor_explain": [],
                "factor_date": [],
                "填充值": [],
                "是否针对注册制做调整": [],
                "T-1日类别": [],
                "逻辑类别": [],
                "是否低耗时因子": []
            }
            for kls in factor_class_list:
                new_factors['factor_name'].append(kls.factor_name)
                new_factors['factor_type'].append(get_factor_type(kls))
                new_factors['factor_owner'].append(kls.owner)
                new_factors['factor_explain'].append(kls.factor_explain)
                new_factors['factor_date'].append(int(upload_date))
                new_factors['填充值'].append(kls.fill_na_value)
                new_factors['是否针对注册制做调整'].append(kls.zcz_adjusted)
                new_factors['T-1日类别'].append(kls.t_1_type)
                new_factors['逻辑类别'].append(kls.logic_type)
                new_factors['是否低耗时因子'].append(kls.low_cost)

            new_factors_df = pd.DataFrame(new_factors)
            df = pd.concat([df, new_factors_df])
            df = df[['factor_name', 'factor_type', 'factor_owner', 'factor_explain', 'factor_date', '填充值', '是否针对注册制做调整',
                     'T-1日类别', '逻辑类别', '是否低耗时因子']]
            df.to_excel(settings.warehouse_settings_dict["metis"]["all_factors_list"], index=False)


        elif strategy == "saturn" or strategy == "sell" or strategy == "mimas" or strategy == "neptune" or strategy == "neptunelong":
            new_factors = {
                "factor_name": [],
                "factor_type": [],
                "factor_owner": [],
                "因子逻辑": [],
                "提交时间": [],
                "emotion": [],
                "填充值": [],
                "是否针对注册制做调整": [],
                "T-1日类别": [],
                "逻辑类别": []
            }
            for kls in factor_class_list:
                new_factors['factor_name'].append(kls.factor_name)
                new_factors['factor_type'].append(get_factor_type(kls))
                new_factors['factor_owner'].append(kls.owner)
                new_factors['因子逻辑'].append(kls.factor_explain)
                new_factors['提交时间'].append(int(upload_date))
                new_factors["emotion"].append("")
                new_factors['填充值'].append(kls.fill_na_value)
                new_factors['是否针对注册制做调整'].append(kls.zcz_adjusted)
                new_factors['T-1日类别'].append(kls.t_1_type)
                new_factors['逻辑类别'].append(kls.logic_type)

            new_factors_df = pd.DataFrame(new_factors)
            df = pd.concat([df, new_factors_df])
            df = df[['factor_name', 'factor_type', 'factor_owner', '因子逻辑', '提交时间', 'emotion','填充值', '是否针对注册制做调整',
                     'T-1日类别', '逻辑类别']]
            df.to_excel(settings.warehouse_settings_dict[strategy]["all_factors_list"], index=False)

    return

def check_daily_data(strategy, factor_type):
    if strategy not in settings.valid_strategy_names:
        raise RuntimeError("check_daily_data - 输入策略名不在预设的策略范围之内！")
    daily_list = settings.warehouse_daily_data_checker[strategy]
    if "[" in factor_type and "]" in factor_type:
        factor_type_list = eval(factor_type)
        for i in factor_type_list:
            if i in daily_list:
                return True

        return False
    else:
        return factor_type in daily_list