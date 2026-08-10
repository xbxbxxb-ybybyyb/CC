import sys
sys.path.append('/data/user/017024/MobiusProd/')

import numpy as np
import pandas as pd
from config.base import *
from models.executor import train
from utils.logger_wsc import LoggerMyself
from utils.data_helper import get_return, get_factor, get_sig_multiseed
from utils.help_functions_wsc import multiprocessing_helper, expanding_helper, save_pickle


def main(need_train=True, need_onnx=True, need_value=True, xy_exists=False):
    # data params
    ticker = 'IF'
    model_name = 'dnn'
    pre_date = '20190101'
    bgn_date = '20220101'
    end_date = '20240401'
    factor_root_name = 'IF_ever'
    factor_list_name = 'if_v9c'
    x_path = os.path.join(factorlib_path, ticker,
                          f'{factor_list_dict[factor_list_name].split("/")[-1].split(".")[0]}_{pre_date}_{end_date}.h5')
    y_path = os.path.join(returnlib_path, f'{ticker}_return_{pre_date}_{end_date}.h5')

    # training_params
    max_process_num = 6 if need_onnx else 12
    rolling_list = [((pd.Timestamp(pre_date), i[0]), i) for i in
                    expanding_helper(bgn_date, end_date, frequency='quarterly', time_mode='start')]
    ret_target_list = [1, 5, 10, 20, 30]
    obj_name_list = ['regression', 'binary']
    cv_list = np.arange(5)
    random_seed_list = [3416, 4351, 7387, 8780, 2537]

    logger = LoggerMyself(f'{factor_list_name}_{model_name}_{bgn_date}_{end_date}.log',
                          os.path.join(log_path, 'update_model'))
    logger.info(f'Model Update: {ticker}_{model_name}_{bgn_date}_{end_date}, '
                f'need train: {need_train}, need onnx: {need_onnx}, need value: {need_value}, '
                f'factorlib is {factor_list_dict[factor_list_name].split("/")[-1].split(".")[0]}, \n'
                f'ret_target_list is {ret_target_list}, obj_name_list is {obj_name_list}, '
                f'random_seed_list is {random_seed_list}', outputs='both')

    # start to update model
    if need_train:
        if not xy_exists:
            get_return(ticker, pre_date, end_date, if_save=True)
            logger.info(f'{ticker}_return dumps, save_path: {y_path}')
            get_factor(ticker, factor_root_name, factor_list_name, pre_date, end_date, if_save=True)
            logger.info(f'{ticker}_input dumps, save_path: {x_path}')
        multiprocessing_helper(train, max_process_num, print, rolling_list, ret_target_list, obj_name_list, cv_list,
                               random_seed_list, x_path=x_path, y_path=y_path, factorlib_name=factor_list_name,
                               model_name=model_name, sig_name=end_date, get_onnx=need_onnx)
        logger.info(f'model has been trained', outputs='both')
        if need_onnx:
            logger.info('onnx has been generated', outputs='both')

    if need_value:
        # get factor_value
        hist_value_path = os.path.join(
            prod_share_path, 'model_update', f'{end_date}_{ticker.lower()}_{factor_list_name}', 'historical_value')
        agg_value_path = os.path.join(
            prod_share_path, 'model_update', f'{end_date}_{ticker.lower()}_{factor_list_name}', 'model_value',
            'model_raw', str(end_date))
        agg_value_path_norm = os.path.join(
            prod_share_path, 'model_update', f'{end_date}_{ticker.lower()}_{factor_list_name}', 'model_value',
            'model_norm', str(end_date))
        os.makedirs(hist_value_path, exist_ok=True)
        os.makedirs(agg_value_path, exist_ok=True)
        os.makedirs(agg_value_path_norm, exist_ok=True)
        for i_obj in obj_name_list:
            temp_sig_dict = dict()
            for i_ret in ret_target_list:
                i_base_root = os.path.join(model_save_path, factor_list_name, model_name)
                i_name = f'{model_name}_{i_obj}_{i_ret}'
                temp_df = get_sig_multiseed(i_base_root, i_obj, i_ret)
                temp_save_path = os.path.join(hist_value_path, i_name + '.pkl')
                save_pickle(temp_df, temp_save_path, protocol_level='default')
                temp_sig_dict[i_name] = temp_df.mean(axis=1)
            temp_sig_df = pd.DataFrame(temp_sig_dict)
            save_pickle(temp_sig_df, os.path.join(agg_value_path, f'{model_name}_{i_obj}.pkl'),
                        protocol_level='default')
        logger.info('sig value dumps\n', outputs='both')


if __name__ == '__main__':
    # step 1：除最新一期外的模型结果，生成因子值（hist_value要用），不需要onnx，TFFF（如果是之后三个月一次的常规迭代，不需要这一步）
    # step 2：最新一期的模型结果，并生成onnx，TTFF
    # step 3：更新信号值，hist_value和model_update，FFTT，这一步和上一步不能合并的原因是这一步要用python3.6的环境（和实盘保持一致）
    # step 2: 最新一期的模型结果，并生成onnx和信号值，TTTF
    main(need_train=True, need_onnx=False, need_value=False, xy_exists=False)
