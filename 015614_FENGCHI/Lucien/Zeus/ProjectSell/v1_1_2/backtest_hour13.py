# coding: utf-8
# Author：fengchi863
# Date ：2023/7/14 16:25

from Zeus.ProjectSell.v1_1_2.path_conf import *
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np
import math

def transStr2Index(df):
    _df = df.copy()
    _df['dt'] = _df['datelist'].map(lambda x: pd.to_datetime(str(x)))
    _df['Ticker'] = df['stockID']
    _df = _df.set_index(['dt', 'Ticker'])
    return _df

def calc_mdd(_s):
    mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
    return -mdd

def calc_sharp(_s, ref_col):
    mean_ret = _s.query('buy_amt > 0')[ref_col].mean()
    std_ret = _s.query('buy_amt > 0')[ref_col].std()
    sharp = abs(mean_ret / std_ret) * math.sqrt(250)
    return sharp

PERIOD = 'period1'
pred_type = 'test'
# pred_fpath = '/data/user/015614/Zeus/pred/ProjectSell/v1_1_2/rffs_XgbRegModel/hyper/1/20191001~20200331_rffs_XgbRegModel_v1.csv'

PERIOD_list = ['period1', 'period1', 'period2', 'period2', 'period3', 'period3']
pred_type_list = ['test', 'fit', 'test', 'fit', 'test', 'fit']

model_list = [
    'fsv8_pct1_XgbRegModel', 'fsv10_pct1_XgbRegModel', 'fsv11_pct1_XgbRegModel', 'fsrs_pct1_XgbRegModel',
    'fsv8_pct1_LgbRegModel', 'fsv10_pct1_LgbRegModel', 'fsv11_pct1_LgbRegModel', 'fsrs_pct1_LgbRegModel',
    'fsv8_pct_XgbRegModel', 'fsv10_pct_XgbRegModel', 'fsv11_pct_XgbRegModel', 'fsrs_pct_XgbRegModel',
    'fsv8_pct_LgbRegModel', 'fsv10_pct_LgbRegModel', 'fsv11_pct_LgbRegModel', 'fsrs_pct_LgbRegModel',
    # 'rffs_GroundTruthModel'
    ]

for model in model_list:
    print(model)
    res_dict = dict()
    for idx, period in enumerate(PERIOD_list):
        pred_type = pred_type_list[idx]
        date_dict = date_config[period]
        start_date, end_date = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
        print(period, pred_type, start_date, end_date)
        pred_fpath = f'/data/user/015614/Zeus/pred/ProjectSell/v1_1_2/{model}/{start_date}~{end_date}_{model}_v{period[-1]}.csv'

        profit_data = pd.read_hdf(profit_data_fpath)
        signal_df = pd.read_csv(pred_fpath)
        signal_df = transStr2Index(signal_df)

        # 叠加买入
        # if period == 'period1':
        #     buy_fpath = f'/data/group/800463/wangj/save_files/Europa_v3/Europa_out_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv'
        # elif period == 'period2':
        #     buy_fpath = f'/data/group/800463/wangj/save_files/Europa_v3/Europa_realout_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv'
        # elif period == 'period3':
        #     buy_fpath = f'/data/group/800463/wangj/save_files/Europa_v3/Europa_realrealout_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv'
        #
        # buy_signal_df = pd.read_csv(buy_fpath, index_col=0).sort_values(['datelist', 'stockID'])
        # buy_signal_df['prediction'] = buy_signal_df['vote_sum_pred'] >= 3
        #
        # train_data = pd.read_pickle(data_test_fpath_with_label)
        # signal_df['buy_date'] = train_data['saturn_dt_last_zt_1'].map(int).loc[signal_df.index]
        # signal_df = signal_df.reset_index()
        # signal_df['buy_Indexs'] = signal_df[['Ticker', 'buy_date']].apply(lambda x: x['Ticker'] + ' ' + str(x['buy_date']), axis=1)
        # signal_df = signal_df.set_index('buy_Indexs')
        # signal_df.index.names = ['Indexs']
        #
        # cross_index = list(set(signal_df.index).intersection(buy_signal_df.index))
        # signal_df = signal_df.loc[cross_index]
        # signal_df['prediction'] = signal_df['prediction'] * buy_signal_df['prediction']
        #
        # signal_df = signal_df.set_index('Indexs')
        ## 叠加买入完成

        attend_ratio_list = list(map(lambda x: x / 100, list(range(2, 41))))

        res_df = pd.DataFrame()
        for attend_ratio in attend_ratio_list:

            # print(attend_ratio)
            threshold = signal_df['pred_Reg'].quantile(1 - attend_ratio)
            signal_df['prediction'] = signal_df['pred_Reg'] >= threshold

            concat_df = pd.merge(signal_df, profit_data, on=['dt', 'Ticker'], how='left')
            concat_df = concat_df.drop_duplicates(['datelist', 'stockID', 'prediction'], keep='first')
            concat_df = concat_df.query('prediction == 1')

            concat_df['profit'] = concat_df['buy_amt'] * concat_df['label_diff_pct']
            daily_profit = concat_df.groupby('datelist')['profit'].sum()
            cumsum_profit = daily_profit.cumsum()

            pct_cost = concat_df['label_diff_pct'].mean()
            mdd = calc_mdd(daily_profit)
            sharp = calc_sharp(concat_df, ref_col='label_diff_pct')
            profit_sharp = calc_sharp(concat_df, ref_col='profit')

            res_df.loc[attend_ratio, '参与率'] = attend_ratio
            res_df.loc[attend_ratio, '阈值'] = threshold
            res_df.loc[attend_ratio, '参与个数'] = concat_df.shape[0]
            res_df.loc[attend_ratio, '累计收益'] = cumsum_profit.iloc[-1]
            res_df.loc[attend_ratio, '平均收益率'] = pct_cost
            res_df.loc[attend_ratio, '最大回撤'] = mdd
            res_df.loc[attend_ratio, '收益风险比'] = cumsum_profit.iloc[-1] / -mdd
            res_df.loc[attend_ratio, '夏普比率'] = sharp
            res_df.loc[attend_ratio, '收益夏普比率'] = profit_sharp

        res_dict[f'{period}_{pred_type}'] = res_df
    FileUtil.save_dict2xls(res_dict, junk_path, f'{model}.xlsx')
    # send_file(junk_path + f'{model}_addBuy.xlsx')




