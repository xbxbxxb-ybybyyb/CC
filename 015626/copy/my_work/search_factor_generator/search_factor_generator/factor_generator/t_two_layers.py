import os
from multifactor.IO import IO
import pandas as pd
from utils_wsc.help_functions import rolling_norm
from operators.operators_single import Operator
import datetime as dt
from factor_test.SIF_Factor_Test5 import check_factor_into_lib
import numpy as np

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

index_data = IO.read_data([start_date, end_date],
                          alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
futures_data = IO.read_data([start_date, end_date],
                            alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
                                'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')

data = pd.concat([index_data, futures_data], axis=1).xs('IF.CFE', level=1).sort_index()
data.columns = [col + '_if' for col in data.columns]
icdata = futures_data.xs('IC.CFE', level=1)
ihdata = futures_data.xs('IH.CFE', level=1)
ihdata.columns = [col + '_ih' for col in ihdata.columns]

icdata_spot = index_data.xs('IC.CFE', level=1)
ihdata_spot = index_data.xs('IH.CFE', level=1)
ihdata_spot.columns = [col + '_ih' for col in ihdata_spot.columns]
data = data.join(icdata).join(ihdata).join(icdata_spot).join(ihdata_spot)

# for col in ['open', 'high', 'low', 'close', 'open_spot', 'high_spot', 'low_spot', 'close_spot',
#            'open_if', 'high_if', 'low_if', 'close_if', 'open_spot_if', 'high_spot_if', 'low_spot_if', 'close_spot_if',
#           'open_ih', 'high_ih', 'low_ih', 'close_ih', 'open_spot_ih', 'high_spot_ih', 'low_spot_ih', 'close_spot_ih']:
#     data[col] = data[col].fillna(method='pad')
data = data.drop(['WIND_CODE', 'WIND_CODE_if', 'WIND_CODE_ih'], axis=1)
data_treasure = data_treasure.reindex(data.index)  # 国债期货某些时段数据会缺失（直接没有index），用股指期货的index去补齐


def factor_generator(data_raw, rolling_window, operator_params, operator_name):
    data_rolling = rolling_norm(data_raw, rolling_window)
    run = Operator(params=operator_params)
    df_factor = getattr(run, operator_name)(data_rolling)

    return df_factor


def main(rolling_norm_init=0):
    # data_raw = read_data(20161201, 20200102, 'IC.CFE', 'dataframe')
    data_raw = data_treasure
    return_points = data['vwap'].shift(-2) - data['vwap'].shift(-1)  # 该分钟股指期货收益点数， 后面计算因子表现要用到
    return_points.name = 'return_points'
    data_rolling = rolling_norm(data_raw, window=rolling_norm_init)
    func_name = [i for i in dir(Operator) if i[0] != '_']  # operators_single中所有算子

    operator_params = {'d': 60, 'min_periods': 30, 'alpha': 0.1, 'a': [0.1, 0.9]}
    operator_params_str = str(operator_params).replace(": ", '')
    run = Operator(params=operator_params)

    t0 = dt.datetime.now()
    print('start to generator factor.')
    for i_operator in func_name:
        # t1 = dt.datetime.now()
        print(i_operator + ' start calculating')
        df_factor_1 = getattr(run, i_operator)(data_rolling)
        # df_factor = rolling_norm(df_factor, 1200)
        df_factor_1.replace([np.inf, -np.inf], np.nan, inplace=True)
        for j_operator in func_name:
            print(j_operator + ' start calculating')
            df_factor = getattr(run, j_operator)(df_factor_1)
            df_factor.replace([np.inf, -np.inf], np.nan, inplace=True)
            df_factor = rolling_norm(df_factor, 1200)
            for i_feature in df_factor.columns:
                print(i_feature)
                df_factor_temp = df_factor[i_feature]
                df_need = pd.concat([df_factor_temp, return_points], axis=1, join='inner')
                if_true = check_factor_into_lib(df_need)
                if if_true is True:
                    print('!!!!!!!!!')
                    print(i_operator + ' ' + j_operator + ' ' + i_feature)
                    df_factor_temp.to_csv(
                        '/data/user/017024/search_factor_generator/IC/two_layers/t/' + i_operator + '_' + j_operator +
                        '_' + i_feature + '_' + operator_params_str + '.csv')
            # t2 = dt.datetime.now()
            # print(i_operator + ' costs: ', t2 - t1)
        t3 = dt.datetime.now()
        print('all operators costs: ', t3 - t0)


if __name__ == '__main__':
    main(rolling_norm_init=0)
