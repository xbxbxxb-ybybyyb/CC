import sys

sys.path.insert(0, '/data/user/020529/mobius_product/code')

import warnings
from multiprocessing import Pool
from config.CRN_CLA_v4 import model_config as crn_cla_cfg
from config.CRN_REG_v4 import model_config as crn_reg_cfg
from config.CRN_SPOT_CLA_v4 import model_config as crn_spot_cla_cfg
from config.CRN_SPOT_REG_v4 import model_config as crn_spot_reg_cfg
from config.CRN_MLP_CLA_v1 import model_config as crn_mlp_cla_cfg
from config.CRN_MLP_REG_v1 import model_config as crn_mlp_reg_cfg
from toolkit.data_helper import fetch_factor_from_list
from toolkit.path_helper import save_factor, copy_model_files, predict, set_model_file, set_model_pred, set_model_trade, set_model_update, add_config_files
from toolkit.misc_helper import get_gpu_version, quarter_last_friday, print_error


def main():
    # **************************************************

    step_1 = False  # prepare data (env: research)
    step_2 = True  # copy model files (env: research)
    step_3 = True  # make predictions (env: research)
    step_4 = True  # pack models (env: research)
    step_5 = True  # copy files (env: research)

    # **************************************************

    path_id = '50'
    strategy = 'ic_v7unifac_crn'
    update_date = '20250627'
    verify_date_list = quarter_last_friday('20201201', '20250328')
    config_list = [
        {
            'config_dict': crn_cla_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever_{}'.format(path_id),
            'factor_list': 'IC_v7c',
            'ticker_type': 'IC_ORIG',
            'return_time': [1, 5, 10],
            'random_seed': [0, 1],
        },
        {
            'config_dict': crn_reg_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever_{}'.format(path_id),
            'factor_list': 'IC_v7c',
            'ticker_type': 'IC_ORIG',
            'return_time': [1, 5, 10],
            'random_seed': [0, 1],
        },
        {
            'config_dict': crn_spot_cla_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever_{}'.format(path_id),
            'factor_list': 'IC_v7c',
            'ticker_type': 'IC_SPOT',
            'return_time': [10, 20, 30],
            'random_seed': [0, 1],
        },
        {
            'config_dict': crn_spot_reg_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever_{}'.format(path_id),
            'factor_list': 'IC_v7c',
            'ticker_type': 'IC_SPOT',
            'return_time': [10, 20, 30],
            'random_seed': [0, 1],
        },
        {
            'config_dict': crn_mlp_cla_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever_{}'.format(path_id),
            'factor_list': 'IC_v7c',
            'ticker_type': 'IC_ORIG',
            'return_time': [1, 5, 10, 20, 30],
            'random_seed': [0, 1],
        },
        {
            'config_dict': crn_mlp_reg_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever_{}'.format(path_id),
            'factor_list': 'IC_v7c',
            'ticker_type': 'IC_ORIG',
            'return_time': [1, 5, 10, 20, 30],
            'random_seed': [0, 1],
        },
    ]

    device_dict = {
        'A100': {'Process': 4},  # 40GB
        'V100': {'Process': 3},  # 32GB
        'P100': {'Process': 1},  # 16GB
        '1080': {'Process': 1},  # 11GB
    }

    # **************************************************

    gpu = get_gpu_version()
    print('GPU: {}'.format(gpu), flush=True)

    gpu_list = [x for x in device_dict if x in gpu]
    assert len(gpu_list) == 1, 'No Qualified GPUs'
    gpu_type = gpu_list[0]
    num_processes = device_dict[gpu_type]['Process']

    # **************************************************

    if step_1:
        # prepare factor
        factor_base_list = [config['factor_base'] for config in config_list]
        factor_base_list = list(set(factor_base_list))
        factor_base_list.sort()
        for factor_base in factor_base_list:
            factor_root_list = [config['factor_root'] for config in config_list if config['factor_base'] == factor_base]
            factor_root_list = list(set(factor_root_list))
            num_factor_roots = len(factor_root_list)
            assert num_factor_roots == 1, f'find {num_factor_roots} factor roots for {factor_base}'
            factor_root_name = factor_root_list[0]
            factor_list_list = [config['factor_list'] for config in config_list if config['factor_base'] == factor_base]
            factor_list_list = list(set(factor_list_list))
            num_factor_lists = len(factor_list_list)
            assert num_factor_lists == 1, f'find {num_factor_lists} factor lists for {factor_base}'
            factor_list_name = factor_list_list[0]
            factor_all = fetch_factor_from_list(factor_root_name=factor_root_name, factor_list_name=factor_list_name, str_date='20170101', end_date=update_date)
            save_factor(factor_base=factor_base, factor_data=factor_all, path_id=path_id)

    # **************************************************

    if step_2:
        for config in config_list:
            model_config = config['config_dict']
            factor_base = config['factor_base']
            ticker_type = config['ticker_type']
            return_time_list = config['return_time']
            random_seed_list = config['random_seed']

            # copy production model
            for return_time in return_time_list:
                for random_seed in random_seed_list:
                    copy_model_files(model_config, factor_base, ticker_type, update_date, return_time, random_seed, path_id, prod_version=True)

            # copy validation model
            for verify_date in verify_date_list:
                for return_time in return_time_list:
                    for random_seed in random_seed_list:
                        copy_model_files(model_config, factor_base, ticker_type, verify_date, return_time, random_seed, path_id, prod_version=False)

    # **************************************************

    if step_3:
        for config in config_list:
            model_config = config['config_dict']
            factor_base = config['factor_base']
            ticker_type = config['ticker_type']
            return_time_list = config['return_time']
            random_seed_list = config['random_seed']

            # predict validation model
            pool = Pool(processes=num_processes)
            for verify_date in verify_date_list:
                for return_time in return_time_list:
                    for random_seed in random_seed_list:
                        pool.apply_async(predict, args=(model_config, factor_base, ticker_type, verify_date, return_time, random_seed, path_id),
                                         kwds={'prod_version': False, 'end_date': update_date}, error_callback=print_error)
            pool.close()
            pool.join()

    # **************************************************

    if step_4:
        for config in config_list:
            model_config = config['config_dict']
            factor_base = config['factor_base']
            ticker_type = config['ticker_type']
            return_time_list = config['return_time']
            random_seed_list = config['random_seed']

            # extract model file and factor list
            set_model_file(model_config, factor_base, ticker_type, update_date, return_time_list, random_seed_list, path_id)

            # extract historical prediction (seeds x folds)
            set_model_pred(model_config, factor_base, ticker_type, update_date, verify_date_list, return_time_list, random_seed_list, path_id)

    # **************************************************

    if step_5:
        for config in config_list:
            model_config = config['config_dict']
            factor_base = config['factor_base']
            ticker_type = config['ticker_type']
            return_time_list = config['return_time']

            # copy model file and factor list from model_file to model_trade
            set_model_trade(strategy, model_config, factor_base, ticker_type, update_date, path_id)

            # copy historical prediction from model_pred to model_update/historical_value and initialize model_update/model_raw
            set_model_update(strategy, model_config, factor_base, ticker_type, update_date, return_time_list, path_id)

        ticker_type_list = [config['ticker_type'][0:2] for config in config_list]
        ticker_type_list = list(set(ticker_type_list))
        num_ticker_types = len(ticker_type_list)
        assert num_ticker_types == 1, f'find {num_ticker_types} ticker types'
        ticker_type = ticker_type_list[0]

        # add model_config.json and factor_name_mapping.csv to model_trade
        add_config_files(strategy, ticker_type, update_date, path_id)

        # copy model_trade to model_update
        # copy_trade_to_update(strategy, ticker_type, update_date, path_id)

    # **************************************************
    return None


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    main()
