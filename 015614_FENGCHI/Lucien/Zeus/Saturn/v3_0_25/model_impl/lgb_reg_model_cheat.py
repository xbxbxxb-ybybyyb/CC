# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 14:54
import sys
sys.path.append('/data/user/015614/Lucien')

import time
import warnings
from itertools import product

import numpy as np
import pandas as pd
from hyperopt import fmin, Trials, tpe
from tqdm import tqdm

from LucienUtil.FileUtil import FileUtil
from Zeus.Saturn.v3_0_25.Tool import multiprocess
from Zeus.Saturn.v3_0_25.hyper_param_space import hyper_lgb_reg_params, multi_lgb_reg_params
from Zeus.Saturn.v3_0_25.hyper_param_space import model_params
from Zeus.Saturn.v3_0_25.models.lgb_reg_model import LGBRegModel
from Zeus.Saturn.v3_0_25.my_logger import MyLogger
from Zeus.Saturn.v3_0_25.path_conf import *
from model_eval.bak.bak20230105_simple_bt.v3_1_SimpleEvalLaunch import EvalLaunch

np.random.RandomState(2022)
warnings.filterwarnings("ignore")

# 各个开关
not_search_but_backtest = False  # 在不进行超参数寻优的时候在训练完以后自动进行回测，一般都开着
pred_type = 'test'   # 这个参数只在not_search_but_backtest为True时起作用，可选test/fit，给敬姐回测框架传的参数，定义文件名
hyper_search_mode = True   # 是否进行超参数寻优
multi_grid_search_mode = False   # 是否进行多进程参数寻优
test_cheat_mode = True   # 是否开启test作弊器
fit_cheat_mode = True  # 是否开启fit作弊器
rolling_type = 'test'   # 可选test/fit
generate_csv_valid_pred = True  # 是否保存结果到csv中供回测，如果只要是寻优这个就要开启

# 版本号信息
strategy_name = 'SaturnS1'
version = 'v3_0_25'
model_name = 'lgb_reg_model'
hyper_remark = '用全部因子进行测试20170101-20200630'
hump_model_name = 'LGBRegModel'
verbose = False
search_time = 0
test_fname = f'20190102~20200630_{hump_model_name}_v1.csv'    # 保存在对应的版本路径下
fit_fname = f'20200701~20201231_{hump_model_name}_v1.csv'


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
    if 'max_depth' in param_copy.keys():
        param_copy['max_depth'] = int(param_copy['max_depth'])
    if 'num_leaves' in param_copy.keys():
        param_copy['num_leaves'] = int(param_copy['num_leaves'])
    if 'min_data_in_leaf' in param_copy.keys():
        param_copy['min_data_in_leaf'] = int(param_copy['min_data_in_leaf'])
    if 'min_child_samples' in param_copy.keys():
        param_copy['min_child_samples'] = int(param_copy['min_child_samples'])

    score_threshold = 0
    if 'factor_num' in param_copy.keys():
        factor_num = int(param_copy.pop('factor_num'))
    if 'score_threshold' in param_copy.keys():
        score_threshold = param_copy['score_threshold'] # 用于外部评估

    date_config = dict(
        train_start_date=20160104,
        train_end_date=20181231,
        valid_start_date=20190102,
        valid_end_date=20190930,
        test_start_date=20191008,
        test_end_date=20200630
    )

    if verbose:
        print(f'现在使用的模型是{model_name}')
    mf_inst = LGBRegModel(model_name=model_name,
                          date_config=date_config,
                          factor_filter_path=filter_factor_fpath,
                          factor_score_path=factor_score_fpath,
                          data_path=saturn_data_test_fpath,
                          factor_num=factor_num,
                          label='label_v2o10d1')

    selected_factor_list = FileUtil.read_list(factor_path + f'{strategy_name}/{model_name}/{version}/', 'factor_list.pkl')
    print(f'使用的因子数量{min(factor_num, len(selected_factor_list))}个')
    mf_inst.set_factor_list(selected_factor_list)

    t1 = time.time()
    param4fit_copy = param_copy.copy()
    X_train, y_train, X_valid, y_valid, X_test, y_test = mf_inst.get_dateset()
    mf_inst.train_model(X_train, y_train, X_valid, y_valid, param=param_copy)
    print(f'此轮训练耗时{round(time.time() - t1, 2)}秒')

    # 评估部分
    y_train_pred = mf_inst.model_predict(X_train.values)
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_train > score_threshold, y_train_pred > score_threshold)
    mse, mae, mae2, r2 = mf_inst.calc_model_reg_score(y_train, y_train_pred)

    y_valid_pred = mf_inst.model_predict(X_valid.values)
    acc_, rec_, prec_, f1_, auc_ = mf_inst.calc_model_score(y_valid > score_threshold, y_valid_pred > score_threshold)
    mse_, mae_, mae2_, r2_ = mf_inst.calc_model_reg_score(y_valid, y_valid_pred)

    y_test_pred = mf_inst.model_predict(X_test.values)
    _acc, _rec, _prec, _f1, _auc = mf_inst.calc_model_score(y_test > score_threshold, y_test_pred > score_threshold)
    _mse, _mae, _mae2, _r2 = mf_inst.calc_model_reg_score(y_test, y_test_pred)

    if verbose:
        print('训练集预测结果：')
        console_output_score(acc, rec, prec, f1, auc, mse, mae, mae2, r2)
        print('验证集预测结果：')
        console_output_score(acc_, rec_, prec_, f1_, auc_, mse_, mae_, mae2_, r2_)
        if rolling_type is 'test':
            print('测试集预测结果：')
            console_output_score(_acc, _rec, _prec, _f1, _auc, _mse, _mae, _mae2, _r2)

    if not generate_csv_valid_pred:
        return mf_inst.best_score # 直接进行寻优，文件都不进行保存

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

    if hyper_search_mode:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/hyper{hyper_remark}/{search_time}/')
    elif multi_grid_search_mode:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/multi_grid/{os.getpid()}/')
        print(f'{os.getpid()}_{search_time}')
    else:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/')
    FileUtil.save_df2csv(valid_test_pred_df, output_path, test_fname)

    if not_search_but_backtest:
        eval_inst = EvalLaunch(date_config=date_config,
                               strategy_name=strategy_name,
                               sel_model_names=['LGBRegModel'],
                               pred_type=pred_type,
                               valid_path_list=[output_path + test_fname],
                               pred_path_list=[output_path + test_fname],
                               file_save_path=output_path,
                               save_flag=True)
        _, _ = eval_inst.launch()
        del eval_inst

    # 如果是在寻优，进行下面的步骤
    if hyper_search_mode or multi_grid_search_mode:
        if test_cheat_mode:
            eval_inst = EvalLaunch(date_config=date_config,
                                   strategy_name=strategy_name,
                                   sel_model_names=['LGBRegModel'],
                                   valid_path_list=[output_path + test_fname],
                                   pred_path_list=[output_path + test_fname],
                                   file_save_path=output_path,
                                   save_flag=False)
            model_eval, model_mingan = eval_inst.launch()
        else:
            model_eval, model_mingan = pd.DataFrame()
            eval_inst = None

        model_mingan = model_mingan.sort_values('收益风险比', ascending=False)
        model_mingan['test_indicator'] = model_mingan['收益风险比'] * model_mingan['累计盈利']

        model_mingan = model_mingan.sort_values('收益风险比', ascending=False)
        model_mingan_copy = model_mingan.copy()
        model_mingan_copy['fit_indicator'] = model_mingan_copy['收益风险比'] * model_mingan_copy['扣费收益率胜率'] * model_mingan_copy['实际参与率']
        model_mingan_copy = model_mingan_copy.query('0.1 < 实际参与率 < 0.3')  # 控制参与率在0.1-0.3之间
        model_mingan_copy = model_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]

        profit_risk_ratio = round(model_eval.loc['收益风险比'][0], 4) if model_eval.shape[0] > 0 else 0
        ic = round(model_eval.loc['预测值与标签IC'][0], 4) if model_eval.shape[0] > 0 else 0
        sharpe_ratio = round(model_eval.loc['夏普比率'][0], 4) if model_eval.shape[0] > 0 else 0
        buy_times = round(model_eval.loc['实际参与次数'][0], 4) if model_eval.shape[0] > 0 else 0
        cum_profit = round(model_eval.loc['累计扣费总收益'][0], 4) if model_eval.shape[0] > 0 else 0
        mdd_profit = round(model_eval.loc['最大回撤'][0], 4) if model_eval.shape[0] > 0 else 0
        winrate = round(model_eval.loc['扣费收益率胜率'][0], 4) if model_eval.shape[0] > 0 else 0
        join_pct = round(model_eval.loc['样本参与率'][0], 4) if model_eval.shape[0] > 0 else 0
        max_profit_risk_ratio = round(model_mingan['收益风险比'][0], 4) if model_mingan.shape[0] > 0 else 0
        max_winrate = round(model_mingan['扣费收益率胜率'].max(), 4) if model_mingan.shape[0] > 0 else 0
        max_cum_profit = round(model_mingan['累计盈利'].max(), 4) if model_mingan.shape[0] > 0 else 0
        max_sharpe_ratio = round(model_mingan['夏普比率'].max(), 4) if model_mingan.shape[0] > 0 else 0
        adapt_profit_risk_ratio = round(model_mingan_copy['收益风险比'], 4) if model_mingan_copy.shape[0] > 0 else 0
        adapt_winrate = round(model_mingan_copy['扣费收益率胜率'], 4) if model_mingan_copy.shape[0] > 0 else 0
        adapt_join_pct = round(model_mingan_copy['实际参与率'], 4) if model_mingan_copy.shape[0] > 0 else 0
        adapt_sharpe_ratio = round(model_mingan_copy['夏普比率'], 4) if model_mingan_copy.shape[0] > 0 else 0
        adapt_cum_profit = round(model_mingan_copy['累计盈利'], 4) if model_mingan_copy.shape[0] > 0 else 0
        adapt_score_threshold = float(model_mingan_copy.name) if model_mingan_copy.shape[0] > 0 else 0

        train_acc, valid_acc, test_acc = acc, acc_, _acc
        train_prec, valid_prec, test_prec = prec, prec_, _prec
        train_auc, valid_auc, test_auc = auc, auc_, _auc
        train_rec, valid_rec, test_rec = rec, rec_, _rec
        train_f1, valid_f1, test_f1 = f1, f1_, _f1
        train_mse, valid_mse, test_mse = mse, mse_, _mse
        train_mae, valid_mae, test_mae = mae, mae_, _mae
        train_mae2, valid_mae2, test_mae2 = mae2, mae2_, _mae2
        train_r2, valid_r2, test_r2 = r2, r2_, _r2

        watch_scores = {
            '收益风险比': profit_risk_ratio,
            '预测值与标签IC': ic,
            '夏普比率': sharpe_ratio,
            '买入笔数': int(buy_times),
            '总收益': cum_profit,
            '最大回撤': mdd_profit,
            '扣费收益率胜率': winrate,
            '样本参与率': join_pct,
            '最大收益风险比': max_profit_risk_ratio,
            '最大扣费收益率胜率': max_winrate,
            '最大累计盈利': max_cum_profit,
            '最大夏普比率': max_sharpe_ratio,
            '自适应风险收益比': adapt_profit_risk_ratio,
            '自适应扣费收益率胜率': adapt_winrate,
            '自适应参与率': adapt_join_pct,
            '自适应夏普比率': adapt_sharpe_ratio,
            '自适应累计盈利': adapt_cum_profit,
            '自适应阈值': adapt_score_threshold,
            'train_acc': train_acc, 'valid_acc': valid_acc, 'test_acc': test_acc,
            'train_prec': train_prec, 'valid_prec': valid_prec, 'test_prec': test_prec,
            'train_rec': train_rec, 'valid_rec': valid_rec, 'test_rec': test_rec,
            'train_auc': train_auc, 'valid_auc': valid_auc, 'test_auc': test_auc,
            'train_f1': train_f1, 'valid_f1': valid_f1, 'test_f1': test_auc,
            'train_mse': train_mse, 'valid_mse': valid_mse, 'test_mse': test_mse,
            'train_mae': train_mae, 'valid_mae': valid_mae, 'test_mae': test_mae,
            'train_mae2': train_mae2, 'valid_mae2': valid_mae2, 'test_mae2': test_mae2,
            'train_r2': train_r2, 'valid_r2': valid_r2, 'test_r2': test_r2,
        }

        if fit_cheat_mode:
            date_config = dict(train_start_date=20170101,
                               train_end_date=20200630,
                               valid_start_date=20191008,
                               valid_end_date=20200630,
                               test_start_date=20200701,
                               test_end_date=20201231)
            mf_inst = LGBRegModel(model_name=model_name,
                                  date_config=date_config,
                                  factor_filter_path=filter_factor_fpath,
                                  factor_score_path=factor_score_fpath,
                                  data_path=saturn_data_fit_fpath,
                                  factor_num=factor_num,
                                  label='label_v2o10d1')
            # 读取train时的因子
            factor_list = FileUtil.read_list(factor_path + f'{strategy_name}/{model_name}/{version}/', f'factor_list.pkl')
            mf_inst.set_factor_list(factor_list)

            X_train, y_train, X_valid, y_valid, X_test, y_test = mf_inst.get_dateset()
            mf_inst.train_model(X_train, y_train, X_valid, y_valid, param=param4fit_copy)
            print(f'此轮训练耗时{round(time.time() - t1, 2)}秒')

            # 评估部分
            y_valid_pred = mf_inst.model_predict(X_valid.values)
            y_test_pred = mf_inst.model_predict(X_test.values)

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

            output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/{version}/hyper{hyper_remark}/{search_time}/')
            FileUtil.save_df2csv(valid_test_pred_df, output_path, fit_fname)

            eval_inst = EvalLaunch(date_config=date_config,
                                   strategy_name=strategy_name,
                                   sel_model_names=['LGBRegModel'],
                                   pred_type=pred_type,
                                   valid_path_list=[output_path + fit_fname],
                                   pred_path_list=[output_path + fit_fname],
                                   file_save_path=output_path,
                                   save_flag=True)
            model_eval, model_mingan = eval_inst.launch()

            model_mingan = model_mingan.sort_values('收益风险比', ascending=False)
            model_mingan_copy = model_mingan.copy()
            model_mingan_copy['fit_indicator'] = model_mingan_copy['收益风险比'] * model_mingan_copy['扣费收益率胜率'] * model_mingan_copy['实际参与率']
            model_mingan_copy = model_mingan_copy.query('0.1 < 实际参与率 < 0.3')    # 控制参与率在0.1-0.3之间
            model_mingan_copy = model_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]

            _profit_risk_ratio = round(model_eval.loc['收益风险比'][0], 4) if model_eval.shape[0] > 0 else 0
            _ic = round(model_eval.loc['预测值与标签IC'][0], 4) if model_eval.shape[0] > 0 else 0
            _sharpe_ratio = round(model_eval.loc['夏普比率'][0], 4) if model_eval.shape[0] > 0 else 0
            _buy_times = round(model_eval.loc['实际参与次数'][0], 4) if model_eval.shape[0] > 0 else 0
            _cum_profit = round(model_eval.loc['累计扣费总收益'][0], 4) if model_eval.shape[0] > 0 else 0
            _mdd_profit = round(model_eval.loc['最大回撤'][0], 4) if model_eval.shape[0] > 0 else 0
            _winrate = round(model_eval.loc['扣费收益率胜率'][0], 4) if model_eval.shape[0] > 0 else 0
            _join_pct = round(model_eval.loc['样本参与率'][0], 4) if model_eval.shape[0] > 0 else 0
            _max_profit_risk_ratio = round(model_mingan['收益风险比'][0], 4) if model_mingan.shape[0] > 0 else 0
            _max_winrate = round(model_mingan['扣费收益率胜率'].max(), 4) if model_mingan.shape[0] > 0 else 0
            _max_cum_profit = round(model_mingan['累计盈利'].max(), 4) if model_mingan.shape[0] > 0 else 0
            _max_sharpe_ratio = round(model_mingan['夏普比率'].max(), 4) if model_mingan.shape[0] > 0 else 0
            _adapt_profit_risk_ratio = round(model_mingan_copy['收益风险比'], 4)  if model_mingan_copy.shape[0] > 0 else 0
            _adapt_winrate = round(model_mingan_copy['扣费收益率胜率'], 4)  if model_mingan_copy.shape[0] > 0 else 0
            _adapt_join_pct = round(model_mingan_copy['实际参与率'], 4)  if model_mingan_copy.shape[0] > 0 else 0
            _adapt_sharpe_ratio = round(model_mingan_copy['夏普比率'], 4)  if model_mingan_copy.shape[0] > 0 else 0
            _adapt_cum_profit = round(model_mingan_copy['累计盈利'], 4) if model_mingan_copy.shape[0] > 0 else 0
            _adapt_score_threshold = float(model_mingan_copy.name) if model_mingan_copy.shape[0] > 0 else 0

            watch_scores.update({
                '收益风险比2': _profit_risk_ratio,
                '预测值与标签IC2': _ic,
                '夏普比率2': _sharpe_ratio,
                '买入笔数2': int(_buy_times),
                '总收益2': _cum_profit,
                '最大回撤2': _mdd_profit,
                '扣费收益率胜率2': _winrate,
                '样本参与率2': _join_pct,
                '最大收益风险比2': _max_profit_risk_ratio,
                '最大扣费收益率胜率2': _max_winrate,
                '最大累计盈利2': _max_cum_profit,
                '最大夏普比率2': _max_sharpe_ratio,
                '自适应风险收益比2': _adapt_profit_risk_ratio,
                '自适应扣费收益率胜率2': _adapt_winrate,
                '自适应参与率2': _adapt_join_pct,
                '自适应夏普比率2': _adapt_sharpe_ratio,
                '自适应累计盈利2': _adapt_cum_profit,
                '自适应阈值2': _adapt_score_threshold,
            })

        del eval_inst, model_eval, model_mingan
        if hyper_search_mode:   # 如果是hyperopt寻优，那么返回目标值
            my_logger.info(f'{watch_scores}: {param}')
            search_time += 1
            return -ic
        elif multi_grid_search_mode:    # 如果是网格搜索寻优，那么返回结果字符串，供后面解析
            return f'{watch_scores}: {param}'

if __name__ == '__main__':
    if hyper_search_mode:
        max_evals = 300
        trials = Trials()
        best_param = fmin(tuning_objective,
                          space=hyper_lgb_reg_params,
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

        multi_params_list = list(multi_lgb_reg_params.values())
        params = list(product(*multi_params_list))
        print(f'超参数的组合个数为{len(params)}个')
        grid_params = [dict(zip(list(multi_lgb_reg_params.keys()), _param)) for _param in params]
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
