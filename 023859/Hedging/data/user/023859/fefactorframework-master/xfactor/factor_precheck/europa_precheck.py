# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import datetime as dt
import importlib
import copy
from loguru import logger
import xfactor.factor_precheck.utils as precheck_utils
import settings
import sys


def value_same_check(kls, result_path, filter_df):
    logger.info('因子一致检查: factor_name={}, strategy={}'.format(kls.factor_name, "europa"))
    if not os.path.exists(result_path):
        os.system("mkdir -p " + result_path)

    factor_name = kls.factor_name
    long_interval = settings.precheck_path_dict["europa"]["long_interval"]
    short_interval_list = settings.precheck_path_dict["europa"]["short_interval_list"]

    db = {}
    factor_instance = precheck_utils.FactorUtil.create_factor_instance(kls)
    fill_na_value = factor_instance.fill_na_value

    try:
        if os.path.exists('{}{}_{}_{}.pkl'.format(result_path, factor_name, long_interval[0], long_interval[1])):
            long_df = pd.read_pickle(
                '{}{}_{}_{}.pkl'.format(result_path, factor_name, long_interval[0], long_interval[1]))
        else:
            if not db:
                db = precheck_utils.prepare_database_for_value_same_check(kls, 'europa', long_interval[0],
                                                                          long_interval[1])
            db_cpy = copy.deepcopy(db)
            if factor_instance.need_pre_calculate_T_N:
                db_cpy = factor_instance.pre_calculate_T_N_data(db_cpy)

            long_df = factor_instance.calculate(db_cpy)
            long_df = long_df.fillna(fill_na_value)
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            long_df.to_pickle('{}{}_{}_{}.pkl'.format(result_path, factor_name, long_interval[0], long_interval[1]))
        if int(np.isinf(long_df).sum()) > 0:
            return '因子值存在inf'
    except Exception as e:
        logger.error('函数测试出错: factor={}, strategy={}, 测试区间:{}-{}-{}'.format(factor_name, "europa", long_interval[0],
                                                                            long_interval[1], e))
        return '函数测试出错: factor={}, strategy={}, 测试区间:{}-{}-{}'.format(factor_name, "europa", long_interval[0],
                                                                      long_interval[1], e)

    # TODO 完善计算短期日期的方式
    try:
        for short_date in short_interval_list:
            if os.path.exists('{}{}_{}_{}.pkl'.format(result_path, factor_name, short_date, short_date)):
                short_df = pd.read_pickle('{}{}_{}_{}.pkl'.format(result_path, factor_name, short_date, short_date))
            else:
                if not db:
                    db = precheck_utils.prepare_database_for_value_same_check(kls, 'europa', str(long_interval[0]),
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
                short_df.to_pickle('{}{}_{}_{}.pkl'.format(result_path, factor_name, short_date, short_date))
            short_df = short_df.loc[pd.Timestamp(str(short_date))]
            tmp_long_df = long_df.loc[pd.Timestamp(str(short_date))]
            basic_index = filter_df.loc[pd.Timestamp(str(short_date))].index
            if np.nanmax((short_df - tmp_long_df).abs().values) > 1e-8:
                logger.error(
                    '因子值不一致1: factor={}, strategy={}, 计算区间:{}-{}和{}-{}'.format(factor_name, "europa", long_interval[0],
                                                                               long_interval[1], short_date,
                                                                               short_date))
                logger.error('symbol={}, max_abs={}'.format((short_df - tmp_long_df).abs().idxmax().values[0],
                                                            np.nanmax((short_df - tmp_long_df).abs().values)))

                return '因子值不一致1: factor={}, strategy={}, 计算区间:{}-{}和{}-{}'.format(
                    factor_name, "europa", long_interval[0], long_interval[1], short_date, short_date)
            if np.nanmax((short_df.reindex(basic_index).fillna(fill_na_value) - tmp_long_df.reindex(basic_index).fillna(
                    fill_na_value)).abs().values) > 1e-8:
                return '因子值不一致2: factor={}, strategy={}, 计算区间:{}-{}和{}-{}'.format(
                    factor_name, "europa", long_interval[0], long_interval[1], short_date, short_date)
    except Exception as e:
        logger.error(
            '函数测试出错: factor={}, strategy={}, 测试区间:{}-{}-{}'.format(factor_name, "europa", short_date, short_date, e))
        return '函数测试出错: factor={}, strategy={}, 测试区间:{}-{}-{}'.format(factor_name, "europa", short_date, short_date, e)
    return 'pass'


def factor_value_test(factor_df, factor_name):
    res = []
    if int(np.isinf(factor_df).sum()) > 0:
        logger.error('因子值存在inf: factor_name={}, strategy={}'.format(factor_name, "europa"))
        res.append('因子值存在inf')
    if factor_df[factor_df.columns[0]].std() == 0:
        logger.error('因子值全部值为常数: factor_name={}, strategy={}'.format(factor_name, "europa"))
        res.append('因子值全部值为常数')
    if factor_df.columns[0] != factor_name:
        logger.error('列名与因子名不符: factor_name={}, strategy={}'.format(factor_name, "europa"))
        res.append('列名与因子名不符')

    if res:
        return ",".join(res)

    return 'pass'


def score_check(factor_name, factor_value_df, filter_df):
    try:
        same_rate = (factor_value_df.reindex(filter_df.index)[factor_name].value_counts().max() / len(
            factor_value_df.reindex(filter_df.index)))
        if same_rate > 0.8:
            return '相同值比例较高: factor_name={}, strategy={},'.format(factor_name, "europa") + ' -%.2f%%' % (
                    same_rate * 100)
        if ('yzhan' in factor_name) and (same_rate > 0.2):
            return '相同值比例较高: factor_name={}, strategy={},'.format(factor_name, "europa") + ' %.2f%%' % (same_rate * 100)

        factor_mean = abs(factor_value_df.reindex(filter_df.index)[factor_name].mean())
        factor_std = factor_value_df.reindex(filter_df.index)[factor_name].std()
        factor_lsd = factor_std / factor_mean
        if (factor_mean < 0.001) and (factor_std < 0.001):
            return '因子波动小: factor_name={}, strategy={}, std:%.8f,mean:%.8f'.format(
                factor_name, "europa", factor_mean, factor_std)

        if factor_lsd < 0.01:
            logger.warning('离散度太低: factor_name={}, strategy={}, 暂未为筛选指标！！！！！！！！！！！'.format(factor_name, "europa"))

        return 'pass'
    except Exception as e:
        logger.error(e)
        return e.__str__()


def europa_precheck_aftercalc(kls, error_factors, start_date, end_date, factor_value, factor_type, result_path):
    logger.info("Start europa factor precheck (after calc):  factor_name={}, factor_owner={}"
                .format(kls.factor_name, kls.owner))
    check_dic = {'代码格式检查': 'pass', '因子值一致性检查': '', '函数运行检查': '', '因子测试': '', '预检测': 'not pass'}
    pkl_path = result_path + '/precheck/europa/result/'
    if not os.path.exists(pkl_path):
        os.system("mkdir -p " + pkl_path)

    if kls.factor_name in error_factors:
        check_dic["函数运行检查"] = "函数运行错误，详见日志"
        pre_check_res = pd.Series(check_dic)
        pre_check_res.to_pickle(pkl_path + '{}.pkl'.format(kls.factor_name))
        return
    filter_df = pd.read_pickle(settings.precheck_path_dict["europa"]["precheck_basic_path"])
    filter_df_cpy = filter_df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))].copy()

    if factor_type == precheck_utils.FactorUtil.FactorType.T_1_FACTOR:
        if str(start_date) == settings.precheck_path_dict["europa"]["long_interval"][0] and str(end_date) == \
                settings.precheck_path_dict["europa"]["long_interval"][1]:
            check_dic['因子值一致性检查'] = value_same_check(kls, result_path + '/precheck/europa/same_test/', filter_df)
        else:
            logger.warning("起止区间与settings中设置不一致，跳过长短区间检测！ factor={}, strategy=europa".format(kls.factor_name))
            check_dic['因子值一致性检查'] = 'pass'
    else:
        check_dic['因子值一致性检查'] = 'pass'
    if check_dic['因子值一致性检查'] != 'pass':
        logger.error("因子值一致性检查未通过！ factor_name={}, strategy={}".format(kls.factor_name, "europa"))

    check_dic['函数运行检查'] = factor_value_test(factor_value, kls.factor_name)
    if check_dic['函数运行检查'] != 'pass':
        logger.error("函数运行检查未通过！ factor_name={}, strategy={}".format(kls.factor_name, "europa"))

    check_dic['因子测试'] = score_check(kls.factor_name, factor_value, filter_df_cpy)

    if check_dic['因子测试'] != 'pass':
        logger.error("因子测试未通过！ factor_name={}, strategy={}".format(kls.factor_name, "europa"))

    if check_dic["函数运行检查"] == 'pass' and check_dic["代码格式检查"] == 'pass' and check_dic["因子值一致性检查"] == "pass" and \
            check_dic["因子测试"] == "pass":
        check_dic["预检测"] = 'pass'
    else:
        logger.error("预检测未通过！ factor_name={}, strategy={}".format(kls.factor_name, "europa"))

    pre_check_res = pd.Series(check_dic)
    pre_check_res.to_pickle(pkl_path + '{}.pkl'.format(kls.factor_name))
    logger.info("预检测完成！ factor_name={}, strategy={}".format(kls.factor_name, "europa"))
    return
