import sys
sys.path.append('/data/group/800442/800319')
from dataApi.tradeDate import *
from dataApi.getData import *
from dataApi.stockList import *
from LimitUpStrategy.StrategyFactorTest2 import StrategyFactorTest2, search_index
import pandas as pd
import numpy as np
import os
from tqdm import tqdm


factor_files = ['tx_tick_WeightedBuyNum.pkl',
 'tx_BigAmt_Yesterday.pkl',
 'MPC4.pkl',
 'SellCR.pkl',
 'BuySellSpread.pkl',
 'tx_TickRet3.pkl',
 'tx_TickRet3_diff.pkl',
 'voldiffabs10.pkl',
 'tx_Up_Speed.pkl',
 'BidRatio.pkl',
 'tx_Limit_to_Amt.pkl',
 'HF_jqreverse10.pkl',
 'OIR_2.pkl',
 'tx_Max_Speed.pkl',
 'tx_WithdrawBuyorder.pkl',
 'MPC1.pkl',
 'tx_Board_Power.pkl',
 'jqCratio10.pkl',
 'byyz.pkl',
 'tx_Buy_WithDrawBuy.pkl',
 'VOI_normal_1.pkl',
 'tx_AbsBidBuy.pkl',
 'tx_WeightedAvgBuyPx.pkl',
 'BuySellPressure.pkl',
 'jqskew10.pkl',
 'MPC2.pkl',
 'zdmr_ratio10_std.pkl',
 'tx_BuyNum_Order.pkl',
 'tx_NumdiffVol.pkl',
 'MV.pkl',
 'value_10.pkl',
 'zdmc_ratio10.pkl',
 'CRSP.pkl',
 'tx_WithdrawSellorder.pkl',
 'zjlx.pkl',
 'tx_WithdrawBuySellorder.pkl',
 'zdmc_ratio10_std.pkl',
 'OIR.pkl',
 'MCI_buy.pkl',
 'tx_Weight_BuySellPressure.pkl',
 'tx_WeightedAvgBuySellPx.pkl',
 'retKP.pkl',
 'tx_IncreasBuy.pkl',
 'tx_tick_WeightedSellNum.pkl',
 'IntervalLargeTrade.pkl',
 'MPC7.pkl',
 'tx_Weight_SellWithdraw30.pkl',
 'VOI_2.pkl',
 'tx_TickRet2.pkl',
 'tx_WeightSellOrder.pkl',
 'VOI_4.pkl',
 'tx_TickBuy_weight.pkl',
 'Pct10d.pkl',
 'netBidRatio_5.pkl',
 'VOI_normal_6.pkl',
 'ZtTime.pkl',
 'tx_Buy_Sell_Pressure.pkl',
 'tx_Speed_Volume.pkl',
 'tx_MeanPx_Weight.pkl',
 'tx_CorrRV.pkl',
 'tx_CorrPV.pkl',
 'zdmr.pkl',
 'MPC3.pkl',
 'LargeBuyRatio.pkl',
 'OIR_1.pkl',
 'HF_corrpv10.pkl',
 'spread_tick.pkl',
 'AggAucVolRatio.pkl',
 'VOI_6.pkl',
 'tx_VolumeWeight.pkl',
 'LargeTradeStrength.pkl',
 'StdBuySellSpread.pkl',
 'tx_NetBidBuy_Shares.pkl',
 'SOIR.pkl',
 'tx_WeightBuySell.pkl',
 'VOI_9.pkl',
 'OIR_6.pkl',
 'UTD.pkl',
 'tx_Sell_WithDrawSell.pkl',
 'tx_CorrRV_shift.pkl',
 'LnMV.pkl',
 'MPC10.pkl',
 'jyfbzdmrje_10.pkl',
 'tx_Buy_Pressure.pkl',
 'MPB.pkl',
 'MPC8.pkl',
 'IntervalNetBuy.pkl',
 'VOI_normal_3.pkl',
 'boyiyinzi_5.pkl',
 'IntervalLargeSell.pkl',
 'zdmr_ratio10.pkl',
 'LargeBuyStrength.pkl',
 'tx_Weight_BuyPressure.pkl',
 'tx_SellPressure.pkl',
 'NetBuyCR.pkl',
 'tx_TickRet4.pkl',
 'TradeCR.pkl',
 'OIR_10.pkl',
 'VOI_normal_9.pkl',
 'MPC9.pkl',
 'tx_BigOrder_Weight.pkl',
 'tx_SellNum_Order.pkl',
 'OIR_3.pkl',
 'HF_reverse10.pkl',
 'VOI_1.pkl',
 'VOI_7.pkl',
 'VOI_normal_10.pkl',
 'OIR_9.pkl',
 'AdjBuySellPressure.pkl',
 'tx_AbsBidBuy_Shares.pkl',
 'tx_Amt_Inday_Weight.pkl',
 'tx_NetBidBuy.pkl',
 'OIR_7.pkl',
 'tx_Position_High.pkl',
 'AmtPerTradeRatio.pkl',
 'tx_Pct_Yesterday.pkl',
 'MPC6.pkl',
 'IntervalLargeBuy.pkl',
 'VOI_8.pkl',
 'VolRatio.pkl',
 'tx_WeightBuyOrder.pkl',
 'tx_WeightedAvgSellPx.pkl',
 'VOI_normal_5.pkl',
 'OIR_4.pkl',
 'VOI_3.pkl',
 'tx_Buy_mean_std.pkl',
 'BuyCR.pkl',
 'VOI_normal_4.pkl',
 'VOI_normal_7.pkl',
 'OIR_8.pkl',
 'tx_Weight_BuyWithdraw30.pkl',
 'voldiffstd10.pkl',
 'tx_NoBuydivBuy.pkl',
 'tx_TickRet4_diff.pkl',
 'tx_UID.pkl',
 'OIR_5.pkl',
 'tx_WeightedAvgPx.pkl',
 'tx_tick_WeightedSell_BuyNum.pkl',
 'netLargeBuyRatio.pkl',
 'VOI_5.pkl',
 'VolPerTradeRatio.pkl',
 'TurnVolStd.pkl',
 'netBidRatio.pkl',
 'tx_Sell_mean_std.pkl',
 'tx_TickRet2_diff.pkl',
 'TurnVolMean.pkl',
 'VOI_normal_8.pkl',
 'VOI_10.pkl',
 'tx_Weight_SellPressure.pkl',
 'tx_CorrPV_shift.pkl',
 'buy_senti10.pkl',
 'MPC5.pkl',
 'LargeSellRatio.pkl',
 'tx_OpenPct.pkl',
 'VOI_normal_2.pkl',
 'battle_20std.pkl',
 'Pct5d.pkl',
 'LargeTradeRatio.pkl',
 'volumebodong10.pkl',
 'tx_Limit_to_Limit.pkl']

pool_result_dict = {
    '/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl': '/data/group/800442/800319/ZTFactorFilter/FactorTest/AllStock.h5',
    '/data/group/800442/800319/ZTFactorFilter/StkPool/CompensateBoard.pkl': '/data/group/800442/800319/ZTFactorFilter/FactorTest/CompensateBoard.h5',
    '/data/group/800442/800319/ZTFactorFilter/StkPool/LowBoard.pkl': '/data/group/800442/800319/ZTFactorFilter/FactorTest/LowBoard.h5',
    '/data/group/800442/800319/ZTFactorFilter/StkPool/DragonBoard.pkl': '/data/group/800442/800319/ZTFactorFilter/FactorTest/DragonBoard.h5',
    '/data/group/800442/800319/ZTFactorFilter/StkPool/Virga2consisBoard.pkl': '/data/group/800442/800319/ZTFactorFilter/FactorTest/Virga2consisBoard.h5',
    '/data/group/800442/800319/ZTFactorFilter/StkPool/AllStrategyBoard.pkl':'/data/group/800442/800319/ZTFactorFilter/FactorTest/AllStrategyBoard.h5'
}

half_year_list = [(20140701, 20141231), (20150101, 20150630), (20150701, 20151231),
                  (20160101, 20160630), (20160701, 20161231), (20170101, 20170630),
                  (20170701, 20171231), (20180101, 20180630), (20180701, 20181231),
                  (20190101, 20190630), (20190701, 20191231)]
half_year = [201412, 201506, 201512, 201606, 201612, 201706, 201712,
             201806, 201812, 201906, 201912]

class FactorFilter(object):

    def __init__(self, start_date=20140101, end_date=20191231,
                 factor_address='/data/group/800442/800319/ZTfactors/',
                 stock_pool_address ='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl',
                 strength_limit=1,
                 retest=False):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        stock_pool = pd.read_pickle(stock_pool_address)

        self.date_list = date_list
        self.start_date = start_date
        self.end_date = end_date
        self.stock_pool = stock_pool
        self.factor_address = factor_address
        self.stock_pool_address = stock_pool_address
        self.strength_limit = strength_limit
        self.retest = retest

    def factor_process(self, factor, n=60):

        factor_s = pd.read_pickle("/data/group/800442/800319/ZTfactors/%s.pkl"%factor)
        stock_pool = pd.read_pickle('/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl')
        factor_s = factor_s.loc[stock_pool.set_index(['date', 'code', 'tick']).index].fillna(0)
        factor_s.index = stock_pool.set_index(['date', 'code', 'tick']).index
        factor_s.name = 'value'
        factor_s = factor_s.loc[(factor_s.index.get_level_values('date') >= 20140101) &
                                (factor_s.index.get_level_values('date') <= self.end_date)]
        num = factor_s.groupby('date').count()
        f1 = factor_s.groupby('date').sum().fillna(0)
        f2 = (factor_s ** 2).groupby('date').sum().fillna(0)

        factor_mean = f1.rolling(n).sum() / num.rolling(n).sum()
        factor_mean.name = 'mean'
        factor_std = np.sqrt((f2.rolling(n).sum() - (num.rolling(n).sum()) * (factor_mean ** 2)) / (num.rolling(n).sum() - 1))
        factor_std.name = 'std'

        factor_mean_tick = pd.merge(factor_s.reset_index(), factor_mean.shift(1).reset_index(),
                                    how='left', on='date')[['date', 'code', 'tick', 'mean']].set_index(['date', 'code', 'tick'])
        factor_std_tick = pd.merge(factor_s.reset_index(), factor_std.shift(1).reset_index(),
                                   how='left', on='date')[['date', 'code', 'tick', 'std']].set_index(['date', 'code', 'tick'])

        factor_standardized = (factor_s - factor_mean_tick['mean'])/factor_std_tick['std']

        return factor_standardized

    def factor_test(self, strength_limit):

        sft = StrategyFactorTest2(start_date=self.start_date, end_date=self.end_date)
        sft.set_stock_pool(start_tick=93000, stock_pool_address=self.stock_pool_address)
        sft.set_test_params(strength_limit=strength_limit, close_limit_up=True)

        if not self.retest:

            backtest_address = pool_result_dict[self.stock_pool_address]
            strength = pd.read_hdf(backtest_address, 'strength')
            strength_if = pd.read_hdf(backtest_address, 'strength_if')
            ret_tmr0_IC = pd.read_hdf(backtest_address, 'ret_tmr0_IC')
            ret_tmr0 = pd.read_hdf(backtest_address, 'ret_tmr0')
            ret_tmr30_IC = pd.read_hdf(backtest_address, 'ret_tmr30_IC')
            ret_tmr30 = pd.read_hdf(backtest_address, 'ret_tmr30')
            amt_mean = pd.read_hdf(backtest_address, 'amt_mean')
            amt_median = pd.read_hdf(backtest_address, 'amt_median')

            append_factor = set(os.listdir(self.factor_address))-set(factor_files)

            if len(append_factor) == 0:
                pass
            else:
                for file in tqdm(append_factor):
                    factor = file[:-4]
                    factor_std = self.factor_process(factor)
                    ft = sft.test_factor(factor=factor_std,  # 因子名称, 可以传入str文件名, 也可直接传入DataFrame
                                           address=None,  # 因子路径, 若直接传DataFrame, 此处需为None
                                           groups=10,  # 连续型因子分组收益的分组数, 若因子值为离散值则此传参无意义
                                           output=None  # 回测结果输出路径, None表示不输出
                                           )
                    a = ft[0]
                    b = ft[1]
                    c = ft[2]
                    d = ft[3]
                    if len(a) == 0:
                        pass
                    else:
                        strength[factor] = a['strength']
                        strength_if[factor] = a['strength_if']
                        ret_tmr0_IC[factor] = a['ret_tmr0']
                        ret_tmr30_IC[factor] = a['ret_tmr30']
                    if b.loc['monotone', ('ALL', 'ret_tmr0')] > 0:
                        ret_tmr0[factor] = b.loc[max(b.index.tolist()[:-1]), (slice(None), 'ret_tmr0')]
                        amt_mean[factor] = d.loc['mean']
                        amt_median[factor] = d.loc['50%']
                    else:
                        ret_tmr0[factor] = b.loc[min(b.index.tolist()[:-1]), (slice(None), 'ret_tmr0')]
                        amt_mean[factor] = c.loc['mean']
                        amt_median[factor] = c.loc['50%']
                    if b.loc['monotone', ('ALL', 'ret_tmr30')] > 0:
                        ret_tmr30[factor] = b.loc[max(b.index.tolist()[:-1]), (slice(None), 'ret_tmr30')]
                    else:
                        ret_tmr30[factor] = b.loc[min(b.index.tolist()[:-1]), (slice(None), 'ret_tmr30')]

        else:
            strength_if = pd.DataFrame()
            strength = pd.DataFrame()
            ret_tmr0_IC = pd.DataFrame()
            ret_tmr0 = pd.DataFrame()
            ret_tmr30_IC = pd.DataFrame()
            ret_tmr30 = pd.DataFrame()
            amt_mean = pd.DataFrame()
            amt_median = pd.DataFrame()


            for file in tqdm(os.listdir(self.factor_address)[:5]):
                factor = file[:-4]
                print(factor)
                factor_std = self.factor_process(factor)
                try:
                    ft = sft.test_factor(factor=factor,  # 因子名称, 可以传入str文件名, 也可直接传入DataFrame
                                            address=self.factor_address,  # 因子路径, 若直接传DataFrame, 此处需为None
                                            groups=10,  # 连续型因子分组收益的分组数, 若因子值为离散值则此传参无意义
                                            output=None  # 回测结果输出路径, None表示不输出
                                            )
                    a = ft[0]
                    b = ft[1]
                    c = ft[2]
                    d = ft[3]
                    if len(a) == 0:
                        pass
                    else:
                        strength[factor] = a['strength']
                        strength_if.loc[factor] = a['strength_if']
                        ret_tmr0_IC.loc[factor] = a['ret_tmr0']
                    if b.loc['monotone', ('ALL', 'ret_tmr0')]>0:
                        ret_tmr0[factor] = b.loc[max(b.index.tolist()[:-1]),(slice(None), 'ret_tmr0')]
                        amt_mean[factor] = d.loc['mean']
                        amt_median[factor] = d.loc['50%']
                    else:
                        ret_tmr0[factor] = b.loc[min(b.index.tolist()[:-1]), (slice(None), 'ret_tmr0')]
                        amt_mean[factor] = c.loc['mean']
                        amt_median[factor] = c.loc['50%']
                    if b.loc['monotone', ('ALL', 'ret_tmr30')] > 0:
                        ret_tmr30[factor] = b.loc[max(b.index.tolist()[:-1]), (slice(None), 'ret_tmr30')]
                    else:
                        ret_tmr30[factor] = b.loc[min(b.index.tolist()[:-1]), (slice(None), 'ret_tmr30')]
                except:
                    pass
        strength = strength.dropna(how='all', axis=1)
        strength_if = strength_if.dropna(how='all', axis=1)
        ret_tmr0_IC = ret_tmr0_IC.dropna(how='all', axis=1)
        ret_tmr0 = ret_tmr0.dropna(how='all', axis=1)
        ret_tmr30_IC = ret_tmr30_IC.dropna(how='all', axis=1)
        ret_tmr30 = ret_tmr30.dropna(how='all', axis=1)
        amt_mean = amt_mean.dropna(how='all', axis=1)
        amt_median = amt_median.dropna(how='all', axis=1)


        return strength, strength_if, ret_tmr0_IC, ret_tmr0, ret_tmr30_IC, ret_tmr30, amt_mean, amt_median

    def calc_corr(self):

        factor_df = pd.DataFrame()
        for file in tqdm(os.listdir(self.factor_address)):
            factor_s = pd.read_pickle('/data/group/800442/800319/ZTfactors/%s' % (file))
            factor = file[:-4]
            factor_df[factor] = factor_s

        stock_pool_stack = self.stock_pool.set_index(['date', 'code', 'tick'])
        factor_df = factor_df.loc[stock_pool_stack.index]

        describe_df = factor_df.describe().T
        describe_df['null_pct'] = factor_df.isnull().sum()/len(factor_df)
        describe_df['inf_pct'] = (np.isinf(factor_df)).sum()/len(factor_df)
        describe_df['zero_pct'] = (factor_df ==0).sum()/len(factor_df)

        corr_df = factor_df.corr()

        return corr_df, describe_df



    def filter_factor(self, IC_limit=0, IC_amount_limit=0, strength_limit=0, strength_amount_limit=0, corr_limit=0.999):

        strength, strength_if, ret_tmr0_IC, ret_tmr0, ret_tmr30_IC, ret_tmr30, amt_mean, amt_median = self.factor_test(strength_limit=self.strength_limit)
        strength.to_hdf(pool_result_dict[self.stock_pool_address], 'strength')
        strength_if.to_hdf(pool_result_dict[self.stock_pool_address], 'strength_if')
        ret_tmr0.to_hdf(pool_result_dict[self.stock_pool_address], 'ret_tmr0')
        ret_tmr0_IC.to_hdf(pool_result_dict[self.stock_pool_address], 'ret_tmr0_IC')
        ret_tmr30.to_hdf(pool_result_dict[self.stock_pool_address], 'ret_tmr30')
        ret_tmr30_IC.to_hdf(pool_result_dict[self.stock_pool_address], 'ret_tmr30_IC')
        amt_mean.to_hdf(pool_result_dict[self.stock_pool_address], 'amt_mean')
        amt_median.to_hdf(pool_result_dict[self.stock_pool_address], 'amt_median')


        corr_df, describe_df = self.calc_corr()
        corr_df.to_hdf(pool_result_dict[self.stock_pool_address], 'corr')

        abs_ret_IC = abs(ret_tmr0_IC).T
        abs_strength = abs(strength).T

        filtered_factor1 = abs_ret_IC[(abs_ret_IC['ALL'] >= IC_limit) &
                                      ((abs_ret_IC >= IC_limit).sum(axis=1) >= IC_amount_limit)].index
        filtered_factor2 = abs_strength[(abs_strength['ALL'] >= strength_limit) &
                                        ((abs_strength >= strength_limit).sum(axis=1) >= strength_amount_limit)].index

        filtered_factor = list(set(filtered_factor1) & set(filtered_factor2))
        print(filtered_factor)
        filtered_corr_df = corr_df.loc[filtered_factor, filtered_factor]
        remove_factor = []
        for factor in filtered_corr_df.index:
            high_corr_factor = filtered_corr_df[factor].loc[(filtered_corr_df[factor] > corr_limit) & (filtered_corr_df[factor] < 1)].index.tolist()
            high_corr_factor = set(high_corr_factor) - set(remove_factor)
            if len(high_corr_factor) == 0:
                pass
            else:
                if (abs(ret_tmr0_IC.loc['ALL', factor] < abs(ret_tmr0_IC.loc['ALL', high_corr_factor]))).sum() == 0:
                    pass
                else:
                    remove_factor.append(factor)

        cor_IC_filtered_factor = ret_tmr0_IC.T.loc[set(filtered_factor) - set(remove_factor)]
        result = pd.concat([strength, strength_if, ret_tmr0_IC, ret_tmr0, describe_df.T], axis=0)[cor_IC_filtered_factor.index]
        result['type'] = np.repeat(['strength', 'stregth_if', 'ret_tmr0_IC', 'ret_tmr0', 'static'], 13)[:-2]
        result= result.reset_index().set_index(['type', 'index']).T


        return result








if __name__ == '__main__':

    self = FactorFilter(start_date=20140701, end_date=20191231, strength_limit=0.8,
                        stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl',
                        factor_address='/data/group/800442/800319/ZTfactors/',
                        retest=True)

    result = self.factor_test(strength_limit=0.8)



