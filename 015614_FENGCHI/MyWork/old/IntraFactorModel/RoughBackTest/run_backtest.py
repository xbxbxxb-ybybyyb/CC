# @Time : 2020/5/27 13:39
# @Author : Zhichen Lu
# @File : run_backtest.py

import os
from multiprocessing import Pool

from dataApi.usefulTools import *


def get_data(file_name, path):
    if 'Wrong' not in file_name:
        temp_signal, _ = pd.read_pickle(path + file_name)
        if len(temp_signal) == 0:
            print(file_name, 0)
            return pd.DataFrame(columns=[file_name.strip('.pkl')])
        temp_signal = temp_signal[['prediction']]
        temp_signal.columns = [file_name.strip('.pkl')]
        print(file_name)
        return temp_signal[file_name.strip('.pkl')]
    else:
        return pd.DataFrame(columns=[file_name.strip('.pkl')])


def integrate_signal(signal_path, out_path, file_name):
    pool = Pool(20)
    file_list = os.listdir(signal_path)
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    res_dict = dict()
    for each in file_list:
        res = pool.apply_async(get_data, (*(each, signal_path),))
        res_dict[each] = res
    # res = pool.map(get_data,file_list[:100])
    pool.close()
    pool.join()

    all_df = []
    for each in res_dict:
        temp_df = res_dict[each].get()
        all_df.append(temp_df)

    all_df = pd.concat(all_df, axis=1)
    all_df = all_df.drop(list(filter(lambda x: 'Wrong' in x, all_df.columns.tolist())), axis=1)
    if not file_name.endswith('.pkl'):
        file_name = file_name + '.pkl'
    pd.to_pickle(all_df, out_path + file_name)


def run_back_test(signal_file_path, out_path, file_name, backtest_type, deal_type, slippage, signal_type='non_tick'):
    wgt_opt_diff = pd.read_hdf('/data/group/800319/junkData/IntraFactorModel/junkClassification/wgt_opt_diff.h5',
                               'wgt_opt_diff')
    signal = pd.read_pickle(signal_file_path)
    # signal = pd.read_pickle('/data/group/800319/junkClassification/predict_signal_lr_20200527_revised.pkl')

    # close = get_minute_1factor('close', start_datetime=201701030925, end_datetime=201912311500, code_list=[int(x) for x in signal.columns.tolist()])
    # daily_twap = get_daily_1factor('twap', date_list=get_date_range(20170103, 20191231), code_list=signal.columns.tolist())
    # close_arr = frame2arr(close)
    # twap_profit = daily_twap.values / close_arr - 1
    # real_lable = (twap_profit > 0) * 1. - 1. * (twap_profit < 0)
    # real_lable[np.isnan(close_arr)] = np.nan
    # signal = arr2frame(real_lable,index=close.index,columns=close.columns)
    # pd.to_pickle(signal,'/data/group/800319/junkClassification/real_label_twap.pkl')
    val_net = pd.read_hdf('/data/group/800319/junkData/IntraFactorModel/junkClassification/val_net.h5', 'val_net')
    val_b = pd.read_hdf('/data/group/800319/junkData/IntraFactorModel/junkClassification/val_b.h5', 'val_b')
    val_g = pd.read_hdf('/data/group/800319/junkData/IntraFactorModel/junkClassification/val_g.h5', 'val_g')
    is_valid = signal.count(axis=0)
    is_valid = is_valid[is_valid > 0]
    signal = signal[is_valid.index]
    signal.columns = [int(x) for x in signal.columns]
    compare, avg_buy, avg_sell, outperform_buy, outperform_sell = \
        IBT.calc_portfolio_improve(signal, wgt_opt_diff, val_g, val_b, val_net, slippage=slippage, buy_improve=None,
                                   sell_improve=None,
                                   backtest_type=backtest_type, deal_type=deal_type, sinal_type=signal_type)
    with pd.ExcelWriter(out_path + file_name) as writer:
        compare.to_excel(writer, sheet_name='净值比较')
        avg_buy.to_excel(writer, '买入均价')
        avg_sell.to_excel(writer, '卖出均价')
        outperform_buy.to_excel(writer, '买入超出TWAP比例')
        outperform_sell.to_excel(writer, '卖出超出TWAP比例')


if __name__ == "__main__":
    # 信号整合 这个要很久
    signal_path = '/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_1min_from2017_selected50factor_20200611/'
    integrate_signal_file_name = 'predict_signal_lr_rise_down_zero_1min_from2017_selected50factor_20200611.pkl'
    classification_path = '/data/group/800319/junkData/IntraFactorModel/junkClassification/'
    integrate_signal(signal_path=signal_path,
                     out_path=classification_path,
                     file_name=integrate_signal_file_name)
    # 回测
    """
    backtest_output_path = '/data/group/800319/junkData/IntraFactorModel/junkClassification/20200605/'
    if not os.path.exists(backtest_output_path):
        os.mkdir(backtest_output_path)
    IBT = IntradayBackTest()
    # all: 分价格区间
    # default: 市价基础上让利slippage
    # add: 1分、2分、3分
    # tick: 对价
    run_back_test(signal_file_path=classification_path + integrate_signal_file_name,
                  out_path=backtest_output_path, file_name='xgb_rise_down_zero_5min_fix_add_0.0005.xlsx',
                  backtest_type='fix', deal_type='default', slippage=0.0005, signal_type='non_tick')
    run_back_test(signal_file_path=classification_path + integrate_signal_file_name,
                  out_path=backtest_output_path, file_name='xgb_rise_down_zero_5min_fix_tick.xlsx',
                  backtest_type='fix', deal_type='tick', slippage=np.nan, signal_type='non_tick')
    run_back_test(signal_file_path=classification_path + integrate_signal_file_name,
                  out_path=backtest_output_path, file_name='xgb_rise_down_zero_5min_fix_add_0.01.xlsx',
                  backtest_type='fix', deal_type='add', slippage=0.01, signal_type='non_tick')
    run_back_test(signal_file_path=classification_path + integrate_signal_file_name,
                  out_path=backtest_output_path, file_name='xgb_rise_down_zero_5min_fix_all.xlsx',
                  backtest_type='fix', deal_type='all', slippage=np.nan, signal_type='non_tick')
    """

    # for i in range(1,4):
    #     run_back_test(signal_file_path='/data/group/800319/junkClassification/predict_signal_mlp_20200601_rise_dwon_zero.pkl',
    #                   out_path=back_test_path, file_name='日内结果_mlp_修正后框架_rise_down_zero_%dcent.xlsx'%i,
    #                   backtest_type='fix', deal_type='add', slippage=0.01*i, signal_type='non_tick')

    # run_back_test(signal_file_path='/data/group/800319/junkClassification/predict_signal_mlp_20200527_revised.pkl',
    #               out_path='/data/group/800319/junkClassification/20200528/',file_name='日内结果_mlp_修正后框架_w0_fix.xlsx',signal_type='fix')
    # run_back_test(signal_file_path='/data/group/800319/junkClassification/predict_signal_mlp_20200527_revised.pkl',
    #               out_path='/data/group/800319/junkClassification/20200528/', file_name='日内结果_mlp_修正后框架_w0_unfix.xlsx', signal_type='unfix')

    # wgt_opt_diff = pd.read_hdf('/data/group/800319/junkClassification/wgt_opt_diff.h5', 'wgt_opt_diff')
    #
    # turover = wgt_opt_diff.fillna(0)!=0
    # price = get_daily_1factor('close',date_list=turover.index.tolist(),code_list=turover.columns.tolist())
    # turned_price = turover*price
    # turned_price[~turover] = np.nan
    # turover_weight = pd.DataFrame(index = wgt_opt_diff.index,columns=wgt_opt_diff.columns)
    # for date in turover_weight.index:
    #     turover_weight.loc[date] = wgt_opt_diff.loc[date].apply(abs)/wgt_opt_diff.loc[date].apply(abs).sum()

    # turover_weight = (turover_weight.T/turover_weight.sum(axis=1)).T
    # check = (turover_weight*turned_price).sum(axis=1)
    # check.mean()
