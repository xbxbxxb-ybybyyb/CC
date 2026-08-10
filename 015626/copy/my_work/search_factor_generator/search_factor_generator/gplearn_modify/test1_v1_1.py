import pandas as pd
import os
from gplearn_modify.functions import _function_map
from gplearn_modify.genetic import SymbolicTransformer
from gplearn_modify.fitness import information_coefficient, sharpe_ratio, fitness1, r_square, fitness2, fitness3
from factor_test.SIF_Factor_Test13 import SIF_Factor_Test



start_date = '20170101'
end_date_insample = '20180831'
end_date_outsample = '20181231'
factor_save_path = os.path.join('/data/user/017024/data/IC_factors/gp_factors_wsc',
                                start_date + '-' + end_date_outsample)
if not os.path.exists(factor_save_path):
    os.makedirs(factor_save_path)
if not os.path.exists(os.path.join(factor_save_path, 'factors')):
    os.makedirs(os.path.join(factor_save_path, 'factors'))
if not os.path.exists(os.path.join(factor_save_path, 'pictures')):
    os.makedirs(os.path.join(factor_save_path, 'pictures'))

if __name__ == '__main__':
    '''数据导入'''
    future_data_ic = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
                                 'MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5').xs('IC.CFE', level=1)
    future_data_ic = future_data_ic[['future_open', 'future_close', 'future_high', 'future_low', 'future_amount',
                                     'future_volume', 'future_vwap', 'future_twap', 'future_position']]
    # future_data_ic = future_data_ic.fillna(method='ffill')
    future_return = future_data_ic['vwap'].shift(-2) / future_data_ic['vwap'].shift(-1) - 1
    future_return.name = 'return'
    # future_return = future_return.fillna(0)

    future_data_ic_insample = future_data_ic[start_date: end_date_insample]
    future_return_insample = future_return[start_date: end_date_insample]
    future_data_ic_outsample = future_data_ic[start_date: end_date_outsample]
    # future_return_outsample = future_return['2016':'2017']

    '''导入gplearn module'''
    function_set = list(_function_map.keys())
    gp1 = SymbolicTransformer(population_size=3000, hall_of_fame=100, n_components=20, generations=20,
                              tournament_size=2, stopping_criteria=0.5, const_range=None, const_params_range=(3, 121),
                              init_depth=(1, 3), init_method='half and half', function_set=function_set,
                              metric=fitness3, parsimony_coefficient=0.0075, p_crossover=0.87, p_subtree_mutation=0.02,
                              p_hoist_mutation=0.02, p_point_mutation=0.02, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(future_data_ic.columns), warm_start=False, low_memory=False, n_jobs=-1,
                              verbose=1, random_state=0, factor_save_path=factor_save_path)

    gp1.fit(future_data_ic_insample, future_return_insample)

    factors_exist_list = [i[:-3] for i in os.listdir(os.path.join(factor_save_path, 'factors'))]
    for i_program in gp1._best_programs:
        program_formula = i_program.__str__()
        print(program_formula)
        factor_value = i_program.execute(future_data_ic_outsample)
        factor_value.name = program_formula
        factor_value = factor_value.to_frame()
        if program_formula not in factors_exist_list:
            factor_value.to_hdf(os.path.join(factor_save_path, 'factors', program_formula) + '.h5', key=program_formula)
            SIF_Factor_Test(df=factor_value, factor_name=factor_value.columns[0], save_image=True, show_image=False,
                            savepath=os.path.join(factor_save_path, 'pictures')).draw_result()
            factors_exist_list.append(program_formula)

