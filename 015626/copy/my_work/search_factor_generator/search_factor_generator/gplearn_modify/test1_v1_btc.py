import os
import numpy as np
import pandas as pd
import datetime as dt
from gplearn_modify.functions import _function_map
from gplearn_modify.genetic import SymbolicTransformer
from gplearn_modify.fitness import information_coefficient, sharpe_ratio, fitness1, r_square, fitness2, fitness3, segmented_information_coefficient, ami
from factor_test.SIF_Factor_Test21 import SIF_Factor_Test


start_date = '20170817'  # 训练集开始时间
end_date_insample = '20191231'  # 训练集结束时间
end_date_outsample = '20201202'  # 验证集结束时间
factor_save_path = os.path.join('/data/user/017024/data/btc/gp',
                                start_date + '-' + end_date_outsample, 'segmented_information_coefficient')
factor_save_path_factors = os.path.join(factor_save_path, 'factors')  # 生成的因子值
factor_save_path_pictures = os.path.join(factor_save_path, 'pictures')  # 生成的因子图片
factor_save_path_fitness = os.path.join(factor_save_path, 'fitness')  # 每一轮进化选出的因子名单
if not os.path.exists(factor_save_path):
    os.makedirs(factor_save_path)
if not os.path.exists(factor_save_path_factors):
    os.makedirs(factor_save_path_factors)
if not os.path.exists(factor_save_path_pictures):
    os.makedirs(factor_save_path_pictures)
time_now = str(dt.datetime.now()).replace(' ', '').replace(':', '').replace('-', '').replace('.', '')
if not os.path.exists(os.path.join(factor_save_path_fitness, time_now)):
    os.makedirs(os.path.join(factor_save_path_fitness, time_now))
    


if __name__ == '__main__':
    '''数据导入'''
    btc_data = pd.read_csv('/data/user/015626/data/share/LOCAL_DATA/CSV/testdata/B_1m.csv', index_col=0, parse_dates=True)
    btc_data.index.name = 'dt'
    btc_data = btc_data[['open', 'close', 'high', 'low', 'amount', 'volume']]
    btc_data.columns = ['btc_open', 'btc_close', 'btc_high', 'btc_low', 'btc_amount', 'btc_volume']
    btc_return = btc_data['btc_close'].shift(-2) / btc_data['btc_close'].shift(-1) - 1  # btc收益率，作为预测标签
    btc_return.name = 'return'
    btc_return = btc_return.fillna(0)

    btc_data_insample = btc_data[start_date: end_date_insample]
    btc_return_insample = btc_return[start_date: end_date_insample]
    btc_data_outsample = btc_data[start_date: end_date_outsample]
    # future_return_outsample = future_return['2016':'2017']

    '''导入gplearn module'''
    function_set = list(_function_map.keys())
    gp1 = SymbolicTransformer(population_size=5000, hall_of_fame=100, n_components=20, generations=8,
                              tournament_size=4, stopping_criteria=1.1, const_range=None, const_params_range=(3, 121),
                              init_depth=(1, 4), init_method='half and half', function_set=function_set,
                              metric=segmented_information_coefficient, parsimony_coefficient=0.0005, p_crossover=0.87, p_subtree_mutation=0.02,
                              p_hoist_mutation=0.02, p_point_mutation=0.02, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(btc_data.columns), warm_start=False, low_memory=False, n_jobs=-1,
                              verbose=1, random_state=114, factor_save_path=factor_save_path, time_now=time_now, rolling_window=1200)

    gp2 = SymbolicTransformer(population_size=30, hall_of_fame=6, n_components=3, generations=3, tournament_size=3,
                              stopping_criteria=1, const_range=None, const_params_range=(3, 241), init_depth=(1, 3),
                              init_method='half and half', function_set=function_set, metric=segmented_information_coefficient,
                              parsimony_coefficient=0.005, p_crossover=0.9, p_subtree_mutation=0.01,
                              p_hoist_mutation=0.01, p_point_mutation=0.01, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(btc_data.columns), warm_start=False, low_memory=False, n_jobs=1,
                              verbose=1, random_state=0, factor_save_path=factor_save_path, time_now=time_now, rolling_window=1200)

    gp1.fit(btc_data_insample, btc_return_insample)

    factors_exist_list = [i[:-3] for i in os.listdir(factor_save_path_factors)]
    for i in np.arange(len(gp1._programs)):
        fitness = pd.read_csv(os.path.join(factor_save_path_fitness, time_now, str(i)) + '.csv', index_col=0).values
        for j_number in fitness:
            j_program = gp1._programs[i][j_number[0]]
            if j_program is not None:
                program_formula = j_program.__str__()
                # print(program_formula)
                if program_formula not in factors_exist_list:
                    factor_value = j_program.execute(btc_data_outsample)
                    factor_value.name = program_formula
                    factor_value = factor_value.to_frame()
                    factor_value.to_hdf(os.path.join(factor_save_path, 'factors', program_formula)
                                        + '.h5', key=program_formula)
                    factor_temp = pd.concat([factor_value[program_formula], btc_return], axis=1)
                    SIF_Factor_Test(df=factor_temp, factor_name=factor_value.columns[0], save_image=True, show_image=False, 
                                    savepath=os.path.join(factor_save_path_pictures, 'insample'), starttime=start_date, endtime=end_date_insample).draw_result()
                    SIF_Factor_Test(df=factor_temp, factor_name=factor_value.columns[0], save_image=True, show_image=False, 
                                    savepath=os.path.join(factor_save_path_pictures, 'outsample'), starttime=end_date_insample, endtime=end_date_outsample).draw_result()
                    SIF_Factor_Test(df=factor_temp, factor_name=factor_value.columns[0], save_image=True, show_image=False, 
                                    savepath=os.path.join(factor_save_path_pictures, 'allhistory'), starttime=start_date, endtime=end_date_outsample).draw_result()
                    factors_exist_list.append(program_formula)


