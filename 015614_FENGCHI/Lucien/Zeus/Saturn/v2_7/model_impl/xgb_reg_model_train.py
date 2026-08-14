# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 14:54

import time
import warnings
from itertools import product

import numpy as np
import pandas as pd
from hyperopt import fmin, Trials, tpe
from tqdm import tqdm

from LucienUtil.FileUtil import FileUtil
from Zeus.Saturn.v2_7.Tool import multiprocess, get_interval_data
from Zeus.Saturn.v2_7.hyper_param_space import hyper_xgb_reg_params, multi_xgb_reg_params
from Zeus.Saturn.v2_7.hyper_param_space import model_params
from Zeus.Saturn.v2_7.models.xgb_reg_model import XGBRegModel
from Zeus.Saturn.v2_7.my_logger import MyLogger
from Zeus.Saturn.v2_7.path_conf import *
from Zeus.Saturn.v2_7.BackTest.SimpleEvalLaunch import EvalLaunch

np.random.RandomState(2022)
warnings.filterwarnings("ignore")

# 各个开关
not_search_but_backtest = False  # 在不进行超参数寻优的时候在训练完以后自动进行回测，一般都开着
pred_type = 'test'   # 这个参数只在not_search_but_backtest为True时起作用，可选test/fit，给敬姐回测框架传的参数，定义文件名
hyper_search_mode = False   # 是否进行超参数寻优
multi_grid_search_mode = False   # 是否进行多进程参数寻优
test_cheat_mode = False   # 是否开启test作弊器
fit_cheat_mode = False  # 是否开启fit作弊器
rolling_type = 'test'   # 可选test/fit
generate_csv_valid_pred = True  # 是否保存结果到csv中供回测，只要是寻优这个就要开启

# 版本号信息
strategy_name = 'Saturn_down'
version = 'v2_7'
model_name = 'xgb_reg_model'
hyper_remark = 'down版本寻优v2'
hump_model_name = 'xgbRegModel'
verbose = False     # 控制是否输出内容
search_time = 0
pred_fname = f'20190102~20200630_{hump_model_name}_v1.csv'    # 保存在对应的版本路径下


if hyper_search_mode:
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
        print('R2: ', round(score_list[8], 4))
        print('EVS: ', round(score_list[9], 4))

def get_interval_period(df, start_date, end_date):
    _df = df.copy()
    _df['trade_date'] = df.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
    _df = _df.query(f'trade_date >= {start_date} & trade_date <= {end_date}')
    _df = _df.drop('trade_date', axis=1)
    return _df

# 可公用函数
def tuning_objective(param):
    global search_time
    param_copy = param.copy()

    # 自定义参数，如果不是在进行寻优，那么这些值是真实的因子，或者是best_param里有的话会覆盖下面的值
    factor_num = 520

    if 'n_estimators' in param_copy.keys():
        param_copy['n_estimators'] = int(param_copy['n_estimators'])
    if 'factor_num' in param_copy.keys():
        param_copy['factor_num'] = int(param_copy['factor_num'])
    # if hyper_search_flag:
    #     my_logger.info(f'第{search_time}轮超参数为: {param}')

    if 'factor_num' in param_copy.keys():
        factor_num = int(param_copy.pop('factor_num'))

    date_config = dict(train_start_date=20160104,
                       train_end_date=20181231,
                       valid_start_date=20190102,
                       valid_end_date=20190930,
                       test_start_date=20191008,
                       test_end_date=20200630)

    if verbose:
        print(f'现在使用的模型是{model_name}')
    mf_inst = XGBRegModel(model_name=model_name,
                          date_config=date_config,
                          factor_filter_path=filter_factor_fpath,
                          factor_score_path=factor_score_fpath,
                          data_path=saturn_data_test_fpath,
                          factor_num=factor_num,
                          label='label_pct')

    # TODO: 用于fit前保存因子顺序
    used_factor_list = mf_inst.factor_list
    # selected_factor_list = FileUtil.read_list(factor_select_path + f'{strategy_name}/{model_name}/{version}/', 'factor_selected.pkl')
    # used_factor_list = sorted(list(set(used_factor_list).intersection(set(selected_factor_list))))
    print(f'使用的因子数量{len(used_factor_list)}个')
    mf_inst.set_factor_list(used_factor_list)
    FileUtil.save_list2pkl(used_factor_list, factor_path + f'{strategy_name}/{model_name}/{version}/', f'{model_name}_factor_list.pkl')

    t1 = time.time()
    param4fit_copy = param_copy.copy()
    y_pred_prob_all, y_pred_clf_all = mf_inst.rolling_train_and_predict(len_train=5000,
                                                                        len_test=1300,
                                                                        rolling_type=rolling_type,
                                                                        param=param_copy)
    print(time.time() - t1, '秒')

    y_train, y_valid, y_test, y_train_prob, y_valid_prob, y_test_prob, y_train_clf, y_valid_clf, y_test_clf = \
        get_interval_data(mf_inst.y, y_pred_prob_all, y_pred_clf_all, date_config)

    # 评估部分
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_train.reindex(y_train_clf.index) > 0, y_train_clf)
    mse, mae, mae2, r2, evs = mf_inst.calc_model_reg_score(y_train.reindex(y_train_clf.index), y_train_prob)
    acc_, rec_, prec_, f1_, auc_ = mf_inst.calc_model_score(y_valid > 0, y_valid_clf)
    mse_, mae_, mae2_, r2_, evs_ = mf_inst.calc_model_reg_score(y_valid, y_valid_prob)
    if rolling_type is 'test':
        _acc, _rec, _prec, _f1, _auc = mf_inst.calc_model_score(y_test > 0, y_test_clf)
        _mse, _mae, _mae2, _r2, _evs = mf_inst.calc_model_reg_score(y_test, y_test_prob)
    else:
        _acc, _rec, _prec, _f1, _auc, _mse, _mae, _mae2, _r2, _evs = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    if verbose:
        print('训练集预测结果：')
        console_output_score(acc, rec, prec, f1, auc, mse, mae, mae2, r2, evs)
        print('验证集预测结果：')
        console_output_score(acc_, rec_, prec_, f1_, auc_, mse_, mae_, mae2_, r2_, evs_)
        if rolling_type is 'test':
            print('测试集预测结果：')
            console_output_score(_acc, _rec, _prec, _f1, _auc, _mse, _mae, _mae2, _r2, _evs)

    if not generate_csv_valid_pred:
        return mse_ # 直接进行寻优，文件都不进行保存

    # 整合valid以及pred，保存
    valid_test_pred = pd.concat([y_valid_clf, y_test_clf], axis=0)
    valid_test_pred_prob = pd.concat([y_valid_prob, y_test_prob], axis=0)
    valid_test_pred_df = pd.DataFrame(index=valid_test_pred.index)
    valid_test_pred_df['prediction'] = valid_test_pred
    valid_test_pred_df['pred_Reg'] = valid_test_pred_prob
    valid_test_pred_df['stockID'] = valid_test_pred_df.index.get_level_values(1)
    valid_test_pred_df['datelist'] = valid_test_pred_df.index.get_level_values(0).strftime('%Y%m%d')
    valid_test_pred_df['Indexs'] = valid_test_pred_df['stockID'] + ' ' + valid_test_pred_df['datelist']
    valid_test_pred_df = valid_test_pred_df.set_index('Indexs', drop=True)

    # 和v6版本样本对齐， TODO: 是否对齐
    # v6_samples = pd.read_csv(fc_path + 'Zeus/pred/SaturnS1/xgb_clf_model/hyper深更半夜的最后一次寻优/198/20190102~20200630_xgbClfModel_v1.csv', index_col=0)
    # valid_test_pred_df = valid_test_pred_df.reindex(index=v6_samples.index)

    if hyper_search_mode:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/hyper{hyper_remark}/{search_time}/')
    elif multi_grid_search_mode:
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
                               file_save_path=output_path,
                               save_flag=True)
        _ = eval_inst.launch()
        del eval_inst

    # 如果是在寻优，进行下面的步骤
    if hyper_search_mode or multi_grid_search_mode:
        if test_cheat_mode:
            eval_inst = EvalLaunch(date_config=date_config,
                                   strategy_name=strategy_name,
                                   sel_model_names=['xgbRegModel'],
                                   valid_path_list=[output_path + pred_fname],
                                   pred_path_list=[output_path + pred_fname],
                                   file_save_path=output_path,
                                   save_flag=False)
            model_eval = eval_inst.launch()
        else:
            model_eval = pd.DataFrame()
            eval_inst = None

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
        train_r2, valid_r2, test_r2 = r2, r2_, _r2
        train_evs, valid_evs, test_evs = evs, evs_, _evs

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
            'train_mae2': train_mae2, 'valid_mae2': valid_mae2, 'test_mae2': test_mae2,
            'train_r2': train_r2, 'valid_r2': valid_r2, 'test_r2': test_r2,
            'train_evs': train_evs, 'valid_evs': valid_evs, 'test_evs': test_evs
        }

        if fit_cheat_mode:
            date_config = dict(train_start_date=20160104,
                               train_end_date=20181231,
                               valid_start_date=20190102,
                               valid_end_date=20200630,
                               test_start_date=20200701,
                               test_end_date=20201231)
            mf_inst = XGBRegModel(model_name=model_name,
                                  date_config=date_config,
                                  factor_filter_path=filter_factor_fpath,
                                  factor_score_path=factor_score_fpath,
                                  data_path=saturn_data_fit_fpath,
                                  factor_num=factor_num,
                                  label='label_pct')
            # 读取train时的因子
            factor_list = FileUtil.read_list(factor_path + f'{strategy_name}/{model_name}/{version}/',
                                             f'{model_name}_factor_list.pkl')
            mf_inst.set_factor_list(factor_list)

            y_pred_prob_all, y_pred_clf_all = mf_inst.rolling_train_and_predict(len_train=5000,
                                                                                len_test=1300,
                                                                                rolling_type=rolling_type,
                                                                                param=param4fit_copy)
            _, _, _, _, y_valid_prob, y_test_prob, y_train_clf, y_valid_clf, y_test_clf = \
                get_interval_data(mf_inst.y, y_pred_prob_all, y_pred_clf_all, date_config)
            # 整合valid以及pred，保存
            valid_test_pred = pd.concat([y_valid_clf, y_test_clf], axis=0)
            valid_test_pred_prob = pd.concat([y_valid_prob, y_test_prob], axis=0)
            valid_test_pred_df = pd.DataFrame(index=valid_test_pred.index)
            valid_test_pred_df['prediction'] = valid_test_pred
            valid_test_pred_df['pred_Reg'] = valid_test_pred_prob
            valid_test_pred_df['stockID'] = valid_test_pred_df.index.get_level_values(1)
            valid_test_pred_df['datelist'] = valid_test_pred_df.index.get_level_values(0).strftime('%Y%m%d')
            valid_test_pred_df['Indexs'] = valid_test_pred_df['stockID'] + ' ' + valid_test_pred_df['datelist']
            valid_test_pred_df = valid_test_pred_df.set_index('Indexs', drop=True)

            output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/')
            FileUtil.save_df2csv(valid_test_pred_df, output_path, pred_fname)

            eval_inst = EvalLaunch(date_config=date_config,
                                   strategy_name=strategy_name,
                                   sel_model_names=['xgbRegModel'],
                                   pred_type=pred_type,
                                   valid_path_list=[output_path + pred_fname],
                                   pred_path_list=[output_path + pred_fname],
                                   save_flag=False)
            model_eval = eval_inst.launch()

            _profit_risk_ratio = round(model_eval.loc['收益风险比'][0], 4) if model_eval.shape[0] > 0 else 0
            _sharpe_ratio = round(model_eval.loc['夏普比率'][0], 4) if model_eval.shape[0] > 0 else 0
            _buy_times = round(model_eval.loc['实际参与次数'][0], 4) if model_eval.shape[0] > 0 else 0
            _cum_profit = round(model_eval.loc['累计扣费总收益'][0], 4) if model_eval.shape[0] > 0 else 0
            _mdd_profit = round(model_eval.loc['最大回撤'][0], 4) if model_eval.shape[0] > 0 else 0
            _winrate = round(model_eval.loc['扣费收益率胜率'][0], 4) if model_eval.shape[0] > 0 else 0
            _join_pct = round(model_eval.loc['样本参与率'][0], 4) if model_eval.shape[0] > 0 else 0

            watch_scores.update({
                '收益风险比2': _profit_risk_ratio,
                '夏普比率2': _sharpe_ratio,
                '买入笔数2': int(_buy_times),
                '总收益2': _cum_profit,
                '最大回撤2': _mdd_profit,
                '扣费收益率胜率2': _winrate,
                '样本参与率2': _join_pct,
            })

        del eval_inst, model_eval
        if hyper_search_mode:   # 如果是hyperopt寻优，那么返回目标值
            my_logger.info(f'{watch_scores}: {param}')
            search_time += 1
            return mse_
        elif multi_grid_search_mode:    # 如果是网格搜索寻优，那么返回结果字符串，供后面解析
            return f'{watch_scores}: {param}'

if __name__ == '__main__':
    if hyper_search_mode:
        max_evals = 300 # 300轮耗时12个半小时左右
        trials = Trials()
        best_param = fmin(tuning_objective,
                          space=hyper_xgb_reg_params,
                          algo=tpe.suggest,
                          trials=trials,
                          max_evals=max_evals,
                          verbose=True,
                          rstate=np.random.RandomState(2022))
        my_logger.info(f'超参数寻优结束，最优超参数为{best_param}')
    elif multi_grid_search_mode:

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
        ret_dict = multiprocess(20, get_param_backtest_result, grid_params)

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

        # FileUtil.save_list2pkl(ret_list, multi_path + f'{strategy_name}_{model_name}_{version}/',
        #                        'multi_gird之后的list结果.pkl')

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

        FileUtil.save_df2xls(multi_df, multi_path + f'{strategy_name}/{model_name}/{version}/',
                             'multi_grid解析后参数表格_nocheat.xlsx')

    else:
        param = model_params[model_name]
        tuning_objective(param)
