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
from tqdm import tqdm
import shutil as stl
import datetime
import os
import sys


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
                 **{'n_estimators': 1024,
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

def marker_closure(marker, collector, ref_open_tag='S_DQ_ADJHIGH', ref_close_tag='S_DQ_ADJOPEN'):
    if not (None in marker):
        ts = marker[0].Index
        pct_chg = getattr(marker[1], ref_close_tag) / getattr(marker[0], ref_open_tag) - 1
        collector[ts] = pct_chg
        return [None, None]
    else:
        return marker


def limit_y(pd_data, ticker, **kwargs):
    tdata = pd_data.xs(ticker, level=1)
    collector = dict()
    marker = [None, None]
    for r in tdata.itertuples():
        if r.S_DQ_TRADESTATUS not in ['停牌', 'N', '待核查']:
            if r.S_DQ_HIGH != r.S_DQ_LOW:
                # follow time sequence
                if marker[0] is not None:
                    marker[1] = r
                    marker = marker_closure(marker, collector, **kwargs)
                if r.S_DQ_HIGH == r.S_DQ_LIMIT:
                    assert marker[1] is None
                    marker[0] = r
    res = pd.Series(collector).sort_index()
    res.name = ticker
    return res


def limit_o2ul(pd_data):
    pd_data['o2ul'] = (pd_data['S_DQ_ADJOPEN'].unstack().shift(-1) / pd_data['S_DQ_ADJHIGH'].unstack() - 1).stack()
    pd_data = pd_data.loc[~pd_data.S_DQ_TRADESTATUS.isin(['停牌', 'N', '待核查'])]
    pd_data = pd_data.loc[~(pd_data.S_DQ_HIGH == pd_data.S_DQ_LOW)]
    o2ul = pd_data[pd_data.S_DQ_HIGH == pd_data.S_DQ_LIMIT]['o2ul']
    return o2ul


def calc_strong_label(EODPrices):
    collector = list()
    universe = np.unique(EODPrices.index.get_level_values(level='Ticker'))
    for ticker in tqdm(universe):
        collector.append(limit_y(EODPrices, ticker))
    final_y = pd.concat(collector, axis=1).stack().sort_index()
    return final_y


def limit_time_helper(td, valid_samples, limit_prices):
    collector = dict()
    min_pd = pd.read_pickle(os.path.join(minute_stock_per_date_path, td.strftime('%Y%m%d') + '.pkl'), compression='gzip')
    min_pd = min_pd.reset_index()
    min_pd['dt'] = min_pd['dt'] * 1E6 + min_pd['minute'] * 100
    min_pd['dt'] = pd.to_datetime(min_pd['dt'].astype('int64'), format='%Y%m%d%H%M%S')
    min_pd['Ticker'] = min_pd['Ticker'].map(ut.ticker_match)
    min_pd = min_pd.set_index(['dt', 'Ticker'])
    # loop tickers for target time
    for ticker in valid_samples.loc[td].index:
        limit_price = limit_prices.loc[td, ticker]
        assert not np.isnan(limit_price)
        try:
            sliced_data = min_pd.xs(ticker, level=1)[['high', 'volume', 'low']]
        except KeyError:
            print(f'{ticker} not found in {td} minute level data')
            continue
        limit_time = sliced_data.high.eq(limit_price).idxmax()
        idx_limit_time = sliced_data.index.get_loc(limit_time)
        try:
            # double check price in case all negatives for idxmax
            assert sliced_data.loc[limit_time, 'high'] == limit_price
        except AssertionError:
            print(f'{ticker} could not reach limit price in {td} minute level data')
            continue
        volume_before_ht = sliced_data.volume.iloc[:idx_limit_time].sum()
        # calculate pattern: 2: close is not limit; 3: close is limit but breaks during trading; 4: close is limit and does not break shape
        try:
            low_price_after_ht = sliced_data.low.iloc[idx_limit_time+1:].dropna()
            if low_price_after_ht.min() == limit_price:
                pattern = 4
            elif low_price_after_ht[-1] == limit_price:
                pattern = 3
            else:
                pattern = 2
        except IndexError:
            print(f'{ticker} reached limit at {limit_time} in {td} minute level data')
            continue
        collector[(td, ticker)] = {'ht': limit_time.time(),
                                   'volume_before_ht': volume_before_ht,
                                   'pattern': pattern}
    return collector


def get_stock_reach_limit_time(valid_samples, limit_prices, max_workers=24):
    # given strong labels and limit prices, search minute data for timestamps which the assets reach limit prices
    assert isinstance(valid_samples.index, pd.MultiIndex) and isinstance(limit_prices.index, pd.MultiIndex)
    valid_dates = valid_samples.index.get_level_values(level=0).unique()
    assert valid_dates.min() in limit_prices.index.get_level_values(level=0)
    assert valid_dates.max() in limit_prices.index.get_level_values(level=0)
    collector = ut.concurrent_apply_func(limit_time_helper, list(valid_dates), max_workers, logger=None, debug_mode=False,
                                         process_type='multiprocess', logger_callback=None,
                                         collect_results=True, void_log_flag=False,
                                         valid_samples=valid_samples, limit_prices=limit_prices)
    return pd.DataFrame(dict(ChainMap(*collector.values()))).T.sort_index()


def linear_fitter(linear_fcts, label_y):
    linear_fcts = fill_infinite(linear_fcts, np.nan)
    linear_fcts = linear_fcts.apply(outlier_median_algo, axis=0)
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


def tree_fitter(nonlinear_fcts, label_y, objective, sample_weight=None, random_state=None,
                binary_label_cut_threshold=0.0075, regression_label_clip_threshold=0.05, rank_qnum=10, ndcg_qnum=10,
                boost_tree_params=None, eval_metric=None, lightgbm_cv_nfold=5,
                n_jobs=0, early_stopping_rounds=50, override_cv_flag=False, **kwargs):
    assert eval_metric is None
    assert objective in ['random-forest-binary', 'extratree-binary',
                         'lightgbm-binary', 'lightgbm-rank',
                         'lightgbm-multiclass', 'lightgbm-regression']
    assert isinstance(nonlinear_fcts, pd.DataFrame) and isinstance(label_y, pd.Series)
    ensemble_tree_params = boost_tree_params.copy() if boost_tree_params is not None else None
    lightgbm_tree_params = boost_tree_params.copy() if boost_tree_params is not None else None
    print(f'tree fitter objective: {objective}')
    nonlinear_fcts = fill_infinite(nonlinear_fcts, np.nan)
    #nonlinear_fcts = nonlinear_fcts.apply(outlier_median_algo, axis=0)
    sample_x = nonlinear_fcts
    sample_x = sample_x.dropna(how='all')
    sample_y = label_y.reindex(sample_x.index).dropna()
    sample_x = sample_x.reindex(sample_y.index)
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
        label_y = sample_y
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
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            dtrain.set_group(group_num.values)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=True, shuffle=True,
                          metrics=eval_metric, early_stopping_rounds=early_stopping_rounds, show_stdv=True, seed=random_state)
            boost_rounds = max(1, pd.Series(lgbm[f'ndcg@{ndcg_qnum}-mean']).idxmax())
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMRanker(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, silent=True, importance_type='split')
        lgbm.fit(sample_x, label_y, sample_weight=sample_weight, group=group_num)
        predict_score = lgbm.predict(nonlinear_fcts, raw_score=True)
        predict_score = pd.Series(predict_score, index=nonlinear_fcts.index)
    elif objective == 'lightgbm-binary':
        if lightgbm_tree_params is None:
            lightgbm_tree_params = LGB_CLS_PARAM.copy()
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=True, shuffle=True,
                          metrics=eval_metric, early_stopping_rounds=early_stopping_rounds, show_stdv=True, seed=random_state)
            boost_rounds = max(1, pd.Series(lgbm['auc-mean']).idxmax())
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMClassifier(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, silent=True, importance_type='split')
        lgbm.fit(sample_x, label_y, sample_weight=sample_weight)
        predict_score = lgbm.predict_proba(nonlinear_fcts, raw_score=False)
        predict_score = pd.Series(predict_score[:, 1], index=nonlinear_fcts.index)
    elif objective == 'lightgbm-multiclass':
        if lightgbm_tree_params is None:
            lightgbm_tree_params = LGB_MULTICLASS_PARAM.copy()
        lightgbm_tree_params['num_class'] = num_class
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=True, shuffle=True,
                          metrics=eval_metric, early_stopping_rounds=early_stopping_rounds, show_stdv=True, seed=random_state)
            boost_rounds = max(1, pd.Series(lgbm['multi_logloss-mean']).idxmin())
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMClassifier(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, silent=True, importance_type='split')
        lgbm.fit(sample_x, label_y, sample_weight=sample_weight)
        predict_score = lgbm.predict_proba(nonlinear_fcts, raw_score=False)
        predict_score = pd.DataFrame(predict_score, index=nonlinear_fcts.index)
    elif objective == 'lightgbm-regression':
        if lightgbm_tree_params is None:
            lightgbm_tree_params = LGB_REG_PARAM.copy()
        if not override_cv_flag:
            dtrain = lgb.Dataset(sample_x, label_y, weight=sample_weight)
            lgbm = lgb.cv(lightgbm_tree_params, dtrain, nfold=lightgbm_cv_nfold, stratified=False, shuffle=True,
                          metrics=eval_metric, early_stopping_rounds=early_stopping_rounds, show_stdv=True, seed=random_state)
            boost_rounds = max(1, pd.Series(lgbm['rmse-mean']).idxmin())
            print(f'best boost rounds {boost_rounds}')
            lightgbm_tree_params['n_estimators'] = boost_rounds
        lgbm = lgb.LGBMRegressor(**lightgbm_tree_params, random_state=random_state, n_jobs=n_jobs, silent=True, importance_type='split')
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
    return model, predict_score


def tree_fitter_helper(task, end_ts=None, use_GPU=False):
    param, sample_cache_path, kwargs = task
    if use_GPU:
        param['device'] = 'gpu'
    sliced_sample_x, sliced_sample_y = ut.diller(sample_cache_path)
    if end_ts is not None:
        end_ts = IO.str_date_parser(end_ts)
        print(f'Resliced Till End: ', end_ts.strftime('%Y%m%d'))
        sliced_sample_x = sliced_sample_x.sort_index().loc[:end_ts]
        sliced_sample_y = sliced_sample_y.reindex(sliced_sample_x.index)
    return tree_fitter(nonlinear_fcts=sliced_sample_x, label_y=sliced_sample_y, boost_tree_params=param, **kwargs)


def kfold_tree_fitter(fcts, label_y, params, random_state=None, shuffle=True, n_splits=5,
                      test_size=None, max_workers=24, tmp_folder=None, test_run=False, task_tag='kfold', **kwargs):
    assert isinstance(fcts, pd.DataFrame) and isinstance(label_y, pd.Series)
    if not isinstance(params, list):
        assert isinstance(params, dict)
        params = [params]
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


def eval_predict_score(predict_score, label_y, threshold, ht_time=None, max_holding_num=None):
    selected_sample = predict_score.loc[predict_score >= threshold]
    filter_final_y = label_y.loc[label_y.index.isin(selected_sample.index)]
    if max_holding_num is not None:
        assert ht_time is not None
        # sort values according to hit limit time
        chunk = pd.concat([filter_final_y, ht_time.reindex(filter_final_y.index)], axis=1).dropna()
        chunk.columns = ['label', 'ht']
        chunk['ht'] = chunk['ht'].map(lambda x: x.hour) * 60 + chunk['ht'].map(lambda x: x.minute)
        chunk.index.names = ['dt', 'Ticker']
        chunk = chunk.reset_index().sort_values(['dt', 'ht']).set_index(['dt', 'Ticker'])
        filter_final_y = chunk.label
        filter_final_y = filter_final_y.groupby(filter_final_y.index.get_level_values(level='dt')).head(n=max_holding_num)
    wr = filter_final_y.loc[filter_final_y > 0].size / filter_final_y.size
    wlr = abs(filter_final_y.loc[filter_final_y > 0].mean() / filter_final_y.loc[filter_final_y < 0].mean())
    oc = filter_final_y.groupby(filter_final_y.index.get_level_values(level='dt')).count()
    if max_holding_num is None:
        daily_pnl = filter_final_y.groupby(filter_final_y.index.get_level_values(level='dt')).mean()
        daily_pnl.cumsum().plot(figsize=(20, 5))
    else:
        daily_pnl = filter_final_y.groupby(filter_final_y.index.get_level_values(level='dt')).mean() * oc / max_holding_num
        daily_pnl.cumsum().plot(figsize=(20, 5))
        oc.plot(figsize=(20, 5), secondary_y=True, linewidth=1.5, style='k-.', alpha=0.25)
    mdd = ut.max_drawdown_ts(daily_pnl.cumsum()).min()
    sharpe = daily_pnl.mean() / daily_pnl.std() * np.sqrt(242)
    calmar = daily_pnl.sum() / abs(mdd)
    daily_wr = daily_pnl.loc[daily_pnl > 0].size / daily_pnl.size
    kelly = (wlr * wr - (1 - wr)) / wlr
    print(f'daily winning rate: {daily_wr:.2%}, sharpe: {sharpe}, max drawdown: {mdd:.2%}, calmar ratio: {calmar}')
    print(f'sample winning rate: {wr:.2%}, win-loss ratio: {wlr}, kelly coef: {kelly}')
    print(oc.groupby(oc.index.year).mean().to_dict())
    return daily_pnl, filter_final_y


def calc_strong_time_stats_helper(ticker, trans, order, check_point=0.5, take_ratio=0.1):
    # given transaction and order dataframes, calculate time info
    assert isinstance(trans, pd.DataFrame) and isinstance(order, pd.DataFrame)
    trans = trans.loc[trans.TradeType == 0]  # normal order, not cancel order
    trans = trans.loc[trans.TradeQty != 0]
    trans = trans.loc[trans.TradePrice != 0]
    ht_price = trans['TradePrice'].max()
    ht = trans['TradePrice'].idxmax() + pd.Timedelta('1ms')
    total_qty_before_ht = trans.loc[ht:]['TradeQty'].sum()
    trans = trans.loc[ht:]  # consider only transactions post hit time
    if trans['TradePrice'].value_counts().loc[ht_price] / len(trans['TradePrice']) >= 0.99 and trans['TradePrice'].iloc[-1] == ht_price:
        is_really_strong = True
    else:
        is_really_strong = False
    assert is_really_strong, 'not that strong'
    after_ht_orders = order.loc[ht:]
    after_ht_buy_orders = after_ht_orders.loc[after_ht_orders.OrderBSFlag == 1]
    total_after_ht_qty = trans.TradeQty.sum()
    buy_detail_info = dict()
    for row in after_ht_buy_orders.itertuples():
        oid = row.OrderIndex if '.SZ' in ticker else row.OrderNO
        trans_recs = trans.loc[trans.TradeBuyNo == oid]
        if len(trans_recs) != 0:
            info = dict()
            info['total_qty_ratio'] = trans_recs.TradeQty.sum() / total_after_ht_qty
            info['order_trade_money'] = trans_recs.TradeMoney.sum()
            info['order_time'] = (row.Index - ht).total_seconds()
            info['fill_init_time'] = (trans_recs.index[0] - ht).total_seconds()
            info['fill_end_time'] = (trans_recs.index[-1] - ht).total_seconds()
            info['fill_used_time'] = (trans_recs.index[-1] - trans_recs.index[0]).total_seconds()
            buy_detail_info[oid] = info
    try:
        buy_detail_info_pd['total_qty_ratio']
        assert buy_detail_info_pd.total_qty_ratio.sum() >= check_point + take_ratio, 'fill rate abnormal'
    except:
        return {'total_after_ht_money': 0,
                'total_qty_before_ht': 0,
                'check_order_order_time': 0,
                'check_order_finish_time': 0}
    buy_detail_info_pd = pd.DataFrame(buy_detail_info).T
    # calculate check point order elapsed time
    check_fill_order_index = (buy_detail_info_pd['total_qty_ratio'].cumsum() >= check_point).idxmax()
    finish_fill_order_index = (buy_detail_info_pd['total_qty_ratio'].cumsum() >= check_point + take_ratio).idxmax()
    check_order_order_time = buy_detail_info_pd.loc[check_fill_order_index].order_time
    check_order_finish_time = buy_detail_info_pd.loc[finish_fill_order_index].fill_end_time
    total_after_ht_money = buy_detail_info_pd.order_trade_money.sum()
    return {'total_after_ht_money': total_after_ht_money,
            'total_qty_before_ht': total_qty_before_ht,
            'check_order_order_time': check_order_order_time,
            'check_order_finish_time': check_order_finish_time}


def mini_strong_helper(param, root_path, check_point):
    td, ticker = param
    td = td.strftime('%Y%m%d')
    trans = pd.read_csv(os.path.join(root_path, f'Transaction/{ticker}/{td}.csv'), index_col=0, parse_dates=True)
    order = pd.read_csv(os.path.join(root_path, f'Order/{ticker}/{td}.csv'), index_col=0, parse_dates=True)
    try:
        info = calc_strong_time_stats_helper(ticker, trans, order, check_point=check_point)
    except AssertionError as _exp:
        print(f'{ticker} raised {_exp} at {td}')
        info = None
    return info


def calc_strong_time_stats(sz_candidates, root_path, check_point=0.5, max_workers=24):
    assert isinstance(sz_candidates.index, pd.MultiIndex)
    collector = ut.concurrent_apply_func(mini_strong_helper, sz_candidates.index.tolist(), max_workers, logger=None, debug_mode=False,
                                         process_type='multiprocess', logger_callback=None,
                                         collect_results=True, void_log_flag=False,
                                         root_path=root_path, check_point=check_point)
    return pd.DataFrame({k: v for k, v in collector.items() if v is not None}).T.sort_index()

