import os
from multifactor.IO import IO
import pandas as pd
from utils.help_functions import rolling_norm
from operators.operators_single import Operator
import datetime as dt
from factor_test.SIF_Factor_Test5_IF import check_factor_into_lib
import numpy as np

start_date = 20161201
end_date = 20200801

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

for col in ['open', 'high', 'low', 'close', 'open_spot', 'high_spot', 'low_spot', 'close_spot',
            'open_if', 'high_if', 'low_if', 'close_if', 'open_spot_if', 'high_spot_if', 'low_spot_if', 'close_spot_if',
            'open_ih', 'high_ih', 'low_ih', 'close_ih', 'open_spot_ih', 'high_spot_ih', 'low_spot_ih', 'close_spot_ih']:
    data[col] = data[col].fillna(method='pad')


def factor_generator(data_raw, rolling_window, operator_params, operator_name):
    data_rolling = rolling_norm(data_raw, rolling_window)
    run = Operator(params=operator_params)
    df_factor = getattr(run, operator_name)(data_rolling)

    return df_factor


def main(rolling_norm_init=0):
    # data_raw = read_data(20161201, 20200102, 'IC.CFE', 'dataframe')
    data_raw = data.drop(['WIND_CODE', 'WIND_CODE_if', 'WIND_CODE_ih'], axis=1)
    return_points = data_raw['vwap_if'].shift(-2) - data_raw['vwap_if'].shift(-1)  # 该分钟股指期货收益点数， 后面计算因子表现要用到
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
        # print(i_operator + ' start calculating')
        df_factor_1 = getattr(run, i_operator)(data_rolling)
        # df_factor = rolling_norm(df_factor, 1200)
        df_factor_1.replace([np.inf, -np.inf], np.nan, inplace=True)
        for j_operator in func_name:
            df_factor = getattr(run, j_operator)(df_factor_1)
            df_factor.replace([np.inf, -np.inf], np.nan, inplace=True)
            df_factor = rolling_norm(df_factor, 1200)
            for i_feature in df_factor.columns:
                # print(i_feature)
                df_factor_temp = df_factor[i_feature]
                df_need = pd.concat([df_factor_temp, return_points], axis=1, join='inner')
                if_true = check_factor_into_lib(df_need)
                if if_true is True:
                    print('!!!!!!!!!')
                    print(i_operator + ' ' + j_operator + ' ' + i_feature)
                    df_factor_temp.to_csv(
                        '/data/user/017024/search_factor_generator/IF/two_layers/' + i_operator + '_' + j_operator +
                        '_' + i_feature + '_' + operator_params_str + '.csv')
            # t2 = dt.datetime.now()
            # print(i_operator + ' costs: ', t2 - t1)
        t3 = dt.datetime.now()
        print('all operators costs: ', t3 - t0)


if __name__ == '__main__':
    main(rolling_norm_init=0)
