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
from Zeus.Saturn.v2_4.Tool import multiprocess, get_interval_data
from Zeus.Saturn.v2_4.hyper_param_space import hyper_xgb_clf_params, multi_xgb_clf_params
from Zeus.Saturn.v2_4.hyper_param_space import model_params
from Zeus.Saturn.v2_4.models.xgb_clf_model import XGBClfModel
from Zeus.Saturn.v2_4.my_logger import MyLogger
from Zeus.Saturn.v2_4.path_conf import *
from Zeus.Saturn.v2_4.BackTest.EvalLaunch import EvalLaunch

np.random.RandomState(2022)
warnings.filterwarnings("ignore")

# 各个开关
not_search_but_backtest = True  # 在不进行超参数寻优的时候在训练完以后自动进行回测，一般都开着
pred_type = 'fit'   # 这个参数只在not_search_but_backtest为True时起作用，可选test/fit
hyper_search_mode = False   # 是否进行超参数寻优
multi_grid_search_mode = False   # 是否进行多进程参数寻优
cheat_mode = False   # 是否开启作弊器
rolling_type = 'fit'   # 可选test/fit
generate_csv_valid_pred = True  # 是否保存结果到csv中供回测，只要是寻优这个就要开启

# 版本号信息
strategy_name = 'Saturn'
version = 'v2_4'
model_name = 'xgb_clf_model'
hyper_remark = ''
hump_model_name = 'xgbClfModel'
verbose = True     # 控制是否输出内容
search_time = 0
pred_fname = f'20190102~20201231_{hump_model_name}_v1.csv'    # 保存在对应的版本路径下


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
    t1 = time.time()

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
                       valid_end_date=20200630,
                       test_start_date=20200701,
                       test_end_date=20201231)

    if verbose:
        print(f'现在使用的模型是{model_name}')
    mf_inst = XGBClfModel(model_name=model_name,
                          date_config=date_config,
                          factor_filter_path=filter_factor_fpath,
                          factor_score_path=factor_score_fpath,
                          data_path=saturn_data_fit_fpath,
                          profit_path=profit_fpath,
                          factor_num=factor_num,
                          label='label_mixed')

    # 读取train时的因子
    factor_list = FileUtil.read_list(factor_path + f'{strategy_name}/{model_name}/{version}/', f'{model_name}_factor_list.pkl')
    mf_inst.set_factor_list(factor_list)

    t1 = time.time()
    y_pred_prob_all, y_pred_clf_all = mf_inst.rolling_train_and_predict(len_train=5000,
                                                                        len_test=1300,
                                                                        rolling_type=rolling_type,
                                                                        param=param_copy)
    print(time.time() - t1, '秒')

    y_train, y_valid, y_test, y_train_prob, y_valid_prob, y_test_prob, y_train_clf, y_valid_clf, y_test_clf = \
        get_interval_data(mf_inst.y, y_pred_prob_all, y_pred_clf_all, date_config)

    # 评估部分
    acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_train.reindex(y_train_clf.index) > 0, y_train_clf)
    acc_, rec_, prec_, f1_, auc_ = mf_inst.calc_model_score(y_valid > 0, y_valid_clf)
    if rolling_type is 'test':
        _acc, _rec, _prec, _f1, _auc = mf_inst.calc_model_score(y_test > 0, y_test_clf)
    else:
        _acc, _rec, _prec, _f1, _auc = 0, 0, 0, 0, 0
    if verbose:
        print('训练集预测结果：')
        console_output_score(acc, rec, prec, f1, auc)
        print('验证集预测结果：')
        console_output_score(acc_, rec_, prec_, f1_, auc_)
        if rolling_type is 'test':
            print('测试集预测结果：')
            console_output_score(_acc, _rec, _prec, _f1, _auc)

    if not generate_csv_valid_pred:
        return -auc # 直接进行寻优，文件都不进行保存

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

    if not_search_but_backtest:
        eval_inst = EvalLaunch(date_config=date_config,
                               strategy_name=strategy_name,
                               sel_model_names=['xgbClfModel'],
                               pred_type=pred_type,
                               valid_path_list=[output_path + pred_fname],
                               pred_path_list=[output_path + pred_fname],
                               file_save_path=output_path,
                               save_flag=True)
        _ = eval_inst.launch()
        del eval_inst

if __name__ == '__main__':
    param = model_params[model_name]
    tuning_objective(param)