# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 14:52

from Zeus.Saturn.v1_2.models.ModelFactory import ModelFactory
from Zeus.Saturn.v1_2.hyper_param_space import model_params
from Zeus.Saturn.v1_2.path_conf import *

out_root_path = root_path + 'fengc/Saturn/v1/linear_model/'



def console_output_score(*score_list):
    print('准确率: ', round(score_list[0], 4))
    print('召回率: ', round(score_list[1], 4))
    print('精确率: ', round(score_list[2], 4))
    print('F1值: ', round(score_list[3], 4))
    print('AUC: ', round(score_list[4], 4))


if __name__ == '__main__':
    model_name = 'linear_model'
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
                           label='label_mixed_0712')
    X_train, y_train, X_valid, y_valid = mf_inst.get_dateset()
    y_train = (y_train > 0).astype(int)
    y_valid = (y_valid > 0).astype(int)
    print('训练集正样本比例为：', round((y_train.sum() / y_train.shape[0])[0], 4))
    print('验证集正样本比例为：', round((y_valid.sum() / y_valid.shape[0])[0], 4))

    param = model_params[model_name]
    mf_inst.train_model(X_train, y_train, param=param)
    y_pred = mf_inst.model_predict(X_train)
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_train, y_pred)
    console_output_score(acc, rec, prec, f1, auc)
    pred_pos_pct = y_pred.sum() / len(y_pred)
    print('预测的正值样本的数量：', round(pred_pos_pct, 4))

    y_pred = mf_inst.model_predict(X_valid)
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_valid, y_pred)
    console_output_score(acc, rec, prec, f1, auc)
    pred_pos_pct = y_pred.sum() / len(y_pred)
    print('预测的正值样本的数量：', round(pred_pos_pct, 4))
