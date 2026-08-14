# @Time : 2020/5/27 13:39
# @Author : Zhichen Lu
# @File : run_backtest.py

import os
from multiprocessing import Pool

import pandas as pd

from conf.path_config import *


# IBT = IntradayBackTest()


def get_data(file_name, path):
    if 'Wrong' not in file_name:
        temp_signal, _ = pd.read_pickle(path + file_name)
        if len(temp_signal) == 0:
            print(file_name, 0)
            return pd.DataFrame(columns=[file_name.strip('.pkl')])
        temp_signal = temp_signal[['prediction']]
        temp_signal.columns = [file_name.strip('.pkl')]
        print(file_name)
        return temp_signal
    else:
        return pd.DataFrame(columns=[file_name.strip('.pkl')])


def integrate_signal(signal_path, out_path, file_name):
    pool = Pool(20)
    file_list = os.listdir(signal_path)
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    res_dict = dict()
    for each in file_list:
        print(each)
        res = pool.apply_async(get_data, (*(each, signal_path),))
        res_dict[each] = res
    # res = pool.map(get_data,file_list[:100])
    pool.close()
    pool.join()

    all_df = []
    for each in res_dict:
        print(each)
        temp_df = res_dict[each].get()
        all_df.append(temp_df)

    print('start concat...')
    all_df = pd.concat(all_df, axis=1)
    print('end')
    all_df = all_df.drop(list(filter(lambda x: 'Wrong' in x, all_df.columns.tolist())), axis=1)
    if not file_name.endswith('.pkl'):
        file_name = file_name + '.pkl'
    pd.to_pickle(all_df, out_path + file_name)


# def run_back_test(signal_file_path, out_path, file_name):
#     wgt_opt_diff = pd.read_hdf('/data/group/800319/junkClassification/wgt_opt_diff.h5', 'wgt_opt_diff')
#     signal = pd.read_pickle(signal_file_path)
#     val_net = pd.read_hdf('/data/group/800319/junkClassification/val_net.h5', 'val_net')
#     val_b = pd.read_hdf('/data/group/800319/junkClassification/val_b.h5', 'val_b')
#     val_g = pd.read_hdf('/data/group/800319/junkClassification/val_g.h5', 'val_g')
#     is_valid = signal.count(axis=0)
#     is_valid = is_valid[is_valid > 0]
#     signal = signal[is_valid.index]
#     signal.columns = [int(x) for x in signal.columns]
#     compare = IBT.calc_portfolio_improve(signal, wgt_opt_diff, val_g, val_b, val_net, slippage=0.0005, buy_improve=None,
#                                          sell_improve=None)
#     compare.to_excel(out_path + file_name)


if __name__ == "__main__":
    # 信号整合 这个要很久
    integrate_signal(
        signal_path='/data/group/800319/junkData/IntraFactorModel/predictions/xgb_rise_down_zero_1min_20200609/',
        out_path=junk_clf_path,
        file_name='predict_signal_xgb_20200609_rise_down_zero_1min.pkl')
    # 回测
    # run_back_test(signal_file_path='/data/group/800319/junkClassification/predict_signal_lr_20200529_rise_down_zero.pkl',
    #               out_path='/data/group/800319/junkClassification/', file_name='日内结果_rise_down_zero_back_lr20200528_fix.xlsx')
