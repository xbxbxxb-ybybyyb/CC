from TSmodel.NNResearch.DataPrepare import split_train_predict, rank_code_list, select_factor_list, load_fix_data,\
    feature_engineering, prepare_model_fold
from TSmodel.NNResearch.XGBoost import set_model, train_model, pred_model
import pandas as pd
import gc
import os
import time

def main(idx, test_id):

    # idx = 100
    # test_id = 0
    test_split = 4
    factor_num = 400

    model_root = '/data/user/015836/HFmodel/NNResearch/20210629XGBCompare/'
    model_name = f'part{test_id}'

    if os.path.exists(f'{model_root}/{model_name}/pred/{idx}.pkl'):
        return

    # if time.gmtime().tm_hour + 8 >= 31:
    #     return

    model_date_list = split_train_predict(
        train_days=200, predict_days=10, future_day=1,
        pred_start=20161221, pred_end=20210616,
        load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')

    train_start = model_date_list[idx][0]
    train_end = model_date_list[idx][1]
    pred_start = model_date_list[idx][2]
    pred_end = model_date_list[idx][3]

    ranked_codes = rank_code_list(train_start, train_end)
    test_codes = sorted(ranked_codes[test_id::test_split])
    train_codes = sorted(list(set(ranked_codes) - set(test_codes)))

    available_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3/available_factor_list.pkl')
    factor_list = select_factor_list(train_end).loc[available_factor_list].sort_values(
        ascending=False).head(factor_num).index.to_list()

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

if __name__ == '__main__':

    for idx in range(109):
        main(idx, 0)
        main(idx, 1)