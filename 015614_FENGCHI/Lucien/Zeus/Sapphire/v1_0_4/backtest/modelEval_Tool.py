# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 10:44:34 2021
931_Saturn_model evaluation
@author: 013550
"""
import os
import numpy as np
import pandas as pd
#from WindPy import w
from xquant.factordata import FactorData
hfactor = FactorData()
from sklearn.metrics import precision_score, recall_score,r2_score,mean_squared_error,roc_auc_score
import datetime as dt
today = dt.datetime.now().strftime('%Y%m%d')
import warnings
warnings.filterwarnings("ignore")
import math
group_num = 10
all_group_num = 20
tradedate_length =42#1000# 42#1000# 42
from model_eval.multifactor.IO import IO
from model_eval.multifactor.IO.IO_enums import *
class modelEval_Tool:
    def __init__(self,strategy_name,pred_data,valid_data,model_name,begindate, enddate,in_begindate, in_enddate,savepath,label_name='label_pct_cost',vote_type=False,scene_flag='',custom_dict={}):
        self.custom_dict = custom_dict
        self.strategy = str(strategy_name)
        self.indi_str = str(model_name)
        self.predcol = self.indi_str + 'proba1'
        self.FilesavePath = savepath
        self.begindate = int(begindate)
        self.enddate = int(enddate)
        self.pred_data = pred_data

        self.valid_data = valid_data
        self.label_data = self.select_label()
        self.profit_data = self.select_profit()

        self.scene_flag = scene_flag
        self.in_begindate = int(in_begindate)
        self.in_enddate = int(in_enddate)
        self.label_name = label_name
        self.vote_type = vote_type
    def select_profit(self):
        if self.strategy not in ['SaturnS0&SaturnS1','SaturnS1&SaturnS3']:
            if self.strategy == 'JupiterN':
                self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
                self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
                self.cost_pct = 0.002
                self.attend_min = 20
                self.attend_max = 51
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy == 'JupiterNSell':
                self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell12_profitdata_foreur_SH300_SZ30.pkl'#'/data/group/800463/project/project1_prod/LabelProfit_fixvol/LabelProfit_zt_pct_931_0.10_800_190_SH450_SZ100.h5'
                self.cost_pct = 0
                self.attend_min = 10
                self.attend_max = 26
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy == 'JupiterNSell34':
                self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell23_profitdata_foreur_SH300_SZ30.pkl'
                self.cost_pct = 0
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy.find( 'JupiterZSell')>=0:
                period_num = self.strategy.split('_')[-1]
                buy_strategy_ind = self.strategy.split('_')[1]
                if buy_strategy_ind.find('jup')>=0:
                    buy_strategy = 'JupiterN'
                elif buy_strategy_ind.find('eur')>=0:
                    buy_strategy = 'Europa'
                #self.profit_path = '/data/group/800463/xiely/save-file/for_wj/jupiterZ/20230215/%s_buySignal_sell_pred1_tmp_combined_forWj_period%s.pkl'%(buy_strategy, period_num)
                self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/jupiterZ/%s_with_JupiterZ_profitdata_foreur_SH300_SZ30.pkl'%buy_strategy
                self.cost_pct = 0.001
                self.attend_min = 20
                self.attend_max = 51
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy == 'JupiterZ':
                self.profit_path = '/data/group/800463/sunss/jupiterZ/newData/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.pkl'#%strategy#'/data/group/800463/sunss/jupiterZ/newData/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
                self.cost_pct = 0.002
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'Europa':
                self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
                self.profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
                self.cost_pct = 0.002
                self.attend_min = 20#5#20
                self.attend_max = 51#81#41
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy == 'Sapphire':
                self.profit_path = '/data/group/800463/sunss/profit/metis/20230817/v1/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5'
                self.europa_profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
                self.cost_pct = 0.002
                self.attend_min = 20#5#20
                self.attend_max = 51#81#41
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy == 'EuropaSell':
                #self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_profitdata_for_alleur_SH450_SZ100.pkl'
                #self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealout_20210701_20220930_profitdata_for_alleur_SH300_SZ30_new.pkl'
                #self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealrealout_20220101_20230331_profitdata_for_alleur_SH300_SZ30.pkl'
                self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealout_20210701_20220930_profitdata_for_alleur_SH300_SZ30_v3new.pkl'
                self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealout_20220101_20230331_profitdata_for_alleur_SH300_SZ30_v3new.pkl'
                self.profit_path='/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealrealout_v3fited_20221001_20230331_profitdata_for_alleur_SH300_SZ30.pkl'
                self.cost_pct = 0.002
                self.attend_min = 20#5#20
                self.attend_max = 51#81#41
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy == 'EuropaSellEnhance':
                self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealout_20210701_20220930_profitdata_for_alleur_SH300_SZ30_v3new.pkl'
                self.profit_path = '/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealout_20220101_20230331_profitdata_for_alleur_SH300_SZ30_v3new.pkl'
                self.profit_path='/data/group/800463/wangj/save_files/Europa_v3/sell/sell123_realrealrealrealout_v3fited_20221001_20230331_profitdata_for_alleur_SH300_SZ30.pkl'
                self.cost_pct = 0
                self.attend_min = 20#5#20
                self.attend_max = 51#81#41
                self.group_ratio = 0.2
                self.extreme_thres = 0.1
            elif self.strategy =='jupiter_sell':
                self.profit_path = ''
                self.cost_pct = 0.002
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'SaturnS0':
                self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_930_0.20_0.10_500_1500.h5'
                self.cost_pct = 0.004
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'SaturnS0_2tick':
                self.profit_path = '/data/group/800463/sunss/saturn/data/p2_profit_930_2tick_0.20_0.10_500_1500.h5'
                self.cost_pct = 0.004
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'SaturnS1':
                #self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_931_0.20_0.10_500_1500.h5'
                self.profit_path = '/data/group/800463/sunss/saturn/data/p2_profit_931_0.20_0.10_500_1500.h5'
                self.cost_pct = 0.004
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'Saturn3S1':
                self.profit_path = '/data/group/800463/sunss/saturn/data/p2_profit_931_3day_0.20_0.10_500_1500.h5'
                self.cost_pct = 0.004
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'SaturnS5':
                self.profit_path =  '/data/group/800463/sunss/for_xly/saturn/935/p2_profit_0.25_0.10_500_1500_20160101_20211231.h5'
                self.cost_pct = 0.004
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'Saturn':
                self.profit_path = '/data/group/800463/project/project2_prod/factor_bank/all_factor_20220712/filter_v2/profit/p2_profit_0.25_0.10_500_1500_20160101_20211231.h5'
                self.cost_pct = 0.004
                self.attend_min = 5
                self.attend_max = 36
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'Saturn_down':
                self.profit_path = '/data/group/800463/sunss/for_xly/saturn/filter_v3/p2_profit_0.25_0.10_500_1500_20160101_20211231.h5'
                self.cost_pct = 0.004
                self.attend_min = 5
                self.attend_max = 36
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 's2':
                self.profit_path = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_932_0.20_0.10_500_1500.h5'
                self.cost_pct = 0.004
                self.attend_min = 10
                self.attend_max = 41
                self.group_ratio = 0.2
                self.extreme_thres = 0.2
            elif self.strategy == 'SaturnS3':
                self.profit_path = '/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_933_3period/p2_profit_933_0.20_0.10_500_1500_20160101_20211231.h5'
                self.cost_pct = 0.004
                self.attend_min = 10
                self.attend_max = 41
                self.extreme_thres = 0.2
                self.group_ratio = 0.2
            elif self.strategy == 'CeresS1':
                self.profit_path = '/data/group/800463/project/project3_prod/profit_backtest/sp2_profit_931_0.20_0.10_500_1500.h5'
                self.cost_pct = 0.004
                self.attend_min = 20
                self.attend_max = 61
                self.group_ratio = 0.5
                self.extreme_thres = 0.2
            elif self.strategy == 'CeresS0':
                self.profit_path = '/data/group/800463/project/project3_prod/profit_backtest/sp2_profit_930_0.20_0.10_500_1500.h5'
                self.cost_pct = 0.004
                self.attend_min = 30
                self.attend_max = 61
                self.group_ratio = 0.5
                self.extreme_thres = 0.2
            if 'profit_path' in self.custom_dict.keys():
                self.profit_path = self.custom_dict['profit_path']

            if self.profit_path.endswith('.h5'):
                profit_data = IO.read_data([20100101, 20301231], alt=self.profit_path)
                if len(profit_data.index.levels) == 3:
                    profit_data = profit_data.reset_index()
                    profit_data['Ticker'] = profit_data['Ticker'] + profit_data['trigger_time'].astype(np.int).astype(str)
                    profit_data = profit_data.set_index(['dt', 'Ticker'])
                if self.strategy == 'Sapphire':
                    europa_profit_data = IO.read_data([20100101, 20301231], alt=self.europa_profit_path)
                    # for col in europa_profit_data.columns:
                    #     if (col not in profit_data.columns) and (col!='pct'):
                    #         profit_data[col] = europa_profit_data[col]
            else:
                profit_data = pd.read_pickle(self.profit_path)
                if len(profit_data.index.levels) == 3:
                    profit_data = profit_data.reset_index()
                    profit_data['Ticker'] = profit_data['Ticker'] + profit_data['trigger_time'].astype(np.int).astype(str)
                    profit_data = profit_data.set_index(['dt', 'Ticker'])
                if self.strategy.find('JupiterZSell') >= 0:
                    period_num = self.strategy.split('_')[-1]
                    profit_data['old_buy_amt'] = profit_data['buy_amt']
                    profit_data['buy_amt'] = profit_data['remain_amt']
                    profit_data['buySignal'] = profit_data['buySignal_%s'%period_num]
                    model = self.pred_data.copy().query('datelist>=%s and datelist<=%s'%(self.begindate,self.enddate)).reset_index()
                    model['dt'] = model['datelist'].apply(lambda x: pd.Timestamp(str(x)))
                    model.set_index(['dt', 'stockID'], inplace=True)
                    sel_index = list(set(model.index.tolist()) & set(profit_data.index.tolist()))

                    #print('before:',len(sel_index))
                    sel_profit = profit_data.loc[sel_index].sort_index()
                    sel_profit['stockID'] = sel_profit.reset_index().Ticker.tolist()

                    #print('after:',len(sel_index))
                    model = model.loc[sel_index].sort_index()
                    buy_type = self.strategy.split('_')[-2]
                    if buy_type == 'pred1':
                        model = model.loc[list(set(sel_profit.loc[model.index].query('buySignal==1 and remain_amt>0').index.tolist()))].sort_index()
                        sel_profit = sel_profit.query('buySignal==1 and remain_amt>0').loc[model.index].sort_index()

                    sel_profit = sel_profit.loc[model.index].sort_index()
                    sel_profit = sel_profit.join(model[['prediction']],on=['dt','Ticker'])
                    cf_df = sel_profit.groupby(['dt', 'Ticker']).count()['jupiterZ_dt'].sort_values()
                    cf_index = cf_df[cf_df > 1].index.tolist()
                    nocf_index = cf_df[cf_df == 1].index.tolist()
                    # sel_index1 = list(set(model.query('prediction==1').index.tolist()) & set(sel_profit.index.tolist()))
                    # sel_index2 = list(set(model.query('prediction==0').index.tolist()) & set(sel_profit.index.tolist()))
                    # print(len(sel_index), len(sel_index1), len(sel_index2), len(sel_profit))
                    sels1 = sel_profit.loc[cf_index].sort_values(['buy_date', 'stockID', 'prediction', 'sell_date']).drop_duplicates(['buy_date', 'stockID'],
                                                                                            keep='first') # 处理1个买入多个卖出的情况，保留第一个预测为 1的卖出信号
                    sel = sels1.sort_values(['sell_date', 'stockID', 'prediction', 'buy_date']).drop_duplicates(['sell_date', 'stockID'],keep='first')# # 处理多个买入对应1个卖出的情况，保留最早的买入信号

                    if sel.index.is_unique:
                        pass
                    else:
                        print('deal 0/1!!!')
                        print('before:',len(sel))
                        sel = sel.sort_values(by=['sell_pred'], ascending=False).sort_index()
                        sel.drop_duplicates(subset=['buy_date', 'stockID'], keep='first', inplace=True)
                        sel.drop_duplicates(subset=['sell_date', 'stockID'], keep='first', inplace=True)
                        print('after:', len(sel))

                    profit_data = pd.concat([sel.copy(),sel_profit.loc[nocf_index]])
                    print(buy_type,len(profit_data),len(model))
                elif self.strategy == 'JupiterNSell':
                    model = self.pred_data.copy().reset_index()
                    model['dt'] = model['datelist'].apply(lambda x: pd.Timestamp(str(x)))
                    model.set_index(['dt', 'stockID'], inplace=True)
                    profit_data['pct'] = profit_data['label_diff_pct']
                elif self.strategy == 'JupiterNSell34':
                    model = self.pred_data.copy().reset_index()
                    model['dt'] = model['datelist'].apply(lambda x: pd.Timestamp(str(x)))
                    model.set_index(['dt', 'stockID'], inplace=True)
                    profit_data[ 'pct'] = profit_data['label_diff_pct_next']
                elif self.strategy == 'EuropaSell':
                    model = self.pred_data.copy().reset_index()
                    model['dt'] = model['datelist'].apply(lambda x: pd.Timestamp(str(x)))
                    model.set_index(['dt', 'stockID'], inplace=True)
                    v1index = model.query('pred_v1==1 and pred_v3==0').index.tolist()
                    v3index = model.query('pred_v1==0 and pred_v3==1').index.tolist()
                    v2index = list(set(model.index.tolist())-set(v1index+v3index))
                    profit_data['old_pct'] = profit_data['pct']
                    profit_data.loc[v1index,'pct'] = profit_data.loc[v1index,'pct_v1'] - 0.001
                    profit_data.loc[v3index, 'pct'] = profit_data.loc[v3index, 'pct_v3'] - 0.001
                    #profit_data.loc[v2index, 'pct'] = profit_data.loc[v2index, 'pct_v2']
                elif self.strategy == 'EuropaSellEnhance':
                    model = self.pred_data.copy().reset_index()
                    model['dt'] = model['datelist'].apply(lambda x: pd.Timestamp(str(x)))
                    model.set_index(['dt', 'stockID'], inplace=True)
                    v1index = model.query('pred_v1==1 and pred_v3==0').index.tolist()
                    v3index = model.query('pred_v1==0 and pred_v3==1').index.tolist()
                    v2index = list(set(model.index.tolist())-set(v1index+v3index))
                    profit_data['old_pct'] = profit_data['pct']
                    profit_data.loc[v1index,'pct'] = profit_data.loc[v1index,'pct_v1'] - 0.001 - profit_data.loc[v1index,'old_pct']
                    profit_data.loc[v3index, 'pct'] = profit_data.loc[v3index, 'pct_v3'] - 0.001 - profit_data.loc[v3index,'old_pct']
                    profit_data.loc[v2index, 'pct'] = profit_data.loc[v2index, 'old_pct'] - 0.002

        else:
            if self.strategy == 'SaturnS0&SaturnS1':
            # 进行s0和s1的合并收益分析
                self.profit_path = '/data/user/013550/project2/saturn_930/20191001~20201231_930vote4_931vote5_combine_profitdata_20211108.pkl'
            elif self.strategy == 'SaturnS1&SaturnS3':
                # 进行s1和s3的合并收益分析
                self.profit_path = '/data/group/800463/wangj/project2/profit/20190101~20201231_s1filterv1&s3_combine_profitdata_20221019.pkl'
            self.cost_pct = 0.004
            self.attend_min = 10
            self.attend_max = 41
            self.extreme_thres = 0.2
            self.group_ratio = 0.2
            profit_data = pd.read_pickle(self.profit_path)
        if 'label_pct_cost' not in profit_data.columns.tolist():

            profit_data.columns = ['label_' + i for i in profit_data.columns.tolist()]
            if self.strategy == 'JupiterZ':
                profit_data['label_pct'] = -profit_data['label_pct']
            profit_data['label_pct_cost'] = profit_data['label_pct'] - self.cost_pct
            profit_data['label_profit_cost'] = profit_data['label_pct_cost'] * profit_data['label_buy_amt']
            profit_data = profit_data.reset_index()
            profit_data['stockID'] = profit_data['Ticker']
            profit_data['datelist'] = profit_data['dt'].apply(lambda x: int(x.to_pydatetime().strftime("%Y%m%d")))
            profit_data['Indexs'] = profit_data['stockID'].astype(str) + ' ' + (profit_data['datelist'].astype(int)).astype(str)
            profit_data.set_index(['Indexs'], inplace=True)
        return profit_data
    def select_label(self):
        addcols = ['dt', 'Ticker']
        if self.strategy == 'SaturnS0&SaturnS1':
            self.label_path = '/data/user/013550/project2/saturn_930/20191001~20201231_930vote4_931vote5_combine_labeldata_20211108.pkl'
            self.label_rev = 'label_v2o10'
            self.label_o2o10 = 'label_o2o10'
            self.label_Tc2To10 = 'label_Tc2To10'
            label_data = pd.read_pickle(self.label_path)
        else:
            if self.strategy == 'JupiterN':
                self.label_path = '/data/group/800463/sunss/jupiter/20221220/factor_df_all_20160101_20220630.pkl'
                self.label_path = '/data/user/018107/share_file/for_wj/%s/factor_df_all_20160101_20230113.pkl' % 'jupiter'
                self.label_rev = 'label_TN_o2ul'
                self.label_o2o10 = 'label_pattern'
            elif self.strategy in ['JupiterNSell','EuropaSell','JupiterNSell34','EuropaSellEnhance']:
                self.label_path =  '/data/group/800463/sunss/%s/%s/factor_df_all_20160101_20211231_931_xly.pkl'%('europa',str(20230317))#'/data/group/800463/sunss/jupiter_931o2ul/20230201/factor_df_all_20160101_20201231.pkl'
                #self.label_path = '/data/user/018107/share_file/fore_wj/europa/20230329/factor_df_all_20160101_20230331_fit.pkl'
                self.label_path='/data/group/800463/sunss/europa/20230329/factor_df_all_20160101_20220630.pkl'
                self.label_rev = 'label_TN_931o2ul'
                self.label_o2o10 = 'label_pattern'
            elif self.strategy.find( 'JupiterZSell')>=0:
                self.label_path = '/data/group/800463/sunss/jupiterZ/20230415/factor_df_all_20160101_20211231_xly.pkl'#'/data/group/800463/sunss/jupiter/20221220/factor_df_all_20160101_20220630.pkl'
                self.label_path = '/data/group/800463/sunss/jupiterZ/20230415/factor_df_all_20160101_20230331_xly.pkl'
                self.label_rev = 'label_TN_o2ul'
                self.label_o2o10 = 'label_pattern'
            elif self.strategy == 'JupiterZ':
                #self.label_path = '/data/group/800463/sunss/jupiterZ/20230205/factor_df_all_20160101_20211231.pkl'
                self.label_path = '/data/group/800463/sunss/jupiterZ/20230415/factor_df_all_20160101_20220630_xly.pkl'
                self.label_rev = 'label_TN_o2ul'
                self.label_o2o10 = 'label_pattern'
            elif self.strategy == 'jupiter003':
                self.label_path = '/data/group/800463/project/project1_prod/factor_manager_v2/all_factor_bank/test_003/all_factor.pkl'
                self.label_rev = 'label_TN_o2ul'
                self.label_o2o10 = 'label_pattern'
            elif self.strategy == 'Europa' :
                self.label_path = '/data/group/800463/sunss/for_xly/europa/20221116_new/factor_df_all_20160101_20220630.pkl'
                self.label_path = '/data/user/018107/share_file/for_wj/%s/factor_df_all_20160101_20230113.pkl'%'europa'
                #self.label_path = '/data/user/018107/share_file/for_wj/europa/20230329/factor_df_all_20160101_20230331_fit.pkl'
                self.label_path = '/data/group/800463/sunss/europa/20230329/factor_df_all_20160101_20220630.pkl'

                self.label_rev = 'label_TN_o2ul'
                self.label_o2o10 = 'label_pattern'
            elif self.strategy =='Sapphire':
                self.label_path = '/data/group/800463/sunss/metis/20230817/v1/factor_df_all_20160101_20211231_graded.pkl'
                self.label_path = '/data/group/800463/sunss/metis/20230821/v1/factor_df_all_20160101_20220930_graded.pkl'

                self.label_rev = 'label_pct'
                self.label_o2o10 = 'label_pattern'
            elif self.strategy == 'SaturnS0':
                self.label_path = '/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
                self.label_path = '/data/group/800463/project/project2_prod/daily_data/sft/sft_basic_origin.h5'
                self.label_rev = 'label_v2o10'
                self.label_o2o10 = 'label_o2o10'
                self.label_Tc2To10 = 'label_Tc2To10'
                self.label_TNo2To10 = 'label_TNo2To10'
            elif self.strategy == 'SaturnS0_2tick':
                # self.label_path = '/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
                self.label_path = '/data/group/800463/sunss/saturn/20230524/factor_df_930_2tick_20160101_20211231_graded.pkl'
                #self.label_path = '/data/group/800463/sunss/saturn/data/sft_basic_origin.h5'
                self.label_rev = 'label_v2o10d2tick'
                self.label_o2o10 = 'label_o2o10d2tick'
                self.label_Tc2To10 = 'label_Tc2To10d2tick'
                self.label_TNo2To10 = 'label_o2o10d2tick'  # 'label_TNo2To10d2tick'
            elif self.strategy == 'SaturnS1':
                #self.label_path = '/data/group/800463/project/project2_prod/daily_data/sft/sft_basic_origin.h5'
                self.label_path = '/data/group/800463/sunss/saturn/data/sft_basic_origin.h5'
                self.label_rev = 'label_v2o10d1'
                self.label_o2o10 = 'label_o2o10d1'
                self.label_Tc2To10 = 'label_Tc2To10d1'
                self.label_TNo2To10 = 'label_TNo2To10d1'
            elif self.strategy == 'Saturn3S1':
                self.label_path = '/data/group/800463/sunss/saturn/20230524/factor_df_931_3day_20160101_20211231_graded.pkl'
                self.label_rev = 'label_3v2o10d1'
                self.label_o2o10 = 'label_3o2o10d1'
                self.label_Tc2To10 = 'label_Tc2To10'
                self.label_TNo2To10 = 'label_3o2o10d1'
            elif self.strategy == 'SaturnS1&SaturnS3':
                #self.label_path = '/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
                self.label_path = '/data/group/800463/wangj/project2/label/20190101~20201231_s1filterv1&s3_combine_labeldata_20221019.pkl'#'/data/group/800463/project/project2_prod/daily_data/sft/sft_basic_origin.h5'
                self.label_rev = 'label_v2o10d1'
                self.label_o2o10 = 'label_o2o10d1'
                self.label_Tc2To10 = 'label_Tc2To10d1'
                self.label_TNo2To10 = 'label_TNo2To10d1'
            elif self.strategy == 'SaturnS5':
                self.label_path = '/data/group/800463/sunss/for_xly/saturn/935/label_20160101_20201231.h5'
                self.label_rev = 'label_v2o10d5'
                self.label_o2o10 = 'label_o2o10d5'
                self.label_Tc2To10 = 'label_Tc2To10d5'
                self.label_TNo2To10 = 'label_TNo2To10d5'
            elif self.strategy in  ['Saturn', 'Saturn_down']:
                self.label_path = '/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
                self.label_path = '/data/group/800463/project/project2_prod/daily_data/sft/sft_basic_origin.h5'
                self.label_rev = 'label_v2o10d1'
                self.label_o2o10 = 'label_o2o10d1'
                self.label_Tc2To10 = 'label_Tc2To10d1'
                self.label_TNo2To10 = 'label_TNo2To10d1'
            elif self.strategy == 's2':
                self.label_path = '/data/group/800463/project/project2_prod/everyday_Basic_v2/20160101_20211231/label_for_model_test_20160101_20211231.pkl'#'/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
                self.label_rev = 'label_v2o10d2'
                self.label_o2o10 = 'label_o2o10d2'
                self.label_Tc2To10 = 'label_Tc2To10d2'
                self.label_TNo2To10 = 'label_TNo2To10d2'
            elif self.strategy == 'SaturnS3':
                #self.label_path = '/data/group/800463/project/project2_prod/everyday_Basic_v2/20160101_20211231/label_for_model_test_20160101_20211231.pkl'#'/data/group/800463/project/project2_prod/daily_data/Label/label.h5'
                self.label_path = '/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_933_3period/sft_basic_origin.h5'
                self.label_rev = 'label_v2o10d3'
                self.label_o2o10 = 'label_o2o10d3'
                self.label_Tc2To10 = 'label_Tc2To10d3'
                self.label_TNo2To10 = 'label_TNo2To10d3'
            elif self.strategy == 'CeresS1':
                self.label_path =  '/data/group/800463/project/project3_prod/daily_data/Label/label.h5'#'/data/group/800463/project/project3_prod/everyday_Basic/20160101_20220419/label_pj3_20160101_20220419.h5'
                self.label_rev = 'label_v2o10d1'
                self.label_o2o10 = 'label_o2o10d1'
                self.label_Tc2To10 = 'label_Tc2To10d1'
                self.label_TNo2To10 = 'label_TNo2To10d1'
            elif self.strategy == 'CeresS0':
                self.label_path = '/data/group/800463/project/project3_prod/everyday_Basic/20160101_20210831/label.pkl'
                self.label_rev = 'label_v2o10'
                self.label_o2o10 = 'label_o2o10'
                self.label_Tc2To10 = 'label_Tc2To10'
                self.label_TNo2To10 = 'label_TNo2To10'

            if self.label_path.endswith('pkl'):
                label_data = pd.read_pickle(self.label_path)
            else:
                label_data = IO.read_data([20100101, 20300101],alt=self.label_path)
            label_data = label_data.filter(regex='label*')#.reset_index()
            label_data =  label_data.fillna(0)

            if len(label_data.index.levels) == 3:
                label_data = label_data.reset_index()
                label_data['Ticker'] = label_data['Ticker'] + label_data['trigger_time'].astype(np.int).astype(str)
                label_data = label_data.set_index(['dt', 'Ticker'])

            if self.strategy in ['SaturnS0_2tick']:
                labeladd = pd.read_hdf('/data/group/800463/sunss/saturn/data/sft_basic_origin.h5')
                label_data = pd.concat([label_data, labeladd[['label_TNo2Tc', 'label_TNv2TNo', 'label_To102To', 'label_Next_close_is_zt', 'label_T_day_first_ZT_Time']]], axis=1)
            if self.strategy in ['Saturn3S1']:
                labeladd = pd.read_hdf('/data/group/800463/sunss/saturn/data/sft_basic_origin.h5')
                label_data = pd.concat([label_data, labeladd[['label_TNo2Tc', 'label_TNv2TNo', 'label_To102To', 'label_Next_close_is_zt','label_Tc2To10']]], axis=1)
                label_data['label_TNv2TNo'] = labeladd['label_TN3v2TN3o'].tolist()
                label_data['label_TNo2Tc'] = labeladd['label_TN3o2Tc'].tolist()

            label_data = label_data.reset_index()
            label_data['stockID'] = label_data['Ticker']
            label_data['datelist'] = label_data['dt'].apply(lambda x: int(x.to_pydatetime().strftime("%Y%m%d")))
            if 'label_T_close_is_zt' not in label_data.columns.tolist() and (self.strategy in ['JupiterN','Europa','Sapphire','jupiter003','JupiterNSell','JupiterNSell34','JupiterZ','EuropaSell','EuropaSellEnhance'] or self.strategy.find( 'JupiterZSell')>=0):
                label_data['label_T_close_is_zt'] = label_data['label_T_is_zt']
            if 'label_Next_close_is_zt' not in label_data.columns.tolist()  and (self.strategy in ['JupiterN','Europa','Sapphire','jupiter003','JupiterNSell','JupiterNSell34','JupiterZ','EuropaSell','EuropaSellEnhance'] or self.strategy.find( 'JupiterZSell')>=0):
                label_data['label_Next_close_is_zt'] = label_data['label_T1_is_zt']
            label_data['Indexs'] = label_data['stockID'].astype(str) + ' ' + (label_data['datelist'].astype(int)).astype(str)
            label_data.set_index(['Indexs'], inplace=True)
        return label_data
    def generate_series_data(self):
        scene_flag = self.scene_flag
        model = self.pred_data
        if self.strategy.find('JupiterZSell')>=0:
            sel_index = list(set(self.pred_data.index.tolist())&set(self.profit_data.index.tolist()))
            model = self.pred_data.loc[sel_index].sort_values(by=['datelist'])
            buy_type = self.strategy.split('_')[-2]
            if buy_type == 'pred1':
                model = model.loc[self.profit_data.loc[model.index].query('label_buySignal==1').index].sort_values(by=['datelist'])
                model = model.loc[self.profit_data.loc[model.index].query('label_buySignal==1').index].sort_values(by=['datelist'])
            print(buy_type,len(model))
        model_valid = self.valid_data
        model_valid = model_valid.query('datelist>=%s and datelist<=%s'%(str(self.in_begindate),str(self.in_enddate)))
        model_valid[self.indi_str] = model_valid['prediction'].tolist()
        model_valid[self.predcol] = model_valid['pred_Reg'].tolist()
        predcol = self.predcol
        model = model.query('datelist>=%s and datelist<=%s'%(str(self.begindate),str(self.enddate)))
        model.sort_values(by=['datelist','stockID'], inplace = True)
        model[self.indi_str] = model['prediction'].tolist()
        model[self.predcol] = model['pred_Reg'].tolist()
        model['Flag_SH'] = [1 if (i.split(' ')[0]).split('.')[1]=='SH' else 0 for i in model.index.tolist()]
        label_data = self.label_data.copy()
        subcols = list(set(label_data.columns.tolist()) & set(model.columns.tolist()))
        model.drop(columns=subcols, inplace=True)
        model = pd.concat([model, label_data], axis=1).reindex(model.index)#, join_axes=[model.index])

        dropcols = list(set(model.columns.tolist())&set(['label_buy_amt','label_pct','label_buy_vol']))
        model.drop(columns=dropcols,inplace=True)

        profit_data = self.profit_data.copy()
        model = pd.concat([model[list(set(model.columns.tolist())-set(profit_data.filter(regex='label*').columns.tolist()))],profit_data.filter(regex='label*')],axis=1).reindex(model.index)#,join_axes=[model.index])

        # 选择label
        model['label_v2o10'] = model[self.label_rev].tolist()
        model['label_o2o10'] = model[self.label_o2o10].tolist()
        model_valid[self.label_rev] = label_data.loc[label_data.index.intersection(model_valid.index), self.label_rev].tolist()
        model_valid[self.label_o2o10] = label_data.loc[label_data.index.intersection(model_valid.index), self.label_o2o10].tolist()
        model_valid['label_v2o10'] = model_valid[self.label_rev].tolist()
        model_valid['label_o2o10'] = model_valid[self.label_o2o10].tolist()

        # if self.strategy in ['SaturnS1', 'SaturnS0','Saturn','Saturn_down','SaturnS5','SaturnS3','SaturnS0&SaturnS1','SaturnS1&SaturnS3']: # ,'CeresS1'
        #     model['To_2pre'] = label_data.loc[model.index, 'T_o2pre'].tolist()
        #     model_valid['To_2pre'] = label_data.loc[model_valid.index, 'T_o2pre'].tolist()
        #     model['T1_2pre'] = label_data.loc[model.index, 'wd_t1_pct'].tolist()
        #     model_valid['T1_2pre'] = label_data.loc[model_valid.index, 'wd_t1_pct'].tolist()

        model['true_label'] = [ 1 if x>=self.cost_pct else 0 for x in model[self.label_rev].tolist()]
        model_valid['true_label'] = [1 if x >= self.cost_pct else 0 for x in model_valid[self.label_rev].tolist()]

        model['label_profit'] = model['label_pct'] * model['label_buy_amt']
        model['label_pct_cost'] = model['label_pct'] - self.cost_pct
        model['label_profit_cost'] = model['label_pct_cost'] * model['label_buy_amt']
        model_valid['label_pct_cost'] = self.profit_data.loc[self.profit_data.index.intersection(model_valid.index)]['label_pct_cost']
        model_valid['label_profit_cost'] = self.profit_data.loc[self.profit_data.index.intersection(model_valid.index)]['label_profit_cost']
        model_valid['label_pct'] = self.profit_data.loc[self.profit_data.index.intersection(model_valid.index)]['label_pct']
        model_valid['label_buy_amt'] = self.profit_data.loc[self.profit_data.index.intersection(model_valid.index)]['label_buy_amt']
        model_valid['label_profit'] = model_valid['label_pct'] * model_valid['label_buy_amt']

        totalResDf, daily_data,statistic_by_sample,daily_data_valid,model_mingan,model_inmingan,group_proba_all,totalResDf_only_extreme = self.generate_test_report(model,model_valid,scene_flag,predcol)
        daily_data.columns = [i + '_%s' % str(self.indi_str) for i in daily_data.columns.tolist()]# [self.indi_str]#
        basic_cols = daily_data.filter(regex='基础').columns.tolist()
        rename_basic_cols = [x.replace('_%s' % str(self.indi_str), '') for x in basic_cols]
        basic_dict = dict(zip(basic_cols, rename_basic_cols))
        daily_data.rename(columns = basic_dict, inplace = True)
        totalResDf.columns = [x.replace('模型表现',self.indi_str) for x in totalResDf.columns.tolist()]#totalResDf.columns = [self.indi_str]
        totalResDf_only_extreme.columns = [x.replace('模型表现', self.indi_str) for x in totalResDf_only_extreme.columns.tolist()]  # totalResDf.columns = [self.indi_str]
        #print(totalResDf.columns)
        daily_data_valid.columns = [self.indi_str]
        #model_mingan = pd.concat([pd.DataFrame([self.indi_str],index=['模型名称'])])
        return totalResDf.fillna(0), daily_data,statistic_by_sample,daily_data_valid,model_mingan,model_inmingan,group_proba_all,totalResDf_only_extreme
    def generate_test_report(self,pred_out, pred_in,scene_flag,probacol):

        pred_out.sort_values(by=['datelist','stockID'], inplace = True)
        pred_in.sort_values(by=['datelist','stockID'], inplace = True)

        sample_data = pred_out.copy()
        sample_data.rename(columns = {'label_buy_amt':'投资金额','label_pct':'收益率','label_pct_cost':'收益率(扣除成本)','label_profit_cost':'盈亏金额(扣除成本)'},inplace= True)
        sample_data['label_pct'] = sample_data['收益率']
        #按样本统计
        statistic_by_sample = pd.DataFrame()
        statistic_by_sample['投资金额'] = sample_data['投资金额']
        statistic_by_sample['收益率'] = sample_data['收益率']
        statistic_by_sample.loc[statistic_by_sample.query('投资金额 == 0').index.tolist(),'收益率'] = sample_data.loc[statistic_by_sample.query('投资金额 == 0').index.tolist(),'收益率']

        statistic_by_sample['盈亏金额'] = statistic_by_sample['收益率'] * statistic_by_sample['投资金额']

        statistic_by_sample['是否T日收盘涨停'] = sample_data['label_T_close_is_zt']

        statistic_by_sample['是否T+1日收盘涨停'] = sample_data['label_Next_close_is_zt']
        statistic_by_sample['收益率(扣除成本)'] = sample_data['收益率'] - self.cost_pct

        statistic_by_sample['盈亏金额(扣除成本)'] = statistic_by_sample['收益率(扣除成本)'] * statistic_by_sample['投资金额']
        if self.strategy not in ['JupiterN', 'jupiter_sell','Europa','Sapphire','jupiter003','JupiterNSell','JupiterNSell34','JupiterZ','EuropaSell','EuropaSellEnhance'] and self.strategy.find( 'JupiterZSell')<0:
            statistic_by_sample['v2o10收益率'] = sample_data[self.label_rev]
            statistic_by_sample['o2o10收益率'] = sample_data[self.label_o2o10]
            statistic_by_sample['o2Tc收益率'] = sample_data['label_TNo2Tc'] # TN日open相对于T日close
            statistic_by_sample['Tc2o10收益率'] = sample_data[self.label_Tc2To10] # T日close相对于T日o10d1
            statistic_by_sample['TNo2To10收益率'] = sample_data[self.label_TNo2To10]  # T日close相对于T日o10d1
            statistic_by_sample['Tv2o收益率'] = sample_data['label_TNv2TNo'] # TN日vwap相对于TN日open
            statistic_by_sample['To102To收益率'] = sample_data['label_To102To']
            statistic_by_sample['T日触板时间'] = sample_data['label_T_day_first_ZT_Time']
            statistic_by_sample['是否正例'] = [1 if x >= self.cost_pct else 0 for x in sample_data[self.label_rev].tolist()]
            # if self.strategy in ['SaturnS1', 'SaturnS0','Saturn','Saturn_down','SaturnS5','SaturnS3','SaturnS1&SaturnS3']:
            #     statistic_by_sample['To_2pre'] = sample_data['To_2pre']
            #     statistic_by_sample['T1_2pre'] = sample_data['T1_2pre']

        else:
            statistic_by_sample['o2ul收益率'] = sample_data[self.label_rev]
            statistic_by_sample['T日形态'] = sample_data[self.label_o2o10]
            if self.strategy.find( 'JupiterZSell')>=0:
                statistic_by_sample['T日收益率'] = 0#sample_data['label_pct_t']
                statistic_by_sample['T+1日收益率'] = 0#sample_data['label_pct_t1']
            else:
                statistic_by_sample['T日收益率'] = sample_data['label_pct_t']
                statistic_by_sample['T+1日收益率'] = sample_data['label_pct_t1']
            if self.strategy == 'EuropaSell':#.find( 'EuropaSell')>=0:
                statistic_by_sample['pred_v1'] = sample_data['pred_v1']
                statistic_by_sample['pred_v3'] = sample_data['pred_v3']
                statistic_by_sample['原始扣费收益率'] = sample_data['label_old_pct'] - self.cost_pct
                statistic_by_sample['卖出增强收益率'] = statistic_by_sample['收益率(扣除成本)'] - statistic_by_sample['原始扣费收益率']

        statistic_by_sample['是否为上海'] = sample_data['Flag_SH']
        statistic_by_sample[self.indi_str] = sample_data['prediction'].astype(int)
        statistic_by_sample[self.predcol] = sample_data['pred_Reg'].astype(float)



        statistic_by_sample['datelist'] = [int(i.split(' ')[1]) for i in statistic_by_sample.index.tolist()]
        statistic_by_sample['stockID'] = [i.split(' ')[0] for i in statistic_by_sample.index.tolist()]
        statistic_by_sample_all = statistic_by_sample.copy()
        statistic_by_sample = statistic_by_sample_all.query('%s==1'%self.indi_str)
        model_valid_mingan = pd.DataFrame()
        model_mingan = pd.DataFrame()
        pred_in_without_extreme = self.remove_extreme_value(pred_in.query('prediction==1').copy(), 'label_pct_cost','label_buy_amt')
        pred_out_without_extreme = self.remove_extreme_value(pred_out.query('prediction==1').copy(), 'label_pct_cost','label_buy_amt')
        pred_in_without_extreme = pd.concat([pred_in_without_extreme, pred_in.loc[pred_in.query('prediction==0').index]]).reindex(pred_in.index)
        pred_out_without_extreme = pd.concat([pred_out_without_extreme, pred_out.loc[pred_out.query('prediction==0').index]]).reindex(pred_out.index)
        pred_out_without_extreme['Flag_is_extreme'] = pred_out_without_extreme['Flag_is_extreme'].fillna(0)
        if self.indi_str.find('vote')<0 or self.indi_str.find('stack')>=0:
            model_mingan = self.cal_model_mingan(pred_out, self.predcol)
            #model_mingan = self.cal_model_mingan_basedout(pred_out,self.predcol)
            #model_valid_mingan1 = self.cal_model_mingan(pred_in_without_extreme, self.predcol)
            model_valid_mingan = self.cal_model_mingan(pred_out_without_extreme, self.predcol)#self.cal_model_mingan_basedout(pred_out_without_extreme, self.predcol)

        #按日统计
        statistic_by_day, statistic_by_sample = self.fun_statistic_by_day(self.begindate, self.enddate, statistic_by_sample,pred_out)
        statistic_by_day_valid = self.fun_statistic_by_day_valid(pred_in.query('prediction==1'))
        #去极值
        statistic_without_extreme_value = self.remove_extreme_value(statistic_by_sample.copy(), '收益率(扣除成本)', '投资金额')
        #去极值
        statistic_without_extreme_value_by_day, _ = self.fun_statistic_by_day(self.begindate, self.enddate, statistic_without_extreme_value,pred_out)

        totalResDf,_,totalResDf1,_,group_proba_all =  self.combine_res_inout(pred_out.copy(),sample_data.copy(),statistic_without_extreme_value.copy(),statistic_by_sample.copy(),statistic_by_day.copy(),pred_in,scene_flag,probacol)

        totalResDf_monthly = totalResDf.copy()#pd.DataFrame()
        #self.indi_str.find('Model')<0 and
        if (self.indi_str.find('Model')<0 and self.indi_str.find('Sell')<0 and self.indi_str.find('stack')<0 and self.indi_str.find('vote')<0 and tradedate_length <len(hfactor.tradingday(self.begindate,self.enddate)) and self.vote_type==False):
            minlist, maxlist = self.generate_date_group(self.begindate, self.enddate, tradedate_length)

            for idx in list(range(len(minlist))):
                start_date, stop_date = minlist[idx], maxlist[idx]
                if idx == len(minlist)-1:
                    pass
                else:
                    stop_date = hfactor.tradingday(stop_date, -2)[0]
                pred_out_tmp = pred_out.query('datelist>=%s and datelist<=%s'%(start_date, stop_date))
                statistic_by_day_tmp, statistic_by_sample_tmp = self.fun_statistic_by_day(start_date,stop_date,statistic_by_sample.query('datelist>=%s and datelist<=%s'%(start_date, stop_date)), pred_out_tmp)
                statistic_without_extreme_value_tmp = self.remove_extreme_value(statistic_by_sample_tmp.copy(), '收益率(扣除成本)', '投资金额')
                totalResDf_tmp, _, _, _, _ = self.combine_res_inout(pred_out_tmp.copy(), sample_data.copy(),
                                                                                        statistic_without_extreme_value_tmp.copy(),
                                                                                        statistic_by_sample_tmp.copy(),
                                                                                        statistic_by_day_tmp.copy(), pred_in,
                                                                                        scene_flag, probacol)
                totalResDf_tmp.columns = ['模型表现_%s_%s'%(start_date,stop_date)]
                totalResDf_monthly = pd.concat([totalResDf_monthly, totalResDf_tmp], axis = 1)
        totalResDf_without_extreme, _, _, _, group_proba_all_without_extreme = self.combine_res_inout(pred_out_without_extreme.copy(), sample_data.copy(),
                                                                                statistic_without_extreme_value.copy(),
                                                                                statistic_without_extreme_value.copy(),
                                                                                statistic_without_extreme_value_by_day.copy(), pred_in_without_extreme,
                                                                                scene_flag, probacol)
        totalResDf_monthly_without_extreme = totalResDf_without_extreme.copy()  # pd.DataFrame()
        # self.indi_str.find('Model')<0 and
        if (self.indi_str.find('Model')<0 and self.indi_str.find('Sell')<0 and self.indi_str.find('stack')<0 and self.indi_str.find('vote')<0 and tradedate_length <len(hfactor.tradingday(self.begindate,self.enddate)) and self.vote_type==False):
            minlist, maxlist = self.generate_date_group(self.begindate, self.enddate, tradedate_length)
            for idx in list(range(len(minlist))):
                start_date, stop_date = minlist[idx], maxlist[idx]
                if idx == len(minlist) - 1:
                    pass
                else:
                    stop_date = hfactor.tradingday(stop_date, -2)[0]
                pred_out_tmp = pred_out_without_extreme.query('datelist>=%s and datelist<=%s' % (start_date, stop_date))
                statistic_by_day_tmp, statistic_by_sample_tmp = self.fun_statistic_by_day(start_date, stop_date,
                                                                                          statistic_without_extreme_value.query(
                                                                                              'datelist>=%s and datelist<=%s' % (
                                                                                              start_date, stop_date)),
                                                                                          pred_out_tmp)
                statistic_without_extreme_value_tmp = self.remove_extreme_value(statistic_by_sample_tmp.copy(),
                                                                                '收益率(扣除成本)', '投资金额')
                totalResDf_tmp, _, _, _, _ = self.combine_res_inout(pred_out_tmp.copy(), sample_data.copy(),
                                                                    statistic_without_extreme_value_tmp.copy(),
                                                                    statistic_by_sample_tmp.copy(),
                                                                    statistic_by_day_tmp.copy(), pred_in,
                                                                    scene_flag, probacol)
                totalResDf_tmp.columns = ['模型表现_%s_%s' % (start_date, stop_date)]
                totalResDf_monthly_without_extreme = pd.concat([totalResDf_monthly_without_extreme, totalResDf_tmp], axis=1)
        # pred_out_only_extreme = pred_out.copy()
        # pred_out_only_extreme['prediction'] = 0
        # pred_out_only_extreme.loc[pred_out_without_extreme.query('Flag_is_extreme == 1').index,'prediction'] = 1
        # statistic_by_day_only_extreme, statistic_by_sample_only_extreme = self.fun_statistic_by_day(self.begindate, self.enddate,
        #                                                                           statistic_by_sample.loc[pred_out_only_extreme.query('prediction==1').index],
        #                                                                           pred_out_only_extreme)
        # statistic_without_extreme_value_only = self.remove_extreme_value(statistic_by_sample_only_extreme.copy(), '收益率(扣除成本)',
        #                                                                 '投资金额')
        # totalResDf_only_extreme, _, _, _, group_proba_all_only_extreme = self.combine_res_inout(
        #     pred_out_only_extreme.copy(), sample_data.copy(),
        #     statistic_without_extreme_value_only.copy(),
        #     statistic_by_sample_only_extreme.copy(),
        #     statistic_by_day_only_extreme.copy(), pred_in,
        #     scene_flag, probacol)

        FilePath = self.FilesavePath + '/回测结果/'
        if not os.path.exists(FilePath):
            os.makedirs(FilePath)
            print("creat folder " + FilePath)
        writer = pd.ExcelWriter(FilePath+'%d~%d_%s_%s_模型评价_%s.xlsx'%(self.begindate,self.enddate,self.strategy,self.indi_str,today))

        statistic_by_sample_all = statistic_by_sample_all.reset_index()
        statistic_by_sample_all.sort_values(by=['datelist'],ascending=True,inplace=True)
        statistic_by_sample_all.to_excel(writer, sheet_name = '按次')
        daily_data = statistic_by_day[['滚动5日基础收益率(扣除成本)','滚动5日收益率(扣除成本)','累计盈亏(扣除成本)']].copy()#,'基础收益率(扣除成本)','收益率(扣除成本)',
        statistic_by_day.to_excel(writer, sheet_name='按日统计')
        daily_data.to_excel(writer, sheet_name = '按日')
        statistic_by_day_valid.to_excel(writer, sheet_name = '样本内按日')
        totalResDf_monthly.to_excel(writer, sheet_name = '模型结果')
        totalResDf_monthly_without_extreme.to_excel(writer, sheet_name = '极值处理模型结果')
        #totalResDf_only_extreme.to_excel(writer, sheet_name = '极值部分模型结果')
        group_proba_all_without_extreme.to_excel(writer, sheet_name = '预测值分层统计')
        model_valid_mingan.to_excel(writer, sheet_name='极值处理不同参与率表现')
        model_mingan.to_excel(writer, sheet_name = '不同参与率表现')
        writer.save()
        return totalResDf_monthly, daily_data,statistic_by_sample_all.set_index(['datelist','stockID']),statistic_by_day_valid,model_mingan,model_valid_mingan,group_proba_all_without_extreme,totalResDf_monthly_without_extreme
    def fun_statistic_by_day(self,start_date, end_date, by_samples,pred_out):
        by_sample = by_samples.reset_index().copy()

        cols = list(set(by_sample.columns.tolist())-set(['stockID','Indexs']))
        by_sample[cols] = by_sample[cols].astype(float)
        by_sample['datelist'] = by_sample['datelist'].astype(int)
        date_index = [ int(i) for i in hfactor.tradingday(str(start_date), str(end_date))]

        by_sample.rename(columns = {'label_pct':'收益率','label_buy_amt':'投资金额','label_profit':'盈亏金额','ZT_Time':'突破时间'},inplace= True)
        if 'label_profit' not in by_sample.columns.tolist():
            by_sample['盈亏金额'] = by_sample['收益率']*by_sample['投资金额']

        by_sample['单日累计投资金额'] = 0
        by_sample['盈亏金额(扣除成本)'] = (by_sample['收益率(扣除成本)'] * by_sample['投资金额'])

        for date in by_sample.datelist.unique().tolist():
            by_day_temp = by_sample.query('datelist == ' + str(date))
            by_day_temp['单日累计投资金额'] = by_day_temp['投资金额'].cumsum()
            by_sample.loc[by_day_temp.index, '单日累计投资金额'] = by_day_temp['单日累计投资金额']

        by_day = pd.DataFrame(index=date_index)
        by_day['标的数量'] = by_sample[by_sample['投资金额']>0].reset_index().groupby('datelist').count()['stockID']

        by_day['触发样本数'] = pred_out.groupby('datelist').count()['stockID'].loc[pred_out.groupby('datelist').count()['stockID'].index.intersection(by_day.index)]

        by_day['参与率'] = by_day['标的数量']/by_day['触发样本数']
        by_day['基础收益(扣除成本)'] = pred_out.groupby('datelist').mean()['label_profit_cost'].reindex(by_day.index)
        #by_day['基础收益率(扣除成本)'] = (pred_out.groupby('datelist').sum()['label_profit_cost'].reindex(by_day.index).fillna(0))/(pred_out.groupby('datelist').sum()['label_buy_amt'].reindex(by_day.index).fillna(0))
        by_day['5日基础收益率'] = (pred_out.groupby('datelist').sum()['label_pct_cost'].reindex(by_day.index).fillna(0)).rolling(5,5).sum()
        by_day['5日基础数量'] = (pred_out.groupby('datelist').count()['stockID'].reindex(by_day.index).fillna(0)).rolling(5,5).sum()
        #by_day['5日基础数量'] = by_day['5日基础数量'].replace([np.inf, -np.inf,0], np.nan)#.fillna(0)
        by_day['滚动5日基础收益率(扣除成本)'] = (by_day['5日基础收益率'].reindex(by_day.index).fillna(0) /(1+by_day['5日基础数量'].reindex(by_day.index).fillna(0))).fillna(0)
        by_day['滚动5日基础收益率(扣除成本)'] = by_day['滚动5日基础收益率(扣除成本)'].replace([np.inf, -np.inf], np.nan).fillna(0)
        by_day = by_day.join(by_sample[by_sample['投资金额']>0].reset_index().groupby('datelist').sum()[['投资金额', '盈亏金额','盈亏金额(扣除成本)']])
        by_day['收益率'] = by_day['盈亏金额'] / by_day['投资金额']
        by_day['收益率(扣除成本)'] = by_day['盈亏金额(扣除成本)']/ by_day['投资金额']
        by_day['滚动5日收益率(扣除成本)'] = ((by_sample.groupby('datelist').sum()['收益率(扣除成本)'].reindex(by_day.index).fillna(0)).rolling(5,5).sum() / (1+by_sample.groupby('datelist').count()['stockID'].reindex(by_day.index).fillna(0)).rolling(5,5).sum()).fillna(0)
        by_day['滚动5日收益率(扣除成本)'] = by_day['滚动5日收益率(扣除成本)'].replace([np.inf, -np.inf], np.nan).fillna(0)
        by_day['累计盈亏(扣除成本)'] = by_day['盈亏金额(扣除成本)'].fillna(0).cumsum()
        by_day['基础累计盈亏(扣除成本)'] = by_day['基础收益(扣除成本)'].fillna(0).cumsum()
        by_day['单日最大回撤金额'] = self.cal_ts_abs_max_down(by_day['盈亏金额(扣除成本)'])
        by_sample.set_index(['Indexs'],inplace=True)
        return by_day.fillna(0), by_sample.fillna(0)
    def fun_statistic_by_day_valid(self,by_samples):
        by_sample = by_samples.reset_index().copy()
        cols = list(set(by_sample.columns.tolist())-set(['stockID','Indexs','jup_dt','sell_dt','Ticker','dt']))
        by_sample[cols] = by_sample[cols].astype(float)
        by_sample['datelist'] = by_sample['datelist'].astype(int)
        start_date, end_date = self.in_begindate, self.in_enddate#20160101, 20190930
        by_sample = by_sample.query('datelist>=%d and datelist<=%d'%(start_date, end_date))
        date_index = [ int(i) for i in hfactor.tradingday(str(start_date), str(end_date))]

        by_day = pd.DataFrame(index=date_index)
        by_day = by_day.join(by_sample.reset_index().groupby('datelist').sum()[['label_profit_cost']]).reindex(date_index)
        by_day['累计盈亏(扣除成本)'] = by_day['label_profit_cost'].fillna(0).cumsum()
        return by_day[['累计盈亏(扣除成本)']].fillna(0)

    def cal_model_mingan(self,sel_raw_data,factor,step=1):
        group_ratio_indi = list(range(self.attend_min,self.attend_max,step))
        plot_data = pd.DataFrame(index = group_ratio_indi)
        sel_data = sel_raw_data.sort_values(by=factor, ascending = False)
        totalnum = sel_data.shape[0]
        sel_data['group_id'] = 0
        if self.indi_str.find('scene')<0:
            #group_size = int(np.floor(sel_data.shape[0] / group_num))
            group_indicator = []
            for group_indi_str in plot_data.index.tolist():
                ratio_num = math.ceil(totalnum * group_indi_str / 100)
                if group_indi_str == self.attend_min:
                    tmp_num = ratio_num
                elif ratio_num >= totalnum:
                    tmp_num = totalnum - math.ceil(totalnum * (group_indi_str-1)/100)
                else :
                    tmp_num = ratio_num - math.ceil(totalnum * (group_indi_str-1)/100)

                group_indicator = group_indicator + tmp_num * [group_indi_str]
            group_indicator = group_indicator + (totalnum-len(group_indicator)) * [group_indi_str+1]
            sel_data['group_id'] = group_indicator
            #print(sel_data.group_id.value_counts().sort_index())
            sel_data.rename(columns = {'收益率':'label_pct','投资金额':'label_buy_amt'},inplace = True)
            if 'label_pct' not in sel_data.columns.tolist():
                sel_data['label_pct'] = sel_data['收益率']
            if 'label_profit_cost' not in sel_data.columns.tolist():
                sel_data['label_profit_cost'] = (sel_data['label_pct'] - self.cost_pct)*sel_data['label_buy_amt']
            if 'label_binary_v2o10' not in sel_data.columns.tolist():
                sel_data['label_binary_v2o10'] = sel_data.apply(lambda x: 1 if x[self.label_rev]>=self.cost_pct else 0,axis=1)
            if 'label_binary_pctcost' not in sel_data.columns.tolist():
                sel_data['label_binary_pctcost'] = sel_data.apply(lambda x: 1 if x['label_pct']>=self.cost_pct else 0,axis=1)
                sel_data['label_binary_highpctcost'] = sel_data.apply(
                    lambda x: 1 if x['label_pct'] >= self.cost_pct + 0.1 else 0, axis=1)
                sel_data['label_binary_lowpctcost'] = sel_data.apply(
                    lambda x: 1 if x['label_pct'] < -0.1 + self.cost_pct else 0, axis=1)
            tot_dt = [int(x) for x in hfactor.tradingday(str(self.in_begindate), str(self.in_enddate))]

            for group_indi_str in plot_data.index.tolist():
                group_df = sel_data.query('group_id<=%s'%str(group_indi_str))
                group_df_daily = group_df.groupby('datelist').sum()[['label_profit_cost']].reindex(tot_dt).fillna(0)
                plot_data.loc[group_indi_str, '实际参与率'] = round(len(group_df)/totalnum,4)
                plot_data.loc[group_indi_str,'因子值范围'] = str(round(float(group_df.min()[factor]), 6))
                plot_data.loc[group_indi_str,'扣费收益率胜率'] = round(group_df['label_binary_pctcost'].mean(),4)
                plot_data.loc[group_indi_str, '扣费收益率'] = round(group_df['label_pct_cost'].mean(), 4)
                plot_data.loc[group_indi_str, '扣费收益率中位数'] = round(group_df['label_pct_cost'].median(), 4)
                plot_data.loc[group_indi_str,'累计盈利'] = int(group_df.sum()['label_profit_cost'])
                plot_data.loc[group_indi_str, '最大回撤'] = int(self.cal_abs_max_drawdown(group_df_daily['label_profit_cost'].cumsum()))
                plot_data.loc[group_indi_str, '收益风险比'] = round(plot_data.loc[group_indi_str,'累计盈利']/abs(plot_data.loc[group_indi_str, '最大回撤']),4)#round(abs(plot_data.loc[group_indi_str,'累计盈利']/plot_data.loc[group_indi_str, '最大回撤']),4)
                group_df_daily['单日最大回撤金额'] = (self.cal_ts_abs_max_down(group_df_daily['label_profit_cost'])).astype(int)
                plot_data.loc[group_indi_str, '平均最大回撤'] = int(group_df_daily['单日最大回撤金额'].mean())
                plot_data.loc[group_indi_str, '夏普比率'] = round(self.cal_sharp(group_df),4)
                plot_data.loc[group_indi_str, '收益夏普比率'] = round(self.cal_sharp(group_df,'盈亏金额(扣除成本)'), 4)
                plot_data.loc[group_indi_str, '高收益率参与率'] = round(group_df['label_binary_highpctcost'].mean(), 4)
                plot_data.loc[group_indi_str, '低收益率参与率'] = round(group_df['label_binary_lowpctcost'].mean(), 4)

            plot_data.set_index(['因子值范围'],inplace=True)
            plot_data.reset_index().to_pickle(self.FilesavePath+'%s_out.pkl'%self.indi_str)
        else:
            plot_data = pd.DataFrame()

        return plot_data

    def cal_model_mingan_basedout(self,sel_raw_data,factor):

        sel_data = sel_raw_data.sort_values(by=factor, ascending = False)

        if self.indi_str.find('scene')<0:
            group_ratio_indi = pd.read_pickle(self.FilesavePath + '%s_out.pkl' % self.indi_str)['因子值范围'].astype(str).tolist()
            plot_data = pd.DataFrame(index=group_ratio_indi)
            sel_data.rename(columns = {'收益率':'label_pct','投资金额':'label_buy_amt'},inplace = True)
            if 'label_pct' not in sel_data.columns.tolist():
                sel_data['label_pct'] = sel_data['收益率']
            if 'label_profit_cost' not in sel_data.columns.tolist():
                sel_data['label_profit_cost'] = (sel_data['label_pct'] - self.cost_pct)*sel_data['label_buy_amt']
            if 'label_binary_v2o10' not in sel_data.columns.tolist():
                sel_data['label_binary_v2o10'] = sel_data.apply(lambda x: 1 if x[self.label_rev]>=self.cost_pct else 0,axis=1)
            if 'label_binary_pctcost' not in sel_data.columns.tolist():
                sel_data['label_binary_pctcost'] = sel_data.apply(lambda x: 1 if x['label_pct']>=self.cost_pct else 0,axis=1)
                sel_data['label_binary_highpctcost'] = sel_data.apply(lambda x: 1 if x['label_pct']>=self.cost_pct+0.1 else 0,axis=1)
                sel_data['label_binary_lowpctcost'] = sel_data.apply(
                    lambda x: 1 if x['label_pct'] < -0.1+self.cost_pct else 0, axis=1)
            tot_dt = [int(x) for x in hfactor.tradingday(str(self.begindate),str(self.enddate))]
            for group_indi_str in plot_data.index.tolist():
                group_df = sel_data.query('%s>=%s'%(factor,str(group_indi_str)))
                group_df_daily = group_df.groupby('datelist').sum()[['label_profit_cost']].reindex(tot_dt).fillna(0)
                plot_data.loc[group_indi_str,'实际参与率'] = round(len(group_df)/len(sel_data),4)
                plot_data.loc[group_indi_str,'因子值范围'] = group_indi_str# + '~' + str(round(float(group_df.max()[factor]), 4))
                plot_data.loc[group_indi_str,'扣费收益率胜率'] = round(group_df['label_binary_pctcost'].mean(),4)
                plot_data.loc[group_indi_str, '扣费收益率'] = round(group_df['label_pct_cost'].mean(), 4)
                plot_data.loc[group_indi_str, '扣费收益率中位数'] = round(group_df['label_pct_cost'].median(), 4)
                plot_data.loc[group_indi_str,'累计盈利'] = int(group_df.sum()['label_profit_cost'])
                plot_data.loc[group_indi_str, '最大回撤'] = int(self.cal_abs_max_drawdown(group_df_daily['label_profit_cost'].cumsum()))
                plot_data.loc[group_indi_str, '收益风险比'] = round(plot_data.loc[group_indi_str,'累计盈利']/abs(plot_data.loc[group_indi_str, '最大回撤']),4)
                group_df_daily['单日最大回撤金额'] = (self.cal_ts_abs_max_down(group_df_daily['label_profit_cost'])).astype(int)
                plot_data.loc[group_indi_str, '平均最大回撤'] = int(group_df_daily['单日最大回撤金额'].mean())
                plot_data.loc[group_indi_str, '夏普比率'] = round(self.cal_sharp(group_df),4)
                plot_data.loc[group_indi_str, '收益夏普比率'] = round(self.cal_sharp(group_df,'盈亏金额(扣除成本)'), 4)
                plot_data.loc[group_indi_str, '高收益率参与率'] = round(group_df['label_binary_highpctcost'].mean(),4)
                plot_data.loc[group_indi_str, '低收益率参与率'] = round(group_df['label_binary_lowpctcost'].mean(), 4)

            plot_data.set_index(['因子值范围'],inplace=True)
        else:
            plot_data = pd.DataFrame()

        return plot_data

    #用正负20%替换极端值
    def remove_extreme_value(self,data, by, zero = '总投资金额'):
        rawdata = data.copy()
        thres = self.extreme_thres
        rawdata['Flag_is_extreme'] = 0
        if rawdata[by][rawdata[by].abs() >thres ].shape[0] > 0:
            rawdata['Flag_is_extreme'][rawdata[by].abs() > thres] = 1
            rawdata[by][rawdata[by] >thres] = thres
            rawdata[by][rawdata[by] <-thres] = -thres


        rawdata['盈亏金额(扣除成本)'] = rawdata[by] * rawdata[zero]
        rawdata['label_profit_cost'] = rawdata[by] * rawdata[zero]
        return rawdata
    def cal_abs_max_drawdown(self,data_list):
        data_list = list(data_list)
        abs_max_down = 100000
        if data_list[0]<0:
            data_list.insert(0, 0)
        for i in range(len(data_list)-1):
            for j in range(i, len(data_list)):
                abs_max_down = min(abs_max_down, data_list[j] - data_list[i])
        return abs_max_down
    def cal_ts_abs_max_down(self,data_list):
        ret = pd.Series(index=data_list.index)
        ret_index = ret.index.tolist()
        data_sum_lst = data_list.fillna(0).cumsum()
        for i in range(len(data_sum_lst)-1):
            abs_max_down = 0
            for j in range(i, len(data_sum_lst)):
                abs_max_down = min(abs_max_down, data_sum_lst.iloc[j] - data_sum_lst.iloc[i])
            ret.loc[ret_index[i]] = abs_max_down
        ret.loc[ret_index[-1]] = 0
        return ret

    def cal_sharp(self,day_data,pct_col='收益率(扣除成本)',stepdate=3):
        tot_dt = [int(x) for x in hfactor.tradingday(int(day_data['datelist'].min()),int(day_data['datelist'].max()))]
        if '投资金额' not in day_data.columns.tolist():
            day_data['投资金额'] = day_data['label_buy_amt'].tolist()
            day_data['盈亏金额'] = day_data['label_profit'].tolist()
            day_data['盈亏金额(扣除成本)'] = day_data['label_profit_cost'].tolist()
        daily_data = day_data.groupby('datelist').sum()[['投资金额', '盈亏金额','盈亏金额(扣除成本)']].reindex(tot_dt)
        daily_data['近%s日盈亏金额(扣除成本)' % str(stepdate)] = daily_data['盈亏金额(扣除成本)'].rolling(stepdate,1).sum()
        daily_data['近%s日投资金额' % str(stepdate)] = daily_data['投资金额'].rolling(stepdate, 1).sum()
        daily_data['收益率(扣除成本)'] = daily_data['近%s日盈亏金额(扣除成本)' % str(stepdate)] / daily_data['近%s日投资金额' % str(stepdate)]
        daily_data['滚动%s日盈亏金额(扣除成本)' % str(stepdate)] = daily_data['盈亏金额(扣除成本)'].rolling(stepdate, 1).mean()
        #if pct_col == '收益率(扣除成本)':
        daily_data['投资金额'] = daily_data['近%s日投资金额' % str(stepdate)].tolist()
        if pct_col=='盈亏金额(扣除成本)':
            daily_data['盈亏金额(扣除成本)'] = daily_data['近%s日盈亏金额(扣除成本)' % str(stepdate)].tolist()
        daily_data = daily_data.fillna(0)
        ret_data = daily_data.copy()#[[pct_col,'投资金额']].rolling(stepdate,1).mean()
        mean_ret = float(ret_data[ret_data['投资金额'] > 0][pct_col].mean())
        std_ret = float(ret_data[ret_data['投资金额'] > 0][pct_col].std())
        sharp = 0 if std_ret==0 else (mean_ret/std_ret)* math.sqrt(250)#abs(mean_ret / std_ret) * math.sqrt(250)
        if pct_col == '盈亏金额(扣除成本)':
            sharp = 0 if std_ret==0 else (mean_ret/std_ret)* math.sqrt(250/stepdate)#abs(mean_ret / std_ret) * math.sqrt(250)
        return sharp
    def cal_sortino(self,day_data,pct_col='收益率(扣除成本)',stepdate=3):
        tot_dt = [int(x) for x in hfactor.tradingday(int(day_data['datelist'].min()),int(day_data['datelist'].max()))]
        if '投资金额' not in day_data.columns.tolist():
            day_data['投资金额'] = day_data['label_buy_amt'].tolist()
            day_data['盈亏金额'] = day_data['label_profit'].tolist()
            day_data['盈亏金额(扣除成本)'] = day_data['label_profit_cost'].tolist()
        daily_data = day_data.groupby('datelist').sum()[['投资金额', '盈亏金额','盈亏金额(扣除成本)']].reindex(tot_dt)
        daily_data['近%s日盈亏金额(扣除成本)' % str(stepdate)] = daily_data['盈亏金额(扣除成本)'].rolling(stepdate,1).sum()
        daily_data['近%s日投资金额' % str(stepdate)] = daily_data['投资金额'].rolling(stepdate, 1).sum()
        daily_data['收益率(扣除成本)'] = daily_data['近%s日盈亏金额(扣除成本)' % str(stepdate)] / daily_data['近%s日投资金额' % str(stepdate)]
        daily_data['滚动%s日盈亏金额(扣除成本)' % str(stepdate)] = daily_data['盈亏金额(扣除成本)'].rolling(stepdate, 1).mean()
        if pct_col == '收益率(扣除成本)':
            daily_data['投资金额'] = daily_data['近%s日投资金额' % str(stepdate)].tolist()

        daily_data = daily_data.fillna(0)
        ret_data = daily_data.copy()#[[pct_col,'投资金额']].rolling(stepdate,1).mean()
        mean_ret = float(ret_data[ret_data['投资金额'] > 0][pct_col].mean())
        std_ret = float(ret_data[(ret_data['投资金额'] > 0)&(ret_data[pct_col]<0)][pct_col].std())
        sortino = 0 if std_ret == 0 else abs(mean_ret / std_ret) * math.sqrt(250)

        return sortino
    def generate_date_group(self,start_date, end_date, stepdate=40):
        date_index = [int(i) for i in hfactor.tradingday(str(start_date), str(end_date))]
        mid_date = []
        for idx in range(len(date_index)-1):
            if (idx//stepdate>0)&(idx%stepdate==0):
                mid_date.append(date_index[idx])
            else:
                pass

        minList = [date_index[0]] + mid_date
        maxList = mid_date + [date_index[-1]]
        if len(hfactor.tradingday(minList[-1],maxList[-1]))<=25:
            minList = minList[:-1]# + minList[-1:]
            maxList = maxList[:-2] + maxList[-1:]
        return minList, maxList
    def generate_rolldate_group(self,start_date, end_date, stepdate):
        date_index = [int(i) for i in hfactor.tradingday(str(start_date), str(end_date))]

        start_date = []
        end_date = []
        for idx in range(len(date_index)-stepdate):
            start_date.append(date_index[idx])
            end_date.append(date_index[idx+stepdate])

        return start_date, end_date
    def combine_res_inout(self,pred_sample_data,sample_data,statistic_without_extreme_value,statistic_by_sample,statistic_by_day,pred_in,flag_scene,proba_col):
        pred_sample_data['盈亏金额(扣除成本)'] = statistic_by_sample['盈亏金额(扣除成本)']

        if 'label_zuhe' not in pred_sample_data.columns.tolist() and (self.strategy in ['JupiterN','Europa','Sapphire','jupiter003','JupiterNSell','JupiterNSell34','JupiterZ','EuropaSell','EuropaSellEnhance'] or self.strategy.find('JupiterZSell')>=0):
            pred_sample_data['label_zuhe'] = pred_sample_data.apply(lambda x: 1 if x[self.label_rev] >= 0 and x[self.label_o2o10] >= 3 else 0, axis=1)
        else:
            pred_sample_data['label_zuhe'] = pred_sample_data.apply(lambda x: 1 if x[self.label_rev] >= self.cost_pct else 0, axis=1)
        if 'label_pat_zuhe' not in pred_sample_data.columns.tolist() and (self.strategy in ['JupiterN','Europa','Sapphire','jupiter003','JupiterNSell','JupiterNSell34','JupiterZ','EuropaSell','EuropaSellEnhance']  or self.strategy.find('JupiterZSell')>=0):
            pred_sample_data['label_pat_zuhe'] = pred_sample_data.apply(lambda x: 1 if x[self.label_o2o10] >= 4 and x[self.label_rev] >= 0 else 0, axis=1)
        if 'pred' not in pred_sample_data.columns.tolist():
            if 'pred_label' in pred_sample_data.columns.tolist():
                pred_sample_data['pred'] = pred_sample_data['pred_label']
            else:
                pred_sample_data['pred'] = pred_sample_data['prediction']
        valid_cumpct = pred_in.query('prediction==1').label_pct_cost.sum()
        [prec_score,rec_score,o2ul_mean,N5resDf,res_df] = self.cal_basicEval(pred_sample_data.query('label_buy_amt>0').copy())

        prec_profit = 0 if statistic_by_sample[(statistic_by_sample['投资金额'] >0)].shape[0]==0 else statistic_by_sample[(statistic_by_sample['投资金额'] >0)&(statistic_by_sample['收益率(扣除成本)'] >0)].shape[0]/statistic_by_sample[(statistic_by_sample['投资金额'] >0)].shape[0]

        ykb = 0 if statistic_by_sample[statistic_by_sample['盈亏金额(扣除成本)']<=0]['收益率(扣除成本)'].mean()==0 else statistic_by_sample[statistic_by_sample['盈亏金额(扣除成本)']>0]['收益率(扣除成本)'].mean()/abs(statistic_by_sample[statistic_by_sample['盈亏金额(扣除成本)']<=0]['收益率(扣除成本)'].mean())
        sharp = self.cal_sharp(statistic_by_sample)
        rev_sharp = self.cal_sharp(statistic_by_sample,'盈亏金额(扣除成本)')
        sortino = self.cal_sortino(statistic_by_sample)
        totalResDf = pd.DataFrame(columns=['模型表现'])

        totalResDf.loc['累计交易日'] = len(pred_sample_data['datelist'].unique())
        totalResDf.loc['基础样本数量'] = pred_sample_data.shape[0]
        if self.strategy in ['JupiterN','Europa','Sapphire','jupiter003','JupiterNSell','JupiterNSell34','JupiterZ','EuropaSell','EuropaSellEnhance'] or self.strategy.find('JupiterZSell')>=0:
            [prec_score, rec_score, o2ul_mean, N5resDf, prec_pat, rec_pat, res_df, pat2_ratio, pat3_ratio, pat4_ratio,
             pat2_o2ul, pat3_o2ul, pat4_o2ul, pat3_posratio, pat4_posratio] = self.cal_basicEval_jup(
                pred_sample_data.query('label_buy_amt>0').copy())
            [pct_mean, pct_t_mean, pct_t1_mean] = statistic_by_sample[(statistic_by_sample['投资金额'] > 0)][
                ['收益率(扣除成本)', 'T日收益率', 'T+1日收益率']].mean().values.tolist()
            totalResDf.loc['基础o2ul均值'] = pred_sample_data[self.label_rev].mean()
            totalResDf.loc['基础形态4占比'] = pred_sample_data.query('label_pattern==4').shape[0] / totalResDf.loc['基础样本数量']
            totalResDf.loc['基础形态3占比'] = pred_sample_data.query('label_pattern==3').shape[0] / totalResDf.loc['基础样本数量']
            totalResDf.loc['基础形态2占比'] = pred_sample_data.query('label_pattern==2').shape[0] / totalResDf.loc['基础样本数量']
            totalResDf.loc['基础组合标签为正占比'] = pred_sample_data.query('label_zuhe==1').shape[0] / \
                                           totalResDf.loc['基础样本数量']
            totalResDf.loc['基础二连板占比'] = pred_sample_data.query('label_T_is_zt==1 and label_T1_is_zt==1').shape[0] / \
                                        totalResDf.loc['基础样本数量']
            totalResDf.loc['组合标签胜率'] = prec_score

            totalResDf.loc['扣费后收益率胜率'] = prec_profit
            totalResDf.loc['样本参与率'] = pred_sample_data.query('prediction==1').shape[0] / totalResDf.loc['基础样本数量']
            totalResDf.loc['组合标签召回率'] = rec_score
            totalResDf.loc['5日胜率均值/标准差'] = N5resDf.loc['p_score_N5']
            totalResDf.loc['5日召回率均值/标准差'] = N5resDf.loc['r_score_N5']

            totalResDf.loc['形态2占比'] = pat2_ratio
            totalResDf.loc['形态2的o2ul均值'] = pat2_o2ul
            totalResDf.loc['形态3占比'] = pat3_ratio
            totalResDf.loc['形态3的o2ul均值'] = pat3_o2ul
            totalResDf.loc['形态3中o2ul为正占比'] = pat3_posratio
            totalResDf.loc['形态4占比'] = pat4_ratio
            totalResDf.loc['形态4的o2ul均值'] = pat4_o2ul
            totalResDf.loc['形态4中o2ul为正占比'] = pat4_posratio
            totalResDf.loc['o2ul均值'] = statistic_by_sample[statistic_by_sample['投资金额']>0]['o2ul收益率'].mean()
            totalResDf.loc['o2ul中位数'] = np.median(statistic_by_sample[statistic_by_sample['投资金额']>0]['o2ul收益率'])
            totalResDf.loc['收益率均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['收益率(扣除成本)'].mean()
            totalResDf.loc['收益率中位数'] = np.median(statistic_by_sample[statistic_by_sample['投资金额']>0]['收益率(扣除成本)'])
            amt_weights = list(statistic_by_sample[statistic_by_sample['投资金额'] > 0]['投资金额'])
            totalResDf.loc['次均规模加权收益率'] = np.average(statistic_by_sample[statistic_by_sample['投资金额'] > 0]['收益率(扣除成本)'],
                                                     weights=amt_weights)
            totalResDf.loc['次均买入当日收益率'] = pct_t_mean
            totalResDf.loc['次均卖出当日收益率'] = pct_t1_mean
            totalResDf.loc['高收益占比'] = \
            statistic_by_sample[(statistic_by_sample['投资金额'] > 0) & (statistic_by_sample['收益率(扣除成本)'] > 0.08)].shape[
                0] / statistic_by_sample[(statistic_by_sample['投资金额'] > 0)].shape[0]
            totalResDf.loc['低收益占比'] = \
            statistic_by_sample[(statistic_by_sample['投资金额'] > 0) & (statistic_by_sample['收益率(扣除成本)'] < -0.08)].shape[
                0] / statistic_by_sample[(statistic_by_sample['投资金额'] > 0)].shape[0]
            totalResDf.loc['二连板占比'] = statistic_by_sample[
                                          (statistic_by_sample['投资金额'] > 0) & (statistic_by_sample['是否T日收盘涨停'] == 1) & (
                                                      statistic_by_sample['是否T+1日收盘涨停'] == 1)].shape[0] / \
                                      statistic_by_sample[(statistic_by_sample['投资金额'] > 0)].shape[0]

            totalResDf.loc['收益率标准差'] = statistic_by_sample[(statistic_by_sample['投资金额'] > 0)]['收益率(扣除成本)'].std()
            o2ul_ykb = statistic_by_sample[(statistic_by_sample['盈亏金额(扣除成本)'] > 0)]['o2ul收益率'].mean() / abs(statistic_by_sample[(statistic_by_sample['盈亏金额(扣除成本)'] <= 0)]['o2ul收益率'].mean())

            totalResDf.loc['o2ul盈亏比'] = o2ul_ykb
            totalResDf.loc['收益率盈亏比'] = ykb

            totalResDf.loc['实际参与交易日'] = len(statistic_by_day[statistic_by_day['投资金额'] > 0])
            totalResDf.loc['成交比例'] = len(statistic_by_sample[statistic_by_sample['投资金额'] > 0]) / len(statistic_by_sample)
            totalResDf.loc['实际参与次数'] = len(statistic_by_sample[statistic_by_sample['投资金额'] > 0])
            totalResDf.loc['次均参与资金规模'] = int(statistic_by_sample['投资金额'][statistic_by_sample['投资金额'] > 0].mean())
            totalResDf.loc['日均参与资金规模'] = int(sum(statistic_by_day[statistic_by_day['投资金额'] > 0]['投资金额']) / len(
                pred_sample_data['datelist'].unique()))
            totalResDf.loc['最大参与资金规模'] = int(np.max(statistic_by_day['投资金额']))
            totalResDf.loc['累计扣费总收益'] = int(sum(statistic_by_sample[statistic_by_sample['投资金额'] > 0]['盈亏金额(扣除成本)']))

            totalResDf.loc['累计扣费总收益(极端值调整后)'] = int(statistic_without_extreme_value['盈亏金额(扣除成本)'].sum())
            totalResDf.loc['最大回撤'] = int(self.cal_abs_max_drawdown(statistic_by_day['盈亏金额(扣除成本)'].cumsum()))

            totalResDf.loc['平均最大回撤'] = int(statistic_by_day['单日最大回撤金额'].mean())
            totalResDf.loc['收益风险比'] = 99 if float(totalResDf.loc['最大回撤'])==0 else totalResDf.loc['累计扣费总收益'] / np.abs(totalResDf.loc['最大回撤'])
            totalResDf.loc['夏普比率'] = sharp
            totalResDf.loc['收益夏普比率'] = rev_sharp
            totalResDf.loc['索提诺比率'] = sortino
            totalResDf.loc['未参与数量'] = statistic_by_sample[(statistic_by_sample['投资金额'] == 0)].shape[0]  # result.loc['理想累计次数'] - result.loc['实际参与次数']
            totalResDf.loc['未参与胜率'] = 0 if int(totalResDf.loc['未参与数量'])==0 else statistic_by_sample[(statistic_by_sample['投资金额'] == 0) & (
                        statistic_by_sample['是否T日收盘涨停'] == 1) & (statistic_by_sample['o2ul收益率'] >= 0)].shape[0] / totalResDf.loc['未参与数量']
            totalResDf.loc['未参与o2ul均值'] = 0 if int(totalResDf.loc['未参与数量'])==0 else statistic_by_sample[(statistic_by_sample['投资金额'] == 0)]['o2ul收益率'].mean()
            totalResDf.loc['未参与o2ul中位数'] = 0 if int(totalResDf.loc['未参与数量'])==0 else np.median(statistic_by_sample[(statistic_by_sample['投资金额'] == 0)]['o2ul收益率'])
            totalResDf.loc['未参与收益率均值'] = 0 if int(totalResDf.loc['未参与数量'])==0 else statistic_by_sample[(statistic_by_sample['投资金额'] == 0)]['收益率(扣除成本)'].mean()
            totalResDf.loc['未参与收益率中位数'] = 0 if int(totalResDf.loc['未参与数量'])==0 else np.median(
                statistic_by_sample[(statistic_by_sample['投资金额'] == 0)]['收益率(扣除成本)'])
        else:

            totalResDf.loc['基础v2o10均值'] = pred_sample_data[self.label_rev].mean()
            totalResDf.loc['基础o2o10均值'] = pred_sample_data[self.label_o2o10].mean()
            totalResDf.loc['基础o2Tc均值'] = pred_sample_data.label_TNo2Tc.mean()
            totalResDf.loc['基础Tc2o10均值'] = pred_sample_data[self.label_Tc2To10].mean()
            totalResDf.loc['基础样本胜率'] = pred_sample_data.query('label_v2o10>=%s' % str(self.cost_pct)).shape[0] / totalResDf.loc['基础样本数量']
            if self.strategy in ['Saturn','Saturn_down']:
                totalResDf.loc['基础样本胜率'] = pred_sample_data.query('label_pct_cost>=%s' % str(self.cost_pct)).shape[0] / totalResDf.loc['基础样本数量']
            totalResDf.loc['基础二连板占比'] = pred_sample_data.query('label_T_close_is_zt==1').shape[0]/totalResDf.loc['基础样本数量']
            #totalResDf.loc['验证集累计收益率'] = valid_cumpct
            totalResDf.loc['扣费收益率胜率'] = prec_profit
            totalResDf.loc['v2o10胜率'] = prec_score
            totalResDf.loc['样本参与率'] = pred_sample_data.query('prediction==1').shape[0]/totalResDf.loc['基础样本数量']
            totalResDf.loc['v2o10召回率'] = rec_score

            totalResDf.loc['5日胜率均值/标准差'] = N5resDf.loc['p_score_N5']
            totalResDf.loc['5日召回率均值/标准差'] = N5resDf.loc['r_score_N5']

            totalResDf.loc['收益率均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['收益率(扣除成本)'].mean()
            totalResDf.loc['收益率中位数'] = np.median(statistic_by_sample[statistic_by_sample['投资金额']>0]['收益率(扣除成本)'])
            amt_weights = list(statistic_by_sample[statistic_by_sample['投资金额'] > 0]['投资金额'])
            totalResDf.loc['次均规模加权收益率'] = np.average(statistic_by_sample[statistic_by_sample['投资金额']>0]['收益率(扣除成本)'], weights = amt_weights)
            totalResDf.loc['v2o10均值'] = statistic_by_sample[statistic_by_sample['投资金额']>0]['v2o10收益率'].mean()
            totalResDf.loc['v2o10中位数'] = np.median(statistic_by_sample[statistic_by_sample['投资金额']>0]['v2o10收益率'])
            totalResDf.loc['Tv2o均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['Tv2o收益率'].mean()
            totalResDf.loc['Tv2o中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['Tv2o收益率'])
            totalResDf.loc['o2Tc均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['o2Tc收益率'].mean()
            totalResDf.loc['o2Tc中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['o2Tc收益率'])
            totalResDf.loc['Tc2o10均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['Tc2o10收益率'].mean()
            totalResDf.loc['Tc2o10中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['Tc2o10收益率'])
            totalResDf.loc['Tc2o10为正占比'] =  statistic_by_sample[(statistic_by_sample['Tc2o10收益率'] >0)&(statistic_by_sample['投资金额'] >0)].shape[0]/statistic_by_sample[(statistic_by_sample['投资金额'] >0)].shape[0]

            #totalResDf.loc['TNo2To10均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] > 0)]['TNo2To10收益率'].mean()
            #totalResDf.loc['TNo2To10中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] > 0)]['TNo2To10收益率'])

            totalResDf.loc['To102To均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] > 0)]['To102To收益率'].mean()
            totalResDf.loc['To102To中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] > 0)]['To102To收益率'])

            totalResDf.loc['高收益占比'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)&(statistic_by_sample['收益率(扣除成本)']>0.08)].shape[0]/statistic_by_sample[(statistic_by_sample['投资金额'] >0)].shape[0]
            totalResDf.loc['低收益占比'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)&(statistic_by_sample['收益率(扣除成本)']<-0.08)].shape[0]/statistic_by_sample[(statistic_by_sample['投资金额'] >0)].shape[0]
            totalResDf.loc['二连板占比'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)&(statistic_by_sample['是否T日收盘涨停']==1)].shape[0]/statistic_by_sample[(statistic_by_sample['投资金额'] >0)].shape[0]

            totalResDf.loc['收益率标准差'] = statistic_by_sample[(statistic_by_sample['投资金额'] >0)]['收益率(扣除成本)'].std()
            totalResDf.loc['收益率盈亏比'] = ykb

            totalResDf.loc['实际参与交易日'] = len(statistic_by_day[statistic_by_day['投资金额']>0])

            totalResDf.loc['成交比例'] = len(statistic_by_sample[statistic_by_sample['投资金额'] > 0])/len(statistic_by_sample)
            totalResDf.loc['实际参与次数'] = len(statistic_by_sample[statistic_by_sample['投资金额']>0])
            totalResDf.loc['次均参与资金规模'] = int(statistic_by_sample['投资金额'][statistic_by_sample['投资金额']>0].mean())
            totalResDf.loc['日均参与资金规模'] = int(sum(statistic_by_day[statistic_by_day['投资金额']>0]['投资金额'])/len(pred_sample_data['datelist'].unique()))
            totalResDf.loc['最大参与资金规模'] = int(np.max(statistic_by_day['投资金额']))
            totalResDf.loc['累计扣费总收益'] = int(sum(statistic_by_sample[statistic_by_sample['投资金额']>0]['盈亏金额(扣除成本)']))

            totalResDf.loc['累计扣费总收益(极端值调整后)'] = int(statistic_without_extreme_value['盈亏金额(扣除成本)'].sum())
            totalResDf.loc['最大回撤'] = int(self.cal_abs_max_drawdown(statistic_by_day['盈亏金额(扣除成本)'].cumsum()))

            totalResDf.loc['平均最大回撤'] = int(statistic_by_day['单日最大回撤金额'].mean())
            totalResDf.loc['收益风险比'] = 99 if float(totalResDf.loc['最大回撤'])==0 else totalResDf.loc['累计扣费总收益']/np.abs(totalResDf.loc['最大回撤'])
            totalResDf.loc['夏普比率'] = sharp
            totalResDf.loc['收益夏普比率'] = rev_sharp
            totalResDf.loc['索提诺比率'] = sortino
            totalResDf.loc['未参与数量'] = statistic_by_sample[(statistic_by_sample['投资金额'] ==0)].shape[0]
            totalResDf.loc['未参与胜率'] = 0 if statistic_by_sample[(statistic_by_sample['投资金额'] ==0)].shape[0]==0 else float(statistic_by_sample[(statistic_by_sample['投资金额'] ==0)&(statistic_by_sample['v2o10收益率'] >=self.cost_pct)].shape[0]/totalResDf.loc['未参与数量'])
            totalResDf.loc['未参与v2o10均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] ==0)]['v2o10收益率'].mean()
            totalResDf.loc['未参与v2o10中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] ==0)]['v2o10收益率'])
        #    totalResDf.loc['未参与o2o10均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] ==0)]['o2o10收益率'].mean()
        #    totalResDf.loc['未参与o2o10中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] ==0)]['o2o10收益率'])
            totalResDf.loc['未参与收益率均值'] = statistic_by_sample[(statistic_by_sample['投资金额'] ==0)]['收益率(扣除成本)'].mean()
            totalResDf.loc['未参与收益率中位数'] = np.median(statistic_by_sample[(statistic_by_sample['投资金额'] ==0)]['收益率(扣除成本)'])
        proba_stats_all = self.group_pattern_stas(pred_sample_data.sort_values(by=proba_col, ascending=False), proba_col, group_num, '')[['标的数量','v2o10均值','v2o10中位数','v2o10为正占比','扣费收益率均值','扣费收益率中位数','扣费收益率为正占比','group_id']]
        if flag_scene=='':
            proba_stats = self.group_pattern_stas(pred_sample_data.sort_values(by=proba_col,ascending=False).iloc[:int(len(pred_sample_data)*self.group_ratio)],proba_col,group_num,'')
            corrdata_ratio = proba_stats.corr('spearman')
            totalResDf.loc['扣费胜率单调性'] = corrdata_ratio['group_id'].loc['扣费收益率为正占比']
            totalResDf.loc['扣费收益率单调性'] = corrdata_ratio['group_id'].loc['扣费收益率均值']
            #totalResDf.loc['v2o10胜率单调性'] = corrdata_ratio['group_id'].loc['v2o10为正占比']
            #totalResDf.loc['v2o10单调性'] = corrdata_ratio['group_id'].loc['v2o10均值']
            #totalResDf.loc['等比例扣费中位数单调性'] = corrdata_ratio['group_id'].loc['v2o10中位数']
        else:
            proba_stats_high = self.group_pattern_stas(pred_sample_data.query('%s==1'%flag_scene).sort_values(by=proba_col,ascending=False).iloc[:int(len(pred_sample_data.query('%s==1'%flag_scene))*self.group_ratio)],proba_col,group_num,'')
            proba_stats_low = self.group_pattern_stas(pred_sample_data.query('%s==0'%flag_scene).sort_values(by=proba_col,ascending=False).iloc[:int(len(pred_sample_data.query('%s==0'%flag_scene))*self.group_ratio)],proba_col,group_num,'')
            corrdata_high = proba_stats_high.corr('spearman')
            corrdata_low = proba_stats_low.corr('spearman')
            num_pd1 = pd.DataFrame(index=['%s=1'%flag_scene],columns=proba_stats_high.columns.tolist())
            num_pd2 = pd.DataFrame(index=['%s=0'%flag_scene],columns=proba_stats_high.columns.tolist())
            proba_stats = pd.concat([num_pd1,proba_stats_high,num_pd2,proba_stats_low])
            totalResDf.loc['扣费胜率单调性'] = (corrdata_high['group_id'].loc['扣费收益率为正占比']+corrdata_low['group_id'].loc['扣费收益率为正占比'])/2
            totalResDf.loc['扣费收益率单调性'] = (corrdata_high['group_id'].loc['扣费收益率均值']+corrdata_low['group_id'].loc['扣费收益率均值'])/2
            #totalResDf.loc['v2o10胜率单调性'] = (corrdata_high['group_id'].loc['v2o10为正占比'] + corrdata_low['group_id'].loc['v2o10为正占比']) / 2
            #totalResDf.loc['v2o10单调性'] = (corrdata_high['group_id'].loc['v2o10均值'] + corrdata_low['group_id'].loc['v2o10均值']) / 2
            #totalResDf.loc['等比例扣费中位数单调性'] = (corrdata_high['group_id'].loc['v2o10中位数']+corrdata_low['group_id'].loc['v2o10中位数'])/2
        totalResDf.loc['MSE_score'] = mean_squared_error(pred_sample_data.query('label_buy_amt>0')[self.label_rev],pred_sample_data.query('label_buy_amt>0')[self.predcol])##/100
        totalResDf.loc['R2_score'] = r2_score(pred_sample_data.query('label_buy_amt>0')[self.label_rev],pred_sample_data.query('label_buy_amt>0')[self.predcol])#/100
        totalResDf.loc['AUC_score'] = roc_auc_score(pred_sample_data.query('label_buy_amt>0')['label_zuhe'],pred_sample_data.query('label_buy_amt>0')[self.indi_str])
        totalResDf.loc['预测值与标签IC'] = pred_sample_data.query('label_buy_amt>0')[[self.label_name,self.predcol]].corr().loc[self.label_name,self.predcol]#roc_auc_score(pred_sample_data.query('label_buy_amt>0')['label_zuhe'],pred_sample_data.query('label_buy_amt>0')[self.indi_str])
        totalResDf.loc['预测值与标签RankIC'] = pred_sample_data.query('label_buy_amt>0')[[self.label_name, self.predcol]].corr('spearman').loc[self.label_name, self.predcol]  #
        pred_sample_data_half = pred_sample_data.query('label_buy_amt>0').sort_values(by=self.predcol,ascending=False)#.iloc[:int(len(pred_sample_data_half)/2)]
        totalResDf.loc['前50%预测值与标签IC'] = pred_sample_data_half.iloc[:int(len(pred_sample_data_half)/2)][[self.label_name, self.predcol]].corr().loc[self.label_name, self.predcol]  # roc_auc_score(pred_sample_data.query('label_buy_amt>0')['label_zuhe'],pred_sample_data.query('label_buy_amt>0')[self.indi_str])
        #totalResDf.loc['滚动5日收益率增强均值'] = float((statistic_by_day['滚动5日收益率(扣除成本)'].fillna(0)-statistic_by_day['滚动5日基础收益率(扣除成本)'].fillna(0)).fillna(0).mean())
        totalResDf.loc['收益率增强均值(未考虑成交)'] = float(statistic_by_sample['收益率(扣除成本)'].mean()-pred_sample_data.label_pct_cost.mean())
        totalResDf.loc['收益率增强均值(考虑成交)'] = float(statistic_by_sample[statistic_by_sample['投资金额']>0]['收益率(扣除成本)'].mean()-pred_sample_data.label_pct_cost.mean())

        proba_stats_all20 = self.group_pattern_stas(pred_sample_data.sort_values(by=proba_col, ascending=False), proba_col, all_group_num, '')
        corrdata_ratio_all20 = proba_stats_all20.corr('spearman')
        totalResDf.loc['全部扣费胜率单调性'] = corrdata_ratio_all20['group_id'].loc['扣费收益率为正占比']
        totalResDf.loc['全部扣费收益率单调性'] = corrdata_ratio_all20['group_id'].loc['扣费收益率均值']
        format = lambda x: round(x,4)
        totalResDf = totalResDf.applymap(format)
        return totalResDf,proba_stats,pd.DataFrame(),pd.DataFrame(),proba_stats_all
    def cal_basicEval(self,pred_sample_data):
        prec_score,rec_score,o2ul_mean = self.cal_proEval(pred_sample_data)
        grouped = pred_sample_data.groupby('datelist')
        count,dt0,dt1 = 0,0,0
        dfList = []
        resDf = pd.DataFrame(columns=['p_score_N5','r_score_N5','o2ul_mean_N5','profit_score_N5','total_o2ul_mean','pred1_num','total_num','true_num','true_ratio'])
        for dt,group in grouped:
            count += 1
            if count==5:
                dt1 = dt
                dfList.append(group)
                dfN5 = pd.concat(dfList)
                p_score_N5 = precision_score(dfN5['label_zuhe'],dfN5['pred'])
                r_score_N5 = recall_score(dfN5['label_zuhe'],dfN5['pred'])

                o2ul_mean_N5 = dfN5[dfN5['pred']==1]['label_v2o10'].mean()
                profit_score_N5 = dfN5[dfN5['pred']==1]['盈亏金额(扣除成本)'].sum()
                pred1_num = dfN5['pred'].sum()
                index = str(dt0)+'~'+str(dt1)
                resDf.loc[index] = [p_score_N5,r_score_N5,o2ul_mean_N5,profit_score_N5,dfN5['label_v2o10'].mean(),pred1_num,len(dfN5),dfN5['label_zuhe'].sum(),dfN5['label_zuhe'].mean()]
                count = 0
                dfList = []
            elif count==1:
                dt0 = dt
                dfList.append(group)
            else:
                dfList.append(group)

        return prec_score,rec_score,o2ul_mean,resDf.mean()/resDf.std(),resDf

    def cal_basicEval_jup(self,pred_sample_data):
        prec_score, rec_score, o2ul_mean, prec_pat, rec_pat, pat2_ratio, pat3_ratio, pat4_ratio, pat2_o2ul, pat3_o2ul, pat4_o2ul, pat3_posratio, pat4_posratio = self.cal_proEval_jup(
            pred_sample_data)
        grouped = pred_sample_data.groupby('datelist')
        count, dt0, dt1 = 0, 0, 0
        dfList = []
        resDf = pd.DataFrame(
            columns=['p_score_N5', 'r_score_N5', 'p_pat_score_N5', 'r_pat_score_N5', 'o2ul_mean_N5', 'profit_score_N5',
                     'total_o2ul_mean', 'pred1_num', 'total_num', 'true_num', 'true_ratio'])
        for dt, group in grouped:
            count += 1
            if count == 5:
                dt1 = dt
                dfList.append(group)
                dfN5 = pd.concat(dfList)
                p_score_N5 = precision_score(dfN5['label_zuhe'], dfN5['pred'])
                r_score_N5 = recall_score(dfN5['label_zuhe'], dfN5['pred'])
                p_pat_score_N5 = precision_score(dfN5['label_pat_zuhe'], dfN5['pred'])
                r_pat_score_N5 = recall_score(dfN5['label_pat_zuhe'], dfN5['pred'])
                o2ul_mean_N5 = dfN5[dfN5['pred'] == 1]['label_TN_o2ul'].mean()
                profit_score_N5 = dfN5[dfN5['pred'] == 1]['盈亏金额(扣除成本)'].sum()
                pred1_num = dfN5['pred'].sum()
                index = str(dt0) + '~' + str(dt1)
                resDf.loc[index] = [p_score_N5, r_score_N5, p_pat_score_N5, r_pat_score_N5, o2ul_mean_N5,
                                    profit_score_N5, dfN5['label_TN_o2ul'].mean(), pred1_num, len(dfN5),
                                    dfN5['label_zuhe'].sum(), dfN5['label_zuhe'].mean()]
                count = 0
                dfList = []
            elif count == 1:
                dt0 = dt
                dfList.append(group)
            else:
                dfList.append(group)

        return prec_score, rec_score, o2ul_mean, resDf.mean() / resDf.std(), prec_pat, rec_pat, resDf, pat2_ratio, pat3_ratio, pat4_ratio, pat2_o2ul, pat3_o2ul, pat4_o2ul, pat3_posratio, pat4_posratio

    def group_pattern_stas(self,sel_raw_data,factor,group_num,flag_scene):
        plot_data = pd.DataFrame(index = [i + 1 for i in list(range(group_num))])
        sel_data = sel_raw_data.sort_values(by=factor, ascending = True)
        sel_data['group_id'] = 0
        if flag_scene=='':

            group_size = int(np.floor(sel_data.shape[0]/group_num))
            group_indicator = []
            for num in list(range(group_num)):
                if num < group_num - 1:
                    group_indicator = group_indicator + group_size * [num + 1]
                else:
                    group_indicator = group_indicator + (len(sel_data) - (group_num - 1)*group_size) * [num + 1]
            sel_data['group_id'] = group_indicator
        else:
            sel_data_high = sel_raw_data.query('%s==1'%flag_scene).sort_values(by=factor, ascending = True)
            group_size_high = int(np.floor(sel_data_high.shape[0]/group_num))
            group_indicator_high = []
            for num in list(range(group_num)):
                if num < group_num - 1:
                    group_indicator_high = group_indicator_high + group_size_high * [num + 1]
                else:
                    group_indicator_high = group_indicator_high + (len(sel_data_high) - (group_num - 1)*group_size_high) * [num + 1]
            sel_data_high['group_id'] = group_indicator_high
            sel_data.loc[sel_data_high.index,'group_id'] = sel_data_high['group_id']
            sel_data_low = sel_raw_data.query('%s==0'%flag_scene).sort_values(by=factor, ascending = True)
            group_size_low = int(np.floor(sel_data_low.shape[0]/group_num))
            group_indicator_low = []
            for num in list(range(group_num)):
                if num < group_num - 1:
                    group_indicator_low = group_indicator_low + group_size_low * [num + 1]
                else:
                    group_indicator_low = group_indicator_low + (len(sel_data_low) - (group_num - 1)*group_size_low) * [num + 1]
            sel_data_low['group_id'] = group_indicator_low
            sel_data.loc[sel_data_low.index,'group_id'] = sel_data_low['group_id']
        sel_data.rename(columns = {'收益率':'label_pct','投资金额':'label_buy_amt'},inplace = True)


        plot_data['标的数量'] = sel_data.reset_index().groupby('group_id').count()['stockID']
        plot_data['因子值均值'] = sel_data.reset_index().groupby('group_id').mean()[factor]
        plot_data['因子值最小值'] = sel_data.reset_index().groupby('group_id').min()[factor]
        plot_data['因子值最大值'] = sel_data.reset_index().groupby('group_id').max()[factor]
        plot_data['因子值范围'] = round(plot_data['因子值最小值'],4).astype(str) + '~' + round(plot_data['因子值最大值'],4).astype(str)
        plot_data['v2o10均值'] = sel_data.reset_index().groupby('group_id').mean()[self.label_rev]
        plot_data['v2o10中位数'] = sel_data.reset_index().groupby('group_id').median()[self.label_rev]
        plot_data['o2o10均值'] = sel_data.reset_index().groupby('group_id').mean()[self.label_o2o10]
        #plot_data['o2Tc均值'] = sel_data.reset_index().groupby('group_id').mean()['label_TNo2Tc']
        #plot_data['c2To10均值'] = sel_data.reset_index().groupby('group_id').mean()[self.label_Tc2To10]
        plot_data['扣费收益率均值'] = sel_data.reset_index().groupby('group_id').mean()['label_pct_cost']
        plot_data['扣费收益率中位数'] = sel_data.reset_index().groupby('group_id').median()['label_pct_cost']
        if 'label_pct' not in sel_data.columns.tolist():
            sel_data['label_pct'] = sel_data['收益率']
        plot_data['收益率均值'] = sel_data.reset_index().groupby('group_id').mean()['label_pct']
        if 'label_profit_cost' not in sel_data.columns.tolist():
            sel_data['label_profit_cost'] = (sel_data['label_pct'] - self.cost_pct)*sel_data['label_buy_amt']
        plot_data['组累计盈利'] = sel_data.reset_index().groupby('group_id').sum()['label_profit_cost']
        plot_data['收盘涨停占比'] = sel_data.reset_index().groupby('group_id').mean()['label_T_close_is_zt']
        if 'label_binary_v2o10' not in sel_data.columns.tolist():
            sel_data['label_binary_v2o10'] = sel_data.apply(lambda x: 1 if x[self.label_rev]>=self.cost_pct else 0,axis=1)
        if 'label_binary_pctcost' not in sel_data.columns.tolist():
            sel_data['label_binary_pctcost'] = sel_data.apply(lambda x: 1 if x['label_pct']>=self.cost_pct else 0,axis=1)
        plot_data['v2o10为正占比'] = sel_data.reset_index().groupby('group_id').mean()['label_binary_v2o10']
        plot_data['扣费收益率为正占比'] = sel_data.reset_index().groupby('group_id').mean()['label_binary_pctcost']

        plot_data['group_id'] = plot_data.index.tolist()
        plot_data.set_index(['因子值范围'],inplace=True)
        return plot_data

    def cal_proEval(self,pred_sample_data):

        pred_sample_data['label_zuhe'] = [1 if x >=self.cost_pct else 0 for x in pred_sample_data[self.label_rev].tolist()]#pred_sample_data.apply(lambda x: 1 if x['label_v2o10']>=cost_pct else 0, axis = 1)
        if 'pred' not in pred_sample_data.columns.tolist():
            if 'pred_label' in pred_sample_data.columns.tolist():
                pred_sample_data['pred'] = pred_sample_data['pred_label']
            else:

                pred_sample_data['pred'] = pred_sample_data['prediction']
        prec_score = precision_score(pred_sample_data['label_zuhe'],pred_sample_data['pred'])
        rec_score = recall_score(pred_sample_data['label_zuhe'],pred_sample_data['pred'])
        pred1_sample_data = pred_sample_data[pred_sample_data['pred']==1]
        o2ul_mean = pred1_sample_data[self.label_rev].mean()
        return prec_score,rec_score,o2ul_mean

    def cal_proEval_jup(self,pred_sample_data):
        if 'label_zuhe' not in pred_sample_data.columns.tolist():
            pred_sample_data['label_zuhe'] = pred_sample_data.apply(
                lambda x: 1 if x[self.label_rev] >= 0 and x[self.label_o2o10] >= 3 else 0, axis=1)
        if 'label_pat_zuhe' not in pred_sample_data.columns.tolist():
            pred_sample_data['label_pat_zuhe'] = pred_sample_data.apply(
                lambda x: 1 if x[self.label_rev] >= 0 and x[self.label_o2o10] >= 4 else 0, axis=1)
        if 'pred' not in pred_sample_data.columns.tolist():
            if 'pred_label' in pred_sample_data.columns.tolist():
                pred_sample_data['pred'] = pred_sample_data['pred_label']
            else:

                pred_sample_data['pred'] = pred_sample_data['prediction']
        prec_score = precision_score(pred_sample_data['label_zuhe'], pred_sample_data['pred'])
        rec_score = recall_score(pred_sample_data['label_zuhe'], pred_sample_data['pred'])

        prec_score_pat = precision_score(pred_sample_data['label_pat_zuhe'], pred_sample_data['pred'])
        rec_score_pat = recall_score(pred_sample_data['label_pat_zuhe'], pred_sample_data['pred'])

        pred1_sample_data = pred_sample_data[pred_sample_data['pred'] == 1]
        o2ul_mean = pred1_sample_data[self.label_rev].mean()
        if pred1_sample_data.shape[0] > 0:
            pat4_ratio = pred1_sample_data.query('label_pattern==4').shape[0] / pred1_sample_data.shape[0]
            pat4_o2ul = pred1_sample_data.query('label_pattern==4')[self.label_rev].mean()
            if pred1_sample_data.query('label_pattern==4').shape[0] > 0:
                pat4_posratio = pred1_sample_data.query('label_pattern==4 and label_TN_o2ul>=0').shape[0] / \
                                pred1_sample_data.query('label_pattern==4').shape[0]
            else:
                pat4_posratio = 0
            pat3_ratio = pred1_sample_data.query('label_pattern==3').shape[0] / pred1_sample_data.shape[0]
            pat3_o2ul = pred1_sample_data.query('label_pattern==3')[self.label_rev].mean()
            if pred1_sample_data.query('label_pattern==3').shape[0] > 0:
                pat3_posratio = pred1_sample_data.query('label_pattern==3 and label_TN_o2ul>=0').shape[0] / \
                                pred1_sample_data.query('label_pattern==3').shape[0]
            else:
                pat3_posratio = 0
            pat2_ratio = pred1_sample_data.query('label_pattern==2').shape[0] / pred1_sample_data.shape[0]
            pat2_o2ul = pred1_sample_data.query('label_pattern==2')[self.label_rev].mean()

        else:
            pat2_ratio, pat3_ratio, pat4_ratio, pat2_o2ul, pat3_o2ul, pat4_o2ul, pat3_posratio, pat4_posratio = 0, 0, 0, 0, 0, 0, 0, 0
        return prec_score, rec_score, o2ul_mean, prec_score_pat, rec_score_pat, pat2_ratio, pat3_ratio, pat4_ratio, pat2_o2ul, pat3_o2ul, pat4_o2ul, pat3_posratio, pat4_posratio