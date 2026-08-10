import pandas as pd
import os
import numpy as np
import datetime as dt
from gplearn_modify.functions import _function_map
from gplearn_modify.genetic import SymbolicTransformer
from gplearn_modify.fitness import information_coefficient, sharpe_ratio, fitness1, r_square, fitness2, fitness3
from factor_test.SIF_Factor_Test13 import SIF_Factor_Test
from utils_wsc.help_functions_wsc import read_pickle

ticker = 'IF.CFE'

start_date = '20170101'  # 训练集开始时间
end_date_train = '20181231'  # 训练集结束时间
end_date_validation = '20190630'  # 验证集结束时间
end_date_test = '20200630'
datetime_now = dt.datetime.now()
factor_save_path_raw = os.path.join('/data/user/017024/data/' + ticker.split('.')[0] + '_factors/gp_factors_wsc',
                                    start_date + '-' + end_date_validation)
factor_save_path = os.path.join(factor_save_path_raw, str(dt.datetime.now()).replace(':', '-').replace(' ', '_'))
factor_save_path_factors = os.path.join(factor_save_path, 'factors')  # 生成的因子值
factor_save_path_pictures = os.path.join(factor_save_path, 'pictures')  # 生成的因子图片
factor_save_path_fitness = os.path.join(factor_save_path, 'fitness')  # 每一轮进化选出的因子名单
if not os.path.exists(factor_save_path_raw):
    os.makedirs(factor_save_path_raw)
if not os.path.exists(factor_save_path):
    os.makedirs(factor_save_path)
if not os.path.exists(factor_save_path_factors):
    os.makedirs(factor_save_path_factors)
if not os.path.exists(factor_save_path_pictures):
    os.makedirs(factor_save_path_pictures)
if not os.path.exists(factor_save_path_fitness):
    os.makedirs(factor_save_path_fitness)

if __name__ == '__main__':
    '''数据导入'''
    future_data_if = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
                                 'MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5').xs(ticker, level=1)
    future_data_if = future_data_if[['open', 'close', 'high', 'low', 'amount',
                                     'volume', 'vwap', 'twap', 'position']]
    future_data_if.columns = ['future_open', 'future_close', 'future_high', 'future_low', 'future_amount',
                              'future_volume', 'future_vwap', 'future_twap', 'future_position']
    # future_data_ic = future_data_ic.fillna(method='ffill')
    index_dict_if = read_pickle('/data/user/015626/data/share/LOCAL_DATA/for_wsc/MINUTE_old/SPOT_DATA_120101_200901.pkl')
    index_data_if = None
    for i_name in sorted(index_dict_if.keys()):
        if i_name.endswith('_if'):
            temp_data = index_dict_if[i_name]
            index_data_if = temp_data if index_data_if is None else pd.concat([index_data_if, temp_data], axis=1)
    index_data_if.columns = ['index_amount', 'index_close', 'index_high', 'index_low', 'index_open', 'index_volume']
    x_if = pd.concat([future_data_if, index_data_if], axis=1, join='inner')

    future_return = future_data_if['future_vwap'].shift(-2) / future_data_if['future_vwap'].shift(
        -1) - 1  # 期指收益率，作为预测标签
    future_return.name = 'return'
    # future_return = future_return.fillna(0)

    x_if_train = x_if[start_date: end_date_train]
    future_return_if_train = future_return[start_date: end_date_train]
    x_if_validation = x_if[start_date: end_date_validation]
    x_if_test = x_if[start_date: end_date_test]
    # future_return_outsample = future_return['2016':'2017']

    '''导入gplearn module'''
    function_set = list(_function_map.keys())
    gp1 = SymbolicTransformer(population_size=3000, hall_of_fame=100, n_components=20, generations=20,
                              tournament_size=2, stopping_criteria=0.5, const_range=None, const_params_range=(3, 121),
                              init_depth=(1, 4), init_method='half and half', function_set=function_set,
                              metric=fitness3, parsimony_coefficient=0.008, p_crossover=0.87, p_subtree_mutation=0.02,
                              p_hoist_mutation=0.02, p_point_mutation=0.02, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(x_if.columns), warm_start=False, low_memory=False, n_jobs=-1,
                              verbose=1, random_state=3, factor_save_path=factor_save_path)

    print(str(gp1))

    gp1.fit(x_if_train, future_return_if_train)

    factors_exist_list = [i[:-3] for i in os.listdir(factor_save_path_factors)]
    for i in np.arange(len(gp1._programs)):
        fitness = pd.read_csv(os.path.join(factor_save_path_fitness, str(i)) + '.csv', index_col=0).values
        for j_number in fitness:
            j_program = gp1._programs[i][j_number[0]]
            if j_program is not None:
                program_formula = j_program.__str__()
                # print(program_formula)
                if program_formula not in factors_exist_list:
                    factor_value = j_program.execute(x_if_test)
                    factor_value.name = program_formula
                    factor_value = factor_value.to_frame()
                    factor_value.to_hdf(os.path.join(factor_save_path_factors, program_formula)
                                        + '.h5', key=program_formula)
                    stats = SIF_Factor_Test(df=factor_value, factor_name=factor_value.columns[0], save_image=False,
                                            ticker=ticker, starttime=start_date, endtime=end_date_validation,
                                            show_image=False, savepath=factor_save_path_pictures).draw_result()
                    if (stats['IC-1min'] > 0.01) & (stats['ret_per_deal'] > 1e-4) & (stats['sharpe_Q3-Q0'] > 2) & \
                       (stats['long_short_mdd'] > -0.1):
                        SIF_Factor_Test(df=factor_value, factor_name=factor_value.columns[0], save_image=True,
                                        ticker=ticker, starttime=start_date, endtime=end_date_test,
                                        show_image=False, savepath=factor_save_path_pictures).draw_result()
                        factors_exist_list.append(program_formula)


