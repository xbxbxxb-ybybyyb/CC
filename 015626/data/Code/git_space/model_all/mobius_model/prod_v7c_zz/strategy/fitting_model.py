import gc, json, sys, os, random
import numpy as np
import pandas as pd
import scipy.optimize as optimize
from scipy import linalg
from scipy.special import boxcox1p
from matplotlib import pyplot

sys.path.insert(0, '..')
from strategy.strategy_utility import *

seed = 2018
np.random.seed(seed)
random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)

from sklearn.metrics import r2_score, mean_squared_error, median_absolute_error, roc_auc_score, precision_score
from sklearn.linear_model import LinearRegression, ElasticNetCV, ElasticNet, Lasso, RandomizedLasso, LassoLarsIC,HuberRegressor, LassoCV, LogisticRegressionCV, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, ExtraTreesClassifier,ExtraTreesRegressor
from sklearn.model_selection import KFold, StratifiedKFold, TimeSeriesSplit
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVR
from sklearn.decomposition import PCA, KernelPCA
from sklearn.preprocessing import StandardScaler, LabelEncoder

from catboost import CatBoostClassifier, CatBoostRegressor
import lightgbm as lgb
import xgboost as xgb

import tensorflow as tf
from keras.layers import Dense, Dropout, Activation, Dense, Conv1D, Conv2D, ConvLSTM2D, Bidirectional,TimeDistributed, LSTM, GRU, ELU, PReLU
from keras.layers.advanced_activations import LeakyReLU, PReLU, ThresholdedReLU
from keras.models import Sequential, model_from_yaml, load_model
from keras.utils import to_categorical, np_utils
from keras import regularizers

from keras.backend.tensorflow_backend import set_session, clear_session, get_session
from tensorflow.python.platform import gfile
from tensorflow.python.framework import graph_util, graph_io

from keras.callbacks import EarlyStopping
from keras.layers.normalization import BatchNormalization
from keras import backend as K
from keras.callbacks import ReduceLROnPlateau
from keras.optimizers import Adam
from keras.initializers import glorot_normal

try:
    import onnx
    import onnxruntime as ort
except:
    1 == 1


# print('import onnx error')


def set_seed(seed=2018):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.set_random_seed(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    os.environ['TF_CUDNN_DETERMINISTIC'] = '1'
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    return


set_seed()

#####################################################################################
"""
data process & normalize
"""


# def binarize_helper(x):
#     x_bin = Binarizer(threshold=0).fit_transform(x)
#     x_bin = place_back_format(x_bin, x)
#     x_bin_encode = get_dummies_helper(x_bin)
#     return x_bin_encode


def get_bin_number(val, bin_num=3, val_range=[0, 1]):
    """assume val in [0,1]"""
    val_range.sort()
    val_max, val_min = val_range[1], val_range[0]
    range_size = val_max - val_min
    if val >= val_max:
        val = val_max - 1e-6
    if val < val_min:
        val = val_min
    if np.isfinite(val):
        val_bin = range_size / bin_num
        bin_number = int(np.floor((val - val_min) / val_bin) + 1)
    # bin_number = min(bin_number,bin_num)
    else:
        bin_number = np.nan
    return bin_number


def use_spec_fold_helper(res_dict_model, fold_list):
    pred_by_fold_raw = pd.concat(list(res_dict_model['misc'].values()), axis=0).sort_index()
    pred_raw_spec_fold = pred_by_fold_raw[fold_list].mean(axis=1)
    return pred_raw_spec_fold


# def discretize_helper(x, bin_num, val_range=[-1, 1]):
#     # x_bin = Binarizer(threshold=0).fit_transform(x)
#     # x_bin = place_back_format(x_bin,x)
#     get_bin_number_itr = partial(get_bin_number, bin_num=bin_num, val_range=val_range)
#     x_bin = x.applymap(get_bin_number_itr)
#     x_bin_encode = get_dummies_helper(x_bin)
#     return x_bin_encode


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
        x_test = x.iloc[sdate_pred_ts_idx:]
    if process_list == 'x':
        process_dat_func = partial(process_dat_wrapper,
                                   process_func=StandardScaler(),
                                   process_col_list=None)
        scaler_dict = process_dat_func(x_train.fillna(0), x_test.fillna(0))
        x_train, x_test = scaler_dict['train'], scaler_dict['test']
    return x_train, x_test


#####################################################################################
"""prediction evalutation"""


#####################################################################################

def eval_pred_helper(y_true, y_pred):
    y_true = y_true.reindex(index=y_pred.index)
    eval_res_dict = {}
    eval_dict = {'r2_score': r2_score,
                 'mean_squared_error': mean_squared_error,
                 'median_absolute_error': median_absolute_error
                 }
    for eval_func_name in eval_dict:
        eval_score = eval_dict[eval_func_name](y_true, y_pred)
        eval_res_dict[eval_func_name] = eval_score
    eval_df = pd.DataFrame(list(eval_res_dict.items()))
    eval_df = eval_df.set_index(0)
    eval_df.columns = y_true.index[[-1]]
    return eval_df


def prep_eval_data(y_true, y_pred):
    if isinstance(y_pred, pd.Series):
        y_pred = pd.DataFrame(y_pred)
    if isinstance(y_true, pd.Series):
        y_true = pd.DataFrame(y_true)
    y_pred.columns = y_true.columns
    date_list = np.intersect1d(y_pred.dropna(how='all').index.tolist(), y_true.dropna(how='all').index.tolist())
    col_list = np.intersect1d(y_pred.dropna(how='all').columns.tolist(), y_true.dropna(how='all').columns.tolist())
    return y_true.reindex(index=date_list, columns=col_list), y_pred.reindex(index=date_list, columns=col_list)


def eval_iter_wrapper(y_true, y_pred, eval_func=eval_pred_helper, eval_type='ts'):
    # no multiple columns
    if eval_type == 'ts':
        eval_list = y_pred.columns.tolist()
    elif eval_type == 'cs':
        eval_list = y_pred.index.tolist()
    res_list = []
    if eval_type == 'ts':
        eval_res = eval_func(y_true, y_pred)
    # eval_res.columns = y_pred.columns
    elif eval_type == 'cs':
        for col in eval_list:
            _ = eval_func(y_true.loc[col], y_pred.loc[col])
            _.columns = [col]
            res_list.append(_)
        eval_res = pd.concat(res_list, axis=1).T
    return eval_res


def eval_pred(y_true, y_pred, eval_func=eval_pred_helper, eval_type='ts', roll_win=None):
    y_true, y_pred = prep_eval_data(y_true, y_pred)
    if y_pred.shape[1] > 1:
        col_list = y_pred.columns.tolist()
        col_res = []
        for col in col_list:
            col_res.append(eval_iter_wrapper(y_true[[col]], y_pred[[col]], eval_func, eval_type))
        eval_res = pd.concat(col_res, axis=1)
        eval_res.columns = col_list
        eval_res = eval_res.T
    else:
        if roll_win is None:
            eval_res = eval_iter_wrapper(y_true, y_pred, eval_func, eval_type)
        else:
            date_list = y_pred.index.tolist()
            date_num = len(date_list)
            eval_list = []
            for i in range(roll_win, date_num):
                date_list_iter = date_list[i - roll_win:i]
                eval_res_iter = eval_iter_wrapper(y_true.loc[date_list_iter], y_pred.loc[date_list_iter], eval_func, eval_type)
                eval_list.append(eval_res_iter)
            eval_res = pd.concat(eval_list, axis=1).T
    return eval_res


def eval_ts_pred(y_true, y_pred, roll_win=20):
    eval_res = eval_pred(y_true, y_pred, eval_func=eval_pred_helper, eval_type='ts')
    print(eval_res)
    y_comb = pd.concat([y_true, y_pred], axis=1)
    y_comb.columns = ['true', 'pred']
    y_diff = y_comb['true'] - y_comb['pred']
    y_comb.rolling(window=roll_win).mean().plot(figsize=[11, 3], title='True vs Prediction')
    plt.show()
    y_diff.rolling(window=roll_win).mean().plot(figsize=[11, 3], title='Diff')
    plt.show()
    return eval_res


def evel_pred_multi(y_test, pred_df):
    res_iter_list = []
    for n in pred_df:
        res_iter = eval_pred(y_test, pred_df[n])
        res_iter_list.append(res_iter)
    res = pd.concat(res_iter_list, axis=1)
    res.columns = pred_df.columns
    return res


#####################################################################################
#####################################################################################


def prep_predict_input(y, x, min_pct=None):
    return  # y_prep,x_prep


def pred_template(x, model, pred='regression', best_iteration=False):
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x_type = 'pd'
        x_np = x.values
    else:
        x_type = 'np'
        x_np = x
    if pred == 'regression':
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


# pred_template for onnx model
def pred_template_onnx(x, model):
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x_type = 'pd'
        x_np = x.values
    else:
        x_type = 'np'
        x_np = x
    ort_sess = ort.InferenceSession(model)
    ys = []
    for t in range(x_np.shape[0]):
        xt = x_np[t:t + 1]
        res = ort_sess.run(None, {ort_sess.get_inputs()[0].name: xt.astype(np.float32)})
        ys.append(res[0])
    y_np = np.concatenate(ys, axis=0)
    return y_np


def change_h5_path_helper(model_fold_itr, res_base_path):
    file_name = os.path.basename(model_fold_itr)
    dest_root = res_base_path.split('.')[0]
    model_fold_itr = os.path.join(dest_root, file_name)
    return model_fold_itr


def pred_helper(x_test, model_dict, pred='regression', check_time=True, return_itr=False, res_base_path=None):
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
            if res_base_path is not None:
                model_fold_itr = change_h5_path_helper(model_fold_itr, res_base_path)
            # ****************************************************************
            if ('source' in model_dict) and (model_dict['source'] == 'onnx'):
                model_fold_itr = onnx.load(model_fold_itr)
                onnx.checker.check_model(model_fold_itr)
                # print(onnx.helper.printable_graph(model_fold_itr.graph))
                model_fold_itr = model_fold_itr.SerializeToString()
                if len(model_dict['config']['input_shape']) == 3:
                    time_step = model_dict['config']['input_shape'][1]
                    pred_idx = len(x_test_fold) - time_step + 1
                    pred_index = x_test_fold.iloc[-pred_idx:].index
                    pred_shape = len(pred_index)
                    x_test_fold = transform_2d_3d_helpher(x_test_fold.values, None, time_step)
                else:
                    pred_index = x_test_fold.index
            # ****************************************************************
            else:
                model_fold_itr = load_model(model_fold_itr)
                model_config = model_fold_itr.get_config()[0]
                if model_config['class_name'] == 'LSTM':  # solve for lstm 3d data, pred return np.array
                    time_step = model_config['config']['batch_input_shape'][1]
                    pred_idx = len(x_test_fold) - time_step + 1
                    pred_index = x_test_fold.iloc[-pred_idx:].index
                    pred_shape = len(pred_index)
                    x_test_fold = transform_2d_3d_helpher(x_test_fold.values, None, time_step)
        # **********************************************************
        if ('source' in model_dict) and (model_dict['source'] == 'onnx'):
            pred_res_itr = pred_template_onnx(x=x_test_fold, model=model_fold_itr)
        # **********************************************************
        else:
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


def pred_helper_lstm(x_fac_test_ts, model_path_itr, time_step=60, pred='classification'):
    pred_np_list = []
    x_test_time_step_3d = transform_2d_3d_helpher(x_fac_test_ts.values, None, time_step)
    pred_idx = len(x_fac_test_ts) - time_step + 1
    pred_index = x_fac_test_ts.iloc[-pred_idx:].index
    model_name = os.path.basename(model_path_itr).split('.')[0]
    model_save_root_itr = os.path.join(os.path.dirname(model_path_itr), model_name)
    model_sr_dict_itr = find_file(model_save_root_itr, 'h5')
    model_h5_list = list(model_sr_dict_itr.keys())
    dt_list = list(set([i.split('_')[0] for i in model_h5_list]))
    fold_list = list(set([int(i.split('_')[1]) for i in model_h5_list]))
    dt_list.sort()
    fold_list.sort()
    ts_take = dt_list[-1]
    model_take_list = ['%s_%s' % (ts_take, i) for i in fold_list]
    fold_num = len(fold_list)
    model_dict = read_pickle(model_path_itr)
    ts_list = list(model_dict['feature_importance'].keys())
    ts_take = ts_list[-1]
    fi_fold = model_dict['feature_importance'][ts_take]

    pred_shape = len(pred_index)
    pred_res = np.zeros(pred_shape)
    print('use model trained on %s with %d fold' % (ts_take, fold_num))
    print('pred shape: %d' % (pred_shape))
    for fold_itr in fold_list:
        print(fold_itr)
        fi_fold_itr = fi_fold[fold_itr]
        fac_list_fold_itr = fi_fold_itr.index.tolist()
        x_test_fold = x_fac_test_ts[fac_list_fold_itr]
        x_test_time_step_3d_fold = transform_2d_3d_helpher(x_test_fold.values, None, time_step)
        model_path_itr_fold = model_sr_dict_itr[model_take_list[fold_itr]]
        model_fold_itr = load_model(model_path_itr_fold)
        pred_np = pred_template(x_test_time_step_3d_fold, model_fold_itr, pred=pred)
        y_preds_k = pd.Series(pred_np.flatten(), index=pred_index)
        pred_np_list.append(y_preds_k)
    pred_res = pd.concat(pred_np_list, axis=1).mean(axis=1)
    return pred_res


###################################


def train_test_split_by_date(x, y, test_size=0.2, validation_by=None):
    """
	:param x:
	:param y:
	:param test_size: percentage of data used for test
	:param validation_by: product to be used in validation step and prediction
	:return: X_train, X_test, y_train, y_test
	"""
    date_list = list(y.index.get_level_values(0).unique())  # could be tick
    date_list.sort()
    date_num = len(date_list)
    if test_size > 1:
        date_num_test = test_size
    else:
        date_num_test = int(date_num * test_size)
    date_num_train = date_num - date_num_test
    date_list_test = date_list[-date_num_test:]
    date_list_train = date_list[:date_num_train]
    X_train, X_test = x.loc[date_list_train], x.loc[date_list_test]
    y_train, y_test = y.loc[date_list_train], y.loc[date_list_test]
    if validation_by is not None:
        X_test = X_test.loc[(slice(None), validation_by), :]
        y_test = y_test.loc[(slice(None), validation_by), :]
    return X_train, X_test, y_train, y_test


def pred_fit_extratree_reg_kf(y_train, x_train, x_test, fold_num=2, params=None,
                              verbose=False, track_feature_importance=True,
                              return_score=False, return_misc=False, return_model=False,
                              std_norm=False, shuffle=False, tsp=False):
    set_seed()
    res_ctn = {}
    if params is None:
        params = {'n_estimators': 1000,
                  'max_depth': 4,
                  'n_jobs': -1}
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle, tsp=tsp)
    y_preds_k = np.zeros(x_test.shape[0])
    score_list, pred_res_list, model_list = [], [], {}
    fi_dict = {}
    for fold_n, (train_index, valid_index) in enumerate(splits):
        model = ExtraTreesRegressor(**params)
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        if std_norm:
            y_train_k_std = y_train_k.std()
            if not isinstance(y_train_k_std, np.float):
                y_train_k_std = y_train_k_std.values
            y_train_k = y_train_k / y_train_k_std
            y_valid_k = y_valid_k / y_train_k_std
        eval_set = [(x_train_k.values, y_train_k.values), (x_valid_k.values, y_valid_k.values)]
        model.fit(x_train_k, y_train_k)
        pred_res_itr = pred_template(x_test, model, pred='regression')
        y_preds_k += pred_res_itr / fold_num
        pred_res_list.append(pred_res_itr)

        if track_feature_importance:
            fi_dict[fold_n] = collect_feature_importance_helper(model, x_train_k)
        if return_score:
            score_list.append(collect_model_score_helper(model, x_train_k, y_train_k))
        del x_train_k, x_valid_k, y_train_k, y_valid_k
        gc.collect()
        if return_misc:
            pred_res_list.append(pred_res_itr)
        if return_model:
            model_list[fold_n] = model
    res_ctn['prediction'] = y_preds_k
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_misc:
        res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list, axis=1))
    if return_score:
        res_ctn['score'] = pd.DataFrame(pd.concat(score_list, axis=1).fillna(0).mean(axis=1), columns=[y_preds_k.index[0]])
    if return_model:
        res_ctn['model'] = model_list
    return res_ctn


def pred_fit_extratree_cla_kf(y_train, x_train, x_test, fold_num=5, params=None,
                              verbose=False, track_feature_importance=True,
                              weight_type='abs_ret', stratified=True, return_score=False,
                              return_misc=False, return_model=False,
                              std_norm=False, shuffle=False, tsp=False):
    set_seed()
    seed = 2018
    res_ctn = {}
    # params = {'n_estimators':1000,'max_depth':4,'n_jobs':-1}
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle, tsp=tsp)
    y_preds_k = np.zeros(x_test.shape[0])
    score_list, pred_res_list, model_list = [], [], {}
    fi_dict = {}
    for fold_n, (train_index, valid_index) in enumerate(splits):
        set_seed()
        model = ExtraTreesClassifier(**params)
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        if std_norm:
            y_train_k_std = y_train_k.std()
            if not isinstance(y_train_k_std, np.float):
                y_train_k_std = y_train_k_std.values
            y_train_k = y_train_k / y_train_k_std
            y_valid_k = y_valid_k / y_train_k_std
        eval_set = [(x_train_k.values, y_train_k.values), (x_valid_k.values, y_valid_k.values)]
        if weight_type is None:
            model.fit(x_train_k, y_train_k)
        else:
            y_train_label_k = y_train_k.copy()
            y_train_label_k[y_train_k.iloc[:, 0] > 0] = 1
            y_train_label_k[y_train_k.iloc[:, 0] <= 0] = 0
            y_train_weight_k = get_sample_weight(y_train_k, weight_type)
            y_train_weight_k[y_train_weight_k > 2] = 2
            if isinstance(y_train_label_k, pd.Series):
                model.fit(x_train_k, y_train_label_k, sample_weight=y_train_weight_k)
            else:
                model.fit(x_train_k, y_train_label_k.iloc[:, 0], sample_weight=y_train_weight_k)
        # model.fit(x_train_k, y_train_label_k.iloc[:,0],sample_weight=y_train_weight_k)
        pred_res_itr = pred_template(x_test, model, pred='classification')
        y_preds_k += pred_res_itr / fold_num
        if track_feature_importance:
            fi_dict[fold_n] = collect_feature_importance_helper(model, x_train_k)
        if return_score:
            score_list.append(collect_model_score_helper(model, x_train_k, y_train_label_k))
        del x_train_k, x_valid_k, y_train_k, y_valid_k
        gc.collect()
        if return_misc:
            pred_res_list.append(pred_res_itr)
        if return_model:
            model_list[fold_n] = model
    res_ctn['prediction'] = y_preds_k
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_misc:
        res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list, axis=1))
    if return_score:
        res_ctn['score'] = pd.DataFrame(pd.concat(score_list, axis=1).fillna(0).mean(axis=1), columns=[y_preds_k.index[0]])
    if return_model:
        res_ctn['model'] = model_list
    return res_ctn


def collect_model_score_helper(model, x_train, y_train, validation_pct=None):
    if isinstance(x_train.index, pd.MultiIndex):
        col = x_train.index[-1][0]
    else:
        col = x_train.index[-1]
    if type(model) in [xgb.XGBClassifier, xgb.XGBRegressor]:
        # if validation_pct is not None:
        if isinstance(y_train, pd.DataFrame):
            model_score = pd.DataFrame([model.best_score], index=y_train.columns, columns=[col])
        else:
            model_score = pd.Series(model.best_score, index=[col])
    # else:
    #    model_score = np.nan
    elif type(model) in [lgb.LGBMRegressor, lgb.LGBMClassifier]:
        if isinstance(y_train, pd.DataFrame):
            model_score = pd.DataFrame(list(model.best_score_['valid'].values()), index=y_train.columns, columns=[col])
        else:
            model_score = pd.Series(list(model.best_score_['valid'].values()), index=[col])
    elif type(model) in [Lasso, ElasticNet, LassoCV, LinearRegression, LassoLarsIC, HuberRegressor,
                         ExtraTreesClassifier, ExtraTreesRegressor]:
        if isinstance(y_train, pd.DataFrame):
            model_score = pd.DataFrame([model.score(x_train, y_train)], index=y_train.columns, columns=[col])
        else:
            model_score = pd.Series([model.score(x_train, y_train)], index=[col])
    else:
        print('model not covered: %s' % (type(model)))
        raise Exception
    return model_score


#######################################
####################################### lightgbm #######################################


def calc_ts_weight_decay(ts_dat, decay_pct=0.8, decay_size=0.8, norm=False):  # 其中n是半衰期，m是序列长度
    total_len = len(ts_dat)
    half_life = int(decay_pct * total_len)
    """last one has highest weight , half life = time to reach 0.5, weight is normalized"""
    weight_list_raw = [decay_size ** ((total_len - i) / half_life) for i in range(total_len)]
    if norm:
        weight_list_norm = weight_list_raw / np.sum(weight_list_raw)
    else:
        weight_list_norm = weight_list_raw  # /np.sum(weight_list_raw)
    weight_decay = place_back_format(weight_list_norm, ts_dat)
    return weight_decay


def learning_rate_010_decay_power_0995(current_iter):
    base_learning_rate = 0.005
    lr = base_learning_rate * np.power(.995, current_iter)
    return lr if lr > 1e-3 else 1e-3


#######################################


def get_data_trunc(dat, cut_limit=0.9999):
    ytu = dat.quantile(cut_limit)
    ytl = dat.quantile(1 - cut_limit)
    print(ytu, ytl)
    dat_trunc = dat.copy()
    dat_trunc[dat_trunc > ytu] = ytu
    dat_trunc[dat_trunc < ytl] = ytl
    return dat_trunc


def get_sample_weight_helper(y_train_k, weight_type='abs_ret', filter_cut=2, trunc_pct=None):
    y_train_label_k = y_train_k.copy()
    y_train_label_k[y_train_k > 0] = 1
    y_train_label_k[y_train_k <= 0] = 0
    y_train_weight_k = get_sample_weight(y_train_k, weight_type, filter_cut, trunc_pct)
    return y_train_weight_k, y_train_label_k


def get_sample_weight(y_train, weight_type='abs_ret', filter_cut=2, trunc_pct=None):
    if weight_type not in ['abs_ret', 'sharpe', 'ret_square']:
        print('weight_type error')
        raise Exception
    if isinstance(y_train, pd.DataFrame):
        y_use = y_train.iloc[:, 0]
    else:
        y_use = y_train
    if trunc_pct is not None:
        y_use = get_data_trunc(y_use, cut_limit=trunc_pct)
    if weight_type == 'abs_ret':
        y_train_abs = np.abs(y_use)
        y_train_weight = y_train_abs / np.sum(y_train_abs) * len(y_train_abs)
    elif weight_type == 'sharpe':
        ret = y_use
        ret_abs = np.abs(ret)
        ret_vol = ret.rolling(120, 1).std()
        ret_sharpe_abs = ret_abs / ret_vol
        ret_sharpe_abs = ret_sharpe_abs.fillna(0)
        y_train_weight = ret_sharpe_abs / np.sum(ret_sharpe_abs) * len(ret_sharpe_abs)
    elif weight_type == 'ret_square':
        ret_sqr = y_use ** 2
        y_train_weight = ret_sqr / np.sum(ret_sqr) * len(ret_sqr)
    if filter_cut is not None:
        y_train_weight[y_train_weight > filter_cut] = filter_cut
    return y_train_weight


def collect_feature_importance_helper(model=None, x_train=None):
    """ if model is None, return dummy list to track factor used """
    if isinstance(x_train.index, pd.MultiIndex):
        col = x_train.index[-1][0]
    else:
        col = x_train.index[-1]
    if model is None:
        fi_raw = np.zeros(len(x_train.columns))
    else:
        if type(model) in [xgb.XGBClassifier, xgb.XGBRegressor, RandomForestClassifier, lgb.LGBMRegressor, 
        				   lgb.LGBMClassifier, ExtraTreesClassifier, ExtraTreesRegressor]:
            fi_raw = model.feature_importances_
        elif type(model) in [Lasso, ElasticNet, LassoCV, LinearRegression, LassoLarsIC, HuberRegressor]:
            fi_raw = model.coef_
        elif type(model) in [LogisticRegression]:
            fi_raw = model.coef_[0]
        elif type(model) in [RandomizedLasso]:
            fi_raw = model.scores_
        else:
            print('feature importance model not covered: %s' % (model))
            raise Exception
    feature_importance = pd.DataFrame(fi_raw, index=x_train.columns, columns=[col])
    return feature_importance


def pred_fit_post_lasso_kf(y_train, x_train, x_test, params=None, fold_num=3, lasso_params=None,
                           verbose=False, track_feature_importance=True,
                           return_score=False, return_misc=False, std_norm=False, std_add_back=False,
                           plot_model=False, return_model=False, shuffle=False, tsp=False):
    if params is None:
        params = {'fit_intercept': True,
                  'normalize': False,
                  'n_jobs': -1}
    if lasso_params is None:
        lasso_params = {'alpha': 0.01,
                        'normalize': False,
                        'fit_intercept': True,
                        'tol': 0.0001,
                        'positive': True,  # not same from default
                        'random_state': 2018}
    set_seed()
    res_ctn = {}
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle, tsp=tsp)

    y_preds_k = np.zeros(x_test.shape[0])
    fi_dict, model_list = {}, {}
    score_list, pred_res_list = [], []
    for fold_n, (train_index, valid_index) in enumerate(splits):
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        eval_set = [(x_train_k.values, y_train_k.values), (x_valid_k.values, y_valid_k.values)]
        model_filter = Lasso(**lasso_params)
        if std_norm:
            y_train_k_std = y_train_k.std()
            if not isinstance(y_train_k_std, np.float):
                y_train_k_std = y_train_k_std.values
            y_train_k = y_train_k / y_train_k_std
        model_filter.fit(x_train_k, y_train_k)
        fi_filter = collect_feature_importance_helper(model_filter, x_train_k)
        fac_filter = fi_filter[fi_filter > 0].dropna()
        fac_filter_list = fac_filter.index.tolist()
        fac_num_use = len(fac_filter_list)
        fac_num = len(fi_filter)
        x_train_filter_k = x_train_k[fac_filter_list]
        x_test_filter = x_test[fac_filter_list]
        print('used %d/%d factors' % (fac_num_use, fac_num))
        model = LinearRegression(**params)
        if isinstance(y_train_k, pd.Series):
            model.fit(x_train_filter_k, y_train_k)
        else:
            model.fit(x_train_filter_k, y_train_k.iloc[:, 0])
        pred_res_itr = pred_template(x_test_filter, model, pred='regression')
        if std_add_back:
            pred_res_itr = pred_res_itr * y_train_k_std
        y_preds_k += pred_res_itr / fold_num
        if return_score:
            score_list.append(collect_model_score_helper(model, x_train_filter_k, y_train_k))
        if return_model:
            model_list[fold_n] = model
        if return_misc:
            pred_res_list.append(pred_res_itr)
        if track_feature_importance:
            fi_dict[fold_n] = collect_feature_importance_helper(model, x_train_filter_k)
        del x_train_k, x_valid_k, y_train_k, y_valid_k
        gc.collect()
    res_ctn['prediction'] = y_preds_k
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_misc:
        res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list, axis=1))
    if return_score:
        res_ctn['score'] = pd.DataFrame(pd.concat(score_list, axis=1).fillna(0).mean(axis=1), columns=[y_preds_k.index[0]])
    if plot_model:
        plot_model_train(model)
    if return_model:
        res_ctn['model'] = model_list
    return res_ctn


def pred_fit_lr_kf(y_train, x_train, x_test, params=None, fold_num=3,
                   verbose=False, track_feature_importance=True, return_score=False,
                   return_misc=False, weight_type='abs_ret', stratified=True,
                   shuffle=True, seed=2018, return_model=False, std_norm=False, tsp=False):
    # seed = 2018
    set_seed()
    res_ctn = {}
    if params is None:
        params = {'C': 1e-5,  # regularize ~ smaller stronger
                  'tol': 1e-4,
                  'class_weight': None,  # ’balanced’
                  'fit_intercept': True,
                  'penalty': 'l2',  # should use l1
                  'tol': 0.0001,
                  'max_iter': 100,
                  'n_jobs': -1,
                  # 'verbose':0,
                  'random_state': 2018}
    params['verbose'] = 2 if verbose else 0
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle, tsp=tsp)

    y_preds_k = np.zeros(x_test.shape[0])
    fi_dict = {}
    score_list, pred_res_list, model_list = [], [], {}
    for fold_n, (train_index, valid_index) in enumerate(splits):
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        if std_norm:
            y_train_k_std = y_train_k.std()
            if not isinstance(y_train_k_std, np.float):
                y_train_k_std = y_train_k_std.values
            y_train_k = y_train_k / y_train_k_std
            y_valid_k = y_valid_k / y_train_k_std
        eval_set = [(x_train_k.values, y_train_k.values), (x_valid_k.values, y_valid_k.values)]
        model = LogisticRegression(**params)
        if weight_type is None:
            model.fit(x_train_k, y_train_k)
        else:
            y_train_label_k = y_train_k.copy()
            y_train_label_k[y_train_k.iloc[:, 0] > 0] = 1
            y_train_label_k[y_train_k.iloc[:, 0] <= 0] = 0
            y_train_weight_k = get_sample_weight(y_train_k, weight_type)
            y_train_weight_k[y_train_weight_k > 2] = 2
            # model.fit(x_train_k, y_train_label_k.iloc[:,0],sample_weight=y_train_weight_k)
            if isinstance(y_train_label_k, pd.Series):
                model.fit(x_train_k, y_train_label_k, sample_weight=y_train_weight_k)
            else:
                model.fit(x_train_k, y_train_label_k.iloc[:, 0], sample_weight=y_train_weight_k)
        pred_res_itr = pred_template(x_test, model, pred='classification')
        y_preds_k += pred_res_itr / fold_num
        if track_feature_importance:
            fi_dict[fold_n] = collect_feature_importance_helper(model, x_train_k)
        if return_score:
            score_list.append(collect_model_score_helper(model, x_train_k, y_train_k))
        if return_model:
            model_list[fold_n] = model
        if return_misc:
            pred_res_list.append(pred_res_itr)

        del x_train_k, x_valid_k, y_train_k, y_valid_k
        gc.collect()
    res_ctn['prediction'] = y_preds_k
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_misc:
        res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list, axis=1))
    if return_score:
        res_ctn['score'] = pd.DataFrame(pd.concat(score_list, axis=1).fillna(0).mean(axis=1), columns=[y_preds_k.index[0]])
    if return_model:
        res_ctn['model'] = model_list
    return res_ctn


###############################
# lgbm_clf_kf


def learning_rate_decay_power(current_iter, base_learning_rate=0.001, lr_decay=0.999, min_ratio=0.5):
    lr = base_learning_rate * np.power(lr_decay, current_iter)
    min_lr = base_learning_rate * min_ratio
    return lr if lr > min_lr else min_lr


def pred_fit_lgbm_cla_kf(y_train, x_train, x_test, param=None, fold_num=2,
                         verbose=True, track_feature_importance=False, return_misc=False,
                         return_score=False, plot_model=False, weight_type='abs_ret',
                         stratified=True, return_model=False, std_norm=False, shuffle=False, tsp=False,
                         filter_cut=None, trunc_pct=None):
    res_ctn = {}
    score_list = []
    model_list, fi_dict = {}, {}
    misc_dict = {}
    if param is None:
        param = {'alpha': 0.1,
                 'booster': 'gbtree',
                 'colsample_bytree': 0.8,
                 'max_depth': 10,
                 'num_leaves': 200,
                 'subsample': 0.4,
                 'learning_rate': 0.0001,
                 'lr_decay': 0.999,
                 'min_ratio': 0.5,
                 'metric': 'auc',
                 'n_estimators': 1000,
                 'n_jobs': -1,
                 'tree_method': 'gpu_hist',
                 'gpu_id': 0}
    if 'learning_rate' in param:
        lr_decay = 0.999 if 'lr_decay' not in param else param['lr_decay']
        min_ratio = 0.5 if 'min_ratio' not in param else param['min_ratio']
        lrdp = partial(learning_rate_decay_power, base_learning_rate=param['learning_rate'], lr_decay=lr_decay, min_ratio=min_ratio)
        # lrdp = partial(learning_rate_decay_power,base_learning_rate=param['learning_rate'],lr_decay=0.999,min_ratio=0.5)
        param = {i: param[i] for i in param if i not in ['lr_decay', 'min_ratio']}
    # k fold prediction
    set_seed()
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle, tsp=tsp)
    y_preds_k = np.zeros(x_test.shape[0])
    pred_res_list = []
    for fold_n, (train_index, valid_index) in enumerate(splits):
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        model = lgb.LGBMClassifier(**param)
        if std_norm:
            y_train_k_std = y_train_k.std()
            if not isinstance(y_train_k_std, np.float):
                y_train_k_std = y_train_k_std.values
            y_train_k = y_train_k / y_train_k_std
            y_valid_k = y_valid_k / y_train_k_std
        if 'eval_metric' in param:
            eval_metric = param['eval_metric']
        elif 'metric' in param:
            eval_metric = param['metric']
        else:
            eval_metric = 'auc'
        fit_params = {"early_stopping_rounds": 20,
                      "eval_metric": eval_metric,
                      "eval_set": [(x_valid_k, y_valid_k)],
                      'eval_names': ['valid'],
                      'callbacks': [lgb.reset_parameter(learning_rate=lrdp)],
                      'verbose': 500,
                      'categorical_feature': 'auto'}
        y_train_label_k = y_train_k.copy()
        y_train_label_k[y_train_k.iloc[:, 0] > 0] = 1
        y_train_label_k[y_train_k.iloc[:, 0] <= 0] = 0
        y_valid_label_k = y_valid_k.copy()
        y_valid_label_k[y_valid_k.iloc[:, 0] > 0] = 1
        y_valid_label_k[y_valid_k.iloc[:, 0] <= 0] = 0
        fit_params['eval_set'] = [(x_valid_k, y_valid_label_k)]
        if weight_type is None:
            model.fit(x_train_k, y_train_label_k, **fit_params)
        else:
            y_train_weight_k = get_sample_weight(y_train_k, weight_type)
            y_train_weight_k[y_train_weight_k > 2] = 2
            if trunc_pct is not None:
                y_train_weight_k = get_sample_weight(y_train_k, weight_type, filter_cut, trunc_pct)
            fit_params['sample_weight'] = y_train_weight_k
            if isinstance(y_train_label_k, pd.Series):
                model.fit(x_train_k, y_train_label_k, **fit_params)
            else:
                model.fit(x_train_k, y_train_label_k.iloc[:, 0], **fit_params)
        pred_res_itr = pred_template(x_test, model, pred='classification')
        y_preds_k += pred_res_itr / fold_num
        pred_res_list.append(pred_res_itr)
        if plot_model:
            lgb.plot_metric(model)
            plt.show()
        if track_feature_importance:
            fi_dict[fold_n] = collect_feature_importance_helper(model, x_train_k)
        # fi_dict[fold_n] = collect_feature_importance_helper(model,x_train)
        if return_score:
            if weight_type is None:
                score_list.append(collect_model_score_helper(model, x_train_k, y_train_k))
            else:
                score_list.append(collect_model_score_helper(model, x_train_k, y_train_label_k))
        """        
		if return_misc:
			misc_dict[fold_n] = pd.DataFrame([model.evals_result_['validation_0'][eval_metric],
											  model.evals_result_['validation_1'][eval_metric]],index=['train','validaiton']).T
		"""
        if return_model:
            model_list[fold_n] = model
        del x_train_k, x_valid_k, y_train_k, y_valid_k
        gc.collect()
    res_ctn['prediction'] = y_preds_k
    pred_res_df = pd.concat(pred_res_list, axis=1)
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_misc:
        res_ctn['misc'] = pred_res_df  # misc_dict
    if return_score:
        res_ctn['score'] = pd.DataFrame(pd.concat(score_list, axis=1).fillna(0).mean(axis=1), columns=[y_preds_k.index[0]])
    if return_model:
        res_ctn['model'] = model_list
    return res_ctn


def pred_fit_lgbm_reg_kf(y_train, x_train, x_test, param=None, fold_num=2,
                         verbose=True, track_feature_importance=False, return_misc=False,
                         return_score=False, plot_model=False, return_model=False,
                         std_norm=False, std_add_back=False, early_stopping_rounds=20,
                         shuffle=False, tsp=False):
    set_seed()
    res_ctn = {}
    score_list = []
    model_list, fi_dict = {}, {}
    misc_dict = {}
    if param is None:
        param = {"eval_metric": 'rmse',
                 'n_jobs': -1,
                 'num_iterations': 2000,
                 'random_state': 2018,
                 'max_depth': -1,
                 'silent': False,
                 'metric': None,
                 'colsample_bytree': 0.6,
                 'min_child_samples': 200,
                 'min_child_weight': 0.01,
                 'num_leaves': 30,
                 'reg_alpha': 5,
                 'reg_lambda': 0,
                 'subsample': 0.5}
    if 'learning_rate' in param:
        lr_decay = 0.999 if 'lr_decay' not in param else param['lr_decay']
        min_ratio = 0.5 if 'min_ratio' not in param else param['min_ratio']
        lrdp = partial(learning_rate_decay_power, base_learning_rate=param['learning_rate'], lr_decay=lr_decay, min_ratio=min_ratio)
        # lrdp = partial(learning_rate_decay_power,base_learning_rate=param['learning_rate'],lr_decay=0.999,min_ratio=0.5)
        param = {i: param[i] for i in param if i not in ['lr_decay', 'min_ratio']}
    # k fold prediction
    """
	if shuffle:
		folds = KFold(n_splits=fold_num,shuffle=shuffle,random_state=2018)
		splits = folds.split(x_train, y_train)
	else:
		if tsp:
			folds = TimeSeriesSplit(n_splits=fold_num)
			splits = folds.split(x_train, y_train)
		else:
			folds = KFold(n_splits=fold_num)
			splits = folds.split(x_train, y_train,x_train.index.date)
	"""
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle, tsp=tsp)
    y_preds_k = np.zeros(x_test.shape[0])
    pred_res_list = []
    for fold_n, (train_index, valid_index) in enumerate(splits):
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        if std_norm:
            y_train_k_std = y_train_k.std()
            if not isinstance(y_train_k_std, np.float):
                y_train_k_std = y_train_k_std.values
            y_train_k = y_train_k / y_train_k_std
            y_valid_k = y_valid_k / y_train_k_std

        model = lgb.LGBMRegressor(**param)
        if 'eval_metric' in param:
            eval_metric = param['eval_metric']
        elif 'metric' in param:
            eval_metric = param['metric']
        else:
            eval_metric = 'rmse'
        fit_params = {"early_stopping_rounds": early_stopping_rounds,
                      "eval_metric": eval_metric,
                      "eval_set": [(x_valid_k, y_valid_k)],
                      'eval_names': ['valid'],
                      'callbacks': [lgb.reset_parameter(learning_rate=lrdp)],
                      'verbose': 500,
                      'categorical_feature': 'auto'}
        model.fit(x_train_k.values, y_train_k.values, **fit_params)
        pred_res_itr = pred_template(x_test, model, pred='regression')
        std_add_back = std_norm
        if std_add_back:
            pred_res_itr = pred_res_itr * y_train_k_std
        y_preds_k += pred_res_itr / fold_num
        pred_res_list.append(pred_res_itr)
        if plot_model:
            lgb.plot_metric(model)
            plt.show()
        if track_feature_importance:
            fi_dict[fold_n] = collect_feature_importance_helper(model, x_train_k)
        if return_score:
            score_list.append(collect_model_score_helper(model, x_train_k, y_train_k))
        if return_misc:
            pred_res_list.append(pred_res_itr)
        if return_model:
            model_list[fold_n] = model
        del x_train_k, x_valid_k, y_train_k, y_valid_k
        gc.collect()
    res_ctn['prediction'] = y_preds_k
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_misc:
        res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list, axis=1))
    if return_score:
        res_ctn['score'] = pd.DataFrame(pd.concat(score_list, axis=1).fillna(0).mean(axis=1), columns=[y_preds_k.index[0]])
    if return_model:
        res_ctn['model'] = model_list
    return res_ctn


###############################################
# lstm


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


# fixed
def data_generator_helper(x_train, y_train, batch_size, shuffle=False, seed=2018, train_weight=None):
    set_seed()
    num_batch = int(np.ceil(len(x_train) / batch_size))
    while True:
        order_list = [i for i in range(x_train.shape[0])]
        if shuffle:
            np.random.shuffle(order_list)
        for i in range(num_batch):
            batch_list = order_list[i * batch_size:(i + 1) * batch_size]
            if shuffle:
                np.random.shuffle(batch_list)
            x_batch = x_train[batch_list]
            y_batch = y_train[batch_list]
            if train_weight is None:
                yield x_batch, y_batch
            else:
                weight_batch = train_weight[batch_list]
                yield x_batch, y_batch, weight_batch


def get_val_size(df, unit='gb'):
    if isinstance(df, np.ndarray):
        df_size = df.size
    elif isinstance(df, pd.DataFrame) or isinstance(df, pd.Series):
        df_size = df.memory_usage().sum()
    if unit == 'gb':
        scale = 1024 ** 3
    elif unit == 'mb':
        scale = 1024 ** 2
    df_size = df_size / scale
    return df_size


def fold_split_helper(x_train, y_train, fold_num, shuffle=False, tsp=False, random_state=2018):
    os.environ['PYTHONHASHSEED'] = str(random_state)
    random.seed(random_state)
    np.random.seed(random_state)
    if shuffle:
        folds = KFold(n_splits=fold_num, shuffle=shuffle, random_state=random_state)
        splits = folds.split(x_train, y_train)
    else:
        if tsp:
            folds = TimeSeriesSplit(n_splits=fold_num)
            splits = folds.split(x_train, y_train)
        else:
            folds = KFold(n_splits=fold_num, random_state=random_state)
            if isinstance(x_train.index, pd.MultiIndex):
                date_info = x_train.index.get_level_values(0).date
            else:
                date_info = x_train.index.date
            splits = folds.split(x_train, y_train, date_info)
    return splits


def pred_fit_lstm_cla_kf(y_train, x_train, x_test, params=None, fold_num=2,
                         res_iter_save_folder=None, return_model=False,
                         verbose=True, track_feature_importance=False, return_misc=False,
                         return_score=False, plot_model=False, stratified=False,
                         use_generator=False, bidirectional=False, time_dist=False, shuffle=False,
                         std_norm=False, rlrop_param=None, gpu_mem_size=8, weight_type='abs_ret', tsp=False):
    if rlrop_param is None:
        rlrop_param = {'factor': 0.5, 'patience': 5}
    seed = 2018
    set_seed()
    res_ctn = {}
    score_dict = {}
    model_dict = {}
    hist_dict = {}
    model_dir_dict = {}
    model_list = {}
    fi_dict = {}
    # parameter
    dropout = params['dropout']
    activation = params['activation']
    layer_list = params['layer']
    first_layer = layer_list[0]
    mid_layer = layer_list[1:-1]
    class_num = layer_list[-1]
    time_step = params['time_step']
    kernel_initializer = params['kernel_initializer']
    pred_type = 'cla' if class_num > 1 else 'reg'
    verbose_num = 1 if verbose else 0  #
    if 'activation_mid' not in params:
        activation_mid = 'tanh'
    else:
        activation_mid = params['activation_mid']

    if 'recurrent_dropout' not in params:
        recurrent_dropout = 0
    else:
        recurrent_dropout = params['recurrent_dropout']

    if 'recurrent_activation' not in params:
        recurrent_activation = 'sigmoid'
    else:
        recurrent_activation = params['recurrent_activation']

    if isinstance(activation, str):
        act_func = Activation(activation)
    else:
        act_func = activation

    # transform data
    # timestep 3d data, requires test data to have n+time_step size for prediction
    edate_train, sdate_test = x_train.index[-1], x_test.index[0]
    x_train_test = pd.concat([x_train, x_test], axis=0)
    x_index_list = x_train_test.index.tolist()
    cut_idx_time_step = x_index_list.index(sdate_test) - time_step + 1
    x_test_time_step = x_train_test.iloc[cut_idx_time_step:, :]
    x_train_time_step = x_train_test.iloc[:cut_idx_time_step, :]
    y_train_time_step = y_train.iloc[:cut_idx_time_step]
    x_train_time_step_np = x_train_time_step.values
    x_test_time_step_np = x_test_time_step.values
    y_train_time_step_np = y_train_time_step.values
    x_train_time_step_3d, y_train_time_step_3d = transform_2d_3d_helpher(x_train_time_step_np, y_train_time_step_np, time_step)
    x_test_time_step_3d = transform_2d_3d_helpher(x_test_time_step_np, None, time_step)
    # k fold prediction
    splits = fold_split_helper(x_train_time_step, y_train_time_step, fold_num, shuffle=shuffle, tsp=tsp)
    y_preds_k = np.zeros(x_test.shape[0])
    for fold_n, (train_index, valid_index) in enumerate(splits):
        set_seed()
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train_time_step.iloc[train_index], x_train_time_step.iloc[valid_index]
        y_train_k, y_valid_k = y_train_time_step.iloc[train_index], y_train_time_step.iloc[valid_index]
        print('transform_2d_to_3d')
        x_train_use_k, y_train_use_k = transform_2d_3d_helpher(x_train_k.values, y_train_k.values, time_step)
        x_eval_use_k, y_eval_use_k = transform_2d_3d_helpher(x_valid_k.values, y_valid_k.values, time_step)
        x_test_time_step_3d_k = transform_2d_3d_helpher(x_test_time_step_np, None, time_step)
        val_set = (x_eval_use_k, y_eval_use_k)

        if weight_type is None:
            sample_weight = None
        else:
            y_train_weight_k, y_train_use_k = get_sample_weight_helper(pd.DataFrame(y_train_use_k),
                                                                       weight_type=weight_type,
                                                                       filter_cut=2)
            y_train_use_k = y_train_use_k.values
            sample_weight = y_train_weight_k.values
        # fit_generator does not support sample_weight
        print('init model')
        # The LSTM architecture
        model = Sequential()
        # First LSTM layer with Dropout regularisation
        if bidirectional:
            model.add(Bidirectional(LSTM(units=first_layer, return_sequences=True, activation=activation_mid,
                                         kernel_initializer=kernel_initializer),
                                    input_shape=(x_train_use_k.shape[1], x_train_use_k.shape[2])))
        else:
            model.add(LSTM(units=first_layer, return_sequences=True, activation=activation_mid,
                           recurrent_dropout=recurrent_dropout, kernel_initializer=kernel_initializer,
                           recurrent_activation=recurrent_activation,
                           input_shape=(x_train_use_k.shape[1], x_train_use_k.shape[2])))
        model.add(BatchNormalization())
        model.add(Dropout(dropout, seed=seed))
        # Second LSTM layer
        # Mid Layer
        layer_num = len(mid_layer)
        for layer_idx in range(1, layer_num + 1):
            rs = False if layer_idx == layer_num else True
            # print(layer_idx,layer_list[layer_idx],rs)
            if bidirectional:
                model.add(Bidirectional(LSTM(units=layer_list[layer_idx], return_sequences=rs, activation=activation_mid,
                                             recurrent_dropout=recurrent_dropout, kernel_initializer=kernel_initializer,
                                             recurrent_activation=recurrent_activation)))
            else:
                model.add(LSTM(units=layer_list[layer_idx], return_sequences=rs, activation=activation_mid,
                               kernel_initializer=kernel_initializer,
                               recurrent_dropout=recurrent_dropout, recurrent_activation=recurrent_activation))
            model.add(BatchNormalization())
            model.add(Dropout(dropout, seed=seed))
        if time_dist:
            model.add(TimeDistributed(units=1, activation=activation, kernel_initializer=kernel_initializer))
        else:
            model.add(Dense(units=1, activation=activation, kernel_initializer=kernel_initializer))
        # compile
        print('compile')
        model.compile(loss=params['loss'], optimizer=Adam(lr=params['learning_rate']), metrics=params['metrics'])
        early_stop = EarlyStopping(monitor='val_loss',  # min_delta=0.0001,
                                   patience=params['callback_patience'],
                                   verbose=verbose_num, mode='auto')  # ,
        # restore_best_weights=True) not in this version
        rlrop = ReduceLROnPlateau(monitor='val_loss', factor=rlrop_param['factor'],
                                  patience=rlrop_param['patience'], verbose=1)
        call_back_spec = [early_stop, rlrop]

        if use_generator:  # lstm
            val_size = get_val_size(x_train_use_k) + get_val_size(y_train_use_k) + get_val_size(x_eval_use_k) + get_val_size(y_eval_use_k)
            scale_ratio = max(gpu_mem_size / val_size, 1)  # if exceed memory,ratio should be smaller than 1
            batch_size = params['batch_size']
            steps_per_epoch = int(np.ceil(len(x_train_use_k) / batch_size / scale_ratio))
            validation_steps = int(np.ceil(len(x_eval_use_k) / batch_size / scale_ratio))
            print('val_size: %.2f / scale_ratio: %.2f / steps_per_epoch: %d' % (val_size, scale_ratio, steps_per_epoch))
            hist = model.fit_generator(data_generator_helper(x_train_use_k, y_train_use_k, batch_size, shuffle),
                                       steps_per_epoch=steps_per_epoch,
                                       epochs=params['epochs'],
                                       validation_data=data_generator_helper(x_eval_use_k, y_eval_use_k, batch_size, shuffle),
                                       validation_steps=validation_steps,
                                       callbacks=call_back_spec,
                                       verbose=verbose_num,
                                       shuffle=shuffle)
        else:
            hist = model.fit(x_train_use_k, y_train_use_k, epochs=params['epochs'], batch_size=params['batch_size'],
                             validation_data=val_set, callbacks=call_back_spec, verbose=verbose_num,
                             shuffle=shuffle, sample_weight=sample_weight)
        print('iter compile done')
        print('make prediction')
        pred_np = pred_template(x_test_time_step_3d, model, pred='classification')
        y_preds_k += pred_np.flatten() / fold_num
        if track_feature_importance:
            fi_dummy_k = collect_feature_importance_helper(model=None, x_train=x_train_k)
            fi_dict[fold_n] = fi_dummy_k
        if plot_model:
            print('plot training process')
            plot_keras_model_train(hist)
            plt.show()
        if return_score:
            score_dict[fold_n] = pd.DataFrame(hist.history)
            print(score_dict[fold_n].tail())
        if res_iter_save_folder is not None:
            if not os.path.exists(res_iter_save_folder):
                os.makedirs(res_iter_save_folder)
            model_ctn_name = 'misc'
            model_name_str = 'model'
            if isinstance(x_test.index, pd.MultiIndex):
                ts_itr = x_test.index[0][0]
            else:
                ts_itr = x_test.index[0]
            ts_str = dt.datetime.strftime(ts_itr, '%Y%m%d%H%M%S')
            itr_path = os.path.join(res_iter_save_folder, '%s_%s.h5' % (ts_str, str(fold_n)))
            model_dir_dict[fold_n] = itr_path
            model.save(itr_path)

        del x_train_k, x_valid_k, y_train_k, y_valid_k
        del x_train_use_k, y_train_use_k, x_eval_use_k, y_eval_use_k
        reset_keras(model, hist)
        for i in range(3): gc.collect()
    print('prediction results collected')
    res_ctn['prediction'] = pd.Series(y_preds_k.flatten(), index=x_test.index)
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_model:
        res_ctn['model'] = model_dir_dict
    if return_misc:
        res_ctn['misc'] = model_dir_dict
    if return_score:
        res_ctn['score'] = score_dict
    return res_ctn


############################################################################################
def get_train_test_sample(y, x, sample_pct=0.5, train_pct=0.75):
    # y_train,y_test,x_train,x_test = get_train_test_sample(y,x,sample_pct=0.5,train_pct=0.75)
    # train 3/4, test 1/4
    row_num = len(y)
    train_num = int(row_num * sample_pct * train_pct)
    test_num = int(row_num * sample_pct * (1 - train_pct))
    y_train, x_train = y.iloc[-train_num:-test_num].dropna(), x.iloc[-train_num:-test_num].dropna()
    y_train = y_train.reindex(index=x_train.index).dropna()
    x_train = x_train.reindex(index=y_train.index).dropna()
    y_test, x_test = y.iloc[-test_num:], x.iloc[-test_num:]
    y_test = y_test.reindex(index=x_test.index).dropna()
    x_test = x_test.reindex(index=y_test.index).dropna()
    print('train time: ', x_train.index[0], x_train.index[-1], '/ sample_size:', x_train.shape)
    print('test time: ', x_test.index[0], x_test.index[-1], '/ sample_size:', x_test.shape)
    return y_train, y_test, x_train, x_test


###################################
#

# def pred_fit_lstm_reg_kf(y_train, x_train, x_test, params=None, fold_num=2, res_iter_save_folder=None,
#                          verbose=True, track_feature_importance=False, return_misc=False,
#                          return_score=False, plot_model=False, scale_input=False):
#     seed = 2018
#     np.random.seed(seed)
#
#     res_ctn = {}
#     score_list = []
#     fi_dict = {}
#     # parameter
#     dropout = params['dropout']
#     activation = params['activation']
#     layer_list = params['layer']
#     first_layer = layer_list[0]
#     mid_layer = layer_list[1:-1]
#     class_num = layer_list[-1]
#     validation_split = params['validation_split']
#     time_step = params['time_step']
#     batch_norm = params['batch_normalization']
#     if class_num > 1:
#         print('wrong layer: %s' % (layer_list))
#         raise Exception
#
#     pred_type = 'cla' if class_num > 1 else 'reg'
#     verbose_num = 1 if verbose else 0  #
#
#     # transform data
#     edate_train, sdate_test = x_train.index[-1], x_test.index[0]
#     x_train_test = pd.concat([x_train, x_test], axis=0)
#     x_index_list = x_train_test.index.tolist()
#     cut_idx_time_step = x_index_list.index(sdate_test) - time_step + 1
#     x_test_time_step = x_train_test.iloc[cut_idx_time_step:, :]
#     x_train_time_step = x_train_test.iloc[:cut_idx_time_step, :]
#     y_train_time_step = y_train.iloc[:cut_idx_time_step]
#     x_train_time_step_np = x_train_time_step.values
#     x_test_time_step_np = x_test_time_step.values
#     y_train_time_step_np = y_train_time_step.values
#     x_train_time_step_3d, y_train_time_step_3d = transform_2d_3d_helpher(x_train_time_step_np, y_train_time_step_np, time_step)
#     x_test_time_step_3d = transform_2d_3d_helpher(x_test_time_step_np, None, time_step)
#     # x_train_use, x_eval, y_train_use, y_eval = train_test_split(x_train_time_step_3d, y_train_time_step_3d,test_size=validation_split, shuffle=False)
#
#     # k fold prediction
#     folds = KFold(n_splits=fold_num)
#     splits = folds.split(x_train_time_step, y_train_time_step)
#     y_preds_k = np.zeros(x_test.shape[0])
#     for fold_n, (train_index, valid_index) in enumerate(splits):
#         print('Fold:', fold_n + 1)
#         x_train_k, x_valid_k = x_train_time_step.iloc[train_index], x_train_time_step.iloc[valid_index]
#         y_train_k, y_valid_k = y_train_time_step.iloc[train_index], y_train_time_step.iloc[valid_index]
#         if scale_input:
#             print('scale input')
#             scaler_dict = process_dat_wrapper(x_train=y_train_k, x_test=y_valid_k,
#                                               process_func=StandardScaler())
#             y_train_k = scaler_dict['train']
#             y_valid_k = scaler_dict['test']
#             scaler = scaler_dict['scaler']
#         x_train_use_k, y_train_use_k = transform_2d_3d_helpher(x_train_k.values, y_train_k.values, time_step)
#         x_eval_use_k, y_eval_use_k = transform_2d_3d_helpher(x_valid_k.values, y_valid_k.values, time_step)
#         x_test_time_step_3d_k = transform_2d_3d_helpher(x_test_time_step_np, None, time_step)
#
#         if pred_type == 'cla':  # - convert to dummay - 2 columns
#             y_train_use_k = np_utils.to_categorical(y_train_use_k)
#             y_eval_use_k = np_utils.to_categorical(y_eval_use_k)
#         else:
#             y_eval_use_k = y_eval_use_k
#         val_set = (x_eval_use_k, y_eval_use_k)
#
#         # The LSTM architecture
#         model = Sequential()
#         # First LSTM layer with Dropout regularisation
#         model.add(LSTM(units=first_layer, return_sequences=True,
#                        input_shape=(x_train_use_k.shape[1], x_train_use_k.shape[2])))
#         if batch_norm:
#             model.add(BatchNormalization())
#             model.add(act_func)
#         model.add(Dropout(dropout))
#         # Second LSTM layer
#         # Mid Layer
#         layer_num = len(mid_layer)
#         for layer_idx in range(1, layer_num + 1):
#             rs = False if layer_idx == layer_num else True
#             print(layer_idx, layer_list[layer_idx], rs)
#             model.add(LSTM(units=layer_list[layer_idx], return_sequences=rs))
#             if batch_norm:
#                 model.add(BatchNormalization())
#                 model.add(act_func)
#             model.add(Dropout(dropout))
#
#         model.add(Dense(units=1, activation=activation))
#
#         # compile
#         model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=params['metrics'])
#         early_stop = EarlyStopping(monitor='val_loss', min_delta=0.0001,
#                                    patience=params['callback_patience'],
#                                    verbose=verbose_num, mode='auto')
#         rlrop = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
#         call_back_spec = [early_stop, rlrop]
#         hist = model.fit(x_train_use_k, y_train_use_k, epochs=params['epochs'], batch_size=params['batch_size'],
#                          validation_data=val_set, callbacks=call_back_spec, verbose=verbose_num)
#
#         print('iter compile done')
#
#         if plot_model:
#             print('plot training process')
#             plot_keras_model_train(hist)
#             plt.show()
#         if track_feature_importance:
#             fi_dummy_k = collect_feature_importance_helper(model=None, x_train=x_train_k)
#             fi_dict[fold_n] = fi_dummy_k
#
#         print('make prediction')
#         pred_np = pred_template(x_test_time_step_3d, model, pred='regression')
#         if scale_input is not None:
#             pred_np = scaler.transform(pred_np)
#         # res_ctn['prediction'] = pd.Series(pred_np.flatten(), index=x_test.index)
#         # y_preds_k += pred_template(x_test,model,pred='classification') / fold_num
#         y_preds_k += pred_np.flatten() / fold_num
#
#         if track_feature_importance:
#             res_ctn['feature_importance'] = fi_dict
#         if return_score:
#             print('na')
#         del x_train_k, x_valid_k, y_train_k, y_valid_k
#         del model, hist
#         gc.collect()
#     print('prediction results collected')
#     res_ctn['prediction'] = pd.Series(y_preds_k.flatten(), index=x_test.index)
#     if track_feature_importance:
#         res_ctn['feature_importance'] = np.nan
#     if return_misc:
#         res_ctn['misc'] = np.nan
#     # res_ctn['misc'] = pd.DataFrame([model.evals_result_['validation_0'][params['eval_metric']],
#     #                                model.evals_result_['validation_1'][params['eval_metric']]],index=['train','validaiton']).T
#     if return_score:
#         res_ctn['score'] = np.nan
#     # res_ctn['score'] = pd.DataFrame(pd.concat(score_list,axis=1).fillna(0).mean(axis=1) ,columns = [y_preds_k.index[0]])
#     return res_ctn


def pred_fit_mlp_reg(y_train, x_train, x_test, params=None, fold_num=2,
                     res_iter_save_folder=None, return_model=False,
                     verbose=True, track_feature_importance=False, return_misc=False,
                     return_score=False, plot_model=False,
                     use_generator=False, rlrop_param=None, std_norm=True,
                     shuffle=False, tsp=False, use_bn=True):
    if rlrop_param is None:
        rlrop_param = {'factor': 0.5, 'patience': 5}
    seed = 2018
    set_seed()
    res_ctn = {}
    score_list, pred_res_list = [], []
    model_dict, hist_dict, model_dir_dict = {}, {}, {}
    model_list, fi_dict = {}, {}
    score_dict = {}
    # parameter
    dropout = params['dropout']
    activation = params['activation']
    layer_list = params['layer']
    kernel_initializer = params['kernel_initializer']

    first_layer = layer_list[0]
    mid_layer = layer_list[1:-1]
    verbose_num = 1 if verbose else 0
    # k fold prediction
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle, tsp=tsp)
    y_preds_k = np.zeros(x_test.shape[0])
    for fold_n, (train_index, valid_index) in enumerate(splits):
        set_seed()
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        if std_norm:
            y_train_k_std = y_train_k.std()
            y_train_k = y_train_k / y_train_k_std
            y_valid_k = y_valid_k / y_train_k_std
        val_set = (x_valid_k, y_valid_k)
        # Input Layer
        model = Sequential()
        model.add(Dense(first_layer, input_dim=x_train_k.shape[1], kernel_initializer=kernel_initializer, activation=activation))
        if use_bn:
            model.add(BatchNormalization())
        model.add(Dropout(dropout, seed=seed))
        # Mid Layer
        layer_num = len(mid_layer)
        for layer_idx in range(1, layer_num + 1):
            model.add(Dense(layer_list[layer_idx], kernel_initializer=kernel_initializer, activation=activation))
            if use_bn:
                model.add(BatchNormalization())
            model.add(Dropout(dropout, seed=seed))
        # Last Layer
        model.add(Dense(1, activation=activation, kernel_initializer=kernel_initializer))
        # compile
        model.compile(loss=params['loss'], optimizer=Adam(lr=params['lr']),
                      metrics=params['metrics'])
        early_stop = EarlyStopping(monitor='val_loss',  # min_delta=1e-5,
                                   patience=params['callback_patience'],
                                   verbose=verbose_num, mode='auto')
        # restore_best_weights=True)# not in this version
        rlrop = ReduceLROnPlateau(monitor='val_loss', factor=rlrop_param['factor'],
                                  patience=rlrop_param['patience'], verbose=1)
        call_back_spec = [early_stop, rlrop]

        if use_generator:  # lstm
            total_size = len(x_train_k)
            batch_size = params['batch_size']
            steps_per_epoch = total_size // batch_size  # int(np.ceil(total_size/batch_size))
            hist = model.fit_generator(data_generator_helper(x_train_k.values, y_train_k.values,
                                                             batch_size, shuffle),
                                       steps_per_epoch=steps_per_epoch,
                                       epochs=params['epochs'],
                                       validation_data=val_set,
                                       callbacks=call_back_spec,
                                       verbose=verbose_num,
                                       shuffle=shuffle)
        else:
            hist = model.fit(x_train_k, y_train_k, epochs=params['epochs'],
                             batch_size=params['batch_size'],
                             validation_data=val_set, callbacks=call_back_spec,
                             verbose=verbose_num,
                             shuffle=shuffle)
        print('iter compile done')
        if plot_model:
            print('plot training process')
            plot_keras_model_train(hist)
            plt.show()
        print('make prediction')
        pred_res_itr = pred_template(x_test, model, pred='regression')
        y_preds_k += pred_res_itr / fold_num
        if track_feature_importance:
            fi_dummy_k = collect_feature_importance_helper(model=None, x_train=x_train_k)
            fi_dict[fold_n] = fi_dummy_k
        if return_score:
            score_dict[fold_n] = pd.DataFrame(hist.history)
        if return_misc:
            pred_res_list.append(pred_res_itr)
        if res_iter_save_folder is not None:
            if not os.path.exists(res_iter_save_folder):
                os.makedirs(res_iter_save_folder)
            model_ctn_name = 'misc'
            model_name_str = 'model'
            if isinstance(x_test.index, pd.MultiIndex):
                ts_itr = x_test.index[0][0]
            else:
                ts_itr = x_test.index[0]
            ts_str = dt.datetime.strftime(ts_itr, '%Y%m%d%H%M%S')
            itr_path = os.path.join(res_iter_save_folder, '%s_%s.h5' % (ts_str, str(fold_n)))
            model_dir_dict[fold_n] = itr_path
            model.save(itr_path)

        del x_train_k, x_valid_k, y_train_k, y_valid_k
        reset_keras(model, hist)
        for i in range(3): gc.collect()
    print('prediction results collected')
    res_ctn['prediction'] = pd.Series(y_preds_k, index=x_test.index)
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_model:
        res_ctn['model'] = model_dir_dict
    if return_misc:
        res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list, axis=1))
    if return_score:
        res_ctn['score'] = score_dict
    return res_ctn


###########################################

def plot_model_train(model):
    if not isinstance(model, dict):
        results = model.evals_result()
    else:
        results = model
    eval_metric = list(results['validation_0'].keys())[0]
    train_error = list(results['validation_0'].values())[0]
    valid_error = list(results['validation_1'].values())[0]
    epochs = len(train_error)
    x_axis = range(0, epochs)
    # plot log loss
    fig, ax1 = pyplot.subplots()
    ax2 = ax1.twinx()
    ax1.plot(x_axis, train_error, label='Train', color='b')
    ax2.plot(x_axis, valid_error, label='Validation', color='r')
    ax1.legend(['train(lhs)'], loc='upper right')
    ax2.legend(['validation(rhs)'], loc='upper center')
    ax1.set_ylabel('train')
    ax2.set_ylabel('validation')
    # pyplot.ylabel(eval_metric)
    pyplot.xlabel('Iteration')
    pyplot.title('Model Train Validation - %s' % (eval_metric))
    # plt.legend(['train', 'validation'], loc='upper right')
    pyplot.show()
    return


def plot_keras_model_train(hist):
    if not isinstance(hist, pd.DataFrame):
        model_hist = pd.DataFrame(hist.history)
    else:
        model_hist = hist
    name_list = model_hist.columns.tolist()
    loss_list = ['val_loss', 'loss']
    acc_list = [i for i in name_list if i not in loss_list]
    acc_name = [i for i in acc_list if i.find('val')][0]
    plt.plot(model_hist[acc_name])
    plt.plot(model_hist['val_%s' % (acc_name)])
    plt.title('model %s' % (acc_name))
    plt.ylabel(acc_name)
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper right')
    plt.show()
    # summarize history for loss
    plt.plot(model_hist['loss'])
    plt.plot(model_hist['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper right')
    plt.show()
    return


def plot_keras_model_train(hist):
    if not isinstance(hist, pd.DataFrame):
        model_hist = pd.DataFrame(hist.history)
    else:
        model_hist = hist
    name_list = model_hist.columns.tolist()
    loss_list = ['val_loss', 'loss']
    acc_list = [i for i in name_list if i not in loss_list]
    acc_name = [i for i in acc_list if i.find('val')][0]
    print(acc_name)
    epochs = len(model_hist)
    x_axis = range(1, epochs + 1)
    # plot log loss
    fig, ax1 = pyplot.subplots()
    ax2 = ax1.twinx()
    ax1.plot(x_axis, model_hist['loss'], label='Train', color='b')
    ax2.plot(x_axis, model_hist['val_loss'], label='Validation', color='r')
    ax1.legend(['train(lhs)'], loc='upper right')
    ax2.legend(['validation(rhs)'], loc='upper center')
    ax1.set_ylabel('train')
    ax2.set_ylabel('validation')
    pyplot.xlabel('Iteration')
    pyplot.title('Model Train Validation - Loss')
    pyplot.show()
    if 'val_%s' % (acc_name) in acc_list:
        fig2, ax3 = pyplot.subplots()
        ax4 = ax3.twinx()
        ax3.plot(x_axis, model_hist[acc_name], label='Train', color='b')
        ax4.plot(x_axis, model_hist['val_%s' % (acc_name)], label='Validation', color='r')
        ax3.legend(['train(lhs)'], loc='upper right')
        ax4.legend(['validation(rhs)'], loc='upper center')
        ax3.set_ylabel('train')
        ax4.set_ylabel('validation')
        pyplot.xlabel('Iteration')
        pyplot.title('Model Train Validation - %s' % (acc_name))
        pyplot.show()
    return


def weight_decay(half_life, total_len):
    """last one has highest weight , half life = time to reach 0.5, weight is normalized"""
    weight_list_raw = [0.5 ** ((total_len - i) / half_life) for i in range(total_len)]
    return weight_list_raw / np.sum(weight_list_raw)


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


##### prod related model ############


def reset_keras(model=None, hist=None):
    sess = get_session()
    clear_session()
    sess.close()
    sess = get_session()
    if model is not None:
        try:
            del model  # this is from global space - change this as you need
            if hist is not None:
                del hist
        except:
            pass
    for i in range(3): gc.collect()
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 1
    config.gpu_options.visible_device_list = "0"
    set_session(tf.Session(config=config))
    return


def h5_to_pb_helper(h5_path, pb_path, rebuild=True, tf_version='1.4.0'):
    reset_keras()
    if str(Path(pb_path).parent) == '.':
        pb_path = str((Path.cwd() / pb_path))
    output_fld = Path(pb_path).parent
    output_model_name = Path(pb_path).name
    output_model_stem = Path(pb_path).stem
    input_output_info_txt = os.path.join(output_fld, output_model_stem + '.txt')
    Path(pb_path).parent.mkdir(parents=True, exist_ok=True)
    K.set_image_data_format('channels_last')
    if isinstance(h5_path, str):
        model = load_model(h5_path)
    else:
        model = h5_path
    if rebuild:
        # get structure & weight ~ rebuild from current environment save as pb
        tf_version_curr = tf.__version__
        if tf_version_curr != tf_version:
            print('version error')
            print('tf version current vs required:%s vs %s' % (tf_version_curr, tf_version))
            raise Exception
        weight_path = 'tmp_weight.h5'
        structure_path = 'tmp_structure.yaml'
        model.save_weights(weight_path)
        yaml_string = model.to_yaml()
        open(structure_path, 'w').write(yaml_string)
        reset_keras(model)
        model = model_from_yaml(yaml_string)  # load structure
        model.load_weights(weight_path)  # load weight
    input_name = model.inputs[0].name
    output_name = model.outputs[0].name
    output_name_list = [node.op.name for node in model.outputs]
    with open(input_output_info_txt, 'w+') as f:
        f.write(input_name + ',')
        f.write(output_name)
    sess = K.get_session()
    constant_graph = graph_util.convert_variables_to_constants(
        sess,
        sess.graph.as_graph_def(),
        output_name_list)
    graph_io.write_graph(constant_graph, str(output_fld), output_model_name,
                         as_text=False)
    reset_keras()
    return


def read_pb_model_helper(pb_path):
    reset_keras()
    if str(Path(pb_path).parent) == '.':
        pb_path = str((Path.cwd() / pb_path))
    output_fld = Path(pb_path).parent
    output_model_name = Path(pb_path).name
    output_model_stem = Path(pb_path).stem
    input_output_info_txt = os.path.join(output_fld, output_model_stem + '.txt')
    fi_path = os.path.join(output_fld, output_model_stem + '.csv')
    fi_list = pd.read_csv(fi_path, index_col=0).index.tolist()
    with open(input_output_info_txt, 'r') as f:
        input_name, output_name = f.readline().split(',')
    sess = tf.Session()
    with gfile.FastGFile(pb_path, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')
    sess.run(tf.global_variables_initializer())
    input_data = sess.graph.get_tensor_by_name(input_name)
    prediction = sess.graph.get_tensor_by_name(output_name)
    pb_obj = {'sess': sess, 'input_data': input_data, 'prediction': prediction,
              'feature_importance': fi_list}
    return pb_obj


def pred_helper_pb_model(pb_obj, x_test):
    sess = pb_obj['sess']
    prediction = pb_obj['prediction']
    input_data = pb_obj['input_data']
    if 'feature_importance' in pb_obj:
        x_test = x_test[pb_obj['feature_importance']]
    if 'lstm' in pb_obj['input_data'].name:
        time_step = pb_obj['input_data'].shape[1].value
        print(time_step)
        x_test_use = transform_2d_3d_helpher(x_test.values, None, time_step)
        pred_idx = len(x_test) - time_step + 1
        pred_index = x_test.iloc[-pred_idx:].index
    else:
        x_test_use = x_test
        pred_index = x_test.index
    pred_raw_np = sess.run(prediction, {input_data: x_test_use})
    if len(pred_raw_np.shape) > 1:
        if pred_raw_np.shape[1] == 2:
            pred_raw_np = pred_raw_np[:, 1]
    pred_raw = pd.Series(pred_raw_np.flatten(), index=pred_index)
    return pred_raw


##### prod related model ############


def create_config(config_path, hpr_spec_dict, fold_list_dict, model_list_dl=['lstm_cla', 'mlp_reg', 'mlp_cla']):
    collect_list = []
    model_list = list(hpr_spec_dict.keys())
    for model in model_list:
        fold_list = fold_list_dict[model]
        file_suffix = '.pmml' if model not in model_list_dl else ''
        holding_period_list = hpr_spec_dict[model]
        for holding_period in holding_period_list:
            for fold in fold_list:
                current_dict = {"parentPath": model,
                                "groupName": "%s_%d" % (model, holding_period),
                                "modelName": "%s_%d_%d" % (model, holding_period, fold),
                                "modelFile": "%s_%d_%d%s" % (model, holding_period, fold, file_suffix),
                                "factorListFile": "%s_%d_%d.csv" % (model, holding_period, fold)}
                collect_list.append(current_dict)

    with open(config_path, 'w') as f:
        json.dump(collect_list, f, indent=2)
    print('config saved:\n %s' % (config_path))
    return


# def pred_helper_multi_model(model_path_dict, hpr_spec_dict, x_test, x_test_ts=None):
#     model_list = list(hpr_spec_dict.keys())
#     raw_dict_update = {}
#     for model in model_list:
#         for model in model_list:
#             holding_period_list = hpr_spec_dict[model]
#             pred_raw_itr_list = []
#             for holding_period in holding_period_list:
#                 itr_name = '%s_%d_r240' % (model, holding_period)
#                 pred = 'regression' if itr_name.find('reg') >= 0 else 'classification'
#                 print(itr_name, pred)
#                 model_path_itr = model_path_dict[model][itr_name]
#                 print(model_path_itr)
#                 model_dict_itr = read_pickle(model_path_itr)
#                 if model not in ['lstm_cla', 'lstm_reg']:
#                     pred_raw_itr = pred_helper(x_test, model_dict_itr, pred=pred)
#                 else:
#                     pred_raw_itr = pred_helper(x_test_ts, model_dict_itr, pred=pred)
#                 pred_raw_itr = pd.DataFrame(pred_raw_itr, columns=[itr_name])
#                 pred_raw_itr_list.append(pred_raw_itr)
#             pred_raw_df = pd.concat(pred_raw_itr_list, axis=1)
#             raw_dict_update[model] = pred_raw_df[model_name_dict[model]]
#     return raw_dict_update


# def collect_model_prediction_helper(model_path_dict, hpr_spec_dict):
#     model_list = list(hpr_spec_dict.keys())
#     for model in model_list:
#         holing_period_list = hpr_spec_dict[model]
#         pred_raw_itr_list = []
#         name_itr_list = []
#         for holding_period in holing_period_list:
#             itr_name = '%s_%d_r240' % (model, holding_period)
#             name_itr_list.append(itr_name)
#             pred = 'regression' if itr_name.find('reg') >= 0 else 'classification'
#             print(itr_name, pred)
#             model_path_itr = model_path_dict[model][itr_name]
#             model_dict_itr = read_pickle(model_path_itr)
#             pred_raw_itr = model_dict_itr['prediction']
#             pred_raw_itr_list.append(pred_raw_itr)
#         pred_raw_df = pd.concat(pred_raw_itr_list, axis=1)
#         pred_raw_df.columns = name_itr_list
#         raw_dict_exist[model] = pred_raw_df
#     return raw_dict_exist


def fix_h5_model_path_helper(model_path_itr, m):
    md = read_pickle(model_path_itr)
    for itr in md['model']:
        mitr = md['model'][itr]
        if mitr is not None:
            mitr_old = mitr.copy()

            for fold_itr in mitr:
                h5_itr = mitr[fold_itr]
                dirname_h5 = os.path.join(os.path.dirname(model_path_itr), m)
                basename_h5 = os.path.basename(h5_itr)
                h5_itr_new = os.path.join(dirname_h5, basename_h5)
                if not os.path.exists(h5_itr_new):
                    print('h5 not found')
                    raise Exception
                else:
                    mitr[fold_itr] = h5_itr_new
            md['model'][itr] = mitr
            print('%s start fix %s' % ('-' * 20, '-' * 20))
            print(mitr_old)
            print(mitr)
            print('%s end fix %s' % ('-' * 20, '-' * 20))
    save_pickle(md, model_path_itr)
    return


def pred_fit_mlp_cla(y_train, x_train, x_test, params=None, fold_num=5,
                     res_iter_save_folder=None, return_model=False,
                     verbose=True, track_feature_importance=False, return_misc=False,
                     return_score=False, plot_model=False,
                     use_generator=False, rlrop_param=None, weight_type='abs_ret', gpu_mem_size=8,
                     shuffle=False, use_bn=True):
    if rlrop_param is None:
        rlrop_param = {'factor': 0.5, 'patience': 5}
    seed = 2018
    set_seed()
    res_ctn = {}
    score_list, pred_res_list = [], []
    model_dict, hist_dict, model_dir_dict = {}, {}, {}
    model_list, fi_dict = {}, {}
    score_dict = {}
    # parameter
    dropout = params['dropout']
    activation = params['activation']
    layer_list = params['layer']
    kernel_initializer = params['kernel_initializer']
    if kernel_initializer == 'glorot_normal':
        kernel_initializer = glorot_normal(seed=seed)
    first_layer = layer_list[0]
    mid_layer = layer_list[1:-1]
    verbose_num = 1 if verbose else 0
    splits = fold_split_helper(x_train, y_train, fold_num, shuffle=shuffle)
    y_preds_k = np.zeros(x_test.shape[0])

    # weight_type_use = weight_type if weight_type is not None else 'abs_ret'
    for fold_n, (train_index, valid_index) in enumerate(splits):
        set_seed()
        print('Fold:', fold_n + 1)
        x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
        y_train_use_k, y_valid_use_k = y_train.iloc[train_index], y_train.iloc[valid_index]
        y_train_weight_k, y_train_use_k = get_sample_weight_helper(pd.DataFrame(y_train_use_k),
                                                                   weight_type=weight_type,
                                                                   filter_cut=2)
        y_train_use_k = y_train_use_k.values

        y_valid_weight_k, y_valid_use_k = get_sample_weight_helper(pd.DataFrame(y_valid_use_k),
                                                                   weight_type=weight_type,
                                                                   filter_cut=2)
        y_valid_use_k = y_valid_use_k.values
        y_train_use_k = np_utils.to_categorical(y_train_use_k)
        y_valid_use_k = np_utils.to_categorical(y_valid_use_k)
        val_set = (x_valid_k, y_valid_use_k)

        if weight_type is None:
            sample_weight = None
        else:
            sample_weight = y_train_weight_k.values
            sample_weight_val = y_valid_weight_k.values
            val_set = (x_valid_k, y_valid_use_k, sample_weight_val)

        # Input Layer
        model = Sequential()
        model.add(Dense(first_layer, input_dim=x_train_k.shape[1], kernel_initializer=kernel_initializer, activation=activation))
        if use_bn:
            model.add(BatchNormalization())
        model.add(Dropout(dropout, seed=seed))
        # Mid Layer
        layer_num = len(mid_layer)
        for layer_idx in range(1, layer_num + 1):
            model.add(Dense(layer_list[layer_idx], kernel_initializer=kernel_initializer, activation=activation))
            if use_bn:
                model.add(BatchNormalization())
            model.add(Dropout(dropout, seed=seed))
        # Last Layer
        model.add(Dense(2, activation=activation, kernel_initializer=kernel_initializer))
        # compile
        model.compile(loss=params['loss'], optimizer=Adam(lr=params['lr']),
                      metrics=params['metrics'])
        early_stop = EarlyStopping(monitor='val_loss',
                                   patience=params['callback_patience'],
                                   verbose=verbose_num, mode='auto')
        rlrop = ReduceLROnPlateau(monitor='val_loss', factor=rlrop_param['factor'],
                                  patience=rlrop_param['patience'], verbose=1)
        call_back_spec = [early_stop, rlrop]

        if use_generator:  # lstm
            val_size = get_val_size(x_train_k) + get_val_size(y_train_use_k) + get_val_size(x_valid_k) + get_val_size(y_valid_use_k)
            scale_ratio = max(gpu_mem_size / val_size, 1)  # if exceed memory,ratio should be smaller than 1
            batch_size = params['batch_size']
            steps_per_epoch = int(np.ceil(len(x_train_k) / batch_size / scale_ratio))
            validation_steps = int(np.ceil(len(x_valid_k) / batch_size / scale_ratio))
            print('val_size: %.2f / scale_ratio: %.2f / steps_per_epoch: %d' % (val_size, scale_ratio, steps_per_epoch))
            hist = model.fit_generator(data_generator_helper(x_train_k.values, y_train_use_k, batch_size, shuffle, sample_weight),
                                       steps_per_epoch=steps_per_epoch,
                                       epochs=params['epochs'],
                                       validation_data=val_set,
                                       callbacks=call_back_spec,
                                       verbose=verbose_num,
                                       shuffle=shuffle)
        else:
            hist = model.fit(x_train_k, y_train_use_k, epochs=params['epochs'],
                             batch_size=params['batch_size'],
                             validation_data=val_set, callbacks=call_back_spec,
                             verbose=verbose_num,
                             shuffle=shuffle,
                             sample_weight=sample_weight)
        print('iter compile done')
        if plot_model:
            print('plot training process')
            plot_keras_model_train(hist)
            plt.show()
        print('make prediction')
        pred_res_itr = pred_template(x_test, model, pred='classification')
        y_preds_k += pred_res_itr / fold_num
        if track_feature_importance:
            fi_dummy_k = collect_feature_importance_helper(model=None, x_train=x_train_k)
            fi_dict[fold_n] = fi_dummy_k
        if return_score:
            score_dict[fold_n] = pd.DataFrame(hist.history)
        if return_misc:
            pred_res_list.append(pred_res_itr)
        if res_iter_save_folder is not None:
            if not os.path.exists(res_iter_save_folder):
                os.makedirs(res_iter_save_folder)
            model_ctn_name = 'misc'
            model_name_str = 'model'
            if isinstance(x_test.index, pd.MultiIndex):
                ts_itr = x_test.index[0][0]
            else:
                ts_itr = x_test.index[0]
            ts_str = dt.datetime.strftime(ts_itr, '%Y%m%d%H%M%S')
            itr_path = os.path.join(res_iter_save_folder, '%s_%s.h5' % (ts_str, str(fold_n)))
            model_dir_dict[fold_n] = itr_path
            model.save(itr_path)
        del x_train_k, x_valid_k, y_train_use_k, y_valid_use_k, val_set
        reset_keras(model, hist)
        # K.clear_session()
        for i in range(3): gc.collect()
    print('prediction results collected')
    res_ctn['prediction'] = pd.Series(y_preds_k, index=x_test.index)
    if track_feature_importance:
        res_ctn['feature_importance'] = fi_dict
    if return_model:
        res_ctn['model'] = model_dir_dict
    if return_misc:
        res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list, axis=1))
    if return_score:
        res_ctn['score'] = score_dict
    return res_ctn


#################################################################


def pred_template2(x, model, pred='regression', best_iteration=False):
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x_type = 'pd'
        x_np = x.values
    else:
        x_type = 'np'
        x_np = x
    if pred == 'regression':
        y_mat = model.predict(x_np)
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


def recut_train_test_by_time_step(x_train, y_train, x_test, time_step):
    # get time_step data for test_set ~
    # transform data
    # timestep 3d data, requires test data to have n+time_step size for prediction
    edate_train, sdate_test = x_train.index[-1], x_test.index[0]
    x_train_test = pd.concat([x_train, x_test], axis=0)
    x_index_list = x_train_test.index.tolist()
    cut_idx_time_step = x_index_list.index(sdate_test) - time_step + 1
    x_test_time_step = x_train_test.iloc[cut_idx_time_step:, :]
    x_train_time_step = x_train_test.iloc[:cut_idx_time_step, :]
    y_train_time_step = y_train.iloc[:cut_idx_time_step]
    return x_train_time_step, y_train_time_step, x_test_time_step
