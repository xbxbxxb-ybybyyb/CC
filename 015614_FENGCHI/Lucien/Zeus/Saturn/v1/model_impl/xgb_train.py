# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 14:54

from Zeus.Saturn.v1.models.ModelFactory import ModelFactory
from Zeus.Saturn.v1.hyper_param_space import model_params
from Zeus.Saturn.v1.path_conf import *
from LucienUtil.FileUtil import FileUtil
import warnings
import pandas as pd
import numpy as np
import random
np.random.RandomState(2022)

warnings.filterwarnings("ignore")

def console_output_score(*score_list):
    print('准确率: ', round(score_list[0], 4))
    print('召回率: ', round(score_list[1], 4))
    print('精确率: ', round(score_list[2], 4))
    print('F1值: ', round(score_list[3], 4))
    print('AUC: ', round(score_list[4], 4))


if __name__ == '__main__':
    factor_num = 450
    score_threshold = 0.4261538353160572

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

    param = model_params[model_name]
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
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_test, y_test_pred)
    console_output_score(acc, rec, prec, f1, auc)
    pred_pos_pct = y_test_pred.sum() / len(y_test_pred)
    print('测试集预测的正值样本的数量：', round(pred_pos_pct, 4))

    """求约登指数"""
    from sklearn.metrics import roc_curve
    tpr, fpr, thresholds = roc_curve(y_test, y_test_pred_prob)
    J = tpr - fpr
    idx = np.argmax(J)
    best_threshold = thresholds[idx]

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
