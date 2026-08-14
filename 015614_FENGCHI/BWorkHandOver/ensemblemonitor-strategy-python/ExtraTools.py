# @Time : 2021/5/2 9:58
# @Author : Zhichen Lu
# @File : ExtraTools.py

import os
# from online_conf import non_fix_in_path,non_fix_output_path
# from dataApi.getData import get_pre_trade_date
import pandas as pd

def get_path_conf(local_config_path, create=False):
    path_conf = dict(
        # 当日收盘持仓信息(持仓量、第一次买入信息、可交易量)
        local_config_path=local_config_path,
        # local_config_path = '/data/group/800319/strategy_local_path_sim/strategy_local_path3_sim20210507/'
        # 当日收盘持仓信息(持仓量、第一次买入信息、可交易量)
        holding_info_path=local_config_path + 'holding_info/',
        # 当日收盘持仓股的买入时间
        buy_time_info_path=local_config_path + 'buy_time_info/',
        # 超参数(均值、标准差)，日期为T-1日，参数用于T日
        hyper_param_path=local_config_path + 'factor_hyper_param/',
        # T-1日计算出用于T日的股票池，名字为T-1日
        code_list_path=local_config_path + 'code_list/',
        # 模型配置文件，文件名为模型更新的日期
        model_config_path=local_config_path + 'model_conf/',
        model_path=local_config_path + 'model/',
        # 模型文件保存路径
        # 每天策略初始化参数路径
        init_conf_path=local_config_path + 'daily_init_config/',
        # 每天输出路径
        daily_out_path=local_config_path + 'daily_output/',
        # 每天输出路径
        daily_out_path_offline=local_config_path + 'daily_output_offline/',
        # 算法交易比例路径,文件名为文件计算日期
        alog_trading_distr_path=local_config_path + 'algo_trading_distr/',
        #
        vol_info_path=local_config_path + 'vol_info/',
        restrict_list_path=local_config_path + 'restrict_list/',
        # 前一日
        # 模型对应的因子列表

        path_for_930=local_config_path + 'FolderFor930/',
        sub_output_path=local_config_path + 'daily_output/out_930/',
        ratio_path=f'{local_config_path}ratio/',
        signal_930_path=f'{local_config_path}/morning_model/val_sign/',
        matrix_conf=local_config_path + 'relation_matrix/',
        condition_path=local_config_path + 'condition/',

    )
    if create:
        for each in path_conf:
            if not os.path.exists(path_conf[each]):
                os.makedirs(path_conf[each])
    return path_conf


def get_nonfix_in_val(factor, date, non_fix_path):
    from dataApi.tradeDate import get_pre_trade_date
    non_fix_in_path = f'{non_fix_path}/daily_input/'
    if factor == 'ini':
        return pd.read_pickle(f'{non_fix_in_path}{date}/{factor}{date}.pkl')
    else:
        return pd.read_pickle(f'{non_fix_in_path}{date}/{factor}{get_pre_trade_date(date)}.pkl')


def save_nonfix_in_val(val, factor, create_day, non_fix_path):
    from dataApi.tradeDate import get_pre_trade_date
    non_fix_in_path = f'{non_fix_path}/daily_input/'
    excute_day = get_pre_trade_date(create_day, -1)
    if not os.path.exists(f'{non_fix_in_path}{excute_day}'):
        os.makedirs(f'{non_fix_in_path}{excute_day}')
    if factor == 'ini':
        pd.to_pickle(val, f'{non_fix_in_path}{excute_day}/{factor}{excute_day}.pkl')
    else:
        pd.to_pickle(val, f'{non_fix_in_path}{excute_day}/{factor}{create_day}.pkl')


def generate_dir(path_conf):
    if 'local_config_path' in path_conf and not os.path.exists(path_conf['local_config_path']):
        os.mkdir(path_conf['local_config_path'])
    for each in path_conf:
        if not os.path.exists(path_conf[each]):
            os.mkdir(path_conf[each])
