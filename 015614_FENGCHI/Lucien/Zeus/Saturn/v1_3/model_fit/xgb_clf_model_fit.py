# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 9:30

from Zeus.Saturn.v1_3.models.ModelFactory import ModelFactory
from Zeus.Saturn.v1_3.hyper_param_space import model_params
from Zeus.Saturn.v1_3.path_conf import *
from LucienUtil.FileUtil import FileUtil
import warnings
import pandas as pd
import numpy as np
from Zeus.Saturn.v1_3.BackTest.EvalLaunch import EvalLaunch
np.random.RandomState(2022)
warnings.filterwarnings("ignore")

strategy_name = 'SaturnS1'
version = 'v1_3'
model_name = 'xgb_clf_model'
hyper_remark = '深更半夜的最后一次寻优'
hump_model_name = 'xgbClfModel'
verbose = True     # 控制是否输出内容
search_time = 0
pred_fname = f'20190102~20201231_{hump_model_name}_v1.csv'    # 保存在/user/015614/pred/路径下

def console_output_score(*score_list):
    print('准确率: ', round(score_list[0], 4))
    print('召回率: ', round(score_list[1], 4))
    print('精确率: ', round(score_list[2], 4))
    print('F1值: ', round(score_list[3], 4))
    print('AUC: ', round(score_list[4], 4))

# 可公用函数
def tuning_objective(param):
    param_copy = param.copy()

    # 自定义参数，如果不是在进行寻优，那么这些值是真实的因子，或者是best_param里有的话会覆盖下面的值
    factor_num = 520
    score_threshold = 0.45970953626866

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
                       test_start_date=20200701,
                       test_end_date=20201231)
    if verbose:
        print(f'现在使用的模型是{model_name}')
    mf_inst = ModelFactory(model_name=model_name,
                           date_config=date_config,
                           factor_filter_path=filter_factor_fpath,
                           factor_score_path=factor_score_fpath,
                           data_path=saturn_data_fit_fpath,
                           factor_num=factor_num,
                           label='label_mixed_0712')
    X_train, y_train, X_valid, y_valid, X_test, y_test = mf_inst.get_dateset()

    factor_list = FileUtil.read_list(factor_path, 'xgb_clf_model_factor_list.pkl')
    X_train = X_train[factor_list]
    X_valid = X_valid[factor_list]
    X_test = X_test[factor_list]

    y_train = (y_train > 0).astype(int)
    y_valid = (y_valid > 0).astype(int)
    y_test = (y_test > 0).astype(int)
    if verbose:
        print('训练集正样本比例为：', round((y_train.sum() / y_train.shape[0])[0], 4))
        print('验证集正样本比例为：', round((y_valid.sum() / y_valid.shape[0])[0], 4))
        print('测试集正样本比例为：', round((y_test.sum() / y_test.shape[0])[0], 4))
        print('*' * 30)

    mf_inst.train_model(X_train, y_train, param=param_copy)
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
    output_path = os.path.join(pred_out_path, f'{strategy_name}/{model_name}/')
    FileUtil.save_df2csv(valid_test_pred_df, output_path, pred_fname)

    eval_inst = EvalLaunch(date_config=date_config,
                           strategy_name=strategy_name,
                           sel_model_names=['xgbClfModel'],
                           valid_path_list=[output_path + pred_fname],
                           pred_path_list=[output_path + pred_fname],
                           pred_type='fit',
                           save_flag=True)
    _ = eval_inst.launch()
    del eval_inst


if __name__ == '__main__':
    param = model_params[model_name]
    tuning_objective(param)