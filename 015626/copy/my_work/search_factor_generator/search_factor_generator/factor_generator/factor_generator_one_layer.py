import os
from multifactor.IO import IO
import pandas as pd
from utils_wsc.help_functions import rolling_norm
from operators.operators_single import Operator
import datetime as dt
from factor_test.SIF_Factor_Test5 import check_factor_into_lib
import numpy as np


# 读取数据
def read_data(start_date, end_date, variety='IF.CFE', return_type='dict'):
    """
    :param start_date: 数据读取的开始日期
    :param end_date: 数据读取的结束日期
    :param variety: 读取的期货品种(IF, IC, IH)
    :return: 字典data_dict, key是各个数据字段, value是对应的时间序列
    """
    data_dict = {}
    data_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    index_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path, 'MD_STOCK_INDEX_SPOT_MINUTE.h5')).xs(
        variety, level=1).sort_index()
    futures_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path,
                                                                         'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')).xs(
        variety, level=1).sort_index()
    tick2minute_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path,
                                                                             'MD_STOCK_INDEX_FUTURES_TICK_TO_MINUTE.h5')).xs(
        variety, level=1).sort_index()
    cfg_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path, 'MD_STOCK_INDEX_CFG_MINUTE.h5')).xs(
        'IC.CFE', level=1).sort_index()
    # cfg_stocks_data = IO.read_data([start_date, end_date],
    #                                alt=os.path.join(data_path, 'IC_STOCKS_MINUTE_DATA.h5')).unstack().sort_index()

    data = pd.concat([index_data, futures_data, tick2minute_data, cfg_data], axis=1).sort_index()
    # cfg = cfg_stocks_data.reindex(data.index)

    plist = ['open', 'high', 'low', 'close', 'open_spot', 'high_spot', 'low_spot', 'close_spot']
    # 'open_zz500', 'high_zz500', 'low_zz500', 'close_zz500']

    # 填充缺失值
    for col in data.columns.get_level_values(0).unique():
        if col in plist:
            data[col] = data[col].fillna(method='pad')
        data_dict[col] = data[col]

    if return_type == 'dict':
        return data_dict
    elif return_type == 'dataframe':
        return data


def factor_generator(data_raw, rolling_window, operator_params, operator_name):
    data_rolling = rolling_norm(data_raw, rolling_window)
    run = Operator(params=operator_params)
    df_factor = getattr(run, operator_name)(data_rolling)

    return df_factor


def main(rolling_norm_init=0):
    data_raw = read_data(20161201, 20200102, 'IC.CFE', 'dataframe')
    data_raw = data_raw.drop(['WIND_CODE'], axis=1)
    return_points = data_raw['vwap'].shift(-2) - data_raw['vwap'].shift(-1)  # 该分钟股指期货收益点数， 后面计算因子表现要用到
    return_points.name = 'return_points'
    data_rolling = rolling_norm(data_raw, window=rolling_norm_init)
    func_name = [i for i in dir(Operator) if i[0] != '_']  # operators_single中所有算子

    operator_params = {'d': 60, 'min_periods': 30, 'alpha': 0.1, 'a': [0.1, 0.9]}
    operator_params_str = str(operator_params).replace(": ", '')
    run = Operator(params=operator_params)

    t0 = dt.datetime.now()
    for i_operator in func_name:
        t1 = dt.datetime.now()
        print(i_operator + ' start calculating')
        df_factor = getattr(run, i_operator)(data_rolling)
        df_factor = rolling_norm(df_factor, 1200)
        df_factor.replace([np.inf, -np.inf], np.nan, inplace=True)
        for i_feature in df_factor.columns:
            print(i_feature)
            df_factor_temp = df_factor[i_feature]
            df_need = pd.concat([df_factor_temp, return_points], axis=1, join='inner')
            if_true = check_factor_into_lib(df_need)
            if if_true is True:
                print('!!!!!!!!!')
                df_factor_temp.to_csv(
                    '/data/user/017024/search_factor_generator/' + i_operator + '_' + i_feature + '_' +
                    operator_params_str + '.csv')
        t2 = dt.datetime.now()
        print(i_operator + ' costs: ', t2 - t1)
    t3 = dt.datetime.now()
    print('all operators costs: ', t3 - t0)


if __name__ == '__main__':
    main(rolling_norm_init=0)
