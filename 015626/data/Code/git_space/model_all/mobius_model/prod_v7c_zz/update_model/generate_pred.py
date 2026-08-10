import sys

sys.path.insert(0, '/data/user/020529/mobius_product_zz/code')

import os
import numpy as np
import pandas as pd

from multifactor.IO import IO
from factor_utility.minute_tool import read_pickle, save_pickle, get_minute_seg_dt, find_file, concat_pd_spec, get_all_pred_helper, read_all_pickle_helper
from strategy.fitting_model import prep_train_test_helper, pred_helper
from ts.utility.ts_utility import read_ts_fac_helper, get_ret_vol, slice_by_minute, get_calendar_info, get_dummies_helper, check_tail_helper, calc_ts_pct, prep_ps2df_save
from minute_config_mobius import fts_path_is, fts_path_os, minute_future_path

####################################################################################################

fac_lib_date = '20250328'

### need to add model_date for each append ~only last 2 dates matter
model_update_dict = {
    'if_v7c': ['20240329', '20240628', '20240927', '20241227', '20250328'],
    'ic_v7unifac': ['20240329', '20240628', '20240927', '20241227', '20250328'],
    'im_v1unifac': ['20240329', '20240628', '20240927', '20241227', '20250328'],

    'if_v7c_spot': ['20240329', '20240628', '20240927', '20241227', '20250328'],
    'ic_v7unifac_spot': ['20240329', '20240628', '20240927', '20241227', '20250328'],
    'im_v1unifac_spot': ['20240329', '20240628', '20240927', '20241227', '20250328']
}

# suffix_list = ['if_v7c']
# suffix_list = ['ic_v7unifac']
# suffix_list = ['im_v1unifac']
# suffix_list = ['if_v7c_spot']
# suffix_list = ['ic_v7unifac_spot']
suffix_list = ['im_v1unifac_spot']

####################################################################################################

research_date = '20240628'

# append_prediction = True
append_prediction = False

# path setting
share_base = '/dfs/user/012398/data/strategy/mobius/mobius_prod_zz'
minute_base = os.path.join(share_base, 'strategy/minute')
pred_index_name = 'pred_index'

### fixed
filter_date = 'prod'
roll_name = '_r720'

for suffix in suffix_list:
    pred_res_base = os.path.join(share_base, '%s/minute/%s_%s' % (pred_index_name, suffix, filter_date))

    if suffix in model_update_dict:
        model_date = model_update_dict[suffix][-1]
    elif (suffix not in model_update_dict) and (not append_prediction):
        model_date = research_date
    else:
        raise RuntimeError('model_date')
    if append_prediction:
        if len(model_update_dict[suffix]) > 1:
            model_date_prev = model_update_dict[suffix][-2]
        else:
            model_date_prev = model_update_dict[suffix][-1]
    else:
        model_date_prev = model_date
    print(suffix, model_date, model_date_prev, flush=True)

    max_process = 8
    parallel = True

    if append_prediction:
        append_last_train_pred = True
        if fac_lib_date == model_date:
            append_true_pred = False
            prev_date = model_date_prev
        else:
            append_true_pred = True
            prev_date = model_date
    else:
        append_last_train_pred = False
        append_true_pred = False
        fac_lib_date = model_date
        prev_date = model_date

    sdate_pred = model_date + '235959'
    update_date = fac_lib_date

    short_list = [1, 5, 10]
    long_list = [10, 20, 30]
    model_list_extra = ['rfe_cla', 'rff_cla']
    slice_range_extra = [[931, 1129], [1300, 1456]]
    comb2_model_list = ['mlp_reg', 'lstm_cla']
    trade_num = 10

    print('trading config', flush=True)

    if suffix in ['if_v7c']:
        trade_contract = 'IF.CFE'
        use_spec = True
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])), flush=True)

        suffix_spec_dict = {'if_v7': ['IF_linear'],
                            'if_v7nl_181': ['IF_linear', 'IF_nonlinear', 'IF_181'],
                            'if_v7nlad_181ad': ['IF_linear', 'IF_nonlinear', 'IF_181', 'IF_nonlinear_diff', 'IF_181_diff']}
        suffix_spec_list = suffix_spec_dict['if_v7nlad_181ad']
        linear_fac_name_list = ['IF_linear']

        fac_list, linear_fac_list = [], []
        for suffix_itr in suffix_spec_list:
            fac_list_itr = [i.replace('.h5', '') for i in fac_ref[suffix_itr]]
            fac_list = fac_list + fac_list_itr
            if suffix_itr in linear_fac_name_list:
                linear_fac_list = linear_fac_list + fac_list_itr
        print(len(linear_fac_list), len(fac_list), flush=True)
        fac_val = read_ts_fac_helper(path_ever, fac_list=fac_list).fillna(0)
        fac = fac_val[linear_fac_list]
        fac_num = fac_val.shape[1]
        fac_num_linear = len(linear_fac_list)
        fac_num_nl = fac_num - fac_num_linear
        print('total fac:%d | linear:%d | nonlinear:%d' % (fac_num, fac_num_linear, fac_num_nl), flush=True)

        if len(set(fac_val)) - fac_val.shape[1] != 0:
            print('fac name error', flush=True)
            raise Exception

        if use_spec:
            model_list_long = ['lstm_cla', 'et_cla']
            model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {**{i: long_list for i in model_list_long},
                             **{i: short_list for i in model_list_short}}
            suffix_save = '%s_spec' % (suffix)
            model_list = model_list_long + model_list_short
        else:
            model_list = ['lstm_cla', 'et_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {i: long_list for i in model_list}
            suffix_save = '%s_102030' % (suffix)
        vol_adj = True

    elif suffix in ['if_v7c_spot']:
        trade_contract = 'IF.CFE'
        use_spec = False
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])), flush=True)

        suffix_spec_dict = {'if_v7': ['IF_linear'],
                            'if_v7nl_181': ['IF_linear', 'IF_nonlinear', 'IF_181'],
                            'if_v7nlad_181ad': ['IF_linear', 'IF_nonlinear', 'IF_181', 'IF_nonlinear_diff', 'IF_181_diff']}
        suffix_spec_list = suffix_spec_dict['if_v7nlad_181ad']
        linear_fac_name_list = ['IF_linear']

        fac_list, linear_fac_list = [], []
        for suffix_itr in suffix_spec_list:
            fac_list_itr = [i.replace('.h5', '') for i in fac_ref[suffix_itr]]
            fac_list = fac_list + fac_list_itr
            if suffix_itr in linear_fac_name_list:
                linear_fac_list = linear_fac_list + fac_list_itr
        print(len(linear_fac_list), len(fac_list), flush=True)
        fac_val = read_ts_fac_helper(path_ever, fac_list=fac_list).fillna(0)
        fac = fac_val[linear_fac_list]
        fac_num = fac_val.shape[1]
        fac_num_linear = len(linear_fac_list)
        fac_num_nl = fac_num - fac_num_linear
        print('total fac:%d | linear:%d | nonlinear:%d' % (fac_num, fac_num_linear, fac_num_nl), flush=True)

        if len(set(fac_val)) - fac_val.shape[1] != 0:
            print('fac name error', flush=True)
            raise Exception

        if use_spec:
            model_list_long = ['lstm_cla', 'et_cla']
            model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {**{i: long_list for i in model_list_long},
                             **{i: short_list for i in model_list_short}}
            suffix_save = '%s_spec' % (suffix)
            model_list = model_list_long + model_list_short
        else:
            model_list = ['lstm_cla', 'et_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {i: long_list for i in model_list}
            suffix_save = '%s_102030' % (suffix)
        vol_adj = True

    elif suffix in ['ic_v7unifac']:
        trade_contract = 'IC.CFE'
        use_spec = True
        if use_spec:
            model_list_long = ['et_cla', 'lstm_cla']
            model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
            model_list = model_list_long + model_list_short
            hpr_spec_dict = {**{i: short_list for i in model_list_short},
                             **{i: long_list for i in model_list_long}}
            suffix_save = '%s_spec' % (suffix)
        else:
            model_list = ['et_cla', 'lstm_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {i: long_list for i in model_list}
            suffix_save = '%s_102030' % (suffix)
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])), flush=True)

        suffix_spec_dict = {'ic_v7_if_v7': ['IC_linear', 'IF_linear'],
                            'ic_v7nl_if_v7nl_181': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181'],
                            'ic_v7nlad_if_v7nlad_181ad': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181', 'IC_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff']}
        suffix_spec_list = suffix_spec_dict['ic_v7nlad_if_v7nlad_181ad']
        linear_fac_name_list = ['IC_linear', 'IF_linear']

        fac_list, linear_fac_list = [], []
        for suffix_itr in suffix_spec_list:
            fac_list_itr = [i.replace('.h5', '') for i in fac_ref[suffix_itr]]
            fac_list = fac_list + fac_list_itr
            if suffix_itr in linear_fac_name_list:
                linear_fac_list = linear_fac_list + fac_list_itr
        print(len(linear_fac_list), len(fac_list), flush=True)
        fac_val = read_ts_fac_helper(path_ever, fac_list=fac_list).fillna(0)
        fac = fac_val[linear_fac_list]
        fac_num = fac_val.shape[1]
        fac_num_linear = len(linear_fac_list)
        fac_num_nl = fac_num - fac_num_linear
        print('total fac:%d | linear:%d | nonlinear:%d' % (fac_num, fac_num_linear, fac_num_nl), flush=True)

        with_desc = True
        vol_adj = False

    elif suffix in ['ic_v7unifac_spot']:
        trade_contract = 'IC.CFE'
        use_spec = False
        if use_spec:
            model_list_long = ['et_cla', 'lstm_cla']
            model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
            model_list = model_list_long + model_list_short
            hpr_spec_dict = {**{i: short_list for i in model_list_short},
                             **{i: long_list for i in model_list_long}}
            suffix_save = '%s_spec' % (suffix)
        else:
            model_list = ['et_cla', 'lstm_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {i: long_list for i in model_list}
            suffix_save = '%s_102030' % (suffix)
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])), flush=True)

        suffix_spec_dict = {'ic_v7_if_v7': ['IC_linear', 'IF_linear'],
                            'ic_v7nl_if_v7nl_181': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181'],
                            'ic_v7nlad_if_v7nlad_181ad': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181', 'IC_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff']}
        suffix_spec_list = suffix_spec_dict['ic_v7nlad_if_v7nlad_181ad']
        linear_fac_name_list = ['IC_linear', 'IF_linear']

        fac_list, linear_fac_list = [], []
        for suffix_itr in suffix_spec_list:
            fac_list_itr = [i.replace('.h5', '') for i in fac_ref[suffix_itr]]
            fac_list = fac_list + fac_list_itr
            if suffix_itr in linear_fac_name_list:
                linear_fac_list = linear_fac_list + fac_list_itr
        print(len(linear_fac_list), len(fac_list), flush=True)
        fac_val = read_ts_fac_helper(path_ever, fac_list=fac_list).fillna(0)
        fac = fac_val[linear_fac_list]
        fac_num = fac_val.shape[1]
        fac_num_linear = len(linear_fac_list)
        fac_num_nl = fac_num - fac_num_linear
        print('total fac:%d | linear:%d | nonlinear:%d' % (fac_num, fac_num_linear, fac_num_nl), flush=True)

        with_desc = True
        vol_adj = False

    elif suffix in ['im_v1unifac']:
        trade_contract = 'IM.CFE'
        use_spec = True
        if use_spec:
            model_list_long = ['et_cla', 'lstm_cla']  #
            model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
            model_list = model_list_long + model_list_short
            hpr_spec_dict = {**{i: short_list for i in model_list_short},
                             **{i: long_list for i in model_list_long}}
            suffix_save = '%s_spec' % (suffix)
        else:
            model_list = ['et_cla', 'lstm_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {i: long_list for i in model_list}
            suffix_save = '%s_102030' % (suffix)

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])), flush=True)

        suffix_spec_dict = {'im_v1_if_v7_2': ['IM_linear', 'IF_linear'],
                            'im_v1nl_181_if_v7_2nl_181': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IM_181', 'IF_181'],
                            'im_v1nlad_181ad_if_v7_2nlad_181ad': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']}
        suffix_spec_list = ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']
        linear_fac_name_list = ['IM_linear', 'IF_linear']

        fac_list, linear_fac_list = [], []
        for suffix_itr in suffix_spec_list:
            fac_list_itr = [i.replace('.h5', '') for i in fac_ref[suffix_itr]]
            fac_list = fac_list + fac_list_itr
            if suffix_itr in linear_fac_name_list:
                linear_fac_list = linear_fac_list + fac_list_itr
        print(len(linear_fac_list), len(fac_list), flush=True)
        fac_val = read_ts_fac_helper(path_ever, fac_list=fac_list).fillna(0)
        fac = fac_val[linear_fac_list]
        fac_num = fac_val.shape[1]
        fac_num_linear = len(linear_fac_list)
        fac_num_nl = fac_num - fac_num_linear
        print('total fac:%d | linear:%d | nonlinear:%d' % (fac_num, fac_num_linear, fac_num_nl), flush=True)
        with_desc = True
        vol_adj = False

    elif suffix in ['im_v1unifac_spot']:
        trade_contract = 'IM.CFE'
        use_spec = False
        if use_spec:
            model_list_long = ['et_cla', 'lstm_cla']  #
            model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
            model_list = model_list_long + model_list_short
            hpr_spec_dict = {**{i: short_list for i in model_list_short},
                             **{i: long_list for i in model_list_long}}
            suffix_save = '%s_spec' % (suffix)
        else:
            model_list = ['et_cla', 'lstm_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']
            hpr_spec_dict = {i: long_list for i in model_list}
            suffix_save = '%s_102030' % (suffix)
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])))

        suffix_spec_dict = {'im_v1_if_v7_2': ['IM_linear', 'IF_linear'],
                            'im_v1nl_181_if_v7_2nl_181': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IM_181', 'IF_181'],
                            'im_v1nlad_181ad_if_v7_2nlad_181ad': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']}
        suffix_spec_list = ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']
        linear_fac_name_list = ['IM_linear', 'IF_linear']

        fac_list, linear_fac_list = [], []
        for suffix_itr in suffix_spec_list:
            fac_list_itr = [i.replace('.h5', '') for i in fac_ref[suffix_itr]]
            fac_list = fac_list + fac_list_itr
            if suffix_itr in linear_fac_name_list:
                linear_fac_list = linear_fac_list + fac_list_itr
        print(len(linear_fac_list), len(fac_list), flush=True)
        fac_val = read_ts_fac_helper(path_ever, fac_list=fac_list).fillna(0)
        fac = fac_val[linear_fac_list]
        fac_num = fac_val.shape[1]
        fac_num_linear = len(linear_fac_list)
        fac_num_nl = fac_num - fac_num_linear
        print('total fac:%d | linear:%d | nonlinear:%d' % (fac_num, fac_num_linear, fac_num_nl), flush=True)
        with_desc = True
        vol_adj = False

    print('read factor done', flush=True)
    print('check model flag', flush=True)

    model_flag_list = ['%s_%s' % (suffix, m) for m in model_list]
    comb2_model_num = np.sum([1 if i in model_list else 0 for i in comb2_model_list])
    comb2_model_ind = comb2_model_num > 0

    use_new = True if append_prediction else False
    use_update = False
    dropna = False
    time_step = 30
    print('*** lstm time_step: %s' % (time_step), flush=True)
    min_pct_tail = 0.8
    tail_length = 237

    train_s = '2016'
    ####### path_np

    fts_data_is = read_pickle(fts_path_is)
    fts_data_os = read_pickle(fts_path_os)
    ret_vol_df = get_ret_vol(fts_data_is, fts_data_os)
    vol_use = ret_vol_df[trade_contract]

    fac_path = os.path.join(share_base, '/factor/minute/%s.pkl' % (suffix))
    ##########

    # factor test config
    norm_day = 20
    ts_pct_win = 240 * norm_day
    ts_pct_win2 = 240 * 10
    min_pct = 0.96
    edate_str = update_date
    fee = 1.5
    price_base = 5000
    layers = 4
    # end of parameter
    ####################################
    process_list = None

    ticker_ini = trade_contract.split('.')[0].lower()
    backtest_root = os.path.join(minute_base, '%s' % (suffix_save))
    save_base = os.path.join(minute_base, '%s/res_%s/%s/%s' % (suffix_save, update_date, ticker_ini, filter_date))
    save_path_bkt = os.path.join(minute_base, '%s/%s/%s/%s' % (suffix_save, fac_lib_date, ticker_ini, filter_date))
    save_base_prev = os.path.join(minute_base, '%s/res_%s/%s/%s' % (suffix_save, prev_date, ticker_ini, filter_date))

    ###### 
    # path
    prod_save_path = os.path.join(save_base, 'norm', )
    prod_save_path_nd = os.path.join(save_base, 'norm_nd')
    prod_save_path_scale = os.path.join(save_base, 'scale')
    prod_save_raw_path = os.path.join(save_base, 'raw')
    prev_raw_path = os.path.join(save_base_prev, 'raw')
    save_path_bkt_orig = os.path.join(save_path_bkt, 'orig')
    save_path_bkt_scale = os.path.join(save_path_bkt, 'scale')
    print(prod_save_path, flush=True)
    print(prod_save_path_nd, flush=True)
    print(prod_save_raw_path, flush=True)
    print(update_date, prev_date, flush=True)
    ##############################
    # prediction model config
    model_name_dict = {model: ['%s_%d%s' % (model, h, roll_name) for h in hpr_spec_dict[model]] for model in model_list}

    # backtest config
    if comb2_model_ind:
        scale_list = ['pred_comb', 'pred_comb2']
    else:
        scale_list = ['pred_comb']

    ##############################
    pred_price_future = 'vwap'
    pred_price_spot = 'close'
    sdate_s = 2016

    slice_range = [[930, 1129], [1300, 1456]]
    sdate, edate = str(20111201), str(fac_lib_date) + '235959'
    read_data = False
    update = True

    ##################
    print('read price data', flush=True)
    print('#' * 40, flush=True)
    print('%s: %s - %s - %s' % (trade_contract, sdate, edate, train_s), flush=True)

    dat_minute = IO.read_data([sdate, edate], alt=minute_future_path)
    dat_index_minute = dat_minute.xs(trade_contract, level=1)
    ts_price_minute = dat_index_minute[pred_price_future]
    ts_price_minute = slice_by_minute(ts_price_minute, slice_range)
    ts_price_minute = ts_price_minute.copy().loc[train_s:edate]
    print(ts_price_minute.index[-1], flush=True)
    print('load price data done', flush=True)
    print('#' * 40, flush=True)

    ######### data 

    ########
    fac_list = fac_val.columns.tolist()
    fac_val = fac_val.fillna(0)
    print(fac_val.shape, flush=True)
    fac_val = slice_by_minute(fac_val, slice_range)
    print('check factor', flush=True)
    min_fac_pct = 0.8

    #######################################

    print('create meta factor', flush=True)
    minute_duration = 60
    ts_price_minute = ts_price_minute.loc[train_s:]

    if trade_contract == 'IM.CFE':
        minute_block = get_minute_seg_dt(fac_val, minute_duration)
        calendar_info = get_calendar_info(fac_val)
    else:
        minute_block = get_minute_seg_dt(ts_price_minute, minute_duration)
        calendar_info = get_calendar_info(ts_price_minute)
    time_info = pd.concat([minute_block, calendar_info], axis=1)
    time_dummies = get_dummies_helper(time_info, dummy_na=True)
    time_dummies2 = get_dummies_helper(time_info, dummy_na=False)
    td2_list = list(set(time_dummies2.columns.tolist()) - set(time_dummies.columns.tolist()))
    time_dummies2 = time_dummies2[td2_list]

    x = pd.concat([fac_val, time_dummies, time_dummies2], axis=1)
    x = slice_by_minute(x, slice_range)
    x = x.loc[train_s:]
    x[~np.isfinite(x)] = 0
    print(x.shape, x.index[-1], flush=True)

    print('pred factor data done', flush=True)
    if append_true_pred:
        x_train, x_test = prep_train_test_helper(x, sdate_pred, time_step=None, train_s=train_s, process_list=process_list)
        x_train_ts, x_test_ts = prep_train_test_helper(x, sdate_pred, time_step=time_step, train_s=train_s, process_list=process_list)

    ######################################
    pred_df_all_dict = {}
    pred_df_dict = {}

    model_root_dict = {model: os.path.join(pred_res_base, 'res_%s/%s/model_%s/%s' % (model_date, trade_contract[:2], filter_date, model)) for model in model_list}
    model_path_dict = {model: {} for model in model_list}
    for model in model_list:
        pred_sub_path = os.path.join(pred_res_base, 'res_%s/%s/model_%s/%s' % (model_date, trade_contract[:2], filter_date, model))
        model_path_dict[model] = find_file(pred_sub_path, 'pkl')
        print(pred_sub_path, flush=True)
        print(model_path_dict[model], flush=True)

    print('generate prediction', flush=True)
    if append_true_pred:
        raw_dict_update = {}
        for model in model_list:
            holding_period_list = hpr_spec_dict[model]
            pred_raw_itr_list = []
            for holding_period in holding_period_list:
                itr_name = '%s_%d%s' % (model, holding_period, roll_name)
                pred = 'regression' if itr_name.find('reg') >= 0 else 'classification'
                print(itr_name, pred, flush=True)
                model_path_itr = model_path_dict[model][itr_name]
                print(model_path_itr, flush=True)

                model_dict_itr = read_pickle(model_path_itr)
                if model not in ['lstm_cla', 'lstm_reg']:
                    pred_raw_itr = pred_helper(x_test, model_dict_itr, pred=pred)
                else:
                    pred_raw_itr = pred_helper(x_test_ts, model_dict_itr, pred=pred, check_time=False)

                pred_raw_itr = pd.DataFrame(pred_raw_itr, columns=[itr_name])
                check_tail_helper(pred_raw_itr, tail_length=tail_length, min_pct=min_pct_tail)
                pred_raw_itr_list.append(pred_raw_itr)

            pred_raw_df = pd.concat(pred_raw_itr_list, axis=1)
            raw_dict_update[model] = pred_raw_df

        for model in model_list:
            print(raw_dict_update[model].tail(), flush=True)
    ###########################################
    # append raw

    raw_path_dict = {model: os.path.join(prod_save_raw_path, '%s.pkl' % (model)) for model in model_list}
    raw_path_dict_prev = {model: os.path.join(prev_raw_path, '%s.pkl' % (model)) for model in model_list}

    print(raw_path_dict, flush=True)
    raw_dict_exist = {}
    raw_dict = {}
    raw_dict_exist_last = {}

    for model in model_list:
        print(model, flush=True)
        if append_prediction:
            print('append prediction', flush=True)
            raw_dict_exist[model] = read_pickle(raw_path_dict_prev[model])
            name_list_itr = model_name_dict[model]
            raw_dict_exist[model] = raw_dict_exist[model][name_list_itr]
            if append_true_pred:
                raw_dict_update[model] = raw_dict_update[model][name_list_itr]
            if append_last_train_pred:
                print('append last model train prediction', flush=True)
                holing_period_list = hpr_spec_dict[model]
                pred_raw_itr_list = []
                name_itr_list = []
                for holding_period in holing_period_list:
                    itr_name = '%s_%d%s' % (model, holding_period, roll_name)
                    name_itr_list.append(itr_name)
                    pred = 'regression' if itr_name.find('reg') >= 0 else 'classification'
                    print(itr_name, pred, flush=True)
                    model_path_itr = model_path_dict[model][itr_name]
                    model_dict_itr = read_pickle(model_path_itr)
                    pred_raw_itr = model_dict_itr['prediction']
                    check_tail_helper(pred_raw_itr, tail_length=tail_length, min_pct=min_pct_tail)
                    pred_raw_itr_list.append(pred_raw_itr)
                pred_raw_df = pd.concat(pred_raw_itr_list, axis=1)
                pred_raw_df.columns = name_itr_list
                raw_dict_exist_last[model] = pred_raw_df
                raw_dict_exist[model] = concat_pd_spec(raw_dict_exist[model], raw_dict_exist_last[model], use_update=use_update, dropna=dropna)
                if append_true_pred:
                    raw_dict[model] = concat_pd_spec(raw_dict_exist[model], raw_dict_update[model], use_update=use_update, dropna=dropna)
                else:
                    raw_dict[model] = raw_dict_exist[model]
            else:
                raw_dict[model] = concat_pd_spec(raw_dict_exist[model], raw_dict_update[model], use_update=use_update, dropna=dropna)
        else:
            print('use existing prediction', flush=True)
            holing_period_list = hpr_spec_dict[model]
            pred_raw_itr_list = []
            name_itr_list = []
            for holding_period in holing_period_list:
                itr_name = '%s_%d%s' % (model, holding_period, roll_name)
                name_itr_list.append(itr_name)
                pred = 'regression' if itr_name.find('reg') >= 0 else 'classification'
                print(itr_name, pred, flush=True)
                model_path_itr = model_path_dict[model][itr_name]
                model_dict_itr = read_pickle(model_path_itr)
                pred_raw_itr = model_dict_itr['prediction']

                check_tail_helper(pred_raw_itr, tail_length=tail_length, min_pct=min_pct_tail)
                pred_raw_itr_list.append(pred_raw_itr)
            pred_raw_df = pd.concat(pred_raw_itr_list, axis=1)
            pred_raw_df.columns = name_itr_list
            raw_dict_exist[model] = pred_raw_df
            raw_dict[model] = raw_dict_exist[model]
            if model in model_list_extra:
                print('note: slice %s by %s' % (model, str(slice_range_extra)), flush=True)
                dt_list_orig = raw_dict[model].index.tolist()
                raw_dict[model] = slice_by_minute(raw_dict[model], slice_range_extra).reindex(index=dt_list_orig)

        save_pickle(raw_dict[model], raw_path_dict[model])

    #######################################################
    pred_res_base_root = os.path.join(pred_res_base, 'res_%s/%s/model_%s' % (model_date, trade_contract[:2], filter_date))
    val_df_src = get_all_pred_helper(pred_res_base_root)
    val_df_des = read_all_pickle_helper(prod_save_raw_path)
    val_diff_sum = (val_df_src - val_df_des).abs().sum()
    if val_diff_sum.sum() > 1e-6:
        print('raw value check wrong !!!', flush=True)
        print(val_diff_sum.sort_values(), flush=True)
    else:
        print('check raw passed !!!', flush=True)
    #######################################################

    print('%s - Form Model Prediction %s' % ('#' * 10, '#' * 10), flush=True)
    collect_dict = {}
    factor_name = 'ew'
    print('calcing %s' % (factor_name), flush=True)
    pred_df_ew_raw = fac.mean(axis=1)
    pred_df_ew = calc_ts_pct(pred_df_ew_raw, ts_pct_win, min_pct=min_pct).loc[:edate]
    ew_norm_hpr = prep_ps2df_save(pred_df_ew, factor_name, save_path=prod_save_path_nd, min_pct=min_pct_tail)
    collect_dict.update({factor_name: ew_norm_hpr})
    print('done with %s' % (factor_name), flush=True)

    print('getting normlized prediction for sub model', flush=True)
    pred_norm_dict = {}
    for model in model_list:
        print('*' * 30, flush=True)
        print(model, flush=True)
        pred_df = raw_dict[model]
        take_list = pred_df.columns
        if model in model_list_extra:
            print('note: slice %s by %s' % (model, str(slice_range_extra)), flush=True)
            dt_list_orig = pred_df.index.tolist()
            pred_df = slice_by_minute(pred_df, slice_range_extra).reindex(index=dt_list_orig)
        pred_norm = {}
        for factor_name in take_list:
            print(factor_name, flush=True)
            pred_norm[factor_name] = calc_ts_pct(pred_df[factor_name], ts_pct_win, min_pct=min_pct)
            pred_norm_df = pd.DataFrame(pred_norm)
            pred_norm_df.index.name = 'dt'
            check_tail_helper(pred_norm_df, tail_length=tail_length, min_pct=min_pct_tail)
        pred_norm_df = pred_norm_df.loc[:edate_str]
        pred_norm_dict[model] = pred_norm_df
        print('*' * 30, flush=True)

    pred_hpr_raw_list = []
    for model in model_list:
        print(model, flush=True)
        factor_name = model
        use_list_spec = ['%s_%d%s' % (model, h, roll_name) for h in hpr_spec_dict[model]]
        hpr_raw = pred_norm_dict[model][use_list_spec].mean(axis=1)
        hpr_norm = prep_ps2df_save(hpr_raw, factor_name, save_path=prod_save_path_nd, min_pct=min_pct_tail)
        check_tail_helper(hpr_norm, tail_length=tail_length, min_pct=min_pct_tail)
        collect_dict.update({factor_name: hpr_norm})
        pred_hpr_raw_list.append(hpr_norm)
    pred_hpr_raw_nd = pd.concat(pred_hpr_raw_list, axis=1)

    ##############

    factor_name = 'pred_comb'
    comb1_list = list(set(model_list) - set(comb2_model_list))
    print(comb1_list, flush=True)
    if len(comb1_list) > 0:
        pred_comb_df = pred_hpr_raw_nd[comb1_list]
        pred_comb_raw = pred_comb_df.mean(axis=1)
        pred_comb = calc_ts_pct(pred_comb_raw, ts_pct_win2, min_pct=min_pct).dropna()
        pred_comb = prep_ps2df_save(pred_comb, factor_name, save_path=prod_save_path_nd, min_pct=min_pct_tail)
        collect_dict.update({factor_name: pred_comb})

    if comb2_model_ind:
        factor_name = 'pred_comb2'
        comb2_list = list(set(comb1_list + comb2_model_list))
        comb2_list = [i for i in comb2_list if i in model_list]
        print(comb2_list, flush=True)
        pred_comb_raw2 = pred_hpr_raw_nd[comb2_list].mean(axis=1)
        pred_comb2 = calc_ts_pct(pred_comb_raw2, ts_pct_win2, min_pct=min_pct)
        pred_comb2 = prep_ps2df_save(pred_comb2, factor_name, save_path=prod_save_path_nd, min_pct=min_pct_tail)
        collect_dict.update({factor_name: pred_comb2})

    ###############

    print('get predction score scaled scale', flush=True)
    collect_df = read_ts_fac_helper(prod_save_path_nd).loc[:edate]
    collect_df.index.names = ['dt']
    collect_dict = {i: collect_df[[i]] for i in collect_df}
    collect_dict_scale = {}
    for scale_name in scale_list:
        if scale_name in collect_dict:
            print(scale_name, flush=True)
            sig_scale = collect_dict[scale_name] * 2 - 1
            if vol_adj:
                sig_scale = sig_scale.multiply(vol_use, axis=0)
            else:
                print('skip scale', flush=True)
            sig_scale.index.name = 'dt'
            factor_name = scale_name + '_scale'
            sig_scale = sig_scale.loc[:edate]
            check_tail_helper(sig_scale, tail_length=tail_length, min_pct=min_pct_tail)
            sig_scale = prep_ps2df_save(sig_scale, factor_name, save_path=prod_save_path_scale, min_pct=min_pct_tail)
            collect_dict_scale[factor_name] = sig_scale

    print('all done', flush=True)
