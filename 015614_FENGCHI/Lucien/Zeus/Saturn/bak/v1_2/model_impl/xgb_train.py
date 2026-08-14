# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 14:54

from Zeus.Saturn.v1_2.models.ModelFactory import ModelFactory
from Zeus.Saturn.v1_2.hyper_param_space import model_params
from Zeus.Saturn.v1_2.path_conf import *
from LucienUtil.FileUtil import FileUtil
import warnings
import pandas as pd
import numpy as np
import time
from Zeus.Saturn.v1_2.my_logger import MyLogger
from Zeus.Saturn.v1_2.hyper_param_space import hyper_xgb_clf_params
from hyperopt import fmin, Trials, tpe
from dataApi.tradeDate import get_today
np.random.RandomState(2022)
warnings.filterwarnings("ignore")


hyper_search_flag = True   # 是否进行超参数寻优

strategy_name = 'SaturnS1'
version = 'v1_2'
model_name = 'xgb_clf_model'
hyper_remark = ''
hump_model_name = 'xgbClfModel'
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

# 可公用函数
def tuning_objective(param):
    global search_time
    t1 = time.time()

    # 自定义参数，如果不是在进行寻优，那么这些值是真实的因子，或者是best_param里有的话会覆盖下面的值
    factor_num = 520
    score_threshold = 0.45970953626866

    if 'n_estimators' in param.keys():
        param['n_estimators'] = int(param['n_estimators'])
    if 'factor_num' in param.keys():
        param['factor_num'] = int(param['factor_num'])
    if hyper_search_flag:
        my_logger.info(f'第{search_time}轮超参数为: {param}')

    if 'factor_num' in param.keys():
        factor_num = int(param.pop('factor_num'))
    if 'score_threshold' in param.keys():
        score_threshold = param.pop('score_threshold')

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
                           factor_num=factor_num,
                           label='label_mixed_0712')
    X_train, y_train, X_valid, y_valid, X_test, y_test = mf_inst.get_dateset()

    y_train = (y_train > 0).astype(int)
    y_valid = (y_valid > 0).astype(int)
    y_test = (y_test > 0).astype(int)
    if verbose:
        print('训练集正样本比例为：', round((y_train.sum() / y_train.shape[0])[0], 4))
        print('验证集正样本比例为：', round((y_valid.sum() / y_valid.shape[0])[0], 4))
        print('测试集正样本比例为：', round((y_test.sum() / y_test.shape[0])[0], 4))
        print('*' * 30)

    mf_inst.train_model(X_train, y_train, param=param)
    y_train_pred = mf_inst.model_predict(X_train.values)
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_train, y_train_pred)
    if verbose:
        console_output_score(acc, rec, prec, f1, auc)
    pred_pos_pct = y_train_pred.sum() / len(y_train_pred)
    if verbose:
        print('训练集预测的正值样本的数量：', round(pred_pos_pct, 4))

    # y_valid_pred = mf_inst.model_predict(X_valid.values)
    y_valid_pred_prob = mf_inst.model.model.predict_proba(X_valid.values)[:, 1]
    y_valid_pred = y_valid_pred_prob > score_threshold
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_valid, y_valid_pred)
    if verbose:
        console_output_score(acc, rec, prec, f1, auc)
    pred_pos_pct = y_valid_pred.sum() / len(y_valid_pred)
    if verbose:
        print('验证集预测的正值样本的数量：', round(pred_pos_pct, 4))

    # y_test_pred = mf_inst.model_predict(X_test.values)
    y_test_pred_prob = mf_inst.model.model.predict_proba(X_test.values)[:, 1]
    y_test_pred = y_test_pred_prob > score_threshold
    _acc, _rec, _prec, _f1, _auc = mf_inst.calc_model_score(y_test, y_test_pred)
    if verbose:
        console_output_score(_acc, _rec, _prec, _f1, _auc)
    pred_pos_pct = y_test_pred.sum() / len(y_test_pred)
    if verbose:
        print('测试集预测的正值样本的数量：', round(pred_pos_pct, 4))

    """求约登指数"""
    # from sklearn.metrics import roc_curve
    # tpr, fpr, thresholds = roc_curve(y_test, y_test_pred_prob)
    # J = tpr - fpr
    # idx = np.argmax(J)
    # best_threshold = thresholds[idx]

    # 整合valid以及pred，保存
    valid_test_pred = list(np.concatenate([y_valid_pred, y_test_pred]))
    valid_test_pred_prob = list(np.concatenate([y_valid_pred_prob, y_test_pred_prob]))
    valid_test_pred_df = pd.DataFrame(index=X_valid.index).append(pd.DataFrame(index=X_test.index))
    valid_test_pred_df['prediction'] = valid_test_pred
    valid_test_pred_df['pred_Reg'] = valid_test_pred_prob
    valid_test_pred_df['stockID'] = valid_test_pred_df.index.get_level_values(1)
    valid_test_pred_df['datelist'] = valid_test_pred_df.index.get_level_values(0).strftime('%Y%m%d')
    valid_test_pred_df['Indexs'] = valid_test_pred_df['stockID'] + ' ' + valid_test_pred_df['datelist']
    valid_test_pred_df = valid_test_pred_df.set_index('Indexs', drop=True)
    if hyper_search_flag:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/hyper{hyper_remark}/{search_time}/')
    else:
        output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/')
    FileUtil.save_df2csv(valid_test_pred_df, output_path, pred_fname)

    # 如果是在寻优，进行下面的步骤
    if hyper_search_flag:
        sys_param = f'{search_time} {strategy_name} {version} {model_name} {hump_model_name} {output_path + pred_fname}'
        os.system(f'python3 /data/user/015614/Lucien/MixedWork/entry_prepare/model_eval/modelEval_launch.py {sys_param}')

        today_date = get_today(dividing_point=0)
        output_path = bt_out_path + f'{strategy_name}/{version}/{model_name}/hyper_opt/{search_time}/回测结果/20191008~20200630_{strategy_name}_{hump_model_name}_模型评价_{today_date}.xlsx'
        bt_result = pd.read_excel(output_path, sheet_name=None, index_col=0)

        check1 = bt_result['模型结果']
        check2 = bt_result['按日统计']
        profit_risk_ratio = round(check1.loc['收益风险比'][0], 4)
        sharpe_ratio = round(check1.loc['夏普比率'][0], 4)
        buy_times = round(check1.loc['实际参与次数'][0], 4)
        cum_profit = round(check2.iloc[-1]['累计盈亏(扣除成本)'], 4)
        mdd_profit = round(check1.loc['最大回撤'][0], 4)
        watch_scores = {
            '收益风险比': profit_risk_ratio,
            '夏普比率': sharpe_ratio,
            '买入笔数': buy_times,
            '总收益': cum_profit,
            '最大回撤': mdd_profit
        }
        my_logger.info(f'第{search_time}轮耗时{round(time.time() - t1, 2)}秒：{watch_scores}')
        search_time += 1
        return -cum_profit * profit_risk_ratio

if __name__ == '__main__':
    if hyper_search_flag:
        max_evals = 200
        trials = Trials()
        best_param = fmin(tuning_objective,
                          space=hyper_xgb_clf_params,
                          algo=tpe.suggest,
                          trials=trials,
                          max_evals=max_evals,
                          verbose=True,
                          rstate=np.random.RandomState(2022))
        my_logger.info(f'超参数寻优结束，最优超参数为{best_param}')
    else:
        param = model_params[model_name]
        tuning_objective(param)