import sys

sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])
from StrongStockModel.model.Modelmpl.CrossValidation.DataPrepare import split_train_predict, rank_code_list, select_factor_list, load_fix_data,\
    feature_engineering, prepare_model_fold
from StrongStockModel.model.Modelmpl.CrossValidation.XGBoostLZC import set_model, train_model, pred_model
import pandas as pd
import gc
import os
import time
import configparser
from tqdm import tqdm

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
para_list = para_list[24:134]
model_date_list = {i:each[1] for i,each in enumerate(para_list)}


def main(idx, test_id,indicator):

    # idx = 100
    # test_id = 0
    test_split = 4
    factor_num = 400

    model_root = f'/data/group/800442/800319/IntradayModel/PL/CrossValidationByCode/XGB_{indicator}/'
    model_name = f'part{test_id}'
    if not os.path.exists(model_root):
        os.makedirs(model_root)
    if os.path.exists(f'{model_root}/{model_name}/pred/{idx}.pkl'):
        print(f'{idx} exist')
        return

    train_start,train_end,pred_start,pred_end = model_date_list[idx]

    ranked_codes = rank_code_list(train_start, train_end)
    test_codes = sorted(ranked_codes[test_id::test_split])
    train_codes = sorted(list(set(ranked_codes) - set(test_codes)))

    available_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3/available_factor_list.pkl')
    factor_list = pd.read_pickle(f'/arch0/group/800442/ExperimentParam/{indicator}_factor_list/{train_end}.pkl')

    train_X, train_y, train_nolimit = load_fix_data(
        start_date=train_start, end_date=train_end, factor_list=factor_list, code_list=train_codes, return_idx=False)
    test_X, test_y, test_nolimit, test_d, test_c, test_t = load_fix_data(
        start_date=train_start, end_date=train_end, factor_list=factor_list, code_list=test_codes, return_idx=True)
    pred_X, pred_y, pred_nolimit, pred_d, pred_c, pred_t = load_fix_data(
        start_date=pred_start, end_date=pred_end, factor_list=factor_list, return_idx=True)

    train_X, train_y = feature_engineering(train_X, train_y, train_nolimit, limit=0.2)
    test_X, test_y, test_d, test_c, test_t = feature_engineering(
        test_X, test_y, test_nolimit, test_d, test_c, test_t, limit=0.2)
    pred_X, pred_y, pred_d, pred_c, pred_t = feature_engineering(
        pred_X, pred_y, pred_nolimit, pred_d, pred_c, pred_t, limit=0.2)


    prepare_model_fold(model_name, model_root)
    model = set_model()
    model = train_model(train_X, train_y, test_X, test_y, model, model_name, model_root, idx)
    pred_model(test_X, test_d, test_t, test_c, model, model_name, model_root, idx, 'test', y=test_y)
    pred_model(pred_X, pred_d, pred_t, pred_c, model, model_name, model_root, idx, 'pred', y=pred_y)
    del model
    gc.collect()
    print(f'{model_root}/{model_name}/pred/{idx}.pkl',train_start,train_end,pred_start,pred_end,test_id,'done')

if __name__ == '__main__':

    bar = tqdm(list(range(len(model_date_list)))[::-1])
    for idx in bar:
        for tag in ['ic_d','ic_c','ic_t']:
            bar.set_description(f'{tag} {model_date_list[idx]}')
            main(idx, 0,tag)
            main(idx, 1,tag)
            main(idx, 2,tag)
            main(idx, 3,tag)