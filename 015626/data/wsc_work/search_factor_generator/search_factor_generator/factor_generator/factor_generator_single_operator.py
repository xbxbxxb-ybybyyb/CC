import os
from multifactor.IO import IO
import pandas as pd
import numpy as np
from utils_wsc.help_functions import rolling_norm
from operators.operators_single import Operator
import datetime as dt
from factor_test.SIF_Factor_Test5 import check_factor_into_lib
from factor_test.SIF_Factor_Test7 import SIF_Factor_Test


# 读取数据
def read_data(start_date, end_date, variety='IC.CFE', return_type='dict'):
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


start_date = 20161101
end_date = 20200801

future_data = IO.read_data([start_date, end_date],
                           alt='/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN'
                               '/MD_CHINA_FUTURES_MINUTE_MAIN.h5')

data_t = future_data.xs('T.CFE', level=1)  # 10年期国债期货
data_t = data_t.drop(['WIND_CODE', 'trading_day', 'EXCHANGE'], axis=1)
data_t.columns = [col + '_t' for col in data_t.columns]

data_tf = future_data.xs('TF.CFE', level=1)  # 5年期国债期货
data_tf = data_tf.drop(['WIND_CODE', 'trading_day', 'EXCHANGE'], axis=1)
data_tf.columns = [col + '_tf' for col in data_tf.columns]

# data_ts = future_data.xs('TS.CFE', level=1)  # 2年期国债期货
# data_ts = data_ts.drop(['WIND_CODE', 'trading_day', 'EXCHANGE'], axis=1)
# data_ts.columns = [col + '_ts' for col in data_ts.columns]

data_treasure = data_t.join(data_tf, how='outer')  # .join(data_ts, how='outer')
# for col in ['open_t', 'high_t', 'low_t', 'close_t', 'open_tf', 'high_tf', 'low_tf', 'close_tf', 'open_ts', 'high_ts',
#             'low_ts', 'close_ts']:
#     data_treasure[col] = data_treasure.fillna(method='ffill')


def factor_generator(data_raw, rolling_window, operator_params, operator_name):
    data_rolling = rolling_norm(data_raw, rolling_window)
    run = Operator(params=operator_params)
    df_factor = getattr(run, operator_name)(data_rolling)

    return df_factor


def main(rolling_norm_init=0):
    # data_raw = read_data(20200301, 20200401, 'IC.CFE', 'dataframe')
    data_raw = data_treasure
    # data_raw = data_raw.drop(['WIND_CODE'], axis=1)
    # return_points = data_raw['vwap'].shift(-2) - data_raw['vwap'].shift(-1)  # 该分钟股指期货收益点数， 后面计算因子表现要用到
    # return_points.name = 'return_points'
    data_rolling = rolling_norm(data_raw, window=rolling_norm_init)

    operator_params = {'d': 60, 'min_periods': 30, 'alpha': 0.1, 'a': [0.1, 0.9]}
    # operator_params_str = str(operator_params).replace(": ", '')
    run = Operator(params=operator_params)

    # print(data_rolling['RetVol'][data_rolling['PriceKurt'] > 0].count())
    df_factor_1 = getattr(run, 'delay')(data_rolling)
    df_factor_1.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_factor = getattr(run, 'ts_sum')(df_factor_1)
    df_factor.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_factor = rolling_norm(df_factor, 1200)
    # df_need1 = pd.concat([df_factor, return_points], axis=1, join='inner')
    # if_true = check_factor_into_lib(df_need1)
    # print(if_true)
    df_need = df_factor.to_frame()
    # print(df_need.count())
    f_test = SIF_Factor_Test(df_need, 'PriceKurt', save_image=False, layers=4)
    f_test.draw_result()
    # for i_feature in df_factor.columns:
    #     print(i_feature)
    #     df_factor_temp = df_factor[i_feature]
    #     df_need = pd.concat([df_factor_temp, return_points], axis=1, join='inner')
    #     if_true = check_factor_into_lib(df_need)
    #     if if_true is True:
    #         print(df_factor_temp.head())


if __name__ == '__main__':
    main(rolling_norm_init=0)
