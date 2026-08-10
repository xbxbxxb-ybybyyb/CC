import os
import logging
import numpy as np
import pandas as pd
import datetime as dt

from search.utils import get_data_num
from search.functions import _function_map
from search.genetic import SymbolicTransformer
from search.fitness import icac_np, icac_np_minus, icht_np, icht_np_minus


if __name__ == '__main__':
    start_date_outsample = '20190101'  # 验证集开始时间
    start_date_insample = '20190101'  # 训练集开始时间
    end_date_insample = '20210630'  # 训练集结束时间
    end_date_outsample = '20211231'  # 验证集结束时间
    ret_target = 'ret_1min'
    metric_method = 'icht_minus_17.5'
    ticker = 'IC'
    folder_name = 'cfg_v3_nodrop_1200'
    search_data_root = 'search_data_ic_1min_cfg_v3_di_20170104_20230605.h5'
    search_label_root = 'ret_ic_vwap_multitime_20170104_20230605.h5'

    metric_num = icht_np_minus
    population_size_num = 10000  # 初始种群大小
    generations_num = 16  # 迭代多少代
    rolling_window_num = 1200  # 公式ts_rank周期
    parsimony_coefficient_num = 0.0045  # icac~0.0003, icht_12.5~0.004, icht_10~0.00375, icht_15~0.00425, icht_7.5~0.0035, icht_17.5~0.0045
    threshold_num = 0.19  # icac~0.0135, icht_12.5~0.17, icht_10~0.16, icht_15~0.18, icht_7.5~0.15 ,icht_17.5~0.19

    base_root = '/dfs/user/015626/data/search'
    factor_save_path = os.path.join(base_root, start_date_outsample + '-' + end_date_outsample,
                                    start_date_insample + '-' + end_date_insample, metric_method,
                                    ticker, folder_name)
    operators_move_list = ['ts_pred_delta', 'macd', 'atr', 'ts_reg_residual', 'di_plus', 'di_minus', 'mfi',
                           'outlier_ratio', 'up_outlier_ratio', 'down_outlier_ratio', 'trima']
    features_move_list = []  # ['bbn_1', 'bbn_2', 'bbn_3', 'bbn_4', 'sbn_1', 'sbn_2', 'sbn_3', 'sbn_4']
    print(factor_save_path)
    factor_save_path_factors = os.path.join(factor_save_path, 'factors')  # 生成的因子值
    factor_save_path_pictures = os.path.join(factor_save_path, 'pictures')  # 生成的因子图片
    factor_save_path_fitness = os.path.join(factor_save_path, 'fitness')  # 每一轮进化选出的因子名单
    factor_save_path_logs = os.path.join(factor_save_path, 'logs')  # 训练日志

    os.makedirs(factor_save_path_factors, exist_ok=True)
    os.makedirs(factor_save_path_pictures, exist_ok=True)
    os.makedirs(factor_save_path_fitness, exist_ok=True)
    os.makedirs(factor_save_path_logs, exist_ok=True)
    time_now = str(len(os.listdir(factor_save_path_fitness))) + '_' + dt.datetime.now().strftime('%Y%m%d%H%M%S%f')
    os.makedirs(os.path.join(factor_save_path_fitness, time_now), exist_ok=True)

    if not os.path.exists(os.path.join(base_root, 'rand_int_used.xlsx')):
        pd.Series().to_excel(os.path.join(base_root, 'rand_int_used.xlsx'))
    rand_int_used = pd.read_excel(os.path.join(base_root, 'rand_int_used.xlsx'), index_col=0)
    rand_int_used_list = np.squeeze(rand_int_used.values)
    rand_int_now = np.random.randint(0, 2 ** 32 - 1)
    while rand_int_now in rand_int_used_list:
        rand_int_now = np.random.randint(0, 2 ** 32 - 1)
    rand_int_used.append(pd.Series(rand_int_now), ignore_index=True).to_excel(
        os.path.join(base_root, 'rand_int_used.xlsx'))

    logging.basicConfig(filename=os.path.join(factor_save_path_logs, 'factor_searcher.log'),
                        level=logging.INFO, format='%(levelname)s: %(asctime)s %(message)s')
    logging.info(
        f'Start to Search factors, the folder for this iteration is {time_now}, the random seed is {rand_int_now},'
        f' insample range is {start_date_insample} to {end_date_insample}, '
        f'validation range is {start_date_outsample} to {end_date_outsample}, ret target is {ret_target}.\n')

    '''数据导入'''
    logging.info(f'Iteration {time_now} start to load data.')
    search_data = pd.DataFrame(pd.read_hdf(os.path.join(base_root, 'search_data', search_data_root))).astype(
        'float32')
    search_label = pd.DataFrame(pd.read_hdf(os.path.join(base_root, 'search_data', search_label_root)))[
        ret_target].astype('float32')
    search_label = search_label.loc[search_data.index]
    search_data.drop(features_move_list, axis=1, inplace=True)

    search_data_index = search_data.index.tolist()
    dt_start_date_ins = get_data_num(search_data, start_date_insample)
    dt_end_date_ins = get_data_num(search_data, end_date_insample)
    dt_start_date_oos = get_data_num(search_data, start_date_outsample)
    dt_end_date_oos = get_data_num(search_data, end_date_outsample)

    data_drop_list = None

    '''导入gplearn module'''
    function_set = list(_function_map.keys())
    for i_op in operators_move_list:
        function_set.remove(i_op)
    gp1 = SymbolicTransformer(population_size=population_size_num, hall_of_fame=100, n_components=20,
                              generations=generations_num, tournament_size=3, stopping_criteria=100,
                              const_range=None, const_params_range=(3, 121),
                              init_depth=(1, 4), init_method='half and half', function_set=function_set,
                              metric=metric_num, parsimony_coefficient=parsimony_coefficient_num,
                              p_crossover=0.87, p_subtree_mutation=0.02,
                              p_hoist_mutation=0.02, p_point_mutation=0.02, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(search_data.columns), warm_start=False, low_memory=True, n_jobs=-1,
                              verbose=1, random_state=rand_int_now, factor_save_path=factor_save_path,
                              rolling_window=rolling_window_num, time_now=time_now, threshold=threshold_num)

    fit_parameters = gp1.__dict__.copy()
    del fit_parameters['function_set']
    del fit_parameters['feature_names']
    logging.info(f'Iteration {time_now} start to fit data, the fit parameters are\n {fit_parameters}\n\n'
                 f'the function_set is\n {function_set}\n')

    gp1.fit(search_data.values, search_label.values, dt_start_date_ins, dt_end_date_ins,
            dt_start_date_oos, dt_end_date_oos, data_drop_list)
    logging.info(f'Factors has been fitted')
    # logging.info(f'Iteration {time_now} done.\n\n\n')


