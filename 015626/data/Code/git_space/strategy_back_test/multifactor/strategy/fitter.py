from sklearn import linear_model
import pandas as pd
import numpy as np
import copy
import xgboost as xgb
from sklearn.metrics import roc_auc_score
import multifactor.utility.common as ut
from hyperopt import hp, fmin, tpe, Trials
import traceback
import sys
import pickle
import warnings


def fillrate_filter(x, threshold=0.2):
    if x.size == 0:
        return False
    _x = x.ravel()
    if np.isfinite(_x).sum() / _x.size >= threshold:
        return True
    else:
        return False


def fill_infinite(x, value=0):
    if np.any([isinstance(x, item) for item in [pd.DataFrame, pd.Series]]):
        return x.replace([np.nan, np.inf, -np.inf], value)
    elif isinstance(x, np.ndarray):
        return np.where(np.isfinite(x), x, value)
    else:
        raise AssertionError


def sklearn_fitter(x, y, *args, fitter='lasso', preprocess=True,
                   w=None, **kwargs):
    '''
    preprocess: fill np.nan, np.inf with ZERO, select isfinit columns
    '''
    assert np.all([isinstance(item, pd.DataFrame) for item in [x]])
    assert np.all([isinstance(item, pd.Series) for item in [y]])
    res = dict()
    if preprocess:
        valid_cols = x.columns[x.apply(fillrate_filter, axis=0)]
        x_ = fill_infinite(x[valid_cols]).values
        y_ = fill_infinite(y).values
    else:
        x_, y_ = x, y
        valid_cols = x.columns
    res['valid_cols'] = valid_cols
    if w is not None:
        assert isinstance(w, np.ndarray)
        w_ = w.ravel()
        x_ = (x_.T * w_).T
        y_ = y_ * w_
    if fitter == 'lasso':
        # model = linear_model.Lasso(alpha=kwargs.get('alpha', 0.001))
        model = linear_model.LassoCV(fit_intercept=kwargs.get('fit_intercept', True),
                                     positive=kwargs.get('positive', False),
                                     alphas=kwargs.get('alphas', None),
                                     max_iter=kwargs.get('max_iter', 1E6))
        model.fit(x_, y_)
        res['score'] = model.score(x_, y_)
        print('model alpha: %f' % model.alpha_)
        # error handling
        if np.nansum(np.abs(model.coef_)) == 0:
            warnings.warn('coefs all zeros, fitting failed')
            return None
        # rule out weak predictions
        if len(model.coef_[model.coef_ != 0]) < min(5, np.ceil(len(valid_cols) * kwargs.get('min_shrinkage_pct', 0.05))):
            warnings.warn('coefs num less than minimum shrinkage pct, fitting failed')
            return None
        print('valid coef num: %d' % len(model.coef_[model.coef_ != 0]))
        res['raw_model'] = copy.deepcopy(model)
        prev_coef = kwargs.get('prev_coef', None)
        # smooth coef
        if kwargs.get('smooth_coef', True):
            if prev_coef is None:
                prev_coef = [pd.Series(model.coef_, index=valid_cols)]
            else:
                assert isinstance(prev_coef, list)
                prev_coef.append(pd.Series(model.coef_, index=valid_cols))
                half_life = kwargs.get('half_life', 3)
                _coef = pd.DataFrame(prev_coef[-int(max(5, half_life*2)):]) \
                        .fillna(0).ewm(halflife=half_life).mean().iloc[-1, :].replace(0, np.nan).dropna()
                # filter coef small items
                scaler = kwargs.get('scaler', 25)
                _coef[_coef.abs() <= _coef.abs().max() / scaler] = np.nan
                _coef = _coef.dropna()
                model.coef_ = _coef.values
                res['valid_cols'] = list(_coef.index)
            res['prev_coef'] = prev_coef
        # prepare output
        res['model'] = model  # model with possibly modified coef for prediction
    else:
        raise NotImplementedError
    return res


def sklearn_predictor(x, res):
    assert np.all([isinstance(item, pd.DataFrame) for item in [x]])
    assert len(res['valid_cols']) != 0
    x_ = fill_infinite(x[res['valid_cols']]).values
    return pd.Series(res['model'].predict(x_).ravel(), index=x.index)


def resampler(x, mode='norm_to_even', group_by_level=None, _grouped_level=None, random_state=1, **kwargs):
    assert isinstance(x, pd.Series)
    x = x.dropna()
    if group_by_level is not None:
        return x.groupby(level=group_by_level).apply(resampler, mode=mode, _grouped_level=group_by_level, **kwargs)
    else:
        if _grouped_level is not None:
            x.index = x.index.droplevel(level=_grouped_level)
        if mode == 'norm_to_even':
            # keep q percent of top & bottom of samples and random sample the same
            # amount of kept samples from the rest
            q = kwargs.get('q', 0.15)
            assert q < 0.25
            up_lim = x.quantile(q=1-q)
            down_lim = x.quantile(q=q)
            _up = x.loc[x >= up_lim].index
            _down = x.loc[x <= down_lim].index
            _res = _up.union(_down)
            _mid = x.reindex(x.index.difference(_res)).sample(frac=2*q/(1-2*q), replace=False, random_state=random_state).index
            res = x.reindex(_res.union(_mid))
        elif mode == 'drop_bottom':
            # drop bottom q percent of samples
            q = kwargs.get('q', 0.15)
            down_lim = x.quantile(q=q)
            res = x.reindex(x.loc[x >= down_lim].index)
        else:
            raise NotImplementedError
        return res


class XGBoostModel:
    def __init__(self, params=None, num_round=1000, early_stopping_rounds=50, verbose=False):
        if params is None:
            self.load_default_params()
        else:
            self.params = params
        self.num_round = num_round
        self.early_stopping_rounds = early_stopping_rounds
        self.verbose = verbose
        self.boost_model = None

    def load_default_params(self):
        self.params = {'booster': 'gbtree',
                       'max_depth': 6,
                       'eta': 0.3,  # learning rate
                       'gamma': 0,  # min split loss
                       'silent': 0,  # 0, 1 for silent mode
                       'nthread' : 8,  # num of processes
                       'subsample': 0.8,  # percentage of samples randomly selected
                       'colsample_bytree': 0.8, # percentage of features randomly selected
                       'alpha': 0.5,  # L1 regularization
                       'lambda': 0.5,  # L2 regularization
                       'eval_metric': 'auc',
                       'objective': 'binary:logistic'}

    def dump_params(self):
        return copy.deepcopy(self.params)

    def fit(self, x, y, monotone=None, **kwargs):
        params = self.params.copy()
        if monotone is not None:
            assert monotone in [-1, 1]
            params['monotone_constraints'] = str(tuple([monotone] * len(x.columns)))
        kwargs['dmatrix'] = True
        kwargs['objective'] = params['objective']
        if kwargs['eval_pct'] is None:
            dtrain = self.prepare_xy(x, y, **kwargs)
            # the point of cv is to find out best num_boost_round
            cv_results = xgb.cv(params, dtrain, num_boost_round=self.num_round, nfold=kwargs['nfold'],
                                early_stopping_rounds=self.early_stopping_rounds, verbose_eval=self.verbose,
                                metrics=params['eval_metric'], stratified=True, shuffle=True)
            evals_result = dict()  # store eval results
            print('best num_boost_round during cv: %d' % cv_results.shape[0])
            boost_model = xgb.train(params, dtrain, num_boost_round=cv_results.shape[0],
                                    evals=[(dtrain, 'train')],
                                    evals_result=evals_result, verbose_eval=self.verbose)
            boost_model.best_ntree_limit = cv_results.shape[0]
            if params['eval_metric'] == 'auc':
                boost_model.best_score = max(evals_result['train'][params['eval_metric']])
            else:
                raise NotImplementedError('metric direction should be further defined')
        else:
            dtrain, deval = self.prepare_xy(x, y, **kwargs)
            boost_model = xgb.train(params, dtrain, num_boost_round=self.num_round,
                                    evals=[(dtrain, 'train'), (deval, 'eval')],
                                    early_stopping_rounds=self.early_stopping_rounds, verbose_eval=self.verbose)
        print('get best eval %s: %f, in step %d' % (self.params['eval_metric'],
                                                    boost_model.best_score, boost_model.best_ntree_limit))
        self.boost_model = boost_model

    def hp_fit(self, x, y, **kwargs):
        kwargs['num_round'] = self.num_round
        kwargs['verbose'] = self.verbose
        kwargs['early_stopping_rounds'] = self.early_stopping_rounds
        kwargs['dmatrix'] = True
        if kwargs['eval_pct'] is None:
            dtrain = self.prepare_xy(x, y, **kwargs)
            deval = None
        else:
            dtrain, deval = self.prepare_xy(x, y, **kwargs)
        self.params, self.boost_model = hp_xgb_fit(dtrain, deval, **kwargs)

    def get_feature_importance(self, importance_type='weight'):
        assert self.boost_model is not None
        importance = pd.Series(self.boost_model.get_score(fmap='xgb.fmap', importance_type=importance_type))
        return importance / importance.sum()

    def predict(self, test_data, index=None, infinite=np.nan):
        assert self.boost_model is not None
        dtest = xgb.DMatrix(fill_infinite(test_data, value=infinite))
        predict_score = self.boost_model.predict(dtest, ntree_limit=self.boost_model.best_ntree_limit)
        if index is None:
            return predict_score
        else:
            return pd.Series(predict_score, index=index)

    def prepare_xy(self, x, y, **kwargs):
        """
        infinite: used to fill infinite values
        eval_pct: percentage reserved for evaluation
        for binary:logistic problems:
        q: percentage to be tagged (1 for not flipped)
        flipped: flip the 0 / 1 tag
        balanced_eval: True / False for validation set generation
        """
        assert np.all([isinstance(item, pd.DataFrame) for item in [x]])
        assert np.all([isinstance(item, pd.Series) for item in [y]])
        # prepare labels
        create_feature_map(x.columns)
        return prepare_xy_helper(x, y, **kwargs)


def prepare_xy_helper(x, y, **kwargs):
    infinite=kwargs.get('infinite', np.nan)
    _y = y.reindex(x.index)
    if isinstance(y.index, pd.MultiIndex):
        # leave y unstacked to split precisely to certain date
        _y = _y.unstack()
    if kwargs['eval_pct'] is not None:
        if isinstance(y.index, pd.MultiIndex):  # alpha tag
            train_y, val_y = split_train_eval(_y, eval_pct=kwargs['eval_pct'], infinite=infinite)
            train_x, val_x = split_train_eval(x, eval_pct=kwargs['eval_pct'], infinite=infinite)
            # validation set ignore ewm
            if kwargs['objective'] == 'binary:logistic':
                kwargs['balanced'] = True  # normally train set samples should be balanced
                train_res = xy_tagger(train_x, train_y, **kwargs)
                if kwargs['qscaler'] is not None:
                    kwargs['q'] = kwargs['q'] * kwargs['qscaler']
                # eval set should be set according to user needs
                kwargs['balanced'] = kwargs['balanced_eval']
                kwargs['use_ewm'] = False
                val_res = xy_tagger(val_x, val_y, **kwargs)
            elif kwargs['objective'] in ['rank:pairwise', 'rank:ndcg', 'rank:map']:
                train_res = xy_tagger(train_x, train_y, **kwargs)
                kwargs['use_ewm'] = False
                val_res = xy_tagger(val_x, val_y, **kwargs)
            else:
                raise NotImplementedError
        else:  # time series tag
            kwargs['balanced'] = kwargs['balanced_eval']
            train_res, val_res = ts_xy_tagger(x, _y, **kwargs)
        if kwargs['dmatrix']:
            res = (train_res, val_res)
        else:
            res = (*train_res, *val_res)
    else:
        # if user needs unbalanced tags, 'balanced' tag should be set directly
        train_y = fill_infinite(_y, value=infinite)
        train_x = fill_infinite(x, value=infinite)
        res = xy_tagger(train_x, train_y, **kwargs)
    return res


def ts_xy_tagger(x, y, objective, **kwargs):
    infinite=kwargs.get('infinite', np.nan)
    # remember to stack y after labeling it
    if objective == 'binary:logistic':
        y_label = binary_tagger(y, q=kwargs['q'], flipped=kwargs['flipped'],
                                balanced=kwargs['balanced'])
        assert isinstance(y_label, pd.Series)
        y_label = y_label.dropna()
    else:
        raise NotImplementedError
    x = x.reindex(y_label.index)
    # split train validation sets after tagging
    train_y, val_y = split_train_eval(y_label, eval_pct=kwargs['eval_pct'], infinite=infinite)
    train_x, val_x = split_train_eval(x, eval_pct=kwargs['eval_pct'], infinite=infinite)
    if kwargs['dmatrix']:
        train_res = dmatrix_helper(train_x, train_y, kwargs['use_ewm'], objective=objective)
        # validation set ignore ewm
        val_res = dmatrix_helper(val_x, val_y, False, objective=objective)
        res = (train_res, val_res)
    else:
        res = ((train_x, train_y), (val_x, val_y))
    return res


def dmatrix_helper(x, y_label, use_ewm, objective=None):
    if objective == 'binary:logistic':
        if use_ewm:
            xy_weight = ewm_helper(y_label)
        else:
            xy_weight = None
        res = xgb.DMatrix(x, label=y_label, weight=xy_weight)
    elif objective in ['rank:pairwise', 'rank:ndcg', 'rank:map']:
        # ranker requires weight for each group instead of sample
        assert isinstance(y_label, pd.Series) and isinstance(y_label.index, pd.MultiIndex)
        res = xgb.DMatrix(x, label=y_label)
        group_num = y_label.groupby(level=0).count()
        res.set_group(np.array(group_num))
        if use_ewm:
            group_weight = ewm_helper(group_num)
            res.set_weight(np.array(group_weight, dtype=np.double))
    else:
        raise NotImplementedError
    return res


def xy_tagger(x, y, objective, **kwargs):
    # remember to stack y after labeling it
    if objective == 'binary:logistic':
        y_label = binary_tagger(y, q=kwargs['q'], flipped=kwargs['flipped'],
                                balanced=kwargs['balanced'])
    elif objective in ['rank:pairwise', 'rank:ndcg', 'rank:map']:
        y_label = rank_tagger(y, q=kwargs['nrank'])
    else:
        raise NotImplementedError
    if isinstance(y_label, pd.DataFrame):
        y_label = y_label.stack()
    else:
        y_label = y_label.dropna()
    # ranker requires sorted samples
    y_label = y_label.sort_index()
    x = x.reindex(y_label.index)
    if kwargs['dmatrix']:
        res = dmatrix_helper(x, y_label, kwargs['use_ewm'], objective=objective)
    else:
        res = x, y_label
    return res


def hp_xgb_helper(space):
    dtrain = space['dtrain']
    deval = space['deval']
    params = {item: space[item] for item in \
             ['booster', 'max_depth', 'eta', 'gamma',
              'silent', 'nthread', 'subsample', 'colsample_bytree',
              'alpha', 'lambda', 'eval_metric', 'objective']}
    monotone = space.get('monotone', None)
    if monotone is not None:
        assert monotone in [-1, 1]
        params['monotone_constraints'] = str(tuple([monotone] * len(dtrain.feature_names)))
    try:
        if deval is None:
            # the point of cv is to find out best num_boost_round
            cv_results = xgb.cv(params, dtrain, num_boost_round=space['num_round'], nfold=space['nfold'],
                                early_stopping_rounds=space['early_stopping_rounds'], verbose_eval=space['verbose'],
                                metrics=params['eval_metric'], stratified=True, shuffle=True)
            evals_result = dict()  # store eval results
            print('best num_boost_round during cv: %d' % cv_results.shape[0])
            boost_model = xgb.train(params, dtrain, num_boost_round=cv_results.shape[0],
                                    evals=[(dtrain, 'train')],
                                    evals_result=evals_result, verbose_eval=space['verbose'])
            boost_model.best_ntree_limit = cv_results.shape[0]
            if params['eval_metric'] == 'auc':
                boost_model.best_score = max(evals_result['train'][params['eval_metric']])
            else:
                raise NotImplementedError('metric direction should be further defined')
        else:
            boost_model = xgb.train(params, dtrain, num_boost_round=space['num_round'],
                                    evals=[(dtrain, 'train'), (deval, 'eval')],
                                    early_stopping_rounds=space['early_stopping_rounds'], verbose_eval=space['verbose'])
        print('get best eval %s: %f, in step %d' % (params['eval_metric'],
                                                    boost_model.best_score, boost_model.best_ntree_limit))
        if params['eval_metric'] == 'auc':
            # drop things cannot be pickled
            del space ['dtrain']
            del space ['deval']
            res = {'loss': -boost_model.best_score,
                   'status': 'ok',
                   'xgb_model': pickle.dumps(boost_model),
                   'space': pickle.dumps(space)}
        else:
            raise NotImplementedError('metric direction should be further defined')
    except Exception:
        print('exception happend:')
        traceback.print_exc(file=sys.stdout)
        print(params)
        res = {'loss': np.nan, 'status': 'fail'}
    return res


def hp_xgb_fit(dtrain, deval, search_space=None,
               nthread=10, monotone=None, num_round=1000, verbose=False, use_ewm=True,
               booster='gbtree', silent=0, eval_metric='auc', objective='binary:logistic',
               suggest='tpe.suggest', max_evals=100, early_stopping_rounds=50, nfold=5, **kwargs):
    if search_space is None:
        search_space = {'dtrain': dtrain,
                        'deval': deval,
                        'monotone': monotone,
                        'num_round': num_round,
                        'verbose': verbose,
                        'use_ewm': use_ewm,
                        'booster': booster,
                        'max_depth': 3 + hp.randint('max_depth', 7),
                        'eta': hp.loguniform('eta', 0, 3) * 0.025 - 0.015,
                        'gamma': hp.loguniform('gamma', 0, 5) / np.exp(5),
                        'silent': silent,
                        'nthread': nthread,
                        'subsample': hp.uniform('subsample', 0.5, 1),
                        'colsample_bytree': hp.uniform('colsample_bytree', 0.2, 1),
                        'alpha': (hp.loguniform('alpha', 0, 2) - 1) / (np.exp(2) - 1),
                        'lambda': hp.loguniform('lambda', np.log(0.5), np.log(4)),
                        'early_stopping_rounds': early_stopping_rounds,
                        'nfold': nfold,
                        'eval_metric': eval_metric,
                        'objective': objective}
    else:
        search_space.update({'dtrain': dtrain,
                             'deval': deval,
                             'monotone': monotone,
                             'num_round': num_round,
                             'verbose': verbose,
                             'use_ewm': use_ewm,
                             'booster': booster,
                             'silent': silent,
                             'nthread': nthread,
                             'early_stopping_rounds': early_stopping_rounds,
                             'nfold': nfold,
                             'eval_metric': eval_metric,
                             'objective': objective})
    trials = Trials()
    fmin(hp_xgb_helper, space=search_space, algo=eval(suggest), max_evals=max_evals, trials=trials)
    scores = [item['loss'] for item in trials.results]
    best_score = np.nanmin(scores)
    if search_space['eval_metric'] == 'auc':
        print('hyperopt best %s: %.3f' % (search_space.get('eval_metric', 'auc'), -best_score))
    else:
        raise NotImplementedError('metric direction should be further defined')
    best_space = pickle.loads(trials.results[scores.index(best_score)]['space'])
    best_xgb_model = pickle.loads(trials.results[scores.index(best_score)]['xgb_model'])
    return best_space, best_xgb_model


def ewm_helper(y, denominator=3):
    if isinstance(y.index, pd.MultiIndex):
        res = y.unstack()
        total_len = len(res)
        _ = ut.weight_decay(int(total_len / denominator), total_len).reshape((-1, 1))
        res[:] = _ / np.mean(_)
        return res.stack().reindex(y.index)
    else:
        res = y.copy()
        total_len = len(res)
        _ = ut.weight_decay(int(total_len / denominator), total_len)
        res[:] = _ / np.mean(_)
        return res


def binary_helper(x, q=0.2, flipped=False, p=None):
    if p is None:
        p = 1 - q
    assert p >= q
    up_lim = x.quantile(q=p)
    down_lim = x.quantile(q=q)
    up = x.loc[x >= up_lim].copy()
    down = x.loc[x <= down_lim].copy()
    if not flipped:
        up[:] = 1
        down[:] = 0
    else:
        up[:] = 0
        down[:] = 1
    return pd.concat([up, down], axis=0).reindex(x.index)


def binary_tagger(y, q, flipped, balanced):
    if balanced:
        p = 1 - q
    else:
        if not flipped:
            q = 1 - q
            p = q
        else:
            p = q
    if isinstance(y, pd.DataFrame):
        return y.apply(binary_helper, axis=1, q=q, p=p, flipped=flipped)
    elif isinstance(y, pd.Series):
        return binary_helper(y, q=q, p=p, flipped=flipped)
    else:
        raise NotImplementedError


def rank_tagger(y, q):
    if isinstance(y, pd.DataFrame):
        return y.apply(pd.qcut, axis=1, raw=False, q=q, labels=False, retbins=False)
    elif isinstance(y, pd.Series):
        assert isinstance(y.index, pd.MultiIndex)
        return y.groupby(level=0).apply(pd.qcut, q=q, labels=False, retbins=False)
    else:
        raise NotImplementedError


def split_train_eval(df, eval_pct=0.2, infinite=None, flipped=True):
    assert isinstance(df, pd.DataFrame) or isinstance(df, pd.Series)
    if isinstance(df.index, pd.MultiIndex):  # ['dt', 'Ticker'] style
        assert df.index.is_lexsorted()
        dummy = pd.Series(True, df.index).unstack()  # only split on level 0
        dummy_train_set, dummy_eval_set = split_train_eval(dummy, eval_pct=eval_pct,
                                                           infinite=None, flipped=flipped)
        train_set = df.reindex(dummy_train_set.stack().index)
        eval_set = df.reindex(dummy_eval_set.stack().index)
    else:
        if not flipped:
            split_idx = int(len(df) * (1 - eval_pct))
            train_set, eval_set = df.iloc[:split_idx], df.iloc[split_idx:]
        else:
            split_idx = int(len(df) * eval_pct)
            eval_set, train_set = df.iloc[:split_idx], df.iloc[split_idx:]
    if infinite is not None:
        train_set = fill_infinite(train_set, value=infinite)
        eval_set = fill_infinite(eval_set, value=infinite)
    return train_set, eval_set


def create_feature_map(features):
    with open('xgb.fmap', 'w') as fout:
        i = 0
        for feat in features:
            fout.write('{0}\t{1}\tq\n'.format(i, feat))
            i = i + 1


