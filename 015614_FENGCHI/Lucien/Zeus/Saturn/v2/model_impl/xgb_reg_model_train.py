# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 14:54

from Zeus.Saturn.v2.models.ModelFactory import ModelFactory
from Zeus.Saturn.v2.hyper_param_space import model_params
from Zeus.Saturn.v2.path_conf import *
from LucienUtil.FileUtil import FileUtil
import warnings
import pandas as pd
import numpy as np
import time
from tqdm import tqdm
from itertools import product
from Zeus.Saturn.v2.Tool import multiprocess
from Zeus.Saturn.v2.my_logger import MyLogger
from Zeus.Saturn.v2.hyper_param_space import hyper_xgb_reg_params, multi_xgb_reg_params
from hyperopt import fmin, Trials, tpe
from Zeus.Saturn.v2.BackTest.EvalLaunch import EvalLaunch
np.random.RandomState(2022)
warnings.filterwarnings("ignore")

# 各个开关
not_search_but_backtest = True  # 在不进行超参数寻优的时候在训练完以后自动进行回测，一般都开着
pred_type = 'test'   # 这个参数只在not_search_but_backtest为True时起作用
hyper_search_flag = False   # 是否进行超参数寻优
multi_grid_search_flag = False   # 是否进行多进程参数寻优

strategy_name = 'SaturnS1'
version = 'v2'
model_name = 'xgb_reg_model'
hyper_remark = '改为auc寻优'
hump_model_name = 'xgbRegModel'
verbose = False     # 控制是否输出内容
search_time = 0
pred_fname = f'20190102~20200630_{hump_model_name}_v1.csv'    # 保存在/user/015614/pred/路径下


if hyper_search_flag:
    my_logger = MyLogger(strategy_name=strategy_name, model_name=model_name, version=version).get_logger()
    my_logger.info(f'{strategy_name} {version} {model_name} {hyper_remark} {hump_model_name}')
else:
    my_logger = None


def console_output_score(*score_list):
    print('准确率: ', round(score_list[0], 4))
    print('召回率: ', round(score_list[1], 4))
    print('精确率: ', round(score_list[2], 4))
    print('F1值: ', round(score_list[3], 4))
    print('AUC: ', round(score_list[4], 4))
    if len(score_list) > 5:
        print('MSE: ', round(score_list[5], 4))
        print('MAE: ', round(score_list[6], 4))
        print('MAE2: ', round(score_list[7], 4))

# 可公用函数
def tuning_objective(param):
    global search_time
    param_copy = param.copy()
    t1 = time.time()

    # 自定义参数，如果不是在进行寻优，那么这些值是真实的因子，或者是best_param里有的话会覆盖下面的值
    factor_num = 520
    score_threshold = 0.0

    if 'n_estimators' in param_copy.keys():
        param_copy['n_estimators'] = int(param_copy['n_estimators'])
    if 'factor_num' in param_copy.keys():
        param_copy['factor_num'] = int(param_copy['factor_num'])
    # if hyper_search_flag:
    #     my_logger.info(f'第{search_time}轮超参数为: {param}')

    if 'factor_num' in param_copy.keys():
        factor_num = int(param_copy.pop('factor_num'))
    if 'score_threshold' in param_copy.keys():
        score_threshold = param_copy.pop('score_threshold')

    date_config = dict(train_start_date=20160104,
                       train_end_date=20181231,
                       valid_start_date=20190102,
                       valid_end_date=20190930,
                       test_start_date=20191008,
                       test_end_date=20200630)

    if verbose:
        print(f'现在使用的模型是{model_name}')
    mf_inst = ModelFactory(model_name=model_name,
                           date_config=date_config,
                           factor_filter_path=filter_factor_fpath,
                           factor_score_path=factor_score_fpath,
                           data_path=saturn_data_test_fpath,
                           factor_num=factor_num,
                           label='label_v2o10d1')
    X_train, y_train, X_valid, y_valid, X_test, y_test = mf_inst.get_dateset()

    # TODO: 用于fit前保存因子顺序
    used_factor_list = X_train.columns.tolist()
    FileUtil.save_list2pkl(used_factor_list, factor_path, 'xgb_reg_model_factor_list.pkl')

    # 因为是回归任务，所以这里加入prefix下划线，只用来统计样本偏离度
    _y_train = (y_train > 0).astype(int)
    _y_valid = (y_valid > 0).astype(int)
    _y_test = (y_test > 0).astype(int)
    if verbose:
        print('训练集正样本比例为：', round((_y_train.sum() / y_train.shape[0])[0], 4))
        print('验证集正样本比例为：', round((_y_valid.sum() / y_valid.shape[0])[0], 4))
        print('测试集正样本比例为：', round((_y_test.sum() / y_test.shape[0])[0], 4))
        print('*' * 30)

    mf_inst.train_model(X_train, y_train, param=param_copy)
    y_train_pred = mf_inst.model_predict(X_train.values)
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_train > score_threshold, y_train_pred > score_threshold)
    mse, mae, mae2 = mf_inst.calc_model_reg_score(y_train, y_train_pred)
    if verbose:
        console_output_score(acc, rec, prec, f1, auc, mse, mae, mae2)
    pred_pos_pct = (y_train_pred > score_threshold).sum() / len(y_train_pred)
    if verbose:
        print('训练集预测的正值样本的数量：', round(pred_pos_pct, 4))

    y_valid_pred = mf_inst.model_predict(X_valid.values)
    acc_, rec_, prec_, f1_, auc_ = mf_inst.calc_model_score(y_valid > score_threshold, y_valid_pred > score_threshold)
    mse_, mae_, mae2_ = mf_inst.calc_model_reg_score(y_valid, y_valid_pred)
    if verbose:
        console_output_score(acc_, rec_, prec_, f1_, auc_, mse_, mae_, mae2_)
    pred_pos_pct = (y_valid_pred > score_threshold).sum() / len(y_valid_pred)
    if verbose:
        print('验证集预测的正值样本的数量：', round(pred_pos_pct, 4))

    y_test_pred = mf_inst.model_predict(X_test.values)
    _acc, _rec, _prec, _f1, _auc = mf_inst.calc_model_score(y_test > score_threshold, y_test_pred > score_threshold)
    _mse, _mae, _mae2 = mf_inst.calc_model_reg_score(y_test, y_test_pred)
    if verbose:
        console_output_score(_acc, _rec, _prec, _f1, _auc, _mse, _mae, _mae2)
    pred_pos_pct = (y_test_pred > score_threshold).sum() / len(y_test_pred)
    if verbose:
        print('测试集预测的正值样本的数量：', round(pred_pos_pct, 4))

    """求约登指数"""
    # from sklearn.metrics import roc_curve
    # tpr, fpr, thresholds = roc_curve(y_test, y_test_pred_prob)
    # J = tpr - fpr
    # idx = np.argmax(J)
    # best_threshold = thresholds[idx]

    # 整合valid以及pred，保存
    valid_test_pred = list(np.concatenate([y_valid_pred > score_threshold, y_test_pred > score_threshold]))
    valid_test_pred_prob = list(np.concatenate([y_valid_pred, y_test_pred]))
    valid_test_pred_df = pd.DataFrame(index=X_valid.index).append(pd.DataFrame(index=X_test.index))
    valid_test_pred_df['prediction'] = valid_test_pred
    valid_test_pred_df['pred_Reg'] = valid_test_pred_prob
    valid_test_pred_df['stockID'] = valid_test_pred_df.index.get_level_values(1)
    valid_test_pred_df['datelist'] = valid_test_pred_df.index.get_level_values(0).strftime('%Y%m%d')
    valid_test_pred_df['Indexs'] = valid_test_pred_df['stockID'] + ' ' + valid_test_pred_df['datelist']
    valid_test_pred_df = valid_test_pred_df.set_index('Indexs', drop=True)

    # 和v6版本样本对齐， TODO: 是否对齐
    # v6_samples = pd.read_csv(fc_path + 'Zeus/pred/SaturnS1/xgb_clf_model/hyper深更半夜的最后一次寻优/198/20190102~20200630_xgbClfModel_v1.csv', index_col=0)
    # valid_test_pred_df = valid_test_pred_df.reindex(index=v6_samples.index)

    if hyper_search_flag:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/hyper{hyper_remark}/{search_time}/')
    elif multi_grid_search_flag:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/multi_grid/{os.getpid()}/')
        print(f'{os.getpid()}_{search_time}')
    else:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/')
    FileUtil.save_df2csv(valid_test_pred_df, output_path, pred_fname)

    if not_search_but_backtest:
        eval_inst = EvalLaunch(date_config=date_config,
                               strategy_name=strategy_name,
                               sel_model_names=['xgbRegModel'],
                               pred_type=pred_type,
                               valid_path_list=[output_path + pred_fname],
                               pred_path_list=[output_path + pred_fname],
                               save_flag=True)
        _ = eval_inst.launch()
        del eval_inst

    # 如果是在寻优，进行下面的步骤
    if hyper_search_flag or multi_grid_search_flag:
        eval_inst = EvalLaunch(date_config=date_config,
                               strategy_name=strategy_name,
                               sel_model_names=['xgbRegModel'],
                               valid_path_list=[output_path + pred_fname],
                               pred_path_list=[output_path + pred_fname],
                               file_save_path=output_path,
                               save_flag=False)
        model_eval = eval_inst.launch()

        profit_risk_ratio = round(model_eval.loc['收益风险比'][0], 4) if model_eval.shape[0] > 0 else 0
        sharpe_ratio = round(model_eval.loc['夏普比率'][0], 4) if model_eval.shape[0] > 0 else 0
        buy_times = round(model_eval.loc['实际参与次数'][0], 4) if model_eval.shape[0] > 0 else 0
        cum_profit = round(model_eval.loc['累计扣费总收益'][0], 4) if model_eval.shape[0] > 0 else 0
        mdd_profit = round(model_eval.loc['最大回撤'][0], 4) if model_eval.shape[0] > 0 else 0
        winrate = round(model_eval.loc['扣费收益率胜率'][0], 4) if model_eval.shape[0] > 0 else 0
        join_pct = round(model_eval.loc['样本参与率'][0], 4) if model_eval.shape[0] > 0 else 0

        train_acc, valid_acc, test_acc = acc, acc_, _acc
        train_prec, valid_prec, test_prec = prec, prec_, _prec
        train_auc, valid_auc, test_auc = auc, auc_, _auc
        train_rec, valid_rec, test_rec = rec, rec_, _rec
        train_f1, valid_f1, test_f1 = f1, f1_, _f1
        train_mse, valid_mse, test_mse = mse, mse_, _mse
        train_mae, valid_mae, test_mae = mae, mae_, _mae
        train_mae2, valid_mae2, test_mae2 = mae2, mae2_, _mae2

        watch_scores = {
            '收益风险比': profit_risk_ratio,
            '夏普比率': sharpe_ratio,
            '买入笔数': int(buy_times),
            '总收益': cum_profit,
            '最大回撤': mdd_profit,
            '扣费收益率胜率': winrate,
            '样本参与率': join_pct,
            'train_acc': train_acc, 'valid_acc': valid_acc, 'test_acc': test_acc,
            'train_prec': train_prec, 'valid_prec': valid_prec, 'test_prec': test_prec,
            'train_rec': train_rec, 'valid_rec': valid_rec, 'test_rec': test_rec,
            'train_auc': train_auc, 'valid_auc': valid_auc, 'test_auc': test_auc,
            'train_f1': train_f1, 'valid_f1': valid_f1, 'test_f1': test_auc,
            'train_mse': train_mse, 'valid_mse': valid_mse, 'test_mse': test_mse,
            'train_mae': train_mae, 'valid_mae': valid_mae, 'test_mae': test_mae,
            'train_mae2': train_mae2, 'valid_mae2': valid_mae2, 'test_mae2': test_mae2
        }
        del eval_inst, model_eval
        if hyper_search_flag:   # 如果是hyperopt寻优，那么返回目标值
            my_logger.info(f'{watch_scores}: {param}')
            search_time += 1
            return mae_
        elif multi_grid_search_flag:    # 如果是网格搜索寻优，那么返回结果字符串，供后面解析
            return f'{watch_scores}: {param}'

if __name__ == '__main__':
    if hyper_search_flag:
        max_evals = 200
        trials = Trials()
        best_param = fmin(tuning_objective,
                          space=hyper_xgb_reg_params,
                          algo=tpe.suggest,
                          trials=trials,
                          max_evals=max_evals,
                          verbose=True,
                          rstate=np.random.RandomState(2022))
        my_logger.info(f'超参数寻优结束，最优超参数为{best_param}')
    elif multi_grid_search_flag:

        def get_param_backtest_result(params_list):
            ret_list = list()
            pbar = tqdm(range(len(params_list)))
            for idx in pbar:
                _param = params_list[idx]
                pbar.set_description('并行回测中|%s' % _param)
                bt_str = tuning_objective(_param)
                ret_list.append(bt_str)
            return ret_list

        multi_params_list = list(multi_xgb_reg_params.values())
        params = list(product(*multi_params_list))
        print(f'超参数的组合个数为{len(params)}个')
        grid_params = [dict(zip(list(multi_xgb_reg_params.keys()), _param)) for _param in params]
        ret_dict = multiprocess(4, get_param_backtest_result, grid_params)

        ret_list = list()
        ret_result = dict()
        for k in ret_dict:
            try:
                ret_result[k] = ret_dict[k].get()
            except Exception as e:
                print('多进程内部出错')
                print(e)

        for k in ret_result:
            ret_list.extend(ret_result[k])

        FileUtil.save_list2pkl(ret_list, multi_path, f'{strategy_name}_{model_name}_multi_gird之后的list结果.pkl')

        key_df = pd.DataFrame()
        value_df = pd.DataFrame()
        params_list = list()
        for _ret in ret_list:
            _key = _ret.split('}: {')[0]
            _value = _ret.split('}: {')[1]
            params_list.append('{' + _value)
            key_df = key_df.append(pd.DataFrame(pd.Series(eval(_key + '}'))).T)
            value_df = value_df.append(pd.DataFrame(pd.Series(eval('{' + _value))).T)

        key_df = key_df.reset_index(drop=True)
        value_df = value_df.reset_index(drop=True)
        multi_df = pd.concat([key_df, value_df], axis=1, join_axes=[value_df.index])
        multi_df['整体参数'] = params_list

        FileUtil.save_df2xls(multi_df, multi_path, f'{strategy_name}_{model_name}_multi_grid解析后参数表格.xlsx')

    else:
        param = model_params[model_name]
        tuning_objective(param)
