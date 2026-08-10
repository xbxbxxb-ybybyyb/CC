import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold, ShuffleSplit
import lightgbm as lgb
from multifactor.IO.naming_config import *
import multifactor.utility.common as ut
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
from multifactor.strategy.fitter import sklearn_fitter, sklearn_predictor
from multifactor.strategy.fitter import fill_infinite
from multifactor.preprocessing.cleansing import outlier_median_algo
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from functools import partial
from collections import ChainMap
# from pandarallel import pandarallel
from tqdm import tqdm
import shutil as stl
import datetime, time
import os
import sys

# pandarallel.initialize(verbose=0)
ENSEMBLE_TREE_CLS_PARAM = {'n_estimators': 512, 'min_samples_split': 0.01, 'min_samples_leaf': 0.005}

LGB_PARAM = {'boosting_type': 'gbdt',
             'num_leaves': 32,
             'max_depth': 6,
             'learning_rate': 0.01,
             'min_child_samples': 64,
             'subsample': 0.25,
             'subsample_freq': 5,
             'colsample_bytree': 0.25,
             'verbose': -1,
             'reg_alpha': 1.0,
             'reg_lambda': 1.0}

LGB_RANKER_PARAM = {**LGB_PARAM,
                    **{'n_estimators': 240,
                       'objective': 'lambdarank',
                       'metric': 'ndcg'}}

LGB_CLS_PARAM = {**LGB_PARAM,
                 **{'n_estimators': 2048,
                    'objective': 'binary',
                    'metric': 'auc'}}

LGB_REG_PARAM = {**LGB_PARAM,
                 **{'n_estimators': 1024,
                    'objective': 'regression',
                    'metric': 'rmse'}}

LGB_MULTICLASS_PARAM = {**LGB_PARAM,
                        **{'n_estimators': 1024,
                           'objective': 'multiclass',
                           'metric': 'multi_logloss'}}


def linear_fitter(linear_fcts, label_y, fix_outlier=True):
    linear_fcts = fill_infinite(linear_fcts, np.nan)
    if fix_outlier:
        linear_fcts = linear_fcts.parallel_apply(outlier_median_algo, axis=0)
    ic = linear_fcts.corrwith(label_y, axis=0)
    linear_fcts = linear_fcts.multiply(np.sign(ic), axis=1)
    norm_linear_fcts = linear_fcts.subtract(linear_fcts.min(), axis=1).divide(linear_fcts.max() - linear_fcts.min(), axis=1)
    label_y = label_y.reindex(norm_linear_fcts.index).dropna()
    norm_linear_fcts = norm_linear_fcts.reindex(label_y.index)
    lasso_model = sklearn_fitter(norm_linear_fcts, label_y, positive=True)
    lasso_score = sklearn_predictor(norm_linear_fcts, lasso_model)
    return lasso_model, lasso_score, np.sign(ic)


def lr_fitter(insample_x, insample_y, random_state=0, factor_scores=None, cv_num=4, binary_label_cut_threshold=0.01):
    insample_y = fill_infinite(insample_y, np.nan).dropna()
    insample_x = fill_infinite(insample_x, 0)
    positive_tag = insample_y.loc[insample_y >= binary_label_cut_threshold]
    negative_tag = insample_y.loc[insample_y <= - binary_label_cut_threshold]
    positive_tag.iloc[:] = 1.0
    negative_tag.iloc[:] = 0.0
    insample_y = pd.concat([positive_tag, negative_tag], axis=0).sort_index()
    insample_x = insample_x.reindex(insample_y.index).dropna(how='all')
    insample_y = insample_y.reindex(insample_x.index)
    clf = LogisticRegressionCV(cv=cv_num, random_state=random_state).fit(insample_x.values, insample_y.values)
    if factor_scores is None:
        factor_scores = insample_x
    else:
        factor_scores = fill_infinite(factor_scores, 0)
    lr_score = clf.predict_proba(factor_scores)
    lr_score = pd.Series(lr_score[:, 1], index=factor_scores.index)
    return clf, lr_score


def qcut_helper(x, q=5):
    return pd.qcut(x, q=q, labels=False, retbins=False, duplicates='drop')


def lightgbm_tree_params_helper(lightgbm_tree_params, use_GPU, use_GPU_DP, max_bin_limit):
    if use_GPU:
        assert isinstance(use_GPU, bool)
        lightgbm_tree_params['device'] = 'cuda'
    if use_GPU_DP is not None:
        assert isinstance(use_GPU_DP, bool)
        lightgbm_tree_params['gpu_use_dp'] = use_GPU_DP
    if max_bin_limit is not None:
        assert isinstance(max_bin_limit, (int, float, complex))
        lightgbm_tree_params['max_bin'] = max_bin_limit
    return lightgbm_tree_params


def tree_fitter(nonlinear_fcts, label_y, objective, fix_outlier=True, sample_weight=None, random_state=None,
                binary_label_cut_threshold=0.0075, regression_label_clip_threshold=0.05, rank_qnum=10, ndcg_qnum=10,
                boost_tree_params=None, eval_metric=None, lightgbm_cv_nfold=5, use_GPU=True, use_GPU_DP=None,
                max_bin_limit=None, n_jobs=0, early_stopping_rounds=50, override_cv_flag=False, **kwargs):
    assert eval_metric is None
    assert objective in ['random-forest-binary', 'extratree-binary',
                         'lightgbm-binary', 'lightgbm-rank',
                         'lightgbm-multiclass', 'lightgbm-regression']
    assert isinstance(nonlinear_fcts, pd.DataFrame) and isinstance(label_y, pd.Series)
    start_time = time.time()
    ensemble_tree_params = boost_tree_params.copy() if boost_tree_params is not None else None
    lightgbm_tree_params = boost_tree_params.copy() if boost_tree_params is not None else None
    print(f'tree fitter objective: {objective}, gpu mode: {use_GPU}')
    print(f'fill infinites with NaN')
    nonlinear_fcts = fill_infinite(nonlinear_fcts, np.nan)
    if fix_outlier:
        print(f'dealing with outliers with median algo')
        nonlinear_fcts = nonlinear_fcts.parallel_apply(outlier_median_algo, axis=0)
    sample_x = nonlinear_fcts
    sample_x = sample_x.dropna(how='all')
    sample_y = label_y.reindex(sample_x.index).dropna()
    sample_x = sample_x.reindex(sample_y.index)
    preprocess_end_time = time.time()
    print('preprocessing complete, used time: {:.2f}s'.format(preprocess_end_time - start_time))
    if 'rank' in objective:
        assert isinstance(nonlinear_fcts.index, pd.MultiIndex) and isinstance(label_y.index, pd.MultiIndex)
        assert nonlinear_fcts.index.names == label_y.index.names == ['dt', 'Ticker']
        sample_y_count = sample_y.groupby(sample_y.index.get_level_values(level='dt')).nunique()
        less_y_index = sample_y_count.loc[sample_y_count <= rank_qnum].index
        sample_y = sample_y.drop(less_y_index, level='dt')
        sample_x = sample_x.reindex(sample_y.index)
        label_y = sample_y.groupby(sample_y.index.get_level_values(level='dt')).transform(qcut_helper, q=rank_qnum)
        group_num = label_y.groupby(level='dt').count()
    elif 'binary' in objective:
        sample_y = sample_y.loc[~((sample_y >= - binary_label_cut_threshold) & (sample_y <= binary_label_cut_threshold))]
        sample_x = sample_x.reindex(sample_y.index)
        label_y = pd.Series(np.where(sample_y > 0, 1, 0), index=sample_y.index)
    elif 'regression' in objective:
        assert regression_label_clip_threshold > 0
        sample_y = sample_y.clip(-regression_label_clip_threshold, regression_label_clip_threshold)
        label_y = sample_y.astype('float64')
    elif 'multiclass' in objective:
        label_y = sample_y
        num_class = label_y.nunique()
        assert sorted(list(label_y.unique())) == list(range(num_class))
        print('multiclass num: ', num_class)
    else:
        raise NotImplementedError
    print('sample shape: ', sample_x.shape)
    if sample_weight is not None:
        assert isinstance(sample_weight, pd.Series)
        sample_weight = sample_weight.reindex(label_y.index).fillna(0)
    # use whole data and cv to estimate n_estimators
    if objective == 'lightgbm-rank':
        if lightgbm_tree_params is None:
            lightgbm_tree_params = LGB_RANKER_PARAM.copy()
        lightgbm_tree_params = lightgbm_tree_params_helper(lightgbm_tree_params, use_GPU, use_GPU_DP, max_bin_limit)
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            dtrain.set_group(group_num.values)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=True, shuffle=True,
                          metrics=eval_metric, callbacks=[lgb.early_stopping(stopping_rounds=early_stopping_rounds)], seed=random_state, return_cvbooster=True)
            boost_rounds = lgbm['cvbooster'].best_iteration
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMRanker(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, importance_type='split')
        lgbm.fit(sample_x, label_y, sample_weight=sample_weight, group=group_num)
        predict_score = lgbm.predict(nonlinear_fcts, raw_score=True)
        predict_score = pd.Series(predict_score, index=nonlinear_fcts.index)
    elif objective == 'lightgbm-binary':
        if lightgbm_tree_params is None:
            lightgbm_tree_params = LGB_CLS_PARAM.copy()
        lightgbm_tree_params = lightgbm_tree_params_helper(lightgbm_tree_params, use_GPU, use_GPU_DP, max_bin_limit)
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=True, shuffle=True,
                          metrics=eval_metric, callbacks=[lgb.early_stopping(stopping_rounds=early_stopping_rounds)], seed=random_state, return_cvbooster=True)
            boost_rounds = lgbm['cvbooster'].best_iteration
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMClassifier(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, importance_type='split')
        lgbm.fit(sample_x, label_y, sample_weight=sample_weight)
        predict_score = lgbm.predict_proba(nonlinear_fcts, raw_score=False)
        predict_score = pd.Series(predict_score[:, 1], index=nonlinear_fcts.index)
    elif objective == 'lightgbm-multiclass':
        if lightgbm_tree_params is None:
            lightgbm_tree_params = LGB_MULTICLASS_PARAM.copy()
        lightgbm_tree_params = lightgbm_tree_params_helper(lightgbm_tree_params, use_GPU, use_GPU_DP, max_bin_limit)
        lightgbm_tree_params['num_class'] = num_class
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=True, shuffle=True,
                          metrics=eval_metric, callbacks=[lgb.early_stopping(stopping_rounds=early_stopping_rounds)], seed=random_state, return_cvbooster=True)
            boost_rounds = lgbm['cvbooster'].best_iteration
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMClassifier(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, importance_type='split')
        lgbm.fit(sample_x, label_y, sample_weight=sample_weight)
        predict_score = lgbm.predict_proba(nonlinear_fcts, raw_score=False)
        predict_score = pd.DataFrame(predict_score, index=nonlinear_fcts.index)
    elif objective == 'lightgbm-regression':
        if lightgbm_tree_params is None:
            lightgbm_tree_params = LGB_REG_PARAM.copy()
        lightgbm_tree_params = lightgbm_tree_params_helper(lightgbm_tree_params, use_GPU, use_GPU_DP, max_bin_limit)
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=False, shuffle=True,
                          metrics=eval_metric, callbacks=[lgb.early_stopping(stopping_rounds=early_stopping_rounds)], seed=random_state, return_cvbooster=True)
            boost_rounds = lgbm['cvbooster'].best_iteration
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMRegressor(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, importance_type='split')
        lgbm.fit(sample_x, label_y, sample_weight=sample_weight)
        predict_score = lgbm.predict(nonlinear_fcts, raw_score=False)
        predict_score = pd.Series(predict_score, index=nonlinear_fcts.index)
    elif objective == 'extratree-binary':
        if ensemble_tree_params is None:
            ensemble_tree_params = ENSEMBLE_TREE_CLS_PARAM.copy()
        clf = ExtraTreesClassifier(n_jobs=n_jobs, random_state=random_state, **ensemble_tree_params)
        clf.fit(sample_x.fillna(0), label_y.fillna(0), sample_weight=sample_weight)
        print('extratree score: %f' % clf.score(sample_x.fillna(0), label_y.fillna(0)))
        predict_score = clf.predict_proba(nonlinear_fcts.fillna(0))
        predict_score = pd.Series(predict_score[:, 1], index=nonlinear_fcts.index)
    elif objective == 'random-forest-binary':
        if ensemble_tree_params is None:
            ensemble_tree_params = ENSEMBLE_TREE_CLS_PARAM.copy()
        clf = RandomForestClassifier(n_jobs=n_jobs, random_state=random_state, **ensemble_tree_params)
        clf.fit(sample_x.fillna(0), label_y.fillna(0), sample_weight=sample_weight)
        print('random forest score: %f' % clf.score(sample_x.fillna(0), label_y.fillna(0)))
        predict_score = clf.predict_proba(nonlinear_fcts.fillna(0))
        predict_score = pd.Series(predict_score[:, 1], index=nonlinear_fcts.index)
    else:
        raise NotImplementedError
    if 'lightgbm' in objective:
        model = lgbm
    elif 'extratree' in objective:
        model = clf
    elif 'random-forest' in objective:
        model = clf
    else:
        raise NotImplementedError
    training_end_time = time.time()
    print('training complete, used time: {:.2f}s'.format(training_end_time - preprocess_end_time))
    return model, predict_score


def tree_fitter_helper(task, end_ts=None, n_jobs=None):
    param, sample_cache_path, kwargs = task
    sliced_sample_x, sliced_sample_y = ut.diller(sample_cache_path)
    if n_jobs is not None:
        assert isinstance(n_jobs, int)
        kwargs['n_jobs'] = n_jobs
    if end_ts is not None:
        end_ts = IO.str_date_parser(end_ts)
        print(f'Resliced Till End: ', end_ts.strftime('%Y%m%d'))
        sliced_sample_x = sliced_sample_x.sort_index().loc[:end_ts]
        sliced_sample_y = sliced_sample_y.reindex(sliced_sample_x.index)
    return tree_fitter(nonlinear_fcts=sliced_sample_x, label_y=sliced_sample_y, boost_tree_params=param, **kwargs)


def kfold_tree_fitter(fcts, label_y, params, random_state=None, shuffle=True, n_splits=5, use_GPU=True, fix_outlier=True,
                      test_size=None, max_workers=24, tmp_folder=None, test_run=False, task_tag='kfold', **kwargs):
    assert isinstance(fcts, pd.DataFrame) and isinstance(label_y, pd.Series)
    if not isinstance(params, list):
        assert isinstance(params, dict)
        params = [params]
    if fix_outlier:
        print(f'dealing with outliers with median algo')
        fcts = fcts.parallel_apply(outlier_median_algo, axis=0)
    if shuffle:
        fcts = fcts.sample(frac=1, random_state=random_state)
    if n_splits <= 2 or test_size is not None:  # not suitable for traditional kfold
        print('Shuffle KFold Engaged')
        assert test_size is not None and isinstance(test_size, float)
        kf = ShuffleSplit(n_splits=n_splits, test_size=test_size, random_state=random_state)
    else:
        print('KFold Engaged')
        kf = KFold(n_splits=n_splits)
    sample_x = fcts
    sample_y = label_y.reindex(sample_x.index).dropna()
    sample_x = sample_x.reindex(sample_y.index)
    task_list = list()
    kf_num = 1
    for train, test in kf.split(sample_x):
        print(f'Preparing Fold {kf_num} for KFold {n_splits}')
        sliced_sample_x = sample_x.iloc[train]
        sliced_sample_y = sample_y.iloc[train]
        # dump data to file to avoid python pickle problems
        tmp_file_name = 'kfold_' + pd.Timestamp.now().strftime('%Y%m%d%H%M%S') + '.pkl'
        if tmp_folder is None:
            tmp_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), tmp_file_name)
        else:
            tmp_file_path = os.path.join(tmp_folder, tmp_file_name)
        # pack additional params
        kwargs['n_jobs'] = 1
        kwargs['random_state'] = random_state
        kwargs['use_GPU'] = use_GPU
        if fix_outlier:  # avoid repetitive outlier removal
            kwargs['fix_outlier'] = False
        ut.diller(tmp_file_path, (sliced_sample_x, sliced_sample_y))
        for param in params:
            task_list.append((param, tmp_file_path, kwargs))
        kf_num += 1
    ut.diller(os.path.join(os.path.dirname(tmp_file_path), f'{task_tag}_task_list.pkl'), task_list)
    print(f'Task List Dumped')
    if not test_run:
        print(f'Engaging Actual Training')
        collector = ut.concurrent_apply_func(tree_fitter_helper, task_list, max_workers, logger=None, debug_mode=False,
                                             process_type='multiprocess', logger_callback=None,
                                             collect_results=True, void_log_flag=False)
    else:
        collector = list()
    for param, tmp_file_path, kwargs in task_list:
        if os.path.exists(tmp_file_path) and tmp_folder is None:
            os.remove(tmp_file_path)
            print(f'{tmp_file_path} Removed')
    return collector



