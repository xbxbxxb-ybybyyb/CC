import os
import pandas as pd
import numpy as np
import datetime as dt
import importlib
from loguru import logger
from settings import RunMode
import xfactor.factor_precheck.utils as precheck_utils
import copy
import settings


def value_same_check(kls, result_path, filter_df):
    factor_name = kls.factor_name
    logger.info('因子一致检查, factor_name={}, strategy={}'.format(factor_name, "sell"))
    if not os.path.exists(result_path):
        os.system("mkdir -p " + result_path)

    long_interval = settings.precheck_path_dict["sell"]["long_interval"]
    short_interval_list = settings.precheck_path_dict["sell"]["short_interval_list"]

    db = {}
    factor_instance = precheck_utils.FactorUtil.create_factor_instance(kls)
    fill_na_value = factor_instance.fill_na_value

    s_xx = precheck_utils.check_factor_sub_type(kls)

    try:
        if os.path.exists(
                result_path + "/{}_{}_{}_{}.pkl".format(s_xx, factor_name, long_interval[0], long_interval[1])):
            long_df = pd.read_pickle(
                result_path + "/{}_{}_{}_{}.pkl".format(s_xx, factor_name, long_interval[0], long_interval[1]))
        else:
            if not db:
                db = precheck_utils.prepare_database_for_value_same_check(kls, "sell", str(long_interval[0]),
                                                                          str(long_interval[1]))
            db_cpy = copy.deepcopy(db)
            if factor_instance.need_pre_calculate_T_N:
                db_cpy = factor_instance.pre_calculate_T_N_data(db_cpy)

            long_df = factor_instance.calculate(db_cpy)
            long_df = long_df.fillna(fill_na_value)

            if not os.path.exists(result_path):
                os.makedirs(result_path)
            long_df.to_pickle(
                result_path + "/{}_{}_{}_{}.pkl".format(s_xx, factor_name, long_interval[0], long_interval[1]))
    except Exception as e:
        return '函数运行出错: factor_name={}, strategy={}, 测试区间:{}-{}-{}'.format(
            factor_name, "sell", long_interval[0], long_interval[1], e)
    # long_df = long_df.reindex(filter_df.index)

    try:
        diff_short_date = []
        for short_date in short_interval_list:
            if os.path.exists(result_path + "/{}_{}_{}_{}.pkl".format(s_xx, factor_name, short_date, short_date)):
                short_df = pd.read_pickle(
                    result_path + "/{}_{}_{}_{}.pkl".format(s_xx, factor_name, short_date, short_date))
            else:
                if not db:
                    db = precheck_utils.prepare_database_for_value_same_check(kls, "sell", str(long_interval[0]),
                                                                              str(long_interval[1]))
                short_db = {"skip": False}
                for data_dict in kls.t_1_factor_data:
                    break_flag = True
                    counter = 0
                    start_date = ""
                    while break_flag:
                        if counter > 5:
                            raise RuntimeError("tradingday接口调用失败超过5次！")

                        try:
                            start_date = \
                                precheck_utils.FactorUtil.factor_data.tradingday(short_date, -int(data_dict["lag"]))[0]
                            break_flag = False
                        except Exception as e:
                            logger.warning("tradingday接口调用失败！重试...")
                            counter += 1
                    short_db[data_dict["name"]] = db[data_dict["name"]].loc[
                                                  pd.Timestamp(str(start_date)):pd.Timestamp(str(short_date))].copy()

                if factor_instance.need_pre_calculate_T_N:
                    short_db = factor_instance.pre_calculate_T_N_data(short_db)
                short_df = factor_instance.calculate(short_db).fillna(fill_na_value)
                short_df.to_pickle(result_path + "/{}_{}_{}_{}.pkl".format(s_xx, factor_name, short_date, short_date))

            # short_df = short_df.reindex(filter_df.index)
            long_ser = long_df.loc[pd.Timestamp(str(short_date))][factor_name]
            short_ser = short_df.loc[pd.Timestamp(str(short_date))][factor_name]
            if (long_ser.shape != short_ser.shape) or ((long_ser - short_ser).abs().max() > 1e-9):
                diff_short_date.append(short_date)
        if len(diff_short_date) > 0:
            return '区间测试未通过: factor_name={}, strategy={}, 不一致日期:{}'.format(factor_name, "sell", str(diff_short_date))

    except Exception as e:
        return '函数运行出错: factor_name={}, strategy={}, 测试区间:{}-{}-{}'.format(factor_name, "sell", short_date, short_date,
                                                                           e)
    return "pass"


def factor_value_test(factor_df, factor_name):
    res = []
    if int(np.isinf(factor_df).sum()) > 0:
        logger.error('因子值存在inf: factor_name={}, strategy={}'.format(factor_name, "sell"))
        res.append('因子值存在inf')
    if factor_df[factor_df.columns[0]].std() == 0:
        logger.error('因子值全部值为常数: factor_name={}, strategy={}'.format(factor_name, "sell"))
        res.append('因子值全部值为常数')
    if factor_df.columns[0] != factor_name:
        logger.error('列名与因子名不符: factor_name={}, strategy={}'.format(factor_name, "sell"))
        res.append('列名与因子名不符')

    if res:
        return ",".join(res)

    return 'pass'


def score_check(factor_name, factor_value_df, filter_df):
    if factor_value_df.reindex(filter_df.index)[factor_name].std() < 1e-15:
        return '因子值波动小: factor_name={}, strategy={}'.format(factor_name, "sell")

    if factor_value_df.reindex(filter_df.index)[factor_name].value_counts(normalize=True).max() > 0.2:
        return '相同值比例较高: factor_name={}, strategy={}, '.format(
            factor_name, "sell") + ' %.2f' % (
                   factor_value_df.reindex(filter_df.index)[factor_name].value_counts(normalize=True).max())

    return 'pass'


def sell_precheck_aftercalc(kls, error_factors, start_date, end_date, factor_value, factor_type, result_path):
    logger.info("Start sell factor precheck (after calc):  factor_name={}, factor_owner={}"
                .format(kls.factor_name, kls.owner))
    check_dic = {'代码格式检查': 'pass', '因子值一致性检查': '', '函数运行检查': '', '因子测试': '', '预检测': 'not pass'}
    pkl_path = result_path + '/precheck/sell/result/'
    if not os.path.exists(pkl_path):
        os.system("mkdir -p " + pkl_path)

    if kls.factor_name in error_factors:
        check_dic["函数运行检查"] = "函数运行错误，详见日志"
        pre_check_res = pd.Series(check_dic)
        pre_check_res.to_pickle(pkl_path + '{}.pkl'.format(kls.factor_name))
        return
    filter_df = pd.read_hdf(settings.precheck_path_dict["sell"]["precheck_basic_path"])
    filter_df_cpy = filter_df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))].copy()

    if factor_type == precheck_utils.FactorUtil.FactorType.T_1_FACTOR:
        if str(start_date) == settings.precheck_path_dict["sell"]["long_interval"][0] and str(end_date) == \
                settings.precheck_path_dict["sell"]["long_interval"][1]:
            check_dic['因子值一致性检查'] = value_same_check(kls, result_path + '/precheck/sell/same_test/', filter_df)

        else:
            logger.warning("起止区间与settings中设置不一致，跳过长短区间检测！ factor={}, strategy=sell".format(kls.factor_name))
            check_dic['因子值一致性检查'] = 'pass'
    else:
        check_dic['因子值一致性检查'] = 'pass'
    if check_dic['因子值一致性检查'] != 'pass':
        logger.error("因子值一致性检查未通过！ factor_name={} ".format(kls.factor_name))

    check_dic['函数运行检查'] = factor_value_test(factor_value, kls.factor_name)
    if check_dic['函数运行检查'] != 'pass':
        logger.error("函数运行检查未通过！ factor_name={}, strategy={}".format(kls.factor_name, "sell"))

    check_dic['因子测试'] = score_check(kls.factor_name, factor_value, filter_df_cpy)

    if check_dic['因子测试'] != 'pass':
        logger.error("因子测试未通过！ factor_name={}, strategy={}".format(kls.factor_name, "sell"))

    if check_dic["函数运行检查"] == 'pass' and check_dic["代码格式检查"] == 'pass' and check_dic["因子值一致性检查"] == "pass" and \
            check_dic["因子测试"] == "pass":
        check_dic["预检测"] = 'pass'
    else:
        logger.error("预检测未通过！ factor_name={}, strategy={}".format(kls.factor_name, "sell"))

    pre_check_res = pd.Series(check_dic)
    pre_check_res.to_pickle(pkl_path + '{}.pkl'.format(kls.factor_name))
    logger.info("预检测完成！ factor_name={}, strategy={}".format(kls.factor_name, "sell"))
    return
