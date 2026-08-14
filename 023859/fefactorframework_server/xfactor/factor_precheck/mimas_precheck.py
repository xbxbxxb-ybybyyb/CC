# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import datetime as dt
import importlib
from loguru import logger
import xfactor.factor_precheck.utils as precheck_utils
import settings

def value_same_check(kls, result_path, filter_df, preload_database):
    logger.info('因子一致检查: factor_name={}, strategy={}'.format(kls.factor_name, "mimas"))
    long_interval = settings.precheck_path_dict["mimas"]["long_interval"]
    short_interval_list = settings.precheck_path_dict["mimas"]["short_interval_list"]

    full_factor_value_path = os.path.join(settings.path_dict["mimas"]["factor_precheck_path"] + "/same_test/",
                                          kls.factor_name + "_{}_{}.pkl".format(long_interval[0], long_interval[1]))

    db = preload_database
    factor_instance = precheck_utils.FactorUtil.create_factor_instance(kls)
    fill_na_value = factor_instance.fill_na_value

    try:
        if os.path.exists(full_factor_value_path):
            long_result = pd.read_pickle(full_factor_value_path)
        else:
            long_db = {"skip": False}
            for data_dict in kls.t_1_factor_data:
                break_flag = True
                counter = 0
                start_date_new = ""
                while break_flag:
                    if counter > 5:
                        raise RuntimeError("tradingday接口调用失败超过5次！")

                    try:
                        start_date_new = \
                            precheck_utils.FactorUtil.factor_data.tradingday(long_interval[0], -int(data_dict["lag"]))[
                                0]
                        break_flag = False
                    except Exception as e:
                        logger.warning("tradingday接口调用失败！重试...")
                        counter += 1
                long_db[data_dict["name"]] = db[data_dict["name"]].loc[
                                             pd.Timestamp(str(start_date_new)):pd.Timestamp(
                                                 str(long_interval[1]))].copy()

            if factor_instance.need_pre_calculate_T_N:
                long_db = factor_instance.pre_calculate_T_N_data(long_db)
            long_df = factor_instance.calculate(long_db)
            long_result = pd.DataFrame()
            vals = long_df[long_df.columns[0]].unstack().shift(1).stack()
            long_result[long_df.columns[0]] = vals
            long_result.fillna(fill_na_value, inplace=True)
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            long_result.to_pickle(full_factor_value_path)
    except Exception as e:
        return '函数运行出错: factor_name={}, strategy={}, 测试区间:{}-{}-{}'.format(
            kls.factor_name, "mimas", long_interval[0], long_interval[1], e)

    try:
        diff_short_date = []
        for short_date in short_interval_list:
            if os.path.exists(result_path + "/{}_{}_{}.pkl".format(kls.factor_name, short_date, short_date)):
                short_result = pd.read_pickle(
                    result_path + "/{}_{}_{}.pkl".format(kls.factor_name, short_date, short_date))
            else:
                if not db:
                    logger.error("mimas precheck - preload database empty!")
                short_db = {"skip": False}
                for data_dict in kls.t_1_factor_data:
                    break_flag = True
                    counter = 0
                    start_date_new = ""
                    while break_flag:
                        if counter > 5:
                            raise RuntimeError("tradingday接口调用失败超过5次！")

                        try:
                            start_date_new = \
                            precheck_utils.FactorUtil.factor_data.tradingday(short_date, -int(data_dict["lag"]))[0]
                            break_flag = False
                        except Exception as e:
                            logger.warning("tradingday接口调用失败！重试...")
                            counter += 1

                    short_db[data_dict["name"]] = db[data_dict["name"]].loc[
                                                  pd.Timestamp(str(start_date_new)):pd.Timestamp(str(short_date))].copy()

                if factor_instance.need_pre_calculate_T_N:
                    short_db = factor_instance.pre_calculate_T_N_data(short_db)
                short_df = factor_instance.calculate(short_db)
                short_result = pd.DataFrame()
                vals = short_df[short_df.columns[0]].unstack().shift(1).stack()
                short_result[short_df.columns[0]] = vals
                short_result.fillna(fill_na_value, inplace=True)
                short_result.to_pickle(result_path + "/{}_{}_{}.pkl".format(kls.factor_name, short_date, short_date))

            long_ser = long_result.loc[pd.Timestamp(str(short_date))][kls.factor_name]
            short_ser = short_result.loc[pd.Timestamp(str(short_date))][kls.factor_name]
            if (long_ser.shape != short_ser.shape) or ((long_ser - short_ser).abs().max() > 1e-6):
                logger.info(
                    '因子检查不一致: factor_name={}, date={}, strategy=mimas, long_shape={}, short_shape={}, diff={}, diff_stock={}'.format(
                        kls.factor_name, short_date, long_ser.shape, short_ser.shape, (long_ser - short_ser).abs().max(),
                        (long_ser - short_ser).abs().idxmax()))
                diff_short_date.append(short_date)
        if len(diff_short_date) > 0:
            return '区间测试未通过: factor_name={}, strategy={}, 不一致日期:{}'.format(kls.factor_name, "mimas", str(diff_short_date))
    except Exception as e:
        return '函数运行出错: factor_name={}, strategy={}, 测试区间:{}-{}-{}'.format(kls.factor_name, "mimas", short_date, short_date, e)
    return "pass"

def factor_value_test(factor_df, factor_name):
    res = []
    if int(np.isinf(factor_df).sum()) > 0:
        logger.error('因子值存在inf: factor_name={}, strategy={}'.format(factor_name, "mimas"))
        res.append('因子值存在inf')
    if factor_df[factor_df.columns[0]].std() == 0:
        logger.error('因子值全部值为常数: factor_name={}, strategy={}'.format(factor_name, "mimas"))
        res.append('因子值全部值为常数')
    if factor_df.columns[0] != factor_name:
        logger.error('列名与因子名不符: factor_name={}, strategy={}'.format(factor_name, "mimas"))
        res.append('列名与因子名不符')

    if res:
        return ",".join(res)

    return 'pass'


def score_check(factor_name, factor_value_df, filter_df):
    try:
        if (factor_value_df[factor_name].isnull().sum() + np.isinf(factor_value_df[factor_name]).sum()) > 0:
            return '因子值存在nan|inf'

        if (factor_value_df.reindex(filter_df.index)[factor_name].isnull().sum() + np.isinf(
                factor_value_df.reindex(filter_df.index)[factor_name]).sum()) > 0:
            return '因子值存在nan|inf'

        if factor_value_df.reindex(filter_df.index)[factor_name].value_counts(normalize=True).max() > 0.2:
            return '相同值比例较高%.2f' % factor_value_df.reindex(filter_df.index)[factor_name].value_counts(normalize=True).max()

        factor_mean = abs(factor_value_df.reindex(filter_df.index)[factor_name].mean())
        factor_std = factor_value_df.reindex(filter_df.index)[factor_name].std()
        factor_lsd = factor_std / factor_mean
        if factor_std < 1e-15:
            return '因子值波动小'
        if (factor_mean < 0.001) and (factor_std < 0.001):
            return '因子波动小-std:%.8f,mean:%.8f' % (factor_mean, factor_std)

        if factor_lsd < 0.01:
            logger.info('离散度太低-暂未为筛选指标！！！！！！！！！！！')

        if factor_value_df[factor_name].std() < 1e-15:
            return '因子值波动小: factor_name={}, strategy={}'.format(factor_name, "mimas")

        if factor_value_df[factor_name].value_counts(normalize=True).max() > 0.2:
            return '相同值比例较高: factor_name={}, strategy={}'.format(factor_name, "mimas") + ', %.2f' % (factor_value_df[factor_name].value_counts(normalize=True).max())

        return 'pass'
    except Exception as e:
        logger.error(e)
        return e.__str__()

def mimas_precheck_aftercalc(kls, pre_calc_check_res, error_factors, start_date, end_date, factor_type, result_path, preload_database):
    logger.info("Start mimas factor precheck (after calc):  factor_name={}, factor_owner={}"
                .format(kls.factor_name, kls.owner))
    check_dic = {'代码格式检查': '', '因子值一致性检查': '', '函数运行检查': '', '因子测试': '', '预检测': 'not pass'}

    if kls.factor_name not in pre_calc_check_res:
        check_dic["代码格式检查"] = "缺少代码格式检查结果"
        logger.warning("缺少代码格式检查结果! factor_name={}, strategy={}".format(kls.factor_name, 'mimas'))
    else:
        check_dic["代码格式检查"] = pre_calc_check_res[kls.factor_name]

    if kls.factor_name in error_factors:
        check_dic["函数运行检查"] = "函数运行错误，详见日志"
        pre_check_res = pd.Series(check_dic)
        pre_check_res.to_pickle(settings.path_dict["mimas"]["factor_precheck_path"] + '{}.pkl'.format(kls.factor_name))
        return

    factor_value_path = os.path.join(settings.path_dict["mimas"]["factor_value_path"], kls.factor_name, kls.factor_name + ".h5")
    if os.path.exists(factor_value_path):
        factor_value = pd.read_hdf(factor_value_path)
    else:
        logger.error("未找到相关因子值文件！ factor_name={}, strategy=mimas, value_path={}".format(kls.factor_name, factor_value_path))
        check_dic["函数运行检查"] = "未找到相关因子值文件"
        pre_check_res = pd.Series(check_dic)
        pre_check_res.to_pickle(settings.path_dict["mimas"]["factor_precheck_path"] + '{}.pkl'.format(kls.factor_name))
        return

    filter_df = pd.read_hdf(settings.precheck_path_dict["mimas"]["precheck_basic_path"])
    filter_df_cpy = filter_df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))].copy()

    if factor_type == precheck_utils.FactorUtil.FactorType.T_1_FACTOR:
        check_dic['因子值一致性检查'] = value_same_check(kls, result_path + '/same_test/', filter_df,preload_database)
    else:
        check_dic['因子值一致性检查'] = 'pass'
    if check_dic['因子值一致性检查'] != 'pass':
        logger.error("因子值一致性检查未通过！ factor_name={} ".format(kls.factor_name))

    check_dic['函数运行检查'] = factor_value_test(factor_value, kls.factor_name)
    if check_dic['函数运行检查'] != 'pass':
        logger.error("函数运行检查未通过！ factor_name={}, strategy={}".format(kls.factor_name, "mimas"))

    check_dic['因子测试'] = score_check(kls.factor_name, factor_value, filter_df_cpy)

    if check_dic['因子测试'] != 'pass':
        logger.error("因子测试未通过！ factor_name={}, strategy={}".format(kls.factor_name, "mimas"))

    if check_dic["函数运行检查"] == 'pass' and check_dic["代码格式检查"] == 'pass' and check_dic["因子值一致性检查"] == "pass" and check_dic["因子测试"] == "pass":
        check_dic["预检测"] = 'pass'
    else:
        logger.error("预检测未通过！ factor_name={}, strategy={}".format(kls.factor_name, "mimas"))

    pre_check_res = pd.Series(check_dic)
    pre_check_res.to_pickle(settings.path_dict["mimas"]["factor_precheck_path"] + '{}.pkl'.format(kls.factor_name))
    logger.info("预检测完成！ factor_name={}, strategy={}".format(kls.factor_name, "mimas"))
    return
