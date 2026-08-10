import os
import numpy as np
import pandas as pd
import datetime as dt
from gplearn_modify.functions import _function_map
from gplearn_modify.genetic import SymbolicTransformer
from gplearn_modify.fitness import information_coefficient, sharpe_ratio, fitness1, r_square, fitness2, fitness3, segmented_information_coefficient
from factor_test.SIF_Factor_Test21 import SIF_Factor_Test


start_date = '20190101'  # 训练集开始时间
end_date_insample = '20200630'  # 训练集结束时间
end_date_outsample = '20201231'  # 验证集结束时间
factor_save_path = os.path.join('/data/user/017024/data/IC_factors/gp_factors_wsc',
                                start_date + '-' + end_date_outsample, 'information_coefficient')
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
    future_data_ic = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
                                 'MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5').xs('IC.CFE', level=1)
    future_data_ic = future_data_ic[['open', 'close', 'high', 'low', 'amount',
                                     'volume', 'vwap', 'twap', 'position']]
    future_data_ic.columns = ['future_open', 'future_close', 'future_high', 'future_low', 'future_amount',
                                     'future_volume', 'future_vwap', 'future_twap', 'future_position']
    spot_data_ic = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5').xs('IC.CFE', level=1)
    spot_data_ic.columns = ['spot_amount', 'spot_close', 'spot_high', 'spot_low', 'spot_open', 'spot_volume']
    future_data_ic = pd.concat([future_data_ic, spot_data_ic], axis=1, join='inner')
    # future_data_ic = future_data_ic.fillna(method='ffill')
    future_return = future_data_ic['future_vwap'].shift(-2) / future_data_ic['future_vwap'].shift(-1) - 1  # 期指收益率，作为预测标签
    future_return.name = 'return'
    # future_return = future_return.fillna(0)

    future_data_ic_insample = future_data_ic[start_date: end_date_insample]
    future_return_insample = future_return[start_date: end_date_insample]
    future_data_ic_outsample = future_data_ic[start_date: end_date_outsample]
    # future_return_outsample = future_return['2016':'2017']

    '''导入gplearn module'''
    function_set = list(_function_map.keys())
    gp1 = SymbolicTransformer(population_size=5000, hall_of_fame=100, n_components=20, generations=20,
                              tournament_size=2, stopping_criteria=0.05, const_range=None, const_params_range=(3, 121),
                              init_depth=(1, 4), init_method='half and half', function_set=function_set,
                              metric=information_coefficient, parsimony_coefficient=0.0005, p_crossover=0.87, p_subtree_mutation=0.02,
                              p_hoist_mutation=0.02, p_point_mutation=0.02, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(future_data_ic.columns), warm_start=False, low_memory=False, n_jobs=-1,
                              verbose=1, random_state=80, factor_save_path=factor_save_path, time_now=time_now)

    gp2 = SymbolicTransformer(population_size=30, hall_of_fame=6, n_components=3, generations=3, tournament_size=3,
                              stopping_criteria=1, const_range=None, const_params_range=(3, 241), init_depth=(1, 3),
                              init_method='half and half', function_set=function_set, metric=fitness2,
                              parsimony_coefficient=0.005, p_crossover=0.9, p_subtree_mutation=0.01,
                              p_hoist_mutation=0.01, p_point_mutation=0.01, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(future_data_ic.columns), warm_start=False, low_memory=False, n_jobs=1,
                              verbose=1, random_state=0, factor_save_path=factor_save_path, time_now=time_now)

    gp1.fit(future_data_ic_insample, future_return_insample)

    factors_exist_list = [i[:-3] for i in os.listdir(factor_save_path_factors)]
    for i in np.arange(len(gp1._programs)):
        fitness = pd.read_csv(os.path.join(factor_save_path_fitness, time_now, str(i)) + '.csv', index_col=0).values
        for j_number in fitness:
            j_program = gp1._programs[i][j_number[0]]
            if j_program is not None:
                program_formula = j_program.__str__()
                # print(program_formula)
                if program_formula not in factors_exist_list:
                    factor_value = j_program.execute(future_data_ic_outsample)
                    factor_value.name = program_formula
                    factor_value = factor_value.to_frame()
                    factor_value.to_hdf(os.path.join(factor_save_path, 'factors', program_formula)
                                        + '.h5', key=program_formula)
                    SIF_Factor_Test(df=factor_value, factor_name=factor_value.columns[0], save_image=True, show_image=False, 
                                    savepath=os.path.join(factor_save_path_pictures, 'insample'), starttime=start_date, endtime=end_date_insample).draw_result()
                    SIF_Factor_Test(df=factor_value, factor_name=factor_value.columns[0], save_image=True, show_image=False, 
                                    savepath=os.path.join(factor_save_path_pictures, 'outsample'), starttime=end_date_insample, endtime=end_date_outsample).draw_result()
                    SIF_Factor_Test(df=factor_value, factor_name=factor_value.columns[0], save_image=True, show_image=False, 
                                    savepath=os.path.join(factor_save_path_pictures, 'allhistory'), starttime=start_date, endtime=end_date_outsample).draw_result()
                    factors_exist_list.append(program_formula)


