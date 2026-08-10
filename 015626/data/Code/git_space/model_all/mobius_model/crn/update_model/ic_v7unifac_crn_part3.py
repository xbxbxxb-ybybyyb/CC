import sys

sys.path.insert(0, '/data/user/020529/mobius_product/code')

import warnings
from multiprocessing import Pool
# from config.CRN_CLA_v4 import model_config as crn_cla_cfg
# from config.CRN_REG_v4 import model_config as crn_reg_cfg
# from config.CRN_SPOT_CLA_v4 import model_config as crn_spot_cla_cfg
# from config.CRN_SPOT_REG_v4 import model_config as crn_spot_reg_cfg
from config.CRN_MLP_CLA_v1 import model_config as crn_mlp_cla_cfg
from config.CRN_MLP_REG_v1 import model_config as crn_mlp_reg_cfg
from framework.execute_v1 import train
from framework.execute_v4 import predict, export
from toolkit.data_helper import fetch_return, fetch_return_spot, fetch_factor_from_list, save_return, save_factor, backup_return, backup_factor
from toolkit.pack_helper import set_model_file, set_model_pred, set_model_trade, set_model_update, add_config_files
from toolkit.misc_helper import get_gpu_version, quarter_last_friday, print_error


def main():
    # **************************************************

    step_1 = True  # prepare data (env: py38_tf24)
    step_2 = True  # train models (env: py38_tf24)
    step_3 = False  # make predictions (env: research)
    step_4 = False  # export/pack models (env: research)
    step_5 = False  # copy files (env: research)

    # **************************************************

    strategy = 'ic_v7unifac_crn'
    update_date = '20250627'
    verify_date_list = quarter_last_friday('20201201', '20250328')
    config_list = [
        # {
        #     'config_dict': crn_cla_cfg,
        #     'factor_base': 'IC_v7c',
        #     'factor_root': 'IC_unifac_ever',
        #     'factor_list': 'IC_v7c',
        #     'ticker_type': 'IC_ORIG',
        #     'return_time': [1, 5, 10],
        #     'random_seed': [0, 1],
        # },
        # {
        #     'config_dict': crn_reg_cfg,
        #     'factor_base': 'IC_v7c',
        #     'factor_root': 'IC_unifac_ever',
        #     'factor_list': 'IC_v7c',
        #     'ticker_type': 'IC_ORIG',
        #     'return_time': [1, 5, 10],
        #     'random_seed': [0, 1],
        # },
        # {
        #     'config_dict': crn_spot_cla_cfg,
        #     'factor_base': 'IC_v7c',
        #     'factor_root': 'IC_unifac_ever',
        #     'factor_list': 'IC_v7c',
        #     'ticker_type': 'IC_SPOT',
        #     'return_time': [10, 20, 30],
        #     'random_seed': [0, 1],
        # },
        # {
        #     'config_dict': crn_spot_reg_cfg,
        #     'factor_base': 'IC_v7c',
        #     'factor_root': 'IC_unifac_ever',
        #     'factor_list': 'IC_v7c',
        #     'ticker_type': 'IC_SPOT',
        #     'return_time': [10, 20, 30],
        #     'random_seed': [0, 1],
        # },
        {
            'config_dict': crn_mlp_cla_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever',
            'factor_list': 'IC_v7c',
            'ticker_type': 'IC_ORIG',
            'return_time': [1, 5, 10, 20, 30],
            'random_seed': [0, 1],
        },
        {
            'config_dict': crn_mlp_reg_cfg,
            'factor_base': 'IC_v7c',
            'factor_root': 'IC_unifac_ever',
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
        # prepare return
        ticker_type_list = [config['ticker_type'] for config in config_list]
        ticker_type_list = list(set(ticker_type_list))
        ticker_type_list.sort()
        for ticker_type in ticker_type_list:
            if ticker_type in {'IF_ORIG', 'IC_ORIG', 'IM_ORIG'}:
                return_all = fetch_return(ticker_type=ticker_type[0:2], str_date='20170101', end_date=update_date)
            elif ticker_type in {'IF_SPOT', 'IC_SPOT', 'IM_SPOT'}:
                return_all = fetch_return_spot(ticker_type=ticker_type[0:2], str_date='20170101', end_date=update_date)
            else:
                raise AssertionError(f'invalid ticker type: {ticker_type}')
            save_return(ticker_type=ticker_type, return_data=return_all)
            backup_return(ticker_type=ticker_type, backup_date=update_date, return_data=return_all)

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
            save_factor(factor_base=factor_base, factor_data=factor_all)
            backup_factor(factor_base=factor_base, backup_date=update_date, factor_data=factor_all)

    # **************************************************

    if step_2:
        for config in config_list:
            model_config = config['config_dict']
            factor_base = config['factor_base']
            ticker_type = config['ticker_type']
            return_time_list = config['return_time']
            random_seed_list = config['random_seed']

            # train production model
            pool = Pool(processes=num_processes)
            for return_time in return_time_list:
                for random_seed in random_seed_list:
                    pool.apply_async(train, args=(model_config, factor_base, ticker_type, update_date, return_time, random_seed),
                                     kwds={'prod_version': True, 'save_info': True, 'show_info': False}, error_callback=print_error)
            pool.close()
            pool.join()

            # train validation model
            pool = Pool(processes=num_processes)
            for verify_date in verify_date_list:
                for return_time in return_time_list:
                    for random_seed in random_seed_list:
                        pool.apply_async(train, args=(model_config, factor_base, ticker_type, verify_date, return_time, random_seed),
                                         kwds={'prod_version': False, 'save_info': True, 'show_info': False}, error_callback=print_error)
            pool.close()
            pool.join()

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
                        pool.apply_async(predict, args=(model_config, factor_base, ticker_type, verify_date, return_time, random_seed),
                                         kwds={'prod_version': False, 'end_date': update_date}, error_callback=print_error)
            pool.close()
            pool.join()

    if step_4:
        for config in config_list:
            model_config = config['config_dict']
            factor_base = config['factor_base']
            ticker_type = config['ticker_type']
            return_time_list = config['return_time']
            random_seed_list = config['random_seed']

            # export production model
            for return_time in return_time_list:
                for random_seed in random_seed_list:
                    export(model_config, factor_base, ticker_type, update_date, return_time, random_seed, prod_version=True)

            # extract model file and factor list
            set_model_file(model_config, factor_base, ticker_type, update_date, return_time_list, random_seed_list)

            # extract historical prediction (seeds x folds)
            set_model_pred(model_config, factor_base, ticker_type, update_date, verify_date_list, return_time_list, random_seed_list)

    # **************************************************

    if step_5:
        for config in config_list:
            model_config = config['config_dict']
            factor_base = config['factor_base']
            ticker_type = config['ticker_type']
            return_time_list = config['return_time']

            # copy model file and factor list from model_file to model_trade
            set_model_trade(strategy, model_config, factor_base, ticker_type, update_date)

            # copy historical prediction from model_pred to model_update/historical_value and initialize model_update/model_raw
            set_model_update(strategy, model_config, factor_base, ticker_type, update_date, return_time_list)

        ticker_type_list = [config['ticker_type'][0:2] for config in config_list]
        ticker_type_list = list(set(ticker_type_list))
        num_ticker_types = len(ticker_type_list)
        assert num_ticker_types == 1, f'find {num_ticker_types} ticker types'
        ticker_type = ticker_type_list[0]

        # add model_config.json and factor_name_mapping.csv to model_trade
        add_config_files(strategy, ticker_type, update_date)

        # copy model_trade to model_update
        # copy_trade_to_update(strategy, ticker_type, update_date)

    # **************************************************
    return None


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    main()
