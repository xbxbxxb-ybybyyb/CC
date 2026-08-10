import sys

sys.path.insert(0, '/data/user/015626/data/Code/git_space/model_all/mobius_model/myzz_prod/')

import os
import time
import pickle
import datetime
import warnings
import traceback
import numpy as np
import pandas as pd
import bottleneck as bk
from bisect import bisect_left
from functools import partial
from sklearn.preprocessing import StandardScaler
from keras.models import load_model
from multiprocessing import Pool

from multifactor.data.utils import get_current_date
from multifactor.utility.dt import get_trading_date_range
from xquant.xqutils.helper import link


def main():
    YMD = '%Y%m%d'
    YMD_HMS = '%Y-%m-%d %H:%M:%S'
    curr_date = str(get_current_date(new_date_time=18))

    now = datetime.datetime.now().strftime(YMD_HMS)
    print(f'[{now}] Check flags', flush=True)
    counter = 0
    while True:
        if check_flags(curr_date):
            break
        elif counter < 60 * 24:
            time.sleep(60)
            counter += 1
        else:
            raise RuntimeError('Timeout')
    now = datetime.datetime.now().strftime(YMD_HMS)
    print(f'[{now}] Flags ready', flush=True)

    # ****************************************************************************************************

    model_date = '20250328'
    start_date = (pd.Timestamp(model_date) + pd.Timedelta(days=1)).strftime(YMD)
    trade_date_list = get_trading_date_range(start_date=start_date, end_date=curr_date)
    trade_date_list = [x.strftime(YMD) for x in trade_date_list]
    # init_model_norm = True

    # used for daily update
    ##########
    trade_date_list = trade_date_list[-3:]
    init_model_norm = False
    ##########

    # dat_root = '/data/group/800466/warehouse/prod'
    dat_root = '/data/user/015626/model/mobius_prod_zz'

    version_list = ['if_v7c_fs', 'ic_v7unifac_fs', 'im_v1unifac_fs']
    model_date_dict = {
        'if_v7c': '20250328_if_if_v7c',
        'ic_v7unifac': '20250328_ic_ic_v7unifac',
        'im_v1unifac': '20250328_im_im_v1unifac',

        'if_v7c_fs': '20250328_if_if_v7c_fs',
        'ic_v7unifac_fs': '20250328_ic_ic_v7unifac_fs',
        'im_v1unifac_fs': '20250328_im_im_v1unifac_fs',
    }
    ts_pct_win_dict = {
        'if_v7c': 20 * 240,
        'ic_v7unifac': 20 * 240,
        'im_v1unifac': 20 * 240,

        'if_v7c_fs': 20 * 240,
        'ic_v7unifac_fs': 20 * 240,
        'im_v1unifac_fs': 20 * 240,
    }
    ts_pct_win_dict2 = {
        'if_v7c': 10 * 240,
        'ic_v7unifac': 10 * 240,
        'im_v1unifac': 10 * 240,

        'if_v7c_fs': 10 * 240,
        'ic_v7unifac_fs': 10 * 240,
        'im_v1unifac_fs': 10 * 240,
    }
    short_list = [1, 5, 10]
    long_list = [10, 20, 30]
    hpr_spec_dict_all = {
        'if_v7c': {**{i: short_list for i in ['lgbm_cla', 'lgbm_reg', 'mlp_reg']}, **{i: long_list for i in ['et_cla', 'lstm_cla']}},
        'ic_v7unifac': {**{i: short_list for i in ['lgbm_cla', 'lgbm_reg', 'mlp_reg']}, **{i: long_list for i in ['et_cla', 'lstm_cla']}},
        'im_v1unifac': {**{i: short_list for i in ['lgbm_cla', 'lgbm_reg', 'mlp_reg']}, **{i: long_list for i in ['et_cla', 'lstm_cla']}},

        'if_v7c_fs': {**{i: short_list for i in ['lgbm_cla_future', 'lgbm_reg_future', 'mlp_reg_future']},
                      **{i: long_list for i in ['et_cla_future', 'lstm_cla_future', 'et_cla_spot', 'lstm_cla_spot', 'lgbm_cla_spot', 'lgbm_reg_spot', 'mlp_reg_spot']}},
        'ic_v7unifac_fs': {**{i: short_list for i in ['lgbm_cla_future', 'lgbm_reg_future', 'mlp_reg_future']},
                           **{i: long_list for i in ['et_cla_future', 'lstm_cla_future', 'et_cla_spot', 'lstm_cla_spot', 'lgbm_cla_spot', 'lgbm_reg_spot', 'mlp_reg_spot']}},
        'im_v1unifac_fs': {**{i: short_list for i in ['lgbm_cla_future', 'lgbm_reg_future', 'mlp_reg_future']},
                           **{i: long_list for i in ['et_cla_future', 'lstm_cla_future', 'et_cla_spot', 'lstm_cla_spot', 'lgbm_cla_spot', 'lgbm_reg_spot', 'mlp_reg_spot']}},
    }
    fac_path_dict = {
        'if_v7c': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7_2/minute_norm',
        'ic_v7unifac': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_prod_v7_2/minute_norm',
        'im_v1unifac': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IM_factors/minute_norm',

        'if_v7c_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7_2/minute_norm',
        'ic_v7unifac_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_prod_v7_2/minute_norm',
        'im_v1unifac_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IM_factors/minute_norm',
    }
    fac_desc_raw_path_dict = {
        'if_v7c': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm',
        'ic_v7unifac': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_diff_zscore/minute_norm',
        'im_v1unifac': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IM_nonlinear_diff_zscore/minute_norm',

        'if_v7c_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm',
        'ic_v7unifac_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_diff_zscore/minute_norm',
        'im_v1unifac_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IM_nonlinear_diff_zscore/minute_norm',
    }
    fac_desc_norm_path_dict = {
        'if_v7c': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm',
        'ic_v7unifac': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_zscore/minute_norm',
        'im_v1unifac': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IM_nonlinear_zscore/minute_norm',

        'if_v7c_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm',
        'ic_v7unifac_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_zscore/minute_norm',
        'im_v1unifac_fs': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IM_nonlinear_zscore/minute_norm',
    }
    with_desc_dict = {
        'if_v7c': True,
        'ic_v7unifac': True,
        'im_v1unifac': True,

        'if_v7c_fs': True,
        'ic_v7unifac_fs': True,
        'im_v1unifac_fs': True,
    }
    with_desc_norm_dict = {
        'if_v7c': True,
        'ic_v7unifac': True,
        'im_v1unifac': True,

        'if_v7c_fs': True,
        'ic_v7unifac_fs': True,
        'im_v1unifac_fs': True,
    }
    time_step_dict = {
        'if_v7c': 10,
        'ic_v7unifac': 10,
        'im_v1unifac': 10,

        'if_v7c_fs': 10,
        'ic_v7unifac_fs': 10,
        'im_v1unifac_fs': 10,
    }
    fac_add_path_dict = {
        'if_v7c': ['/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm/',
                   '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm/'],
        'ic_v7unifac': ['/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7_2/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm/'],
        'im_v1unifac': ['/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7_2/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm/',
                        '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm/'],

        'if_v7c_fs': ['/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm/',
                      '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm/'],
        'ic_v7unifac_fs': ['/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7_2/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm/'],
        'im_v1unifac_fs': ['/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7_2/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm/',
                           '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm/'],
    }
    roll_name_dict = {
        'if_v7c': '_r720',
        'ic_v7unifac': '_r720',
        'im_v1unifac': '_r720',

        'if_v7c_fs': '_r720',
        'ic_v7unifac_fs': '_r720',
        'im_v1unifac_fs': '_r720',
    }

    model_list_rnn = ['lstm_cla_future', 'lstm_reg_future', 'lstm_cla_spot', 'lstm_reg_spot']
    model_list_extra = ['rff_cla', 'rfe_cla']

    index_root_dict = {
        'IH': '/data/user/015626/model/mobius_prod/model_update/rank_index/ih_60000_25_75',
        'IF': '/data/user/015626/model/mobius_prod/model_update/rank_index/if_60000_25_75',
        'IC': '/data/user/015626/model/mobius_prod/model_update/rank_index/ic_60000_25_75',
        'IM': '/data/user/015626/model/mobius_prod/model_update/rank_index/im_60000_25_75',
    }

    min_pct = 0.96
    use_update = True
    dropna = True
    return_itr = True
    check_time = False
    train_s = '2016'
    process_list = None
    slice_range_extra = [[931, 1129], [1300, 1456]]

    # ****************************************************************************************************

    if init_model_norm:
        print('initialize model_norm', flush=True)
        for version in version_list:
            print(version, model_date, flush=True)
            strategy = model_date_dict[version]

            work_space = os.path.join(dat_root, 'model_update/%s' % str(strategy))
            model_name_list = []
            for file_name in os.listdir(os.path.join(work_space, 'model_value', 'model_raw', model_date)):
                name, ext = os.path.splitext(file_name)
                model_name_list.append(name)
            model_name_list.sort()
            print(model_name_list, flush=True)

            for model_name in model_name_list:
                # model_norm
                signal_path = os.path.join(work_space, 'model_value', 'model_raw', model_date, f'{model_name}.pkl')
                signal_raw = pd.read_pickle(signal_path)
                signal_all = calc_ts_pct(signal_raw, ts_pct_win_dict[version], min_pct=min_pct)
                signal_avg = signal_all.mean(axis=1)
                signal_norm = signal_avg.to_frame(name=model_name)
                output_path = os.path.join(work_space, 'model_value', 'model_norm', model_date, f'{model_name}.pkl')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                save_pickle(signal_norm, output_path)

                # model_norm2
                index_root = index_root_dict[strategy.split('_')[1].upper()]
                signal_list = []
                signal_date_list = pd.to_datetime(signal_raw.index.date).drop_duplicates().strftime('%Y%m%d').to_list()
                for signal_date in signal_date_list:
                    signal_temp = signal_raw[signal_date]
                    signal_norm = pd.DataFrame(np.full(signal_temp.shape, np.nan), index=signal_temp.index, columns=signal_temp.columns)
                    index_path = os.path.join(index_root, f'{signal_date}.pkl')
                    index_list = load_pickle(index_path)
                    index_diff = pd.to_datetime(index_list).difference(signal_raw.index)
                    if len(index_diff) > 0:
                        fmt = '%Y-%m-%d'
                        # print(f'[{signal_date}] miss historical value: {len(index_diff)} points, from {index_diff[0].strftime(fmt)} to {index_diff[-1].strftime(fmt)}')
                    else:
                        signal_base = signal_raw[signal_raw.index.isin(index_list)]
                        for col in signal_raw.columns:
                            a = np.sort(signal_base[col].values)
                            signal_norm[col] = [bisect_left(a, x) for x in signal_temp[col].values]
                        signal_norm = signal_norm.div(len(signal_base)).mul(2).sub(1)
                    signal_list.append(signal_norm)
                signal_all = pd.concat(signal_list, axis=0)
                signal_avg = signal_all.mean(axis=1)
                signal_norm = signal_avg.to_frame(name=model_name)
                output_path = os.path.join(work_space, 'model_value', 'model_norm2', model_date, f'{model_name}.pkl')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                save_pickle(signal_norm, output_path)
            print('-' * 50, flush=True)

    # ****************************************************************************************************

    print('update model_value', flush=True)
    for version in version_list:
        print(version, flush=True)
        model_date = model_date_dict[version]
        ts_pct_win = ts_pct_win_dict[version]
        ts_pct_win2 = ts_pct_win_dict2[version]
        hpr_spec_dict = hpr_spec_dict_all[version]
        fac_path = fac_path_dict[version]
        fac_desc_path = fac_desc_raw_path_dict[version]
        fac_desc_norm_path = fac_desc_norm_path_dict[version]
        with_desc = with_desc_dict[version]
        with_desc_norm = with_desc_norm_dict[version]
        time_step = time_step_dict[version]
        roll_name = roll_name_dict[version]

        model_list = list(hpr_spec_dict.keys())
        print(model_list, flush=True)

        # model_root = os.path.join(dat_root, 'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_file/' % str(model_date_use))
        # pred_raw_root = os.path.join(dat_root, 'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw' % str(model_date_use))
        # pred_raw_itr_root = os.path.join(dat_root, 'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw_itr' % str(model_date_use))
        # pred_norm_root = os.path.join(dat_root, 'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_norm' % str(model_date_use))

        model_root = os.path.join(dat_root, 'model_update/%s/model_file/' % str(model_date))
        pred_raw_root = os.path.join(dat_root, 'model_update/%s/model_value/model_raw' % str(model_date))
        pred_raw_itr_root = os.path.join(dat_root, 'model_update/%s/model_value/model_raw_itr' % str(model_date))
        pred_norm_root = os.path.join(dat_root, 'model_update/%s/model_value/model_norm' % str(model_date))

        # read factors
        fac_val_list = []
        print('read factors', flush=True)
        fac = read_ts_fac_helper(fac_path)
        fac_val_list.append(fac)
        if with_desc:
            fac_desc = read_ts_fac_helper(fac_desc_path)
            fac_val_list.append(fac_desc)
        if with_desc_norm:
            fac_desc_norm = read_ts_fac_helper(fac_desc_norm_path)
            fac_val_list.append(fac_desc_norm)
        dummy_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm'
        dummy = read_ts_fac_helper(dummy_path)
        dummy2 = dummy.copy()
        dummy2.columns = [i + '.0' for i in dummy.columns]
        dummy_use = pd.concat([dummy, dummy2], axis=1)
        fac_val_list.append(dummy_use)
        if version in fac_add_path_dict:
            for path_itr in fac_add_path_dict[version]:
                fac_itr = read_ts_fac_helper(path_itr)
                fac_val_list.append(fac_itr)

        for edate in trade_date_list:
            print(edate, flush=True)
            x_test = pd.concat(fac_val_list, axis=1).loc[:edate].fillna(0)
            dt_list = list(set(x_test.index.date))
            dt_list = [datetime.datetime.strftime(i, '%Y%m%d') for i in dt_list]
            dt_list.sort()
            edate_prev = dt_list[dt_list.index(edate) - 1]

            sdate_pred = edate
            x_train, x_test_itr = prep_train_test_helper(x_test, sdate_pred, time_step=None, train_s=train_s, process_list=process_list)
            x_train_ts, x_test_itr_ts = prep_train_test_helper(x_test, sdate_pred, time_step=time_step, train_s=train_s, process_list=process_list)

            raw_path_dict_prev = {model: os.path.join(pred_raw_root, str(edate_prev), '%s.pkl' % (model)) for model in model_list}
            raw_path_dict = {model: os.path.join(pred_raw_root, edate, '%s.pkl' % (model)) for model in model_list}
            norm_path_dict = {model: os.path.join(pred_norm_root, edate, '%s.pkl' % (model)) for model in model_list}
            raw_dict_update = {}

            # def mmodel(model):
            #     holding_period_list = hpr_spec_dict[model]
            #     raw_list = []
            #     for holding_period in holding_period_list:
            #         pa_path = os.path.join(model_root, model, '%s_%d%s.pkl' % (model, holding_period, roll_name))
            #         model_dict = read_pickle(pa_path)
            #         raw_itr_path = os.path.join(pred_raw_itr_root, edate, '%s_%d.pkl' % (model, holding_period))
            #         pred = 'regression' if model.find('reg') >= 0 else 'classification'
            #         if model in model_list_rnn:
            #             x_test_input = x_test_itr_ts
            #         else:
            #             x_test_input = x_test_itr
            #         pred_raw_itr, pred_res_itr_df = pred_helper(x_test_input, model_dict, pred=pred, check_time=check_time, return_itr=return_itr)
            #         raw_list.append(pred_raw_itr)
            #         save_pickle(pred_res_itr_df, raw_itr_path)
            #     raw_df_itr = pd.concat(raw_list, axis=1)
            #     raw_df_itr.columns = ['%s_%d' % (model, i) for i in holding_period_list]
            #     raw_dict_update[model] = raw_df_itr
            #     return [model, raw_df_itr]

            with Pool(24) as pool:
                # raw_dict_update1 = pool.map(mmodel, model_list)
                mmodel_wrapper = partial(mmodel,
                                         hpr_spec_dict=hpr_spec_dict,
                                         model_root=model_root,
                                         roll_name=roll_name,
                                         pred_raw_itr_root=pred_raw_itr_root,
                                         edate=edate,
                                         model_list_rnn=model_list_rnn,
                                         x_test_itr_ts=x_test_itr_ts,
                                         x_test_itr=x_test_itr,
                                         check_time=check_time,
                                         return_itr=return_itr,
                                         raw_dict_update=raw_dict_update)
                raw_dict_update1 = pool.map(mmodel_wrapper, model_list)
            for item in raw_dict_update1:
                raw_dict_update[item[0]] = item[1]

            # １.　拼接最新预测值与过去的预测值
            raw_dict_exist = {}
            raw_dict = {}

            # 每个模型的名字列表 比如 lasso_reg_10 (laso_reg针对10分钟的预测)
            model_name_dict = {model: ['%s_%d' % (model, h) for h in hpr_spec_dict[model]] for model in model_list}
            print('1. append prediction', flush=True)
            for model in model_list:
                raw_dict_exist[model] = read_pickle(raw_path_dict_prev[model])
                name_list_itr = model_name_dict[model]
                raw_dict_exist[model] = raw_dict_exist[model][name_list_itr]
                raw_dict_update[model] = raw_dict_update[model][name_list_itr]
                if model in model_list_extra:
                    raw_dict[model] = concat_pd_spec(raw_dict_exist[model], raw_dict_update[model], use_update=use_update, dropna=dropna, spec=True)
                else:
                    raw_dict[model] = concat_pd_spec(raw_dict_exist[model], raw_dict_update[model], use_update=use_update, dropna=dropna)
                save_pickle(raw_dict[model], raw_path_dict[model])

            # ２. 针对每个模型，每个持仓周期预测原始值进行标准化
            print('2. getting normlized prediction for sub model', flush=True)
            pred_norm_dict = {}
            for model in model_list:
                pred_df = raw_dict[model]
                take_list = pred_df.columns
                if model in model_list_extra:
                    dt_list_orig = pred_df.index.tolist()
                    pred_df = slice_by_minute(pred_df, slice_range_extra).reindex(index=dt_list_orig)
                pred_norm = {}
                for factor_name in take_list:
                    pred_norm[factor_name] = calc_ts_pct(pred_df[factor_name], ts_pct_win, min_pct=min_pct)
                pred_norm_df = pd.DataFrame(pred_norm)
                pred_norm_df.index.name = 'dt'
                pred_norm_dict[model] = pred_norm_df

            # ３. 将所有标准化后的模型预测，5个模型分别3个预测周期，总共15个预测值进行平均，再做一次标准化得到pred_comb为最终结果
            print('3. stack all prediction', flush=True)
            pred_hpr_raw_list = []
            for model in model_list:
                # print(model, flush=True)
                use_list_spec = ['%s_%d' % (model, h) for h in hpr_spec_dict[model]]
                hpr_raw = pred_norm_dict[model][use_list_spec].mean(axis=1)
                hpr_raw = pd.DataFrame(hpr_raw, columns=[model])
                pred_hpr_raw_list.append(hpr_raw)
                save_pickle(hpr_raw, norm_path_dict[model])

            pred_hpr_raw = pd.concat(pred_hpr_raw_list, axis=1)

            factor_name = 'pred_comb'
            norm_path_dict[factor_name] = os.path.join(pred_norm_root, edate, '%s.pkl' % (factor_name))
            pred_comb_raw = pred_hpr_raw.mean(axis=1)
            pred_comb = calc_ts_pct(pred_comb_raw, ts_pct_win2, min_pct=min_pct)
            save_pickle(pred_comb, norm_path_dict[factor_name])

            factor_name = 'pred_comb2'
            norm_path_dict[factor_name] = os.path.join(pred_norm_root, edate, '%s.pkl' % (factor_name))
            pred_comb_raw2 = pred_hpr_raw.mean(axis=1)
            pred_comb2 = calc_ts_pct(pred_comb_raw2, ts_pct_win2, min_pct=min_pct)
            save_pickle(pred_comb2, norm_path_dict[factor_name])

            # update model_norm2
            print('generate norm2', flush=True)
            strategy = model_date_dict[version]
            work_space = os.path.join(dat_root, 'model_update/%s' % str(strategy))
            update_date = edate
            index_root = index_root_dict[strategy.split('_')[1].upper()]
            update_model_norm2(work_space, update_date, index_root)
        print('-' * 50, flush=True)
    return None


def check_flags(date):
    flag1 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/if_factors.success')
    flag2 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/ic_factors.success')
    flag3 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/im_factors.success')
    flag4 = os.path.exists(f'/data/user/015626/model/flag/{date}/rank_index.success')
    ready = flag1 and flag2 and flag3 and flag4
    return ready


def mmodel(model, hpr_spec_dict, model_root, roll_name, pred_raw_itr_root, edate, model_list_rnn, x_test_itr_ts, x_test_itr, check_time, return_itr, raw_dict_update):
    holding_period_list = hpr_spec_dict[model]
    raw_list = []
    for holding_period in holding_period_list:
        pa_path = os.path.join(model_root, model, '%s_%d%s.pkl' % (model, holding_period, roll_name))
        model_dict = read_pickle(pa_path)
        raw_itr_path = os.path.join(pred_raw_itr_root, edate, '%s_%d.pkl' % (model, holding_period))
        pred = 'regression' if model.find('reg') >= 0 else 'classification'
        if model in model_list_rnn:
            x_test_input = x_test_itr_ts
        else:
            x_test_input = x_test_itr
        pred_raw_itr, pred_res_itr_df = pred_helper(x_test_input, model_dict, pred=pred, check_time=check_time, return_itr=return_itr)
        raw_list.append(pred_raw_itr)
        save_pickle(pred_res_itr_df, raw_itr_path)
    raw_df_itr = pd.concat(raw_list, axis=1)
    raw_df_itr.columns = ['%s_%d' % (model, i) for i in holding_period_list]
    raw_dict_update[model] = raw_df_itr
    return [model, raw_df_itr]


def concat_pd_spec(exist_df, update_df, use_update=False, dropna=True, spec=False):
    if spec == True:
        exist_df[(exist_df.index.hour == 9) & (exist_df.index.minute == 30)] = 9999
        update_df[(update_df.index.hour == 9) & (update_df.index.minute == 30)] = 9999
    if dropna:
        update_df = update_df.dropna()
        exist_df = exist_df.dropna()
    if spec == True:
        exist_df[(exist_df.index.hour == 9) & (exist_df.index.minute == 30)] = np.nan
        update_df[(update_df.index.hour == 9) & (update_df.index.minute == 30)] = np.nan
    if isinstance(use_update, bool):
        if use_update:
            new_index = update_df.index[0]
            update_df_slice = update_df
            exist_df_slice = exist_df.loc[:new_index]
            if new_index in exist_df_slice.index:
                exist_df_slice = exist_df_slice.iloc[:-1]
        else:
            new_index = exist_df.index[-1]
            exist_df_slice = exist_df
            update_df_slice = update_df.loc[new_index:]
            if new_index in update_df_slice.index:
                update_df_slice = update_df_slice.iloc[1:]
    else:
        exist_df_slice = exist_df.loc[:use_update]
        new_index = exist_df_slice.index[-1]
        update_df_slice = update_df.loc[new_index:]
    if len(exist_df_slice) > 0:
        sdate_exist, edate_exist = exist_df_slice.index[0], exist_df_slice.index[-1]
    else:
        sdate_exist, edate_exist = '', ''
    if len(update_df_slice) > 0:
        sdate_update, edate_update = update_df_slice.index[0], update_df_slice.index[-1]
    else:
        sdate_update, edate_update = '', ''
    print('ConcatPD: use_update:%s dropna:%s |exists:%s ~ %s | update: %s ~ %s' % (use_update, dropna, sdate_exist, edate_exist, sdate_update, edate_update))
    pred_cat_df = pd.concat([exist_df_slice, update_df_slice], axis=0)
    return pred_cat_df


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=True):
    min_win = max(int(min_pct * roll_win), 1)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def read_pickle(save_path=None):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict


def save_pickle(save_dict, save_path):
    print('saving data to:\n', save_path, flush=True)
    folder = os.path.dirname(save_path)
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            pass
    if os.path.exists(save_path):
        try:
            print('remove existing one', flush=True)
            os.remove(save_path)
        except:
            pass
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict, input, protocol=pickle.HIGHEST_PROTOCOL)
    return


def find_file(root_path, suffix='h5', file_name_only=False):
    factor_path_dict = {}
    for path, subdirs, files in os.walk(root_path):
        for name in files:
            if suffix in name:
                fac_name = name[:-len(suffix) - 1]
                factor_path_dict[fac_name] = os.path.join(path, name)
    if file_name_only:
        factor_path_dict = {fac: os.path.basename(fac).replace('.%s' % (suffix), '') for fac in factor_path_dict}
        factor_path_dict = list(factor_path_dict.values())
    return factor_path_dict


def read_ts_fac_helper(fac_base, xs_name=None):
    fac_path_dict = find_file(fac_base, 'h5')
    fac_val_list = []
    fac_name_list = []
    for fac_name in fac_path_dict:
        fac_itr = pd.read_hdf(fac_path_dict[fac_name])
        if xs_name is not None:
            fac_itr = fac_itr.xs(xs_name, level=1)
        if isinstance(fac_itr, pd.DataFrame):
            if 'norm' in fac_itr.columns:
                fac_itr = fac_itr['norm']
        fac_val_list.append(fac_itr)
        fac_name_list.append(fac_name)
    fac_val = pd.concat(fac_val_list, axis=1)
    fac_val.columns = fac_name_list
    print(fac_val.shape)
    return fac_val


# fixd on 20221220 ~ 1. support onnx format 2. support address change for h5/onnx if pass in res_base_path
def pred_helper(x_test, model_dict, pred='regression', check_time=True, return_itr=False):
    # accept lstm with time_step  / keras model ~ mlp
    sdt_pred = x_test.index[0]
    ts_list = list(model_dict['model'].keys())
    ts_list.sort()
    ts_take = ts_list[-1]
    if check_time:
        if sdt_pred < ts_take:
            print('Raise Error: modeled trained in future time')
            print('model: %s / pred: %s' % (str(ts_take), str(sdt_pred)))
            raise Exception

    model_fold = model_dict['model'][ts_take]
    if 'feature_importance' in model_dict:
        fi_fold = model_dict['feature_importance'][ts_take]
    else:
        fi_fold = x_test.columns.tolist()
    pred_shape = x_test.shape[0]
    fold_list = list(model_fold.keys())
    fold_num = len(fold_list)
    print('use model trained on %s with %d fold' % (ts_take, fold_num))
    pred_res_itr_list = []
    for fold_itr in fold_list:
        fi_fold_itr = fi_fold[fold_itr]
        fi_fold_itr_list = fi_fold_itr.index.tolist()
        x_test_fold = x_test[fi_fold_itr_list]
        model_fold_itr = model_fold[fold_itr]
        if isinstance(model_fold_itr, str):
            model_fold_itr = load_model(model_fold_itr)
            model_config = model_fold_itr.get_config()[0]
            if model_config['class_name'] == 'LSTM':  # solve for lstm 3d data, pred return np.array
                time_step = model_config['config']['batch_input_shape'][1]
                pred_idx = len(x_test_fold) - time_step + 1
                pred_index = x_test_fold.iloc[-pred_idx:].index
                pred_shape = len(pred_index)
                x_test_fold = transform_2d_3d_helpher(x_test_fold.values, None, time_step)
        pred_res_itr = pred_template(x=x_test_fold, model=model_fold_itr, pred=pred)
        if isinstance(pred_res_itr, np.ndarray):
            pred_res_itr = pd.Series(pred_res_itr.flatten(), index=pred_index)
        pred_res_itr_list.append(pred_res_itr)
    print('pred shape: %d' % (pred_shape))
    pred_res_itr_df = pd.concat(pred_res_itr_list, axis=1)
    pred_res_itr_df.columns = fold_list
    pred_res = pred_res_itr_df.mean(axis=1)
    if return_itr:
        return pred_res, pred_res_itr_df
    else:
        return pred_res


def pred_template(x, model, pred='regression', best_iteration=False):
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x_type = 'pd'
        x_np = x.values
    else:
        x_type = 'np'
        x_np = x
    if pred == 'regression':
        # if 'predict' in model_fold_itr.__dir__():
        y_mat = model.predict(x_np)
    else:
        if len(x_np.shape) > 2:
            y_mat = model.predict_proba(x_np).flatten()
        else:
            if best_iteration:
                y_mat = model.predict_proba(x_np, ntree_limit=model.best_iteration)[:, 1]
            else:
                y_mat_temp = model.predict_proba(x_np)
                if np.shape(y_mat_temp)[1] > 2:
                    y_mat = y_mat_temp[:, -1] - y_mat_temp[:, 0]
                else:
                    y_mat = y_mat_temp[:, 1]

    if x_type == 'pd':
        y = pd.Series(y_mat.flatten(), index=x.index)
    else:
        y = y_mat
    return y


####20211201##### add mlp/lstm prediction fucntion
# support slice data by time_step 
def process_dat_wrapper_inner(x_train, x_test=None, x_val=None, process_func=StandardScaler()):
    """
    process_func: MinMaxScaler / StandardScaler / QuantileTransformer
    """
    scaler = process_func
    scaler.fit(x_train)
    # print(scaler.mean_)
    x_train_norm_np = scaler.transform(x_train)
    x_train_norm = place_back_format(x_train_norm_np, x_train)
    res_dict = {}
    res_dict['train'] = x_train_norm
    res_dict['scaler'] = scaler
    if x_test is not None:
        x_test_norm_np = scaler.transform(x_test)
        x_test_norm = place_back_format(x_test_norm_np, x_test)
        res_dict['test'] = x_test_norm
    if x_val is not None:
        x_val_norm_np = scaler.transform(x_val)
        x_val_norm = place_back_format(x_val_norm_np, x_val)
        res_dict['val'] = x_val_norm
    return res_dict


def process_dat_wrapper(x_train, x_test=None, x_val=None, process_func=StandardScaler(), process_col_list=None):
    col_list = x_train.columns.tolist()
    if process_col_list is None:
        res_dict = process_dat_wrapper_inner(x_train=x_train, x_test=x_test, x_val=x_val, process_func=StandardScaler())
    else:
        left_col_list = [i for i in x_train.columns if i not in process_col_list]
        x_train_process = x_train[process_col_list]
        x_train_left = x_train[left_col_list]
        if x_test is None:
            x_test_process = None
        else:
            x_test_process = x_test[process_col_list]
            x_test_left = x_test[left_col_list]
        if x_val is None:
            x_val_process = None
        else:
            x_val_process = x_val[process_col_list]
            x_val_left = x_val[left_col_list]
        rdp = process_dat_wrapper_inner(x_train=x_train_process,
                                        x_test=x_test_process,
                                        x_val=x_val_process, process_func=process_func)
        res_dict = {}
        res_dict['train'] = pd.concat([rdp['train'], x_train_left], axis=1)
        res_dict['train'] = res_dict['train'][col_list]
        if x_test is None:
            res_dict['test'] = None
        else:
            res_dict['test'] = pd.concat([rdp['test'], x_test_left], axis=1)
            res_dict['test'] = res_dict['test'][col_list]
        if x_val is None:
            res_dict['val'] = None
        else:
            res_dict['val'] = pd.concat([rdp['val'], x_val_left], axis=1)
            res_dict['val'] = res_dict['val'][col_list]
    return res_dict


def prep_train_test_helper(x, sdate_pred, time_step=None, train_s='2016', process_list=None):
    # if time_step consider, it's okay to use full train with overalp to get scaler
    x_train = x.loc[train_s:sdate_pred]
    x_test = x.loc[sdate_pred:]
    if time_step is not None:
        x_dt_list = x.index.tolist()
        sdate_pred_dt = x_test.index[0]
        sdate_pred_ts_idx = x_dt_list.index(sdate_pred_dt) - time_step + 1
        # x_train = x.iloc[:sdate_pred_ts_idx]
        x_test = x.iloc[sdate_pred_ts_idx:]
    if process_list == 'x':
        process_dat_func = partial(process_dat_wrapper,
                                   process_func=StandardScaler(),
                                   process_col_list=None)
        scaler_dict = process_dat_func(x_train.fillna(0), x_test.fillna(0))
        x_train, x_test = scaler_dict['train'], scaler_dict['test']
    return x_train, x_test


def transform_2d_3d_helpher(x_use, y_use=None, time_step=1):
    x_len = len(x_use)
    if x_len < time_step:
        print('x length shorter than time step')
        raise Exception
    # reshape input to be [samples, time steps, features]
    if time_step == 1:
        x_use_3d = x_use.reshape((x_use.shape[0], 1, x_use.shape[1]))
        y_use_3d = y_use
    else:
        x_use_3d = []
        for i in range(x_len - time_step + 1):
            x_sequence = x_use[i:i + time_step, :]
            x_use_3d.append(x_sequence)
        x_use_3d = np.array(x_use_3d)
    if y_use is None:
        return x_use_3d
    else:
        y_use_3d = y_use[time_step - 1:]
    return x_use_3d, y_use_3d


def slice_by_minute(dat, slice_range=[1000, 1454]):
    """ minute mark at the start
         use left close, right open  - except 1500 - include that
         slice_range = [[1125,1129],[1300,1310]]

    """
    if isinstance(dat.index, pd.MultiIndex):
        index_list = dat.index.get_level_values(0)
    else:
        index_list = dat.index
    hour_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.hour]
    minute_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.minute]
    hour_minute_list = [int('%s%s' % (i, j)) for i, j in zip(hour_list, minute_list)]
    if isinstance(slice_range[0], list):
        range_a = slice_range[0]
        range_b = slice_range[1]
        range_a.sort()
        range_b.sort()
        slice_mask = [(i <= range_a[-1] and i >= range_a[0]) or
                      (i <= range_b[-1] and i >= range_b[0])
                      for i in hour_minute_list]
    else:
        slice_range.sort()
        slice_mask = [i <= slice_range[-1] and i >= slice_range[0] for i in hour_minute_list]
    dat_slice = dat[slice_mask]
    return dat_slice


def load_pickle(path):
    with open(path, mode='rb') as file:
        data = pickle.load(file)
    return data


def update_model_norm2(work_space, update_date, index_root):
    model_name_list = []
    for file_name in os.listdir(os.path.join(work_space, 'model_value', 'model_raw', update_date)):
        name, ext = os.path.splitext(file_name)
        model_name_list.append(name)
    model_name_list.sort()

    pred_comb2 = []
    for model_name in model_name_list:
        signal_path = os.path.join(work_space, 'model_value', 'model_raw', update_date, f'{model_name}.pkl')
        signal_raw = load_pickle(signal_path)

        signal_date = update_date
        signal_temp = signal_raw[signal_date]
        signal_norm = pd.DataFrame(np.full(signal_temp.shape, np.nan), index=signal_temp.index, columns=signal_temp.columns)
        index_path = os.path.join(index_root, f'{signal_date}.pkl')
        index_list = load_pickle(index_path)
        index_diff = pd.to_datetime(index_list).difference(signal_raw.index)
        if len(index_diff) > 0:
            fmt = '%Y-%m-%d'
            print(f'[{signal_date}] miss historical value: {len(index_diff)} points, from {index_diff[0].strftime(fmt)} to {index_diff[-1].strftime(fmt)}')
        else:
            signal_base = signal_raw[signal_raw.index.isin(index_list)]
            for col in signal_raw.columns:
                a = np.sort(signal_base[col].values)
                signal_norm[col] = [bisect_left(a, x) for x in signal_temp[col].values]
            signal_norm = signal_norm.div(len(signal_base)).mul(2).sub(1)
        signal_new = signal_norm.mean(axis=1).to_frame(name=model_name)

        latest_date = None
        date_root = os.path.join(work_space, 'model_value', 'model_norm2')
        date_list = os.listdir(date_root)
        date_list = sorted(date_list, reverse=False)
        for date in date_list:
            if int(date) < int(update_date):
                latest_date = str(date)
        assert latest_date is not None, 'miss historical raw value'
        signal_path = os.path.join(work_space, 'model_value', 'model_norm2', latest_date, f'{model_name}.pkl')
        signal_old = load_pickle(signal_path)
        signal_norm2 = pd.concat([signal_old, signal_new], axis=0)

        output_path = os.path.join(work_space, 'model_value', 'model_norm2', update_date, f'{model_name}.pkl')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(output_path)
        save_pickle(signal_norm2, output_path)

        pred_comb2.append(signal_norm2)
    pred_comb2 = pd.concat(pred_comb2, axis=1)
    pred_comb2 = pred_comb2.mean(axis=1)

    output_path = os.path.join(work_space, 'model_value', 'model_norm2', update_date, 'pred_comb2.pkl')
    print(output_path)
    save_pickle(pred_comb2, output_path)
    return None


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    try:
        main()
    except:
        traceback.print_exc()
        link.LinkMessage().sendMessage('Error: model_value_mobius_20250328 (data zz)')
