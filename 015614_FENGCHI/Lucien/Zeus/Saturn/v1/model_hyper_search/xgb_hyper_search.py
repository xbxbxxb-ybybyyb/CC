# coding: utf-8
# Author：fengchi863
# Date ：2022/7/14 10:52

from Zeus.Saturn.v1.models.ModelFactory import ModelFactory
from Zeus.Saturn.v1.hyper_param_space import model_params, hyper_xgb_clf_params
from Zeus.Saturn.v1.path_conf import *
from LucienUtil.FileUtil import FileUtil
import warnings
import pandas as pd
import numpy as np
from hyperopt import Trials, fmin, tpe
from Zeus.Saturn.v1.my_logger import my_logger
import time
from hyperopt.mongoexp import MongoTrials
warnings.filterwarnings("ignore")
search_times = 0


def console_output_score(*score_list):
    print('准确率: ', round(score_list[0], 4))
    print('召回率: ', round(score_list[1], 4))
    print('精确率: ', round(score_list[2], 4))
    print('F1值: ', round(score_list[3], 4))
    print('AUC: ', round(score_list[4], 4))


def tuning_objective(param):
    global search_times

    factor_num = 450
    score_threshold = 0.5

    if 'n_estimators' in param.keys():
        param['n_estimators'] = int(param['n_estimators'])
    my_logger.info(f'第{search_times}轮超参数为: {param}')

    if 'factor_num' in param.keys():
        factor_num = int(param.pop('factor_num'))
    if 'score_threshold' in param.keys():
        score_threshold = param.pop('score_threshold')

    t1 = time.time()
    strategy = 'Saturn_v1'
    model_name = 'xgb_clf_model'
    date_config = dict(train_start_date=20160104,
                       train_end_date=20181231,
                       valid_start_date=20190102,
                       valid_end_date=20190930,
                       test_start_date=20191008,
                       test_end_date=20200630)

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
    print('训练集正样本比例为：', round((y_train.sum() / y_train.shape[0])[0], 4))
    print('验证集正样本比例为：', round((y_valid.sum() / y_valid.shape[0])[0], 4))
    print('测试集正样本比例为：', round((y_test.sum() / y_test.shape[0])[0], 4))
    print('*' * 30)

    mf_inst.train_model(X_train, y_train, param=param)
    y_train_pred = mf_inst.model_predict(X_train.values)
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_train, y_train_pred)
    console_output_score(acc, rec, prec, f1, auc)
    pred_pos_pct = y_train_pred.sum() / len(y_train_pred)
    print('训练集预测的正值样本的数量：', round(pred_pos_pct, 4))

    # y_valid_pred = mf_inst.model_predict(X_valid.values)
    y_valid_pred_prob = mf_inst.model.model.predict_proba(X_valid.values)[:, 1]
    y_valid_pred = y_valid_pred_prob > score_threshold
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_valid, y_valid_pred)
    console_output_score(acc, rec, prec, f1, auc)
    pred_pos_pct = y_valid_pred.sum() / len(y_valid_pred)
    print('验证集预测的正值样本的数量：', round(pred_pos_pct, 4))

    # y_test_pred = mf_inst.model_predict(X_test.values)
    y_test_pred_prob = mf_inst.model.model.predict_proba(X_test.values)[:, 1]
    y_test_pred = y_test_pred_prob > score_threshold
    _acc, _rec, _prec, _f1, _auc = mf_inst.calc_model_score(y_test, y_test_pred)
    console_output_score(_acc, _rec, _prec, _f1, _auc)
    pred_pos_pct = y_test_pred.sum() / len(y_test_pred)
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
    output_path = os.path.join(pred_out_path, f'{strategy}/{model_name}/')
    fname = f'20190102~20200630_fcModel_v1.csv'
    FileUtil.save_df2csv(valid_test_pred_df, output_path, fname)

    os.system('python3 /data/user/015614/Lucien/MixedWork/entry_prepare/model_eval_old/modelEval_SaturnS1.py')

    bt_result = pd.read_excel('/data/group/800463/fengc/Saturn/v1/bactest/回测结果/20191008~20200630_SaturnS1_xgbClfModel_模型评价_20220714.xlsx', sheet_name=None, index_col=0)
    check1 = bt_result['模型结果']
    check2 = bt_result['按日统计']
    profit_risk_ratio = check1.loc['收益风险比'][0]
    sharpe_ratio = check1.loc['夏普比率'][0]
    buy_times = check1.loc['实际参与次数'][0]
    cum_profit = check2.iloc[-1]['累计盈亏(扣除成本)']
    mdd_profit = check1.loc['最大回撤'][0]
    watch_scores = [profit_risk_ratio, sharpe_ratio, buy_times, cum_profit, mdd_profit]
    watch_scores_str = ', '.join(list(map(lambda x: str(round(x, 4)) if ~np.isnan(x) else 'nan', watch_scores)))
    my_logger.info(f'此轮耗时{round(time.time() - t1, 2)}秒：{watch_scores_str}')
    search_times += 1
    return -auc


if __name__ == '__main__':
    # tuning_objective(model_params['xgb_clf_model'])
    max_evals = 250
    trials = Trials()
    best_param = fmin(tuning_objective,
                      space=hyper_xgb_clf_params,
                      algo=tpe.suggest,
                      trials=trials,
                      max_evals=max_evals,
                      verbose=True,
                      rstate=np.random.RandomState(2022))
    my_logger.info(f'超参数寻优结束，最优超参数为{best_param}')
    for idx, trial in enumerate(trials.trials[:max_evals]):
        my_logger.info(f'第{idx}次: {trial}')
