# coding: utf-8
# Author：fengchi863
# Date ：2021/9/16 16:35

import numpy as np
import pandas as pd
from tqdm import tqdm
import datetime,time
from LimitUpPredStrategy.dataApi import getData, tradeDate, stockList
from LimitUpPredStrategy.dataApi.tradeDate import get_date_range
from LimitUpPredStrategy.dataApi.stockList import trans_windcode2int,trans_datetime2int,trans_int2windcode
from LimitUpPredStrategy.ConceptApi import ConceptApi
from LimitUpPredStrategy.backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare
from LimitUpPredStrategy.Util.tools import get_stock_name, get_stock_name_dict

def del_sellVolume(start_date=20140101,end_date=20210228,save_path='/data/group/800319/LimitStrategy_Test/'):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = pd.read_pickle('/data/group/800319/LimitUpStrategy/FilteredTick.pkl')
    LimitPool_after1 = LimitPool.copy()
    LimitPool_after1['tick'] = LimitPool_after1['tick'].apply(lambda x:int((datetime.datetime.strptime(str(x), '%H%M%S')+datetime.timedelta(seconds=3)).strftime("%H%M%S")))
    LimitPool_after2 = LimitPool.copy()
    LimitPool_after2['tick'] = LimitPool_after2['tick'].apply(lambda x: int((datetime.datetime.strptime(str(x), '%H%M%S') + datetime.timedelta(seconds=6)).strftime("%H%M%S")))

    LimitPool = pd.concat([LimitPool,LimitPool_after1,LimitPool_after2]).sort_values(by=['date','code','tick'])
    LimitPool['tick'] = LimitPool['tick'].apply(lambda x:130000 if x==113000 else 130003 if x==113003 else x)
    LimitPool.drop_duplicates(inplace=True)
    LimitPool.reset_index().drop('index',axis=1,inplace=True)
    LimitPool = LimitPool[LimitPool['tick'] < 150000]
    LimitPool.set_index(['date', 'code','tick'],inplace=True)

    Sell1OrderQty = dp.get_data_by_date_list(item='Sell1OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell2OrderQty = dp.get_data_by_date_list(item='Sell2OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell3OrderQty = dp.get_data_by_date_list(item='Sell3OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell4OrderQty = dp.get_data_by_date_list(item='Sell4OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell5OrderQty = dp.get_data_by_date_list(item='Sell5OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell6OrderQty = dp.get_data_by_date_list(item='Sell6OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell7OrderQty = dp.get_data_by_date_list(item='Sell7OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell8OrderQty = dp.get_data_by_date_list(item='Sell8OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell9OrderQty = dp.get_data_by_date_list(item='Sell9OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    Sell10OrderQty = dp.get_data_by_date_list(item='Sell1OrderQty',start_date=start_date, end_date=end_date, return_idx=True)
    TotalVolumeTrade = dp.get_data_by_date_list(item='TotalVolumeTrade',start_date=start_date, end_date=end_date, return_idx=True)
    Buy1OrderQty = dp.get_data_by_date_list(item='Buy1OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    HighPx = dp.get_data_by_date_list(item='HighPx',start_date=start_date, end_date=end_date, return_idx=True)
    LastPx = dp.get_data_by_date_list(item='LastPx',start_date=start_date, end_date=end_date, return_idx=True)
    Sell1Price = dp.get_data_by_date_list(item='Sell1Price',start_date=start_date, end_date=end_date, return_idx=True)

    LimitPrice = HighPx.loc[:, 92500:].max(axis=1)
    # 1、获取当前tick的总共卖单 #
    Sell_Volume=Sell1OrderQty+Sell2OrderQty+Sell3OrderQty+Sell4OrderQty+Sell5OrderQty+Sell6OrderQty+Sell7OrderQty+Sell8OrderQty+Sell9OrderQty+Sell10OrderQty
    Sell_Volume = Sell_Volume.loc[:,92500:].stack().loc[LimitPool.index]
    Sell_Volume.to_hdf(save_path+'Sell_Volume.h5',key='Sell_Volume')

    # 2、获取该tick后累计成交量
    Remain_Volume = (-TotalVolumeTrade.T + TotalVolumeTrade[150000]).T
    Remain_Volume = Remain_Volume.loc[:,92500:].stack().loc[LimitPool.index]
    Remain_Volume.to_hdf(save_path+'Remain_Volume.h5',key='Remain_Volume')

    # 3、剩余成交量=(tick后累计成交量-买一量)*buy_weight
    Buy_Volume = Buy1OrderQty.stack().loc[LimitPool.index]
    All_Volume = (Remain_Volume - Buy_Volume).astype(int)  # 剩余成交量=(tick后累计成交量-买一量)*buy_weight
    All_Volume = All_Volume.apply(lambda x: max(x, 0))
    All_Volume.to_hdf(save_path + 'All_Volume.h5', key='All_Volume')

    # 4、获取买一价<涨停价的tick
    NoLimit = (Sell1Price.loc[:, 92500:].T < LimitPrice).T
    NoLimit = NoLimit.stack().loc[LimitPool.index]
    NoLimit.to_hdf(save_path + 'NoLimit.h5', key='NoLimit')

    # 5、获取开过板的个股
    IF_open = LastPx.T.iloc[::-1].expanding().min().iloc[::-1].T
    IF_open = (IF_open.loc[:, 92500:].T < LimitPrice).T # 如果后面的最新成交价格<涨停价，那就意味着开板了
    IF_open = IF_open.stack().loc[LimitPool.index]
    IF_open.to_hdf(save_path + 'IF_open.h5', key='IF_open')

    return None

def get_volume(start_date,end_date,buy_weight=0.1,tick_delay=3,save_path='/data/group/800319/LimitStrategy_Test/'):  #个股成交比例
    # 如果买一价=最新价（涨停价），剩余成交量=(tick后累计成交量-买一量)*buy_weight
    # 如果买一价<最新价（涨停价），剩余成交量=max{当前全部卖单挂单量，tick后累计成交量*buy_weight}
    # 如果后续开板了，剩余成交量=max{当前全部卖单挂单量，tick后累计成交量*buy_weight}
    dp = TickDataPrepare()  # 实例化类
    LimitPool = pd.read_pickle('/data/group/800319/LimitUpStrategy/FilteredTick.pkl')
    LimitPool['tick'] = LimitPool['tick'].apply(lambda x: int((datetime.datetime.strptime(str(x), '%H%M%S') + datetime.timedelta(seconds=tick_delay)).strftime("%H%M%S")))
    LimitPool['tick'] = LimitPool['tick'].apply(lambda x: 130000 if x == 113000 else 130003 if x == 113003 else x)
    LimitPool.drop_duplicates(inplace=True)
    LimitPool.reset_index().drop('index', axis=1, inplace=True)
    LimitPool = LimitPool[LimitPool['tick'] < 150000]
    LimitPool.set_index(['date', 'code', 'tick'], inplace=True)

    HighPx = dp.get_data_by_date_list(item='HighPx',start_date=start_date, end_date=end_date, return_idx=True)
    LimitPrice = HighPx.loc[:, 92500:].max(axis=1)
    #（1）获取当前全部卖单挂单量(股）
    Sell_Volume = pd.read_hdf(save_path + 'Sell_Volume.h5', key='Sell_Volume').loc[LimitPool.index]
    #（2）获取tick后累计成交量
    Remain_Volume = pd.read_hdf(save_path + 'Remain_Volume.h5', key='Remain_Volume').loc[LimitPool.index]
    #（3）当卖一价无时：获取剩余成交量=(tick后累计成交量-买一量)*buy_weight
    All_Volume = (pd.read_hdf(save_path + 'All_Volume.h5', key='All_Volume')*buy_weight).loc[LimitPool.index]
    #（4）当卖一价存在时：两类成交量的计算方法
    Del_Volume=pd.concat([Sell_Volume,Remain_Volume*buy_weight],axis=1).max(axis=1)  #剩余成交量=max{当前全部卖单挂单量，tick后累计成交量*buy_weight}
    #（5）获取买一价<涨停价的tick
    NoLimit=pd.read_hdf(save_path + 'NoLimit.h5', key='NoLimit').loc[LimitPool.index]
    #（6）获取开过板的个股
    IF_open = pd.read_hdf(save_path + 'IF_open.h5', key='IF_open').loc[LimitPool.index]

    # 写入成交量
    Volume = pd.DataFrame(index=All_Volume.index, columns=['Volume'])
    Limit_index = NoLimit[NoLimit == False].index
    NoLimit_index = NoLimit[NoLimit == True].index
    Open_index = IF_open[IF_open == True].index

    Volume.loc[Limit_index, 'Volume'] = All_Volume.loc[Limit_index]  # 获取第一类：最新价=涨停价，那么就用剩余成交量计算
    Volume.loc[NoLimit_index, 'Volume'] = Del_Volume.loc[NoLimit_index]  # 获取第二类：最新价<涨停价，那么就用挂单数计算生于成交
    Volume.loc[Open_index, 'Volume'] = Del_Volume.loc[Open_index]  # 获取第三类：个股开过板

    #########组合成dataframe，date stock tick volume price################
    Volume['price']=LimitPrice.loc[Volume.index]
    ########保存数据#################
    Volume.to_hdf(save_path+'Strategy_Volume'+str(int(buy_weight*100))+'_'+ str(tick_delay)+'.h5',key='Strategy_Volume'+str(int(buy_weight*100))+'_'+ str(tick_delay))

    return None

def sell_DateTime(start_date=20140101,end_date=20210228,save_path='/data/group/800319/LimitStrategy_Test/'):
    ########获取股票池##############
    LimitPool = pd.read_pickle('/data/group/800319/LimitUpStrategy/FilteredTick.pkl')
    LimitPool_after1 = LimitPool.copy()
    LimitPool_after1['tick'] = LimitPool_after1['tick'].apply(lambda x: int((datetime.datetime.strptime(str(x), '%H%M%S') + datetime.timedelta(seconds=3)).strftime("%H%M%S")))
    LimitPool_after2 = LimitPool.copy()
    LimitPool_after2['tick'] = LimitPool_after2['tick'].apply(lambda x: int((datetime.datetime.strptime(str(x), '%H%M%S') + datetime.timedelta(seconds=6)).strftime("%H%M%S")))

    LimitPool = pd.concat([LimitPool, LimitPool_after1, LimitPool_after2]).sort_values(by=['date', 'code', 'tick'])
    LimitPool['tick'] = LimitPool['tick'].apply(lambda x: 130000 if x == 113000 else 130003 if x == 113003 else x)
    LimitPool.drop_duplicates(inplace=True)
    LimitPool.reset_index().drop('index', axis=1, inplace=True)
    LimitPool = LimitPool[LimitPool['tick'] < 150000]
    LimitPool.set_index(['date', 'code', 'tick'], inplace=True)

    #########准备卖出日期的数据############
    date_list = getData.get_date_range(start_date, 20210324)
    sell_end_date = date_list[-1]

    min_low = getData.get_minute_1factor('low', start_datetime=start_date, end_datetime=sell_end_date).dropna(how='all',axis=1)

    Limit_Price = ConceptApi.get_basic_values('Limit_price', start_date=start_date, end_date=sell_end_date)
    Lowest_Price = ConceptApi.get_basic_values('Lowest_Price', start_date=start_date, end_date=sell_end_date)

    Low = getData.get_daily_1factor('low', date_list=date_list).sort_index()
    High = getData.get_daily_1factor('high', date_list=date_list).sort_index()

    code_list = list(set(Limit_Price.columns).intersection(set(Low.columns)).intersection(set(High.columns)).intersection(set(Lowest_Price.columns)))
    #######如果非一字跌停板，或者非一字涨停板，那就显示为True，其余为FALSE
    If_Sell = ((Low[code_list] < Limit_Price[code_list]) & (High[code_list] > Lowest_Price[code_list]) & (High[code_list] > Low[code_list]))  # 为False就是可以卖出的日期
    ############创建卖出dataframe####################
    Temp_index = LimitPool.reset_index().drop('tick',axis=1).drop_duplicates().set_index(['date','code'])
    Sell_Result = pd.DataFrame(index=Temp_index.index, columns=['sell_date', 'sell_time'])
    for x in tqdm(Sell_Result.index):
        sell_date = If_Sell.loc[x[0]:, x[1]].iloc[1:][If_Sell.loc[x[0]:, x[1]].iloc[1:] == True]
        if len(sell_date) > 0:
            Sell_Result.loc[x, 'sell_date'] = sell_date.index[0]
            #######可以开始卖出的时间窗口：日内分钟最低价！=涨停价###########
            sell_time = (min_low.loc[Sell_Result.loc[x, 'sell_date']][x[1]] < Limit_Price.loc[Sell_Result.loc[x, 'sell_date'], x[1]])
            if len(sell_time[sell_time == True]) > 0:
                Sell_Result.loc[x, 'sell_time'] = sell_time[sell_time == True].index[0]

    Sell_Result = Sell_Result.loc[LimitPool.index]

    Sell_Result.to_hdf(save_path+'Sell_Result.h5',key='Sell_Result')

    return Sell_Result

class StrategyTest(object):
    def __init__(self, start_date=20140101, end_date=20201231,buy_money=10000000,  #单只个股买入金额，单只个股成交比例
                 buy_weight=0.1,tick_delay=3,read_path='/data/group/800319/LimitStrategy_Test/'):
        self.start_date=start_date
        self.end_date=end_date
        self.buy_money=buy_money
        self.tick_delay = tick_delay

        dp = TickDataPrepare()  # 实例化类
        LastPx = dp.get_data_by_date_list(item='LastPx', start_date=start_date, end_date=end_date,return_idx=True)
        LastPx = LastPx.loc[:, 92500:].stack()
        LastPx.index.names=['date','code','tick']
        self.LastPx = LastPx
        ######获取涨停个股的成交量和成交金额情况###########
        try:
            Limit_Result = pd.read_hdf(read_path+'Strategy_Volume'+str(int(buy_weight*100))+'_'+ str(tick_delay)+'.h5',key='Strategy_Volume'+str(int(buy_weight*100))+'_'+ str(tick_delay)).loc[start_date : end_date]
        except:
            print('该成交比例暂无，先行写入')
            Limit_Result = get_volume(start_date=20140101, end_date=20210228, buy_weight=0.1).loc[start_date : end_date]

        #####先对比以当前资金一共能成交多数数量的股票，然后取最小#########
        Limit_Result['LastPx'] = LastPx

        Limit_Result['Volume'] = pd.concat([(buy_money / Limit_Result['LastPx'] / 100).astype(int) * 100,(Limit_Result['Volume'] / 100).astype(int) * 100], axis=1).min(axis=1)
        Limit_Result['money'] = Limit_Result['Volume']*Limit_Result['LastPx']
        Sell_Result= pd.read_hdf(read_path + 'Sell_Result.h5', key='Sell_Result').loc[start_date : end_date]
        Limit_Result=pd.concat([Limit_Result,Sell_Result.loc[Limit_Result.index]],axis=1)

        self.Limit_Result = Limit_Result

        sell_end_date=max(Limit_Result['sell_date'])
        #########日内分钟获取成交量，成交额##################
        min_amt = getData.get_minute_1factor('amt', start_datetime=start_date, end_datetime=sell_end_date).dropna(how='all',axis=1)
        min_vol = getData.get_minute_1factor('vol', start_datetime=start_date, end_datetime=sell_end_date).dropna(how='all',axis=1)

        self.min_amt=min_amt
        self.min_vol=min_vol

        adjfactor=getData.get_daily_1factor('adjfactor')
        self.adjfactor=adjfactor

        minute_list = sorted(list(set(min_amt.index.levels[1])))
        self.minute_list = minute_list

        open=getData.get_daily_1factor('open')
        self.open=open

    def get_strategy_result(self,factor,N=10,cost=0.001):
        ###传入参数：0-1因子值###
        factor = factor.loc[self.start_date : self.end_date]
        factor.index.names = ['date', 'code', 'tick']
        factor = pd.DataFrame(factor)
        factor.columns = ['factor']
        factor = factor[factor['factor'] == 1].sort_values(by=['date', 'code', 'tick'])
        # 1、个股一天内只能交易一次，因此每只个股只会取当日第一次触发的时间###
        Stock_Trade = factor.groupby(['date', 'code']).apply(lambda x: x.index[0][2])
        Stock_Trade = pd.DataFrame(Stock_Trade, columns=['tick']).reset_index()
        Stock_Trade['buy_sign'] = 1
        # 2、往后推迟tick_delay秒：
        if self.tick_delay > 0:
            Stock_Trade['tick'] = Stock_Trade['tick'].apply(lambda x:int((datetime.datetime.strptime(str(x), '%H%M%S')+datetime.timedelta(seconds=self.tick_delay)).strftime("%H%M%S")))
            Stock_Trade['tick'] = Stock_Trade['tick'].apply(lambda x: 130000 if x == 113000 else 130003 if x == 113003 else x)
            Stock_Trade.drop_duplicates(inplace=True)
            Stock_Trade.reset_index().drop('index', axis=1, inplace=True)
        # 3、成交时间在93000及以前和125957及以后的股票 删除
        Stock_Trade = Stock_Trade[Stock_Trade['tick'] < 145957][Stock_Trade['tick'] > 93000]
        Stock_Trade.set_index(keys=['date', 'code', 'tick'], inplace=True)

        ###2、获取交易，并且把成交量<1000的股票，成交价格低于2元的股票，成交时间在93000及以前和125957及以后的股票 删除###
        Limit_Result = self.Limit_Result.loc[Stock_Trade.index]
        Trade_Result = Limit_Result[Limit_Result['Volume'] > 1000]
        Trade_Result=Trade_Result[Trade_Result['LastPx'] > 2]

        ###开始循环获取卖出价格######
        for index in tqdm(Trade_Result.index):
            date=Trade_Result.loc[index,'sell_date']
            minute=Trade_Result.loc[index,'sell_time']
            stock=index[1]
            ######N 为用未来N分钟的均价###############
            if np.isnan(date)==False:
                if np.isnan(minute)==True:
                    minute=925
                    minuet_N=1500
                elif (self.minute_list.index(minute)+N)<len(self.minute_list):
                    minuet_N=self.minute_list[self.minute_list.index(minute)+N]
                else:
                    minuet_N=1500
                Trade_Result.loc[index,'sell_price']=self.min_amt.loc[date][stock].loc[minute:minuet_N].sum()/self.min_vol.loc[date][stock].loc[minute:minuet_N].sum()
                if np.isnan(Trade_Result.loc[index,'sell_price']):
                    Trade_Result.loc[index, 'sell_price'] = self.min_amt.loc[date][stock].sum() / self.min_vol.loc[date][stock].sum()
                    if np.isnan(Trade_Result.loc[index,'sell_price']):
                        #####如果还是nan，就使用开盘价交易###########
                        Trade_Result.loc[index, 'sell_price'] = self.open.loc[date,stock]

                Trade_Result.loc[index, 'sell_price'] = Trade_Result.loc[index, 'sell_price'] * self.adjfactor.loc[date,stock]/self.adjfactor.loc[index[0],stock]

        ###开始统计卖出收益率：卖出收益率（收益率计算），实际收益率（按照单笔1000万计算）####
        Trade_Result['收益率']=Trade_Result['sell_price']/Trade_Result['price']-1-cost*2
        Trade_Result['实际收益']=(Trade_Result['sell_price']-Trade_Result['price'])*Trade_Result['Volume']\
                             -(Trade_Result['sell_price']+Trade_Result['price'])*Trade_Result['Volume']*cost
        Trade_Result['实际收益率']=Trade_Result['实际收益']/self.buy_money

        self.Trade_Result=Trade_Result

    def statistic_factor(self,save_path=None):
        #######平均收益率，胜率，盈亏比############
        date_list=get_date_range(self.start_date,self.end_date)
        ##1、收益率
        BuyLimit_Trade_Result = self.Trade_Result[self.Trade_Result['price'] == self.Trade_Result['LastPx']]
        BuyNoLimit_Trade_Result = self.Trade_Result[self.Trade_Result['price'] > self.Trade_Result['LastPx']]
        Result_list=[]
        for Trade_Result,name in zip([self.Trade_Result,BuyLimit_Trade_Result,BuyNoLimit_Trade_Result],['all','BuyLimit','BuyNoLimit']):
            Result = pd.DataFrame(index=['胜率', '平均收益率', '盈亏比','成交比例'], columns=['数值收益', '实际收益'])

            Result.loc['胜率','数值收益']=len(Trade_Result['收益率'][Trade_Result['收益率']>0])/ len(Trade_Result)
            Result.loc['平均收益率', '数值收益']=Trade_Result['收益率'].mean()
            Result.loc['盈亏比', '数值收益'] = -Trade_Result['收益率'][Trade_Result['收益率']>0].mean()/Trade_Result['收益率'][Trade_Result['收益率']<0].mean()

            Result.loc['胜率', '实际收益'] = len(Trade_Result['实际收益率'][Trade_Result['实际收益率'] > 0]) / len(Trade_Result)
            Result.loc['平均收益率', '实际收益'] = Trade_Result['实际收益率'].mean()
            Result.loc['盈亏比', '实际收益'] = -Trade_Result['实际收益率'][Trade_Result['实际收益率'] > 0].mean() / Trade_Result['实际收益率'][Trade_Result['实际收益率'] < 0].mean()
            Result.loc['成交比例'] = (Trade_Result['money']/self.buy_money).mean()

            Result.index = pd.Series(Result.index).apply(lambda x:x+'_'+name)
            Result_list.append(Result)

        Result = pd.concat(Result_list)

        ##2、净值曲线
        Net_Profit=pd.DataFrame(index=self.Trade_Result.index.levels[0],columns=['净盈利','实际收益-净收益率','数值收益-净收益率','日交易次数','日胜率'])

        Net_Profit['净盈利']=self.Trade_Result['实际收益'].groupby('date').sum().expanding().sum()
        Net_Profit['实际收益-净收益率']=self.Trade_Result['实际收益率'].groupby('date').mean().expanding().sum()
        Net_Profit['数值收益-净收益率'] = self.Trade_Result['收益率'].groupby('date').mean().expanding().sum()
        Net_Profit['日交易次数']=self.Trade_Result['收益率'].groupby('date').count()
        Net_Profit['日胜率']=(self.Trade_Result['收益率']>0).groupby('date').sum()/Net_Profit['日交易次数']
        ##赋予原始值##
        Net_Profit=Net_Profit.loc[date_list]
        Net_Profit['日交易次数'].fillna(0,inplace=True)
        for i in ['净盈利','实际收益-净收益率','数值收益-净收益率']:
            Net_Profit[i].fillna(method='ffill',inplace=True)
            Net_Profit[i].fillna(0,inplace=True)

        ##3、年度收益率结果统计
        year_list = [date//10000 for date in date_list]
        year_list = sorted(list(set(year_list)))
        Year_Profit_list = []
        for Trade_Result, name in zip([self.Trade_Result, BuyLimit_Trade_Result, BuyNoLimit_Trade_Result],['all', 'BuyLimit', 'BuyNoLimit']):

            Year_Profit=pd.DataFrame(index=year_list,columns=['胜率','数值收益-平均收益率','数值收益-盈亏比','实际收益-平均收益率','实际收益-盈亏比','触发次数'])
            for year in year_list:
                year_result = Trade_Result.loc[year*10000+101:year*10000+1231]
                if len(year_result)>0:
                    Year_Profit.loc[year,'胜率'] = len(year_result['收益率'][year_result['收益率']>0])/len(year_result['收益率'])
                    Year_Profit.loc[year, '数值收益-平均收益率'] = year_result['收益率'].mean()
                    Year_Profit.loc[year, '数值收益-盈亏比'] =-year_result['收益率'][year_result['收益率']>0].mean()/year_result['收益率'][year_result['收益率']<0].mean()
                    Year_Profit.loc[year, '实际收益-平均收益率'] =year_result['实际收益率'].mean()
                    Year_Profit.loc[year, '实际收益-盈亏比'] =-year_result['实际收益率'][year_result['实际收益率']>0].mean()/year_result['实际收益率'][year_result['实际收益率']<0].mean()
                    Year_Profit.loc[year, '触发次数'] = len(year_result)
                    Year_Profit.loc[year, '成交比例'] = (year_result['money']/self.buy_money).mean()

            Year_Profit.index = pd.Series(Year_Profit.index).apply(lambda x:str(x)+'_'+name)
            Year_Profit_list.append(Year_Profit)

        Year_Profit = pd.concat(Year_Profit_list)

        if save_path:
            with pd.ExcelWriter(save_path) as w:
                stock_name_dict = get_stock_name_dict()
                Trade_Result = self.Trade_Result.reset_index()
                Trade_Result['股票名称'] = Trade_Result['code'].apply(lambda x: get_stock_name(x, stock_name_dict))
                Trade_Result.to_excel(w, '原始数据')
                Result.to_excel(w, '统计结果')
                Net_Profit.to_excel(w, '净值曲线')
                Year_Profit.to_excel(w,'年度结果')

        return self.Trade_Result,Result,Net_Profit,Year_Profit

if __name__ == '__main__':
    self = StrategyTest(start_date=20150101, end_date=20191231, buy_money=10000000, buy_weight=0.1, tick_delay=3)

    factor = pd.read_pickle('/data/group/800319/Afengchi/LimitUpPredStrategy/predict_result/linear_reg/linear_reg_trainPeriod60_predictPeriod10_factorNum80_pctThreshold0.03_signal_r2s3.pkl')
    factor = factor['prediction']
    self.get_strategy_result(factor,N=10,cost=0.001)   # 卖出周期为N分钟
    Trade_Result,Result,Net_Profit,Year_Profit=self.statistic_factor(save_path=None)
