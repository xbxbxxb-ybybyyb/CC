import sys

sys.path.insert(0, '/data/user/020529/arrow_product_zz/code')

import os
import gc
import numpy as np
import pandas as pd
import datetime as dt
from functools import partial

from factor_utility.factor_tool import get_rebal_list_smart
from strategy.fitting_model import pred_fit_lgbm_cla_kf, pred_fit_lgbm_reg_kf
from strategy.fitting_model import pred_fit_extratree_cla_kf
from strategy.fitting_model import pred_fit_post_lasso_kf
from strategy.fitting_model import pred_fit_lr_kf
from strategy.fitting_model import pred_fit_mlp_reg, pred_fit_mlp_cla
from strategy.fitting_model import process_dat_wrapper, StandardScaler, set_seed, predict_rolling_cs_wrapper2
from strategy.strategy_utility import read_pickle, save_pickle

####################################################################################################

# model_list = ['lasso_reg']
model_list = ['lgbm_reg']
# model_list = ['mlp_reg']
# model_list = ['lasso_reg', 'lgbm_reg', 'mlp_reg']

# step 1: set end date
edate = '20250328'

# step 2: train individual models
run_stack = False

# step 3: train stack model (lasso_reg)
# run_stack = True

####################################################################################################

track_feature_importance = True
return_score = True
verbose = True
return_misc = False
plot_model = False
fold_num = 5
return_model = 10
shuffle = True

# lgbm_cla
param = {'reg_alpha': 0.01,
         'reg_lambda': 0.0001,
         'colsample_bytree': 0.2,
         'subsample': 0.4,
         'max_depth': 8,
         'num_leaves': 200,
         'learning_rate': 0.01,
         'lr_decay': 0.9995,
         'min_ratio': 0.001,
         'metric': 'auc',
         'n_estimators': 2000 * 2,
         'n_jobs': 24,
         'random_state': 2018}
fit_pred_func_lgbm_cla = partial(pred_fit_lgbm_cla_kf, param=param, fold_num=fold_num,
                                 weight_type='abs_ret', stratified=False,
                                 verbose=verbose, track_feature_importance=track_feature_importance,
                                 return_score=return_score, return_model=return_model,
                                 return_misc=return_misc,
                                 plot_model=plot_model,
                                 shuffle=shuffle)

# lgbm_reg
param = {'reg_alpha': 0.01,
         'reg_lambda': 0.0001,
         'colsample_bytree': 0.2,
         'subsample': 0.4,
         'max_depth': 8,
         'num_leaves': 120,
         'learning_rate': 0.01,
         'lr_decay': 0.99999,
         'min_ratio': 0.01,
         'metric': 'rmse',
         'n_estimators': 2000 * 2,
         'n_jobs': 24,
         'random_state': 2018}
fit_pred_func_lgbm_reg = partial(pred_fit_lgbm_reg_kf, param=param, fold_num=fold_num,
                                 verbose=verbose, track_feature_importance=track_feature_importance,
                                 return_score=return_score, return_misc=return_misc,
                                 plot_model=plot_model, return_model=return_model,
                                 shuffle=shuffle)

# et_cla
params = {'n_estimators': 3000,
          'min_samples_split': 0.005,
          'max_features': 'auto',
          'criterion': 'gini',
          'bootstrap': False,
          'oob_score': False,
          'n_jobs': 24,
          'class_weight': 'balanced',
          'random_state': 2018}
fit_pred_func_et_cla = partial(pred_fit_extratree_cla_kf, fold_num=fold_num, params=params, verbose=verbose,
                               return_score=return_score, weight_type='abs_ret', stratified=True,
                               track_feature_importance=track_feature_importance,
                               return_misc=return_misc, return_model=return_model,
                               shuffle=shuffle)

# lasso_reg
lasso_params = {'alpha': 1e-5,
                'normalize': False,
                'fit_intercept': True,
                'tol': 1e-4,
                'positive': False,
                'random_state': 2018}
params = {'fit_intercept': True}
fit_pred_func_lasso_reg = partial(pred_fit_post_lasso_kf, params=params, lasso_params=lasso_params,
                                  fold_num=fold_num, verbose=verbose, return_score=return_score,
                                  return_misc=return_misc, track_feature_importance=track_feature_importance,
                                  std_norm=True, return_model=return_model,
                                  shuffle=shuffle)

# lr_cla
params = {'C': 1e-3,
          'tol': 1e-4,
          'class_weight': 'balanced',
          'fit_intercept': False,
          'penalty': 'l2',
          'max_iter': 100,
          'n_jobs': -1,
          'random_state': 2018}
fit_pred_func_lr_cla = partial(pred_fit_lr_kf, params=params,
                               fold_num=fold_num, weight_type='abs_ret', verbose=verbose,
                               track_feature_importance=track_feature_importance,
                               return_misc=return_misc, stratified=True, return_model=return_model,
                               shuffle=shuffle)

# mlp_reg
params = {'dropout': 0.2,
          'activation': 'elu',
          'layer': [128, 64, 1],
          'lr': 1e-3,
          'loss': 'mean_squared_error',
          'optimizer': 'adam',
          'metrics': ['mse'],
          'callback_patience': 10,
          'epochs': 5000,
          'batch_size': 2 ** 13,
          'kernel_initializer': 'glorot_normal'}
rlrop_param = {'factor': 0.8, 'patience': 5}
fit_pred_func_mlp_reg = partial(pred_fit_mlp_reg, fold_num=fold_num, params=params, verbose=verbose, return_score=return_score,
                                return_misc=return_misc, plot_model=plot_model, track_feature_importance=track_feature_importance,
                                return_model=return_model, use_generator=False, rlrop_param=rlrop_param,
                                shuffle=shuffle)

# mlp_cla
params = {'dropout': 0.2,
          'activation': 'sigmoid',
          'layer': [512, 256, 2],
          'lr': 0.01,  # 1e-3,
          'loss': 'binary_crossentropy',
          'optimizer': 'adam',
          'metrics': ['acc'],
          'callback_patience': 10,
          'epochs': 5000,
          'batch_size': 2 ** 13,
          'kernel_initializer': 'glorot_normal'}
rlrop_param = {'factor': 0.8, 'patience': 5}
fit_pred_func_mlp_cla = partial(pred_fit_mlp_cla, fold_num=fold_num, params=params, verbose=verbose, return_score=return_score,
                                return_misc=return_misc, plot_model=plot_model, track_feature_importance=track_feature_importance,
                                return_model=return_model, use_generator=False, rlrop_param=rlrop_param,
                                shuffle=shuffle, weight_type='abs_ret')

fit_func_dict = {'lasso_reg': fit_pred_func_lasso_reg,
                 'lr_cla': fit_pred_func_lr_cla,
                 'et_cla': fit_pred_func_et_cla,
                 'lgbm_cla': fit_pred_func_lgbm_cla,
                 'lgbm_reg': fit_pred_func_lgbm_reg,
                 'mlp_reg': fit_pred_func_mlp_reg,
                 'mlp_cla': fit_pred_func_mlp_cla}

####################################################################################################

fac_root = '/data/user/000072/share/arrow_prod/full/factor'
model_root = '/data/user/020529/share/arrow_prod_zz/full/model'
# model_root = '/data/user/012315/share/pred_fit/arrow_prod/full/model'

sdate_fit = '20180101'  # fit start date

model_list_dl = ['mlp_cla', 'mlp_reg']

test_run = None  # full history update
# test_run = -3 # update only the last n rounds

expanding_window = True
roll_win = 60
holding_period = 1
process_list = None

rebal_mode_dict = {'quarter_quarter': '20210101'}
rebal_name = '_q2m' if 'quarter_month' in rebal_mode_dict else ''
process_dat_func = None

suffix_list = ['open', '']

run_stack_reg = True  # only stack regression models

if run_stack_reg:
    model_list_stack = ['lasso_reg', 'lgbm_reg', 'mlp_reg']
else:
    model_list_stack = ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']

val_path_dict = {i: os.path.join(model_root, 'factor/%s.pkl' % (i)) for i in suffix_list}

for suffix in suffix_list:
    edate_str = edate + '_' + suffix if suffix != '' else edate

    fac_path = os.path.join(fac_root, edate_str, 'factor_input.pkl')
    y_path = os.path.join(fac_root, edate_str, 'ylabel.pkl')
    print(f'factor path: {fac_path}', flush=True)
    print(f'ylabel path: {y_path}', flush=True)

    if run_stack:
        pred_raw_dict = {}
        print(model_list_stack, flush=True)
        res_save_path_dict = {model: os.path.join(model_root, edate_str, '%s.pkl' % (model)) for model in model_list_stack}
        if run_stack_reg:
            res_stack_path_dict = {model: os.path.join(model_root, edate_str, 'stack_model_reg', '%s.pkl' % (model)) for model in model_list}
        else:
            res_stack_path_dict = {model: os.path.join(model_root, edate_str, 'stack_model', '%s.pkl' % (model)) for model in model_list}
        for model in model_list_stack:
            pred_raw_dict[model] = read_pickle(res_save_path_dict[model])['prediction'].stack()
        pred_raw_df = pd.DataFrame(pred_raw_dict)
        if pred_raw_df.shape[1] != len(model_list_stack):
            print('model list stack dimension error', flush=True)
            print(model_list_stack, flush=True)
            print(pred_raw_df.columns, flush=True)
            raise Exception
        x_use = pred_raw_df
    else:
        res_save_path_dict = {model: os.path.join(model_root, edate_str, '%s.pkl' % (model)) for model in model_list}
        res_folder_dict = {model: os.path.join(model_root, edate_str, model) for model in model_list}
        if fac_path.find('.pkl') > 0:
            x_use = read_pickle(fac_path)
        elif fac_path.find('h5') > 0:
            x_use = pd.read_hdf(fac_path)
        else:
            raise RuntimeError('factor not found')

    x_use = x_use.loc[:pd.Timestamp(edate)].fillna(0)
    fac_cnt = x_use.shape[1]
    remove_list = []
    tl = [i for i in x_use.columns if i not in remove_list]
    x_use = x_use[tl]
    fac_cnt_curr = x_use.shape[1]
    print(fac_cnt, fac_cnt_curr, flush=True)
    sdate_dat_x = x_use.index[0][0]
    edate_dat_x = x_use.index[-1][0]
    if y_path.find('.pkl') > 0:
        y_use = read_pickle(y_path)
    else:
        y_use = pd.read_hdf(y_path)

    y_use = y_use.loc[sdate_dat_x:pd.Timestamp(edate)].fillna(0)
    try:
        y_use = y_use.iloc[:, 0]
    except:
        print('only_one', flush=True)
    sdate_dat_y = y_use.index[0][0]
    edate_dat_y = y_use.index[-1][0]
    process_inf = True
    if process_inf:
        x_use = x_use.replace({np.inf: 0, -1 * np.inf: 0})

    date_list = list(set(x_use.index.get_level_values(0)))
    date_list.sort()
    min_date = dt.datetime.strftime(date_list[roll_win + 1:][0], '%Y%m%d')
    sdate_fit = max(min_date, sdate_fit)
    print('sdate_fit: %s' % (sdate_fit), flush=True)
    print('X: %s ~ %s' % (sdate_dat_x, edate_dat_x), flush=True)
    print('Y: %s ~ %s' % (sdate_dat_y, edate_dat_y), flush=True)

    rebal_freq = get_rebal_list_smart(sdate_fit, edate, rebal_mode_dict)
    rebal_freq = [pd.Timestamp(i) for i in rebal_freq]
    print('rebal_mode: %s | %d iterations | %s ~ %s ' % (rebal_mode_dict, len(rebal_freq), rebal_freq[0], rebal_freq[-1]), flush=True)

    res_dict_model = {}

    if process_list == 'x':
        process_dat_func = partial(process_dat_wrapper, process_func=StandardScaler())
    else:
        process_dat_func = None

    if run_stack:
        model_list = ['lasso_reg']

    for model in model_list:
        print(model, flush=True)
        res_dict_model = {}
        fit_pred_func = fit_func_dict[model]
        if model in model_list_dl:
            res_iter_save_folder = res_folder_dict[model]
            fit_pred_func = partial(fit_pred_func, res_iter_save_folder=res_iter_save_folder)
        set_seed()
        print(x_use.shape, flush=True)
        print(y_use.shape, flush=True)
        res_dict_model[model] = predict_rolling_cs_wrapper2(y_use, x_use, roll_win, holding_period, process_dat_func=process_dat_func,
                                                            process_list=process_list,
                                                            rebal_freq=rebal_freq, fit_pred_func=fit_pred_func, x_test=None,
                                                            test_run=test_run, expanding_window=expanding_window,
                                                            return_model=return_model, sort_col=False)
        if run_stack:
            save_pickle(res_dict_model[model], res_stack_path_dict[model])
        else:
            save_pickle(res_dict_model[model], res_save_path_dict[model])

    del x_use, y_use
    gc.collect()
