import os
import pandas as pd
import numpy as np
import datetime as dt
import importlib
import copy
from loguru import logger

import settings
import xfactor.factor_precheck.utils as precheck_utils
from xfactor.factor_precheck import jupiter_precheck, europa_precheck, sell_precheck, saturn_precheck, mimas_precheck, metis_precheck, mercury_precheck, neptune_precheck, neptunelong_precheck
from xfactor import FactorUtil

func_map = {
    "jupiter": jupiter_precheck.jupiter_precheck_aftercalc,
    "europa": europa_precheck.europa_precheck_aftercalc,
    "saturn": saturn_precheck.saturn_precheck_aftercalc,
    "mercury": mercury_precheck.mercury_precheck_aftercalc,
    "sell": sell_precheck.sell_precheck_aftercalc,
    "mimas": mimas_precheck.mimas_precheck_aftercalc,
    "metis": metis_precheck.metis_precheck_aftercalc,
    "neptune": neptune_precheck.neptune_precheck_aftercalc,
    "neptunelong": neptunelong_precheck.neptunelong_precheck_aftercalc,
}

def pre_calc_check(factor_class_list):
    pre_calc_check_res_dict = {}
    for factor in factor_class_list:
        res = format_check(factor)
        pre_calc_check_res_dict[factor.factor_name] = res
    return pre_calc_check_res_dict


def run_precheck(strategy, error_factors, kls, start_date, end_date, res, factor_type, output_dir):

    if strategy in func_map:
        errors = []
        if strategy in error_factors:
            errors = error_factors[strategy]
        func_map[strategy](kls, errors, start_date, end_date, res, factor_type,
                                                    output_dir)
    else:
        logger.error("run precheck failed, startegy not known! input_strategy=" + strategy)
    return

def format_check(kls):
    factor_name = kls.factor_name
    logger.info('代码格式检查, factor={}'.format(factor_name))
    try:
        modname = 'factor.factor_%s' % (factor_name)
        module = importlib.import_module(modname)

    except Exception as e:
        logger.error('文件名不符合规定，factor={}'.format(factor_name))
        raise RuntimeError('文件名不符合规定-%s;' % (e))

    try:
        dic_use_data = kls.t_1_factor_data_types
        f = open(os.getcwd() + '/factor/factor_%s.py' % (factor_name))
        py_code = f.readlines()
        real_use_data = precheck_utils.get_use_data(py_code)
        if (len(set(dic_use_data) - set(real_use_data)) > 0) or (len(set(real_use_data) - set(dic_use_data)) > 0):
            logger.error('t_1_factor_data_types列举错误, factor=%s, 列举%s-实际使用%s;' % (factor_name, dic_use_data, real_use_data))
            raise RuntimeError('t_1_factor_data_types列举错误')

    except Exception as e:
        raise RuntimeError('t_1_factor_data_types列举错误')

    # 不允许同时使用_CS和任何高频数据（T日、xdb）
    try:
        all_data_list_t_xdb = [x['name'] for x in kls.xdb_data] + [x for x in kls.t_day_data]
        cs_data_list = [x for x in all_data_list_t_xdb if '_cs' in x]
        not_cs_data_list = [x for x in all_data_list_t_xdb if '_cs' not in x]
        if len(cs_data_list) > 0 and len(not_cs_data_list) > 0:
            logger.error(f'不允许同时使用_cs后缀的数据和其他高频数据，目前cs_data为{cs_data_list}，非cs的高频数据为{not_cs_data_list}')
            raise RuntimeError('不允许同时使用_cs后缀的数据和其他高频数据')
    except Exception as e:
        raise RuntimeError('不允许同时使用_cs后缀的数据和其他高频数据')

    # fillna_check
    '''
    Neptune/Neptunelong可以额外使用的fillna：2个元素的元组，第一个元素为mean,median,industry_mean,industry_median其中之一，第二个元素为数值
    '''
    fill_na_value = kls.fill_na_value
    strategy_name = kls.strategy_name
    if type(fill_na_value) != int and type(fill_na_value) != float and type(fill_na_value) != tuple:
        logger.error('fill_na_value不为定值也不为tuple！factor={}'.format(factor_name))
        raise RuntimeError('fill_na_value格式错误！')
    elif type(fill_na_value) == tuple:
        if strategy_name not in ['neptune', 'neptunelong']:
            logger.error('fill_na_value为tuple，但非neptune/neptunelong策略！factor={}'.format(factor_name))
            raise RuntimeError('fill_na_value格式错误！')
        elif len(fill_na_value) != 2:
            logger.error('fill_na_value为tuple，但长度不为2！factor={}'.format(factor_name))
            raise RuntimeError('fill_na_value格式错误！')
        elif fill_na_value[0] not in ["median","mean","industry_median","industry_mean"]:
            logger.error('fill_na_value为tuple，属性不在 "median","mean","industry_median","industry_mean"中 ！factor={}'.format(factor_name))
            raise RuntimeError('fill_na_value格式错误！')
        elif type(fill_na_value[1]) != float and type(fill_na_value[1]) != int:
            logger.error('fill_na_value为tuple，值不为float和int ！factor={}'.format(factor_name))
            raise RuntimeError('fill_na_value格式错误！')
        elif fill_na_value[1] == float("inf") or fill_na_value[1] == float("-inf"):
            logger.error('fill_na_value为inf！factor={}'.format(factor_name))
            raise RuntimeError('fill_na_value格式错误！')
    elif type(fill_na_value) != float and type(fill_na_value) != int:
        logger.error('fill_na_value为定值，值不为float和int ！factor={}'.format(factor_name))
        raise RuntimeError('fill_na_value格式错误！')
    elif fill_na_value == float("inf") or fill_na_value == float("-inf"):
        logger.error('fill_na_value为inf！factor={}'.format(factor_name))
        raise RuntimeError('fill_na_value为inf！')
    return 'pass'

