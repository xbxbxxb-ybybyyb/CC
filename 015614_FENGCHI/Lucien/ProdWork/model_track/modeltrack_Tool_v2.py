import os
import numpy as np
import pandas as pd
import math
from xquant.factordata import FactorData
hfactor = FactorData()
from sklearn.metrics import precision_score, recall_score,r2_score,mean_squared_error,roc_auc_score
import warnings
warnings.filterwarnings("ignore")
import datetime as dt
today = dt.datetime.now().strftime('%Y%m%d')
#today = '20220719'
tommorow = hfactor.tradingday(today,2)[-1]
yesterday = hfactor.tradingday(today,-2)[0]
year = str(yesterday)[:4]
month = str(yesterday)[4:6]
day = str(yesterday)[6:]
last_Fri = hfactor.tradingday(today,-3)[0]
llast_Fri = hfactor.tradingday(today,-8)[0]
fk_startdate = hfactor.tradingday(today,-30)[0]
from xquant.marketdata import MarketData
mdp = MarketData()
from ProdWork.CommonTools import *

class modeltrack_Tool:
    def __init__(self,strategy_name, begindate, enddate, savepath, basic_df, sel_models, all_models, vote_thres):
        self.strategy = str(strategy_name)
        self.FilesavePath = savepath
        self.begindate = begindate
        self.enddate = enddate
        self.basic_data = basic_df
        self.sub_models = sel_models
        self.all_sub_models = all_models
        self.vote_thres = int(vote_thres)
        self.sub_models_proba1 = [x.split('Model')[0] + '_proba1' for x in self.sub_models]
        self.all_sub_models_proba1 = [x.split('Model')[0] + '_proba1' for x in self.all_sub_models]
        self.begindate_str, self.enddate_str = self.begindate.replace('-', ''), self.enddate.replace('-', '')
        self.tot_dt = hfactor.tradingday(self.begindate_str, self.enddate_str)
        self.tot_dt_datetime = [pd.Timestamp(x) for x in self.tot_dt]
        self.label_data = self.select_label()
        self.profit_data = self.select_profit()
        #self.rawdata = self.combine_labelandprofit()

    def select_profit(self):
        if self.strategy == 'jupiter':
            # self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fix/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5' # v9
            self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixnew/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5' # v10的时候改成这个
            self.cost_pct = 0.0020
            self.attend_min = 10
            self.attend_max = 51
            self.group_ratio = 0.2
        elif self.strategy == 'Europa':
            # self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fix/001/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5'
            self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixnew/001/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5'
            self.cost_pct = 0.002
            self.attend_min = 10
            self.attend_max = 51
            self.group_ratio = 0.2
        elif self.strategy == 's0':
            self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_930_0.20_0.10_500_1500.h5'
            self.cost_pct = 0.004
            self.attend_min = 10
            self.attend_max = 41
            self.group_ratio = 0.2
        elif self.strategy == 's1':
            # self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_931_0.20_0.10_500_1500.h5'
            # self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_931_0.20_0.10_1000_1500_250_20.h5'   # 20231205更新为新的
            self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_interval_931_1000_0.10_0.10_1000_1500_250_20.h5'   # 20241127更新为新的
            self.cost_pct = 0.004
            self.attend_min = 10
            self.attend_max = 41
            self.group_ratio = 0.2
        elif self.strategy == 's2':
            self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_932_0.20_0.10_500_1500.h5'
            self.cost_pct = 0.004
            self.attend_min = 10
            self.attend_max = 41
            self.group_ratio = 0.2
        elif self.strategy == 's3':
            self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_933_0.20_0.10_500_1500.h5'
            self.cost_pct = 0.004
            self.attend_min = 10
            self.attend_max = 41
        elif self.strategy == 'ceress1':
            self.profit_path = '/data/group/800463/project/project3_prod/profit_backtest/sp2_profit_931_0.20_0.10_500_1500.h5'
            self.cost_pct = 0.004
            self.attend_min = 20
            self.attend_max = 61
            self.group_ratio = 0.5
        elif self.strategy == 'ceress0':
            self.profit_path = '/data/group/800463/project/project3_prod/profit_backtest/sp2_profit_930_0.20_0.10_500_1500.h5'
            self.cost_pct = 0.004
            self.attend_min = 30
            self.attend_max = 61
            self.group_ratio = 0.5
        elif self.strategy == 'JupiterNSell':
            # self.profit_path = '/data/group/800463/project/projectS_prod/LabelProfit_fix/Sell_pct_0.15_2000_300_SH250_SZ20.pkl'
            self.profit_path = '/data/group/800463/project/projectS_prod/LabelProfit_fix/Sell_pct_0.10_2000_300_SH250_SZ20.pkl'
            self.cost_pct = 0
            self.attend_min = 10
            self.attend_max = 26  # 41
            self.group_ratio = 0.2
            self.extreme_thres = 0.1
        elif self.strategy == 'JupiterNSell34':
            self.profit_path = '/data/group/800463/project/projectS_prod/LabelProfit_fix/Sell_pct_0.15_2000_300_SH250_SZ20.pkl'
            self.cost_pct = 0
            self.attend_min = 10
            self.attend_max = 41
            self.group_ratio = 0.2
            self.extreme_thres = 0.1
        elif self.strategy == 'JupiterZ':
            # self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fix_beforeZ/JupiterZ_Label_0.10_800_190_SH300_SZ30.pkl'
            # self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fix_beforeZ/JupiterZ_Label_0.15_2000_300_SH250_SZ20.pkl'
            self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fix_beforeZ/JupiterZ_Label_0.10_2000_300_SH250_SZ20.pkl'
            self.cost_pct = 0
        elif self.strategy == 'Metis':
            # self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fix/metis/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5'
            self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fix/metis/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5'
            self.cost_pct = 0
        elif self.strategy == 'Leda':
            self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixnew/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5'
            self.cost_pct = 0

        if self.profit_path.endswith('pkl'):
            profit_data = pd.read_pickle(self.profit_path)
        else:
            profit_data = pd.read_hdf(self.profit_path)
        profit_data.columns = ['label_' + i for i in profit_data.columns]
        if 'label_pct' in profit_data.columns:
            profit_data['label_pct_cost'] = profit_data['label_pct'] - self.cost_pct
            profit_data['label_profit_cost'] = profit_data['label_pct_cost'] * profit_data['label_buy_amt']
            profit_data['label_zuhe'] = profit_data.apply(lambda x: 1 if x['label_pct_cost'] > 0 else 0, axis=1)
        else:
            if self.strategy == 'JupiterNSell':
                profit_data['label_pct'] = profit_data['label_label_diff_pct']
            elif self.strategy == 'JupiterNSell34':
                profit_data['label_pct'] = profit_data['label_label_diff_pct_next']
            elif self.strategy == 'JupiterZ':
                profit_data['label_pct'] = profit_data['label_label_diff_pct']
            profit_data['label_pct_cost'] = profit_data['label_pct'] - self.cost_pct
            profit_data['label_profit_cost'] = profit_data['label_pct_cost'] * profit_data['label_buy_amt']
        if 'label_zuhe' not in profit_data.columns:
            profit_data['label_zuhe'] = profit_data.apply(lambda x: 1 if x[self.label_rev] >= self.cost_pct else 0, axis=1)
        return profit_data

    def select_label(self):
        """
        jupiterN一开始是generalStrong_v3/和factor_manager_v2
        后来是left_v2212和right_v2212
        现在是left_v2310和right_v2412
        """
        if self.strategy == 'jupiter':
            # self.label_path = '/data/group/800463/project/project1_prod/left_v2212/Label_zt/Label_zt.h5'
            self.label_path = '/data/group/800463/project/project1_prod/left_v2310/Label_zt/Label_zt.h5'
            self.label_rev = 'label_TN_o2ul'
            self.label_o2o10 = 'label_T_is_zt'
        elif self.strategy == 'Europa':
            self.label_path = '/data/group/800463/project/project1_prod/left_v2212/Label_zt_test/Label_zt_001.h5'
            self.label_rev = 'label_TN_o2ul'
            self.label_o2o10 = 'label_T_is_zt'
        elif self.strategy == 's0':
            self.label_path = '/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
            self.label_rev = 'label_v2o10'
            self.label_o2o10 = 'label_o2o10'
            self.label_Tc2To10 = 'label_Tc2To10'
        elif self.strategy == 's1':
            self.label_path = '/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
            self.label_rev = 'label_v2o10d1'
            self.label_o2o10 = 'label_o2o10d1'
            self.label_Tc2To10 = 'label_Tc2To10d1'
        elif self.strategy == 's2':
            self.label_path = '/data/group/800463/project/project2_prod/everyday_Basic_v2/20160101_20211231/label_for_model_test_20160101_20211231.pkl'#'/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
            self.label_rev = 'label_v2o10d2'
            self.label_o2o10 = 'label_o2o10d2'
            self.label_Tc2To10 = 'label_Tc2To10d2'
        elif self.strategy == 's3':
            self.label_path = '/data/group/800463/project/project2_prod/everyday_Basic_v2/20160101_20211231/label_for_model_test_20160101_20211231.pkl'#'/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
            self.label_rev = 'label_v2o10d3'
            self.label_o2o10 = 'label_o2o10d3'
            self.label_Tc2To10 = 'label_Tc2To10d3'
        elif self.strategy == 'ceress1':
            self.label_path =  '/data/group/800463/project/project3_prod/daily_data/Label/label.h5'
            self.label_rev = 'label_v2o10d1'
            self.label_o2o10 = 'label_o2o10d1'
            self.label_Tc2To10 = 'label_Tc2To10d1'
        elif self.strategy == 'ceress0':
            self.label_path = '/data/group/800463/project/project3_prod/everyday_Basic/20160101_20210831/label.pkl'
            self.label_rev = 'label_v2o10'
            self.label_o2o10 = 'label_o2o10'
            self.label_Tc2To10 = 'label_Tc2To10'
        elif self.strategy in 'JupiterNSell':
            self.label_path = '/data/group/800463/project/projectS_prod/LabelProfit_fix/Sell_pct_0.15_2000_300_SH250_SZ20.pkl'
            self.label_rev = 'label_label_diff_pct'
            self.label_o2o10 = 'label_pattern'
        elif self.strategy in 'JupiterNSell34':
            self.label_path = '/data/group/800463/project/projectS_prod/LabelProfit_fix/Sell_pct_0.15_2000_300_SH250_SZ20.pkl'
            self.label_rev = 'label_label_diff_pct_next'
            self.label_o2o10 = 'label_pattern'
        elif self.strategy in 'JupiterZ':
            # self.label_path = '/data/group/800463/project/project1_prod/LabelProfit_fix_beforeZ/JupiterZ_Label_0.10_800_190_SH300_SZ30.pkl'
            self.label_path = '/data/group/800463/project/project1_prod/LabelProfit_fix_beforeZ/JupiterZ_Label_0.15_2000_300_SH250_SZ20.pkl'
            self.label_rev = 'label_label_diff_pct'
            self.label_o2o10 = 'label_pattern'
        elif self.strategy in 'Metis':
            self.label_path = '/data/group/800463/project/project1_prod/left_v2212/Label_zt/Label_zt.h5'
            self.label_rev = 'label_TN_o2ul'
            self.label_o2o10 = 'label_pattern'
        elif self.strategy in 'Leda':
            self.label_path = '/data/group/800463/project/project1_prod/left_v2310/Label_zt/Label_zt.h5'
            self.label_rev = 'label_TN_o2ul'
            self.label_o2o10 = 'label_pattern'

        if self.label_path.endswith('pkl'):
            label_data = pd.read_pickle(self.label_path)
        else:
            label_data = pd.read_hdf(self.label_path)
        label_data =  label_data.fillna(0)
        return label_data

    def combine_labelandprofit(self):
        local_basic_file_non_zt_need = self.basic_data.copy()
        fac_cols = list(set(self.basic_data.columns.tolist()))# - (set(self.basic_data.filter(regex='label_').columns.tolist())-set(['lzt_label_pattern'])))
        # 这个是本地拼接的样本: local_basic_file_non_zt_need， 进行收益数据和标签数据的拼接
        add_labelcols = list(set(self.label_data.columns.tolist())-set(fac_cols+['dt','Ticker']))
        merged_basic = self.basic_data[fac_cols].join(self.label_data[add_labelcols].reindex(local_basic_file_non_zt_need.index))
        merged_basic = merged_basic.join(self.profit_data.filter(regex='label_').reindex(local_basic_file_non_zt_need.index))
        self.mergeddata = merged_basic.copy()
        merged_basic = self.filter_data(merged_basic)
        return merged_basic

    def filter_data(self, rawdata):
        if self.strategy == 'jupiter':
            df_need = self.jupiter_filter(rawdata)
        elif self.strategy == 'Europa':
            df_need = self.europa_filter(rawdata)
        elif self.strategy == 's1':
            df_need = self.s1_filter(rawdata)
        elif self.strategy == 's0':
            df_need = self.s0_filter(rawdata)
        elif self.strategy == 'ceress1':
            df_need = self.cers1_filter(rawdata)
        elif self.strategy in ['JupiterNSell', 'JupiterNSell34']:
            df_need = self.sell_filter(rawdata)
            # df_need = rawdata
        elif self.strategy in ['JupiterZ']:
            df_need = self.jupz_filter(rawdata)
        elif self.strategy in ['Metis']:
            df_need = self.metis_filter(rawdata)
        elif self.strategy in ['Leda']:
            df_need = self.leda_filter(rawdata)
        return df_need

    def sell_filter(self, df):
        # after_not_ul_len_filter = df['saturn_after_not_ul_len'] > 10
        # open_filter = (df['label_T_open_is_zt'] == False) & (df['label_T_open_is_dt'] == False)
        # can_buy_filter = df['label_T_first_trans_ZT'] != 1
        # s1_filter = ((df['label_T_day_first_ZT_Time'] <= 93100000) == False) & ((df['T_day_first_DT_Time'] <= 93100000) == False)
        # pattern_filter = df['saturn_lzt_day_pattern'].isin([3, 4])
        # all_filter = after_not_ul_len_filter & open_filter & can_buy_filter & s1_filter & pattern_filter
        # all_df = df[all_filter]
        # filter_df = all_df[(all_df['jpt_ZT_Time'] >= 93000000) & (all_df['jpt_open_is_zt'] == 0) & (all_df['jpt_high_price'] < (all_df['jpt_ul_price']))].copy()
        from xquant.xqutils.helper import link
        lm = link.LinkMessage()
        message = f'模型跟踪输出：Sell nan样本为{df["label_pct"].isna().sum()}个'
        lm.sendMessage(message)
        filter_df = df.loc[~df['label_pct'].isna()]
        return filter_df

    @staticmethod
    def leda_filter(df):
        print(1)
        df_need = df[(df['ZT_Time'] >= 93000000) & \
                     (df['ZT_Time'] <= 143000000) & \
                     (df['open_is_zt'] == 0) & \
                     (df['T_o2pre'] >= -0.05) & \
                     (df['after_not_ul_len'] > 10) & \
                     (df['pre_close'] >= 1.6) & \
                     (df['high_price'] < (df['ul_price'])) & \
                     (df['min_is_dt'] == 0) & \
                     (df['last_is_zt'] == 1) & \
                     (df['saturn_lzt_day_pattern'].isin([3, 4]))]
        return df_need

    @staticmethod
    def jupiter_filter(df):
        df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        df['ul_ban'] = df['after_not_ul_len'] <= 10
        df.loc[df[df['zcz']].index, 'ul_ban'] = (df['list_len'] <= 15).reindex(df[df['zcz']].index)
        df_need = df[(df['high_price'] != df['ul_price']) &
                     (df['open_is_zt'] == False) &
                     (df['T_o2pre'] >= -0.05) &
                     (df['last_is_zt'] == 0) &
                     (df['ul_ban'] == False) &
                     (df['pre_close'] >= 2) &
                     (df['ZT_Time'] <= 143000000)]
        return df_need

    @staticmethod
    def metis_filter(df):
        df_need = df[(df['ZT_Time'] >= 93000000) &
                      (df['ZT_Time'] <= 143000000) &
                       (df['open_is_zt'] == 0) &
                        (df['T_o2pre'] >= -0.05) &
                         (df['after_not_ul_len'] > 10) &
                          (df['pre_close'] >= 2) &
                           (df['high_price'] < df['ul_price']) &
                            (df['last_is_zt'] == 0) &
                             (df['last_buy_rise'] <= 0.025) &
                              (df['trigger_time'] <= 143000000)].copy()
        return df_need

    @staticmethod
    def jupiter_filter_local(df):
        df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        df['ul_ban'] = df['after_not_ul_len'] <= 10
        df.loc[df[df['zcz']].index, 'ul_ban'] = (df['list_len'] <= 15).reindex(df[df['zcz']].index)
        df_need = df[(df['high_price'] != df['ul_price']) &
                     (df['open_is_zt'] == False) &
                     (df['T_o2pre'] >= -0.05) &
                     (df['last_is_zt'] == 0) &
                     (df['ul_ban'] == False) &
                     (df['pre_close']>=2) &
                     (df['ZT_Time'] <= 143000000)]
        return df_need

    @staticmethod
    def europa_filter(df):
        df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        df['ul_ban'] = df['after_not_ul_len'] <= 10
        df.loc[df[df['zcz']].index, 'ul_ban'] = (df['list_len'] <= 15).reindex(df[df['zcz']].index)
        df_need = df[(df['high_price'] < df['trigger_price']) &
                     (df['open_is_zt'] == False) &
                     (df['T_o2pre'] >= -0.05) &
                     (df['ul_ban'] == False) &
                     (df['last_is_zt'] == 0) &
                     (df['pre_close'] >= 2) &
                     (df['ZT_Time'] <= 143000000) &
                     (df['ZT_Time'] >= 93000000) &
                     (df['last_buy_rise'] <= 0.025)]
        return df_need

    @staticmethod
    def s1_filter(df):
        """v5筛选条件"""
        # #label_df = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Label/label.h5')
        # #df = pd.concat([df, label_df[['label_st_indicator', 'label_v2o10d1']]], axis=1, join_axes=[df.index])
        # df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        # df['ul_ban'] = df['after_not_ul_len'] <= 10
        # # df.loc[df[df['zcz']].index, 'ul_ban'] = (df['after_not_ul_len'] <= 15).reindex(df[df['zcz']].index)
        # df_need = df[((df['lzt_label_pattern'] == 3) | (df['lzt_label_pattern'] == 4)) &
        #              (df['T_open_is_dt'] == False) &
        #              (df['ul_ban'] == False) & (df['label_v2o10d1'] != -1) & (df['label_st_indicator'] == 0) &
        #              (df['T_open_is_zt'] == False) &
        #              ((df['T_day_first_ZT_Time'] <= 93100000) == False)]
        """v6筛选条件 敬姐提供"""
        df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        df['ul_ban'] = df['after_not_ul_len'] <= 10
        df_need = df[((df['lzt_label_pattern'] == 3) | (df['lzt_label_pattern'] == 4)) &
                     (df['T_open_is_dt'] == False) &
                     (df['ul_ban'] == False) & (df['label_v2o10d1'] != -1) & (df['label_v2o10d1'] != -3) & (df['label_st_indicator'] == 0) &
                     (df['T_open_is_zt'] == False) & (df['T_first_trans_ZT'] != -1) &
                     ((df['T_day_first_ZT_Time'] <= 93100000) == False) & ((df['T_day_first_DT_Time'] <= 93100000) == False)]
        return df_need

    @staticmethod
    def cers1_filter(df):
        #label_df = pd.read_hdf('/data/group/800463/project/project3_prod/daily_data/Label/label.h5')
        #df = pd.concat([df, label_df[['label_st_indicator', 'label_v2o10d1']]], axis=1, join_axes=[df.index])
        df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        df['ul_ban'] = df['after_not_ul_len'] <= 10
        # df.loc[df[df['zcz']].index, 'ul_ban'] = (df['after_not_ul_len'] <= 15).reindex(df[df['zcz']].index)
        df_need = df[
            (df['label_T_open_is_dt'] == False) &
            (df['ul_ban'] == False) & (df['label_v2o10d1'] != -1) & (df['label_st_indicator'] == 0) &
            (df['label_T_open_is_zt'] == False) &
            ((df['label_T_day_first_ZT_Time'] <= 93100000) == False)]
        return df_need

    @staticmethod
    def s0_filter(df):
        df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        df['ul_ban'] = df['after_not_ul_len'] <= 10
        # df.loc[df[df['zcz']].index, 'ul_ban'] = (df['after_not_ul_len'] <= 15).reindex(df[df['zcz']].index)
        df_need = df[((df['lzt_label_pattern'] == 3) | (df['lzt_label_pattern'] == 4)) &
                     (df['T_open_is_dt'] == False) &
                     (df['ul_ban'] == False) &
                     (df['T_o2pre'] <= 0.08) &
                     (df['T_o2pre'] >= -0.01) &
                     (df['T_open_is_zt'] == False)]
        return df_need

    @staticmethod
    def jupz_filter(df):
        df_need = df[(df['ZT_Time'] >= 93000000) & (df['ZT_Time'] <= 143000000) & (df['open_is_zt'] == 0)
                     & (df['T_o2pre'] >= -0.05) & (df['after_not_ul_len'] > 10) & (df['pre_close'] >= 2)
                     & (df['high_price'] < (df['ul_price'])) & (df['last_is_zt'] == 1)].copy()
        df_need = df_need.query('saturn_lzt_day_pattern == 3 or saturn_lzt_day_pattern == 4')
        return df_need

    @staticmethod
    def metis_filter(df):
        df['zcz'] = df.reset_index()['Ticker'].apply(lambda x: x[0] == '3').values
        df['ul_ban'] = df['after_not_ul_len'] <= 10
        df.loc[df[df['zcz']].index, 'ul_ban'] = (df['list_len'] <= 15).reindex(df[df['zcz']].index)
        df_need = df[(df['high_price'] != df['ul_price']) &
                     (df['open_is_zt'] == False) &
                     (df['T_o2pre'] >= -0.05) &
                     (df['last_is_zt'] == 0) &
                     (df['ul_ban'] == False) &
                     (df['pre_close'] >= 2) &
                     (df['ZT_Time'] <= 143000000) &
                     (df['trigger_time'] <= 143000000)]
        return df_need

    def cal_return(self, model_name):
        data = self.rawdata.copy()
        sel_modelpred = data[data[model_name] == 1]
        profit = sel_modelpred.groupby('dt').sum()[['label_profit_cost']].reindex(self.tot_dt_datetime).reindex(self.tot_dt_datetime).fillna(0).cumsum()#sel_modelpred['label_profit_cost'].fillna(0).sum()
        profit.columns = [model_name]
        return profit #pd.Series({model_name: profit})

    def cal_modeltrack_data(self, type='vote'):
        self.rawdata = self.combine_labelandprofit().loc[pd.Timestamp(self.begindate_str):pd.Timestamp(self.enddate_str)].copy()
        self.rawdata['vote_sum_pred'] = self.rawdata[self.sub_models].sum(1)
        model_num = len(self.sub_models)
        #self.rawdata['shouldBuySignal'] = self.rawdata['vote_sum_pred'].apply(lambda x: 1 if x >= np.ceil(model_num/2) else 0)
        self.rawdata['shouldBuySignal'] = self.rawdata['vote_sum_pred'].apply(lambda x: 1 if x >= self.vote_thres else 0)
        for idx in list(range(3, model_num + 1)):
            self.rawdata['vote%s' % str(idx)] = self.rawdata['vote_sum_pred'].apply(lambda x: 1 if x == idx else 0)
        need_signal = self.all_sub_models
        if type == 'vote':
            #need_signal = ['shouldBuySignal'] + ['vote%s'%str(x) for x in list(range(int(np.ceil(model_num/2)),model_num+1))]
            need_signal = ['shouldBuySignal'] + ['vote%s' % str(x) for x in list(range(self.vote_thres, model_num + 1))]
        tot_local_return = pd.DataFrame()
        tot_local_predict_summary = pd.DataFrame()
        for model in need_signal:
            print(model)
            tot_local_predict_summary = pd.concat([tot_local_predict_summary, self.cal_stats_sheet(model)], axis=1)
            tot_local_return = pd.concat([tot_local_return, self.cal_return(model)], axis=1)
        return tot_local_return.fillna(0), tot_local_predict_summary.fillna(0)

    def cal_stats_sheet(self, model_name):
        data = self.rawdata #.loc[pd.Timestamp(self.begindate_str):pd.Timestamp(self.enddate_str)].copy()

        out_dict = {}
        tot_profit = data[data[model_name] == 1]['label_profit_cost'].sum()
        tot_maxdown = self.cal_abs_max_drawdown(data[data[model_name] == 1][['label_profit_cost']])
        raw_stats = data.groupby(['dt']).apply(lambda x: pd.Series({'总正样本数量': x['label_zuhe'].sum(),
                                                                    '预测正确正样本数量': ((x['label_zuhe']==1) & (x[model_name] == 1)).sum(),
                                                                    '预测正样本数量': x[model_name].sum(),
                                                                    '预测正样本且成交数量': ((x[model_name]==1)&(x['label_buy_amt']>0)).sum(),
                                                                    #'预测正确正收益样本数量': ((x['label_pct_cost']>0) & (x[model_name] == 1)).sum(),
                                                                    '总样本数量': len(x)}))
        tot_signal_number = data[model_name].sum()
        if model_name.find('Model') >= 0:
            indicator_wj = model_name.split('Model')[0].find('Wj')>=0
            indicator_xly = model_name.split('Model')[0].find('Xly') >= 0
            indicator_xbc = model_name.split('Model')[0].find('Xbc') >= 0
            indicator_fc = model_name.split('Model')[0].find('Fc') >= 0
            indicator_skk = model_name.split('Model')[0].find('Skk') >= 0
            indicator_dj = model_name.split('Model')[0].find('Dj') >= 0
            indicator_zwh = model_name.split('Model')[0].find('Zwh') >= 0
            if indicator_wj:
                out_dict['开发人'] = 'Wj'
            elif indicator_xly:
                out_dict['开发人'] = 'Xly'
            elif indicator_xbc:
                out_dict['开发人'] = 'Xbc'
            elif indicator_fc:
                out_dict['开发人'] = 'Fc'
            elif indicator_skk:
                out_dict['开发人'] = 'Skk'
            elif indicator_dj:
                out_dict['开发人'] = 'Dj'
            elif indicator_zwh:
                out_dict['开发人'] = 'Zwh'
            else:
                out_dict['开发人'] = 'Unknown'
            if model_name in self.sub_models:
                out_dict['是否实盘'] = 1
            else:
                out_dict['是否实盘'] = 0
        out_dict['信号次数'] = tot_signal_number
        out_dict['参与率'] = raw_stats['预测正样本数量'].sum() / raw_stats['总样本数量'].sum()
        out_dict['成交率'] = raw_stats['预测正样本且成交数量'].sum()/raw_stats['预测正样本数量'].sum()
        out_dict['扣费胜率'] = raw_stats['预测正确正样本数量'].sum() / raw_stats['预测正样本数量'].sum()
        out_dict['召回率'] = raw_stats['预测正确正样本数量'].sum() / raw_stats['总正样本数量'].sum()
        out_dict['AUC'] = roc_auc_score(data['label_zuhe'], data[model_name])
        if model_name.find('Model') >= 0:
            model_proba = model_name.split('Model')[0] + '_proba1'
            out_dict['MSE'] = mean_squared_error(data['label_pct_cost'], data[model_proba])
            out_dict['RankIC'] = float(data[['label_pct_cost',model_proba]].rank().corr().loc['label_pct_cost', model_proba])
            out_dict['重合部分平均收益率'] = self.cal_cross_pct(model_name)
        else:
            out_dict['平均交易规模'] = float(data[data[model_name]==1]['label_buy_amt'].mean())
        if self.strategy in ['jupiter','Europa']:
            str_model_pct = 'o2ul'
        elif self.strategy in ['Metis']:
            str_model_pct = 'o2ul'
        else:
            str_model_pct = 'v2o10'
        out_dict['%s均值' % str_model_pct] = data[data[model_name] == 1][self.label_rev].mean()
        out_dict['扣费收益率均值'] = data[data[model_name] == 1]['label_pct_cost'].mean()
        out_dict['扣费收益率中位数'] = np.median(data[data[model_name] == 1]['label_pct_cost'].fillna(0))
        out_dict['扣费总收益'] = tot_profit
        out_dict['最大回撤'] = tot_maxdown
        out_dict['收益风险比'] = tot_profit / np.abs(tot_maxdown) if tot_maxdown != 0 else 99  # tot_profit/tot_maxdown if tot_maxdown != 0 else 99#
        out_dict['收益夏普比率'] = self.cal_sharp(data[data[model_name] == 1], 'label_profit_cost')
        return pd.DataFrame(pd.Series(out_dict), columns=[model_name])

    def cal_cross_pct(self, model):
        all_model = self.all_sub_models
        rawdata = self.rawdata.copy()
        result_pct = pd.DataFrame(index=[model], columns=all_model)
        for col1 in [model]:
            for col2 in all_model:
                tempdata = rawdata[[col1, col2]]
                result_pct.loc[col1, col2] = rawdata.loc[tempdata.query(col1 + '==1 and ' + col2 + '==1').index].label_pct_cost.mean()
        res = result_pct.T.mean()
        return float(res)

    @staticmethod
    def cal_abs_max_drawdown(df_rev, label_col='label_profit_cost'):
        data_list1 = df_rev.copy().reset_index()
        data_list1['datelist'] = data_list1.apply(lambda x: int(x['dt'].to_pydatetime().strftime("%Y%m%d")), axis=1)
        data_list1[[label_col]] = data_list1[[label_col]].fillna(0).astype(float)
        df_day = data_list1.groupby('datelist').sum()[[label_col]]
        data_list_ori = df_day[label_col]
        data_list = (data_list_ori.cumsum()).tolist()
        data_list = [0]+ data_list
        abs_max_down = 10000000
        for i in range(len(data_list) - 1):
            for j in range(i, len(data_list)):
                abs_max_down = min(abs_max_down, data_list[j] - data_list[i])
        return abs_max_down

    def cal_sharp(self, day_data, pct_col='label_profit_cost', stepdate=3):
        if 'datelist' not in day_data.columns.tolist():
            day_data['datelist'] = [pd.Timestamp(x).strftime('%Y%m%d') for x in day_data.reset_index()['dt'].tolist()]

        tot_dt = self.tot_dt
        daily_data = day_data.groupby('datelist').sum()[['label_buy_amt', 'label_profit_cost']].reindex(tot_dt).fillna(0)
        daily_data['近%s日盈亏金额(扣除成本)' % str(stepdate)] = daily_data['label_profit_cost'].rolling(stepdate, 1).sum()
        daily_data['近%s日投资金额' % str(stepdate)] = daily_data['label_buy_amt'].rolling(stepdate, 1).sum()
        daily_data['收益率(扣除成本)'] = daily_data['近%s日盈亏金额(扣除成本)' % str(stepdate)] / daily_data['近%s日投资金额' % str(stepdate)]
        daily_data['滚动%s日盈亏金额(扣除成本)' % str(stepdate)] = daily_data['label_profit_cost'].rolling(stepdate, 1).mean()

        daily_data = daily_data.fillna(0)
        ret_data = daily_data.copy()
        mean_ret = float(ret_data[ret_data['label_buy_amt'] > 0][pct_col].mean())
        std_ret = float(ret_data[ret_data['label_buy_amt'] > 0][pct_col].std())
        sharp = (mean_ret / std_ret) * math.sqrt(250)
        return sharp