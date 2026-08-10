import IOLib
import pandas as pd
import datetime
import importlib
import os
import numpy as np
import multiprocessing
import sys
import time, pickle
import json
from keras.models import load_model
from loguru import logger



def get_universe_filter_stock():
    univ_file = './universe/stock_universe.pkl'
    if not os.path.exists(univ_file):
        logger.error("{} no exists!".format(univ_file))
    univ = pd.read_pickle(univ_file).reset_index()
    logger.info("univ={}".format(univ.values))
    for i in univ.values:
        try:
            data = IOLib.read_data('./data/Stock/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
            data = data.loc[data.dt < str(i[0] + datetime.timedelta(hours=9, minutes=26))].iloc[-1]
            pre_close_px = data.PreClosePx

            data = IOLib.read_data('./data/Transaction/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
            data = data.loc[(data.dt < str(i[0] + datetime.timedelta(hours=9, minutes=26))) & (data.TradePrice > 0)].iloc[-1]
            last_px = data.TradePrice
            if last_px >= pre_close_px:
                univ.drop(univ.index[univ.Ticker == i[1]], inplace=True)
        except:
            univ.drop(univ.index[univ.Ticker == i[1]], inplace=True)

    univ = univ.set_index(['dt', 'Ticker'])
    logger.info("univ_filter={}".format(univ.index))
    univ.to_pickle('./universe/stock_universe_filtered.pkl')
    return univ


def run_factor(py_path):
    try:
        sys.path.insert(0, py_path)
        pool = multiprocessing.Pool(processes=24)
        factors = [x[:-3] for x in os.listdir(py_path) if x.endswith('.py')]

        for i in factors:
            pool.apply_async(calc, (i,))

        pool.close()
        pool.join()
    except Exception as expt:
        logger.error("TOCLIENT: RunFactor error, " + str(expt))


def rolling_norm(df, today):
    df = df.replace([-np.inf, np.inf], np.nan)
    for col in df:
        ub = df[col].mean() + 3 * df[col].std()
        lb = df[col].mean() - 3 * df[col].std()
        df.loc[df[col] > ub, col] = ub
        df.loc[df[col] < lb, col] = lb

    result = ((df - df.mean()) / df.std()).loc[today:]
    return result


def norm_zd(df, today):
    df = df.replace([-np.inf, np.inf], np.nan)
    df = df.loc[today:]
    for col in df:
        ub = df[col].mean() + 3 * df[col].std()
        lb = df[col].mean() - 3 * df[col].std()
        df.loc[df[col] > ub, col] = ub
        df.loc[df[col] < lb, col] = lb

    result = (df - df.mean()) / df.std()
    result.columns += '_zd'
    return result


def factor_normalize(univ):
    factor_list = os.listdir('./factors/factor_raw/')
    logger.info("factor_list={}".format(factor_list))
    factor_raw = []
    for f in factor_list:
        factor_raw.append(pd.read_pickle('./factors/factor_raw/' + f))
    factor_raw = pd.concat(factor_raw, axis=1)
    factor_new = pd.read_pickle('./factors/factor_new.pkl')
    factor_hist = pd.read_pickle('./factors/factor_hist.pkl')
    factor_dummy = pd.read_pickle('./factors/factor_dummy.pkl')

    #univ = get_universe_filter_stock()
    factor_new = factor_new.reindex(univ.index)
    factor_dummy = factor_dummy.reindex(univ.index)
    logger.info("concat history and today factors")
    factor_df = pd.concat([factor_hist, pd.concat([factor_raw, factor_new], axis=1)], sort=True)
    today = pd.Timestamp(np.unique(factor_df.reset_index(0).dt)[-1]).strftime('%Y%m%d')
    factor_input = pd.concat([rolling_norm(factor_df, today), norm_zd(factor_df, today), factor_dummy], axis=1).fillna(
        0)

    logger.info("factor_input shape={}".format(factor_input.shape))
    factor_input.to_pickle('./factors/factor_input.pkl')
    return today


def calc(i):
    importlib.import_module(i)


######  prediction functions defined here  ##################


def read_pickle(save_path=None, verbose=True):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict


def save_pickle(save_dict, save_path):
    logger.info('saving data to: {}'.format(save_path))
    folder = os.path.dirname(save_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if os.path.exists(save_path):
        logger.info('remove existing one')
        os.remove(save_path)
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


def change_h5_path_helper(model_fold_itr, res_base_path):
    file_name = os.path.basename(model_fold_itr)
    dest_root = res_base_path.split('.')[0]
    model_fold_itr = os.path.join(dest_root, file_name)
    logger.info("change h5 file path to {}".format(model_fold_itr))
    return model_fold_itr


def pred_helper(x_test, model_dict, pred='regression', check_time=True, return_itr=False, res_base_path=None):
    # accept lstm with time_step  / keras model ~ mlp
    if isinstance(x_test.index, pd.MultiIndex):
        sdt_pred = x_test.index[0][0]
    else:
        sdt_pred = x_test.index[0]
    ts_list = list(model_dict['model'].keys())
    ts_take = ts_list[-1]
    if check_time:
        if sdt_pred < ts_take:
            logger.error(
                'Raise Error: modeled trained in future time, model: %s / pred: %s' % (str(ts_take), str(sdt_pred)))
            raise Exception

    model_fold = model_dict['model'][ts_take]
    if 'feature_importance' in model_dict:
        fi_fold = model_dict['feature_importance'][ts_take]
    else:
        fi_fold = x_test.columns.tolist()
    fold_list = list(model_fold.keys())
    #     print('use model trained on %s with %d fold'%(ts_take,fold_num))
    pred_res_itr_list = []
    for fold_itr in fold_list:
        fi_fold_itr = fi_fold[fold_itr]
        fi_fold_itr_list = fi_fold_itr.index.tolist()
        x_test_fold = x_test[fi_fold_itr_list]
        model_fold_itr = model_fold[fold_itr]
        if isinstance(model_fold_itr, str):
            if res_base_path is not None:
                model_fold_itr = change_h5_path_helper(model_fold_itr, res_base_path)
            logger.info("loadModel model_fold={}".format(model_fold_itr))
            model_fold_itr = load_model(model_fold_itr)
            model_config = model_fold_itr.get_config()[0]
            if model_config['class_name'] == 'LSTM':  # solve for lstm 3d data, pred return np.array
                time_step = model_config['config']['batch_input_shape'][1]
                pred_idx = len(x_test_fold) - time_step + 1
                pred_index = x_test_fold.iloc[-pred_idx:].index
                pred_shape = len(pred_index)
                x_test_fold = transform_2d_3d_helpher(x_test_fold.values, None, time_step)
        logger.info("call predict_template, fold_itr={}".format(fold_itr))
        pred_res_itr = pred_template(x=x_test_fold, model=model_fold_itr, pred=pred)
        if isinstance(pred_res_itr, np.ndarray):
            pred_res_itr = pd.Series(pred_res_itr.flatten(), index=pred_index)
        pred_res_itr_list.append(pred_res_itr)
        logger.info("predict end, fold_itr={}".format(fold_itr))
    #     print('pred shape: %d'%(pred_shape))
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


def get_model_pred_helper(res_base_path, model_name=None):
    if isinstance(res_base_path, dict):
        model_base_dict = res_base_path
    else:
        if res_base_path.find('pkl') > 0:
            model_base_dict = {os.path.basename(res_base_path).split('.')[0]: res_base_path}
        else:
            model_base_dict = find_file(res_base_path, 'pkl')
    if model_name is not None:
        if isinstance(model_name, str):
            model_base_dict = {i: model_base_dict[i] for i in model_base_dict
                               if i.find(model_name) >= 0}
        elif isinstance(model_name, list):
            model_base_dict = {i: model_base_dict[i] for i in model_base_dict
                               if i in model_name}
    model_dict = {i: read_pickle(model_base_dict[i]) for i in model_base_dict}
    pred_df = extract_model_pred(model_dict)
    return pred_df, model_dict


def pred_helper_wrapper(x_test, res_base_path, pred='regression', model_name=None, chg_name=False):
    pred_df, model_dict_itr = get_model_pred_helper(res_base_path, model_name)
    if isinstance(x_test.index, pd.MultiIndex):
        date_list_pred = x_test.index.get_level_values(level=0).unique().tolist()
        date_list_exist = pred_df.index.get_level_values(level=0).unique().tolist()
    else:
        date_list_pred = x_test.index.tolist()
        date_list_exist = pred_df.index.tolist()
    date_list_pred.sort()
    date_list_exist.sort()
    last_exist = date_list_exist[-1]
    if last_exist in date_list_pred:
        last_exist_idx = date_list_pred.index(last_exist)
        if last_exist_idx < len(date_list_pred) - 1:
            sdate_pred = date_list_pred[last_exist_idx + 1]
            pred_task = True
        else:
            pred_task = False
            logger.info('no need for prediction')
    else:
        pred_task = True
        sdate_pred = date_list_pred[0]
    if pred_task:
        x_test_use = x_test.loc[sdate_pred:]
        pred_raw_list = []
        for k in model_dict_itr:
            #             print(k)
            pred = 'classification' if k.find('_cla') > 0 else 'regression'
            pred_raw_itr = pred_helper(x_test_use, model_dict_itr[k], pred=pred, res_base_path=res_base_path)
            pred_raw_list.append(pred_raw_itr)
        pred_raw_df = pd.concat(pred_raw_list, axis=1)
        pred_raw_df.columns = list(model_dict_itr.keys())
        pred_df_all = pd.concat([pred_df, pred_raw_df], axis=0)
    else:
        pred_df_all = pred_df
    if chg_name:
        pred_df_all.columns = [int(i.split('_')[2]) for i in pred_df_all.columns]
    return pred_df_all


def extract_model_pred(model_dict):
    model_list = list(model_dict.keys())
    model_list.sort()
    pred_list = []
    #     print(model_list)
    for model in model_list:
        model_pred = model_dict[model]['prediction']
        if isinstance(model_pred, pd.DataFrame):
            if model_pred.shape[1] > 1:
                model_pred = model_pred.stack()
        pred_list.append(model_pred)
    pred_df = pd.concat(pred_list, axis=1)
    pred_df.columns = model_list
    return pred_df


def transform_2d_3d_helpher(x_use, y_use=None, time_step=1):
    x_len = len(x_use)
    if x_len < time_step:
        logger.info('x={} length shorter than time step {}'.format(x_len, time_step))
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


def pred_one_helper(x_test, res_base_path, pred='regression', model_name=None, chg_name=False):
    pred_df, model_dict_itr = get_model_pred_helper(res_base_path, model_name)
    pred_raw_list = []
    for k in model_dict_itr:
        pred = 'classification' if k.find('_cla') > 0 else 'regression'
        path = res_base_path if k.find('mlp') >= 0 else None
        pred_raw_itr = pred_helper(x_test, model_dict_itr[k], pred=pred, res_base_path=path)
        pred_raw_list.append(pred_raw_itr)
    pred_df_all = pd.concat(pred_raw_list, axis=1)
    if chg_name:
        pred_df_all.columns = [int(i.split('_')[2]) for i in pred_df_all.columns]
    return pred_df_all


def predict(today):
    model_root = 'models'

    model_list = ['lr_cla', 'lasso_reg', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']
    stack_model = 'lasso_reg'
    # path setting
    fac_path = './factors/factor_input.pkl'
    model_path_dict = {m: os.path.join(model_root, '%s.pkl' % (m)) for m in model_list}
    stack_model_path = os.path.join(model_root, 'stack_model', '%s.pkl' % (stack_model))

    # read factor
    fac_val = pd.read_pickle(fac_path)

    # read model ~ history result
    model_dict = {m: read_pickle(model_path_dict[m]) for m in model_path_dict}
    pred_raw_exist_dict = {m: model_dict[m]['prediction'].stack() for m in model_dict}
    pred_raw_exist_df = pd.DataFrame(pred_raw_exist_dict)
    stack_model_dict = read_pickle(stack_model_path)
    pred_raw_exist_df['stack'] = pd.DataFrame(stack_model_dict['prediction'].stack(), columns=['stack'])

    pred_raw_dict = {}
    get_all_pred = False  # True: piece existing raw result, else just predict new result
    x_test = fac_val.loc[today]

    model_list = ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_cla', 'mlp_reg']
    for model in model_list:
        logger.info("Model={} begin to predict".format(model))
        model_save_itr = model_path_dict[model]
        pred = 'regression' if model.split('_')[1] == 'reg' else 'classification'
        if get_all_pred:
            pred_raw = pred_helper_wrapper(x_test, model_save_itr, pred, model).unstack()
        else:
            pred_raw = pred_one_helper(x_test, model_save_itr, pred, model).unstack()
        pred_raw_dict[model] = pred_raw.stack().iloc[:, 0]
        logger.info("Model={} prediction end".format(model))
    pred_raw_df = pd.DataFrame(pred_raw_dict)

    model = stack_model
    model_save_itr = stack_model_path
    x_test_stack = pred_raw_df[model_list]
    pred = 'regression' if model.split('_')[1] == 'reg' else 'classification'
    logger.info("pred={} begin to call pred_one_helper".format(pred))
    pred_stack = pred_one_helper(x_test_stack, model_save_itr, pred, model).unstack()
    pred_raw_dict['stack'] = pred_stack.stack().iloc[:, 0]
    pred_raw_df = pd.DataFrame(pred_raw_dict)
    return pred_raw_df


def get_trade_param(json_file):
    with open(json_file) as f:
        param_dict = json.load(f)
        return param_dict


def gen_final_trade_file(pred_raw_df, today):
    param_dict = get_trade_param('setting/params.json')
    if param_dict is None:
        logger.error("TOCLIENT: failed to read json")
    # trading  parameters
    threshold = param_dict['threshold']  # 0.15  # 绝对阈值
    daily_max_num = param_dict['daily_max_num']  # 20  # 每日最大买入上限
    daily_min_num = param_dict['daily_min_num']  # 2  # 每日最小买入下限
    order_price = param_dict['order_price']  # '1'  # 委托价格
    start_time = param_dict['start_time']  # '93000'  # 开始时间
    end_time = param_dict['end_time']  # '93500'  # 结束时间
    stop_time = param_dict['stop_time']  # '145600'  # 终止时间
    algo = param_dict['algo']  # 'tvol'  # 算法
    tvol_ratio = param_dict['tvol_ratio']  # '25'  # 跟量比例
    order_interval = param_dict['order_interval']  # '1'  # 下单间隔
    withdraw_time = param_dict['withdraw_time']  # '1'  # 撤单间隔
    reorder_price = param_dict['reorder_price']  # '99'  # 补单价格
    money_per_stock = param_dict['money_per_stock']  # 单票买入金额

    final_score = pred_raw_df['stack']
    buy_list = final_score[final_score > threshold].nlargest(daily_max_num).reset_index().Ticker.values
    num = len(buy_list)

    if num >= daily_min_num:
        logger.info("generate trading file, buyList={}".format(buy_list))
        px = []
        for i in buy_list:
            data = IOLib.read_data('./data/Transaction/' + i + '/' + today + '.csv')
            data = data.loc[(data.dt < today + ' 09:26:00') & (data.TradePrice > 0)].iloc[-1]
            last_px = data.TradePrice
            px.append(last_px)

        # money_per_stock = 2000000
        qty = [int(round(x, -2)) for x in money_per_stock / np.array(px)]

        trade_list = pd.read_csv('trade_list.csv')
        buy_trade_list = pd.DataFrame([buy_list,
                                       qty,
                                       [order_price] * num,
                                       ['B'] * num,
                                       [start_time] * num,
                                       [end_time] * num,
                                       [stop_time] * num,
                                       [algo] * num,
                                       [tvol_ratio] * num,
                                       [order_interval] * num,
                                       [withdraw_time] * num,
                                       [reorder_price] * num]).T

        buy_trade_list.columns = trade_list.columns
        trade_list = pd.concat([trade_list, buy_trade_list])
        trade_list.to_csv('trade_list.csv', index=False)
        logger.info("trading file finished.")
    else:
        logger.warning("BuyListNum={} < daily_min_num={}, not gen trade csv.".format(num, daily_min_num))


def main():
    tag = '20221220'
    version = 'v1.0.0'
    args = sys.argv
    if len(args) <= 1:
        print("args <= 1")
        exit(-1)
    elif len(args) >= 4:
        py_path = args[1]
        log_name = args[2]
        data_path = args[3]
        logger.add(log_name, retention="1 days")
        logger.info("PythonStrategy for Arrow, tag={}, version={}, time={}".format(tag, version, time.ctime()))
        logger.info("parameters: python_path={}, log_file={}, data_path={}", py_path, log_name, data_path)
        logger.info("work path {}".format(os.getcwd()))
        IOLib.set_source("BIN")
        if not data_path.endswith('/'):
            data_path = data_path + '/'
        IOLib.set_path(data_path)
        try:
            logger.info("begin to filter stock")
            univ = get_universe_filter_stock()
            logger.info("begin to trigger factors calculation.")
            run_factor(py_path + "/factors/factor_list")
            logger.info("begin to trigger factor normalization.")
            today = factor_normalize(univ)
            logger.info("begin to predict.")
            pred_df = predict(today)
            logger.info("begin to generate trading files.")
            gen_final_trade_file(pred_df, today)
            logger.info("Python finished, exit.")
        except Exception as expt:
            logger.error("TOCLIENT: python module catch exception, " + str(expt))
            exit(-99)


if __name__ == "__main__":
    main()
