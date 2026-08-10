import os
import shutil
import traceback
import pandas as pd
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
import bottleneck as bk
from xquant.factordata import FactorData
from multiprocessing import Pool
from multifactor.IO import IO
from function_tools import *

class FactorEvaluator(object):

    def __init__(self):
        OUTER_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

        # self.variety_list = ['IC', 'IH', 'IF']
        # self.multi_variety_list = ['IH_IC', 'IC_IH', 'IF_IC', 'IC_IF', 'IH_IF', 'IF_IH']
        # self.data_type_dict = {'1T': 'minute_pickles',
        #                        'minute_index': 'minute_index_pickles',
        #                        'multi_minute': 'multi_minute_pickles',
        #                        '10s': '10s_pickles',
        #                        'tick': 'temp_pickles'}

        self.__factor_data_path = '{}/data_center/factor_data'.format(OUTER_ROOT_PATH)
        self.__minute_future_path = '/data/group/800002/FutureTrader/test/MD/CHINA_FUTURES/MINUTE'
        self.__store_data_path = '/data/user/015615/IndexFuture/research_data_center/factor_data'
        self.__factor_status_path = '/data/user/015615/IndexFuture/research_data_center/factor_data/factor_status.pkl'

        self.MAX_CORR = 0.5

    
    def get_trading_days(self, start_date, end_date):
        return sorted(get_trading_days(start_date, end_date))


    def get_factor_value(self, factor_name, variety):
        return pd.read_hdf('{}/minute_raw/{}/{}.h5'.format(self.__factor_data_path, variety, factor_name))


    def get_factor_tsrank(self, factor_name, variety):
        return pd.read_hdf('{}/minute_norm/{}/{}.h5'.format(self.__factor_data_path, variety, factor_name))

    
    def __get_factor_list(self, variety):

        df_factor_status = pd.read_pickle(self.__factor_status_path)
        df_factor_by_variety = df_factor_status.loc[variety]

        return list(df_factor_by_variety.index)

    def merge_all_tsrank_factor(self, variety, start_date, end_date):

        factor_status = pd.read_pickle(self.__factor_status_path)
        factor_list = factor_status.loc[factor_status['is_criteria_2']==True].loc[variety].index.values
        factor_df_list = []
        for f in factor_list:
            factor_df_list.append(pd.read_hdf('{}/factor_tsrank/{}/{}.h5'.format(self.__store_data_path, variety, f))[start_date:end_date])
        return pd.concat(factor_df_list, axis=1)


    def calc_tsrank_max_corr_by_df(self, factor_df, variety, start_date, end_date):

        df_all = self.merge_all_tsrank_factor(variety, start_date, end_date)
        factor_name = factor_df.columns[0]
        s_corr = abs(df_all.corrwith(factor_df.iloc[:, 0], axis=0)).sort_values(ascending=False)
        if factor_name == s_corr.index[0]:
            max_corr = s_corr.iloc[1]
        else:
            max_corr = s_corr.iloc[0]
        print(s_corr)
        
        return max_corr < self.MAX_CORR


    def calc_tsrank_max_corr_by_name(self, factor_name, variety, start_date, end_date):

        df_all = self.merge_all_tsrank_factor(variety, start_date, end_date)
        factor_df = self.get_factor_tsrank(factor_name, variety)
        s_corr = abs(df_all.corrwith(factor_df.iloc[:, 0], axis=0)).sort_values(ascending=False)
        if factor_name == s_corr.index[0]:
            max_corr = s_corr.iloc[1]
        else:
            max_corr = s_corr.iloc[0]
        # print(s_corr)
        
        return max_corr < self.MAX_CORR
    
    
    def calc_tsrank_max_corr_by_name_list(self, factor_name_list, variety, start_date, end_date):
        df_all = self.merge_all_tsrank_factor(variety, start_date, end_date)
        df_new_factors = pd.concat([self.get_factor_tsrank(factor_name, variety) for factor_name in factor_name_list], axis=1)

        df_total = pd.concat([df_all, df_new_factors], axis=1)
        df_total = df_total.iloc[:, ~df_total.columns.duplicated()]

        max_corr_dict = {}
        df_corr = abs(df_total.corr())

        for i in range(len(factor_name_list)):
            ts_rank_name = factor_name_list[i]
            temp_corr = df_corr.loc[ts_rank_name].sort_values(ascending=False)
            temp_unique_corr = temp_corr.loc[temp_corr.index != ts_rank_name]
            max_corr_dict[ts_rank_name] = {'factor_name': temp_unique_corr.index[0],
                                           'max_corr_value': temp_unique_corr.iloc[0]}
            df_result = pd.DataFrame.from_dict(max_corr_dict).T
            df_result['is_corr_passed'] = df_result['max_corr_value'] < self.MAX_CORR

        return df_result
    
    
    def get_max_corr_passed_df(self, factor_name_list, variety, data_type, start_date, end_date):
        df_max_corr = self.calc_max_corr_by_name_list(factor_name_list, variety, start_date, end_date)
        df_max_corr['max_corr'] = df_max_corr['max_corr_value'] < self.MAX_CORR
        return df_max_corr['max_corr'].to_frame()


    def get_Trading_Twap_by_period(self, variety, start_date, end_date, instrument_type='main'):

        future_data = IO.read_data([start_date, end_date+'235959'],alt='{}/{}_MINUTE.h5'.format(self.__minute_future_path, variety))
        twap = select_data_by_univ(future_data, variety, instrument_type).reset_index().set_index('dt').shift(-1)['twap']

        return twap


    def backtest_factor_by_group(self, mergeinfo, groupid, groupnum):

        mergeinfo['flag']=0 
        mergeinfo.loc[mergeinfo['group'] == groupid,'flag'] = 1
        midpoint = (groupnum+1)/2
        if groupid > midpoint:
            mergeinfo.loc[mergeinfo['group'] <= midpoint, 'flag'] = -1
        elif groupid <= midpoint:
            mergeinfo.loc[mergeinfo['group'] > midpoint, 'flag'] = -1

        DealsRtn = {}
        DealsHoldPeriods = {}       

        for date in [date.strftime('%Y%m%d') for date in np.unique(mergeinfo.index.date)]:
            dailydealsrtn = []
            dailydealsstarttime = []
            dailydealsendtime = []
            dailydealsholdperiods = []

            factordaily = mergeinfo.loc[date]
            opentwap = 0
            lastindex = 0

            if factordaily['flag'].values[0] == 1 :
                opentwap = factordaily['twap'].values[0]
                lastindex = 0
                dailydealsstarttime.append(factordaily.index[0])

            for i in range(1,len(factordaily)-1):
                if factordaily['flag'].values[i] == -1 and len(dailydealsstarttime) != len(dailydealsendtime):
                    rtn = factordaily['twap'].values[i]/opentwap-1
                    dailydealsrtn.append(rtn)
                    dailydealsendtime.append(factordaily.index[i])
                    dailydealsholdperiods.append(i-lastindex)

                if factordaily['flag'].values[i] == 1 and len(dailydealsstarttime) == len(dailydealsendtime):
                    opentwap = factordaily['twap'].values[i]
                    dailydealsstarttime.append(factordaily.index[i])
                    lastindex=i

            if len(dailydealsstarttime) == len(dailydealsendtime)+1:
                rtn = factordaily['twap'].values[-1]/opentwap-1
                dailydealsrtn.append(rtn)
                dailydealsendtime.append(factordaily.index[-1])
                dailydealsholdperiods.append(237-lastindex)
            
            DealsRtn[date] = dailydealsrtn
            DealsHoldPeriods[date] = dailydealsholdperiods

        result = {}
        for date in DealsRtn.keys():
            result[date] = pd.DataFrame([DealsRtn[date],DealsHoldPeriods[date]]).transpose()

        result = pd.concat(result)
        result.columns=['rtn', 'holdperiods']
        
        return result


    def calc_statistic_by_factor_tsrank_df(self, factor_df, variety, start_date, end_date, groupnum=10, ncore=20):

        factor_name = factor_df.columns[0]
        df_tsfactor = factor_df[start_date:end_date][[factor_name]]
                
        twap = self.get_Trading_Twap_by_period(variety, start_date, end_date)
        mergeinfo = pd.concat([df_tsfactor, twap], axis=1).dropna()
        mergeinfo['group'] = np.ceil((mergeinfo[factor_name] * groupnum))
        mergeinfo['group'][mergeinfo['group']==0] = 1

        RESULT = {}

        pool = Pool(ncore)
        tasks = []
        for groupid in range(1, groupnum+1):
            tasks.append([pool.apply_async(self.backtest_factor_by_group, args=(mergeinfo, groupid, groupnum)), groupid])
        pool.close()

        for t, groupid in tasks:
            try:
                RESULT[groupid]= t.get()
            except Exception as e:
                print(e, traceback.format_exc())
        pool.join()

        tmp = pd.concat(RESULT)['rtn'].unstack(0)
        DailyDealNum = (~tmp.isnull()).groupby(level=0).sum().mean()
        AvgHoldPeriods = pd.concat(RESULT).unstack(0)['holdperiods'].groupby(level=0).mean().mean()
        SegementDailyReturn = pd.concat(RESULT).unstack(0)['rtn'].fillna(0).groupby(level=0).sum()*100
        Longshort = (SegementDailyReturn.iloc[:,-1]-SegementDailyReturn.iloc[:,0])

        ProfitPerDeal = pd.concat(RESULT)['rtn'].unstack(0).mean()*100

        SegementDailyReturn.cumsum().plot(title='Daily Profit Segment Curve')
        plt.show()

        ProfitPerDeal.plot(kind='bar', title='Profit Per Deal Segment Curve')
        plt.show()

        summary = pd.concat([ProfitPerDeal, DailyDealNum, AvgHoldPeriods, SegementDailyReturn.mean()], axis=1)
        summary.columns=['ProfitPerDeal (%)', 'DailyDealNum', 'AvgHoldPeriods',' DailyReturn (%)']
        print(summary.transpose())
        Longshort.cumsum().plot(title='Long Short Curve')
        plt.show()

        summarydict = {}
        summarydict['LongShortAnualReturn (%)'] = Longshort.mean()*250
        summarydict['LongShortSR'] = Longshort.mean()/Longshort.std()
        summarydict['ProfitPerDealDiff (%)'] = ProfitPerDeal.max() - ProfitPerDeal.min()
        summarydict['MaxProfitGroup'] = ProfitPerDeal[ProfitPerDeal==ProfitPerDeal.max()].index.values[0]
        summarydict['MinProfitGroup'] = ProfitPerDeal[ProfitPerDeal==ProfitPerDeal.min()].index.values[0]

        flag = summarydict['ProfitPerDealDiff (%)'] > 0.04 and \
               summarydict['MaxProfitGroup'] - summarydict['MinProfitGroup'] >= 7 and \
               summarydict['LongShortSR'] >= 0.1
        
        summarydictdf = pd.DataFrame(summarydict, index=[factor_name]).transpose()
        print(summarydictdf)

        return flag, summarydict['LongShortSR'], summarydict['ProfitPerDealDiff (%)']


    def calc_statistic_by_factor_name(self, factor_name, variety, start_date, end_date, groupnum=10):

        factor_df = self.get_factor_tsrank(factor_name, variety)
        return self.calc_statistic_by_factor_tsrank_df(factor_df, variety, start_date, end_date, groupnum)


    def Strategy_Simple_Test(self, prediction, variety='IC', tslookback=5, OpenLong=0.9, OpenShort=0.1, CloseLong=0.5, CloseShort=0.5, fee=0.0004):

        start_date = prediction.unstack().index[0]
        end_date = prediction.unstack().index[-1]
        tradingprice = self.get_Trading_Twap_by_period(variety, start_date, end_date)
        mergeinfo = pd.concat([prediction, tradingprice],axis=1).dropna()
        mergeinfo.columns=['prediction', 'tradeprice']
        mergeinfo['tsrank'] = (bk.move_rank(mergeinfo['prediction'].values, 237*tslookback)+1)/2
        DealsRtn = {}
        DealsStartTime = {}
        DealsEndTime = {}
        DealsHoldPeriods = {}

        for date in mergeinfo.unstack().index[tslookback+1:]:
            dailydealsrtn = []
            dailydealsstarttime = []
            dailydealsendtime = []
            dailydealsholdperiods = []

            factordaily = mergeinfo.loc[date]
            opentwap = 0
            lastindex = 0

            if factordaily['tsrank'].values[0] >= OpenLong :
                opentwap = factordaily['tradeprice'].values[0]
                lastindex = 0
                dailydealsstarttime.append(factordaily.index[0])

            for i in range(1,len(factordaily)-1):
                if factordaily['tsrank'].values[i] < CloseLong and factordaily['tsrank'].values[i-1] >= CloseLong and len(dailydealsstarttime) != len(dailydealsendtime) :
                    rtn = factordaily['tradeprice'].values[i]/opentwap-1 -fee
                    dailydealsrtn.append(rtn)
                    dailydealsendtime.append(factordaily.index[i])
                    dailydealsholdperiods.append(i-lastindex)

                if factordaily['tsrank'].values[i-1] < OpenLong and factordaily['tsrank'].values[i] >= OpenLong and len(dailydealsstarttime) == len(dailydealsendtime) :
                    opentwap = factordaily['tradeprice'].values[i]
                    dailydealsstarttime.append(factordaily.index[i])
                    lastindex=i

            if len(dailydealsstarttime) == len(dailydealsendtime)+1:
                rtn = factordaily['tradeprice'].values[-1] / opentwap - 1 - fee
                dailydealsrtn.append(rtn)
                dailydealsendtime.append(factordaily.index[-1])
                dailydealsholdperiods.append(237-lastindex)

            DealsRtn[date] = dailydealsrtn
            DealsStartTime[date] = dailydealsstarttime
            DealsEndTime[date] = dailydealsendtime
            DealsHoldPeriods[date] = dailydealsholdperiods

        result_long = {}
        for date in DealsRtn.keys():
            tmp = pd.DataFrame([DealsRtn[date], DealsStartTime[date], DealsEndTime[date], DealsHoldPeriods[date]]).transpose()
            result_long[date] = tmp

        result_long = pd.concat(result_long)
        result_long.columns=['rtn', 'starttime', 'endtime', 'holdperiods']

        DealsRtn = {}
        DealsStartTime = {}
        DealsEndTime = {}
        DealsHoldPeriods = {}

        for date in mergeinfo.unstack().index[tslookback+1:]:
            dailydealsrtn = []
            dailydealsstarttime = []
            dailydealsendtime = []
            dailydealsholdperiods = []

            factordaily = mergeinfo.loc[date]
            opentwap = 0
            lastindex = 0

            if factordaily['tsrank'].values[0] <= OpenShort :
                opentwap = factordaily['tradeprice'].values[0]
                lastindex = 0
                dailydealsstarttime.append(factordaily.index[0])

            for i in range(1,len(factordaily)-1):
                if factordaily['tsrank'].values[i] > CloseShort and factordaily['tsrank'].values[i-1] <= CloseShort and len(dailydealsstarttime) != len(dailydealsendtime) :
                    rtn = factordaily['tradeprice'].values[i]/opentwap-1+fee
                    dailydealsrtn.append(rtn)
                    dailydealsendtime.append(factordaily.index[i])
                    dailydealsholdperiods.append(i-lastindex)

                if factordaily['tsrank'].values[i-1] > OpenShort and factordaily['tsrank'].values[i] <= OpenShort and len(dailydealsstarttime) == len(dailydealsendtime) :
                    opentwap = factordaily['tradeprice'].values[i]
                    dailydealsstarttime.append(factordaily.index[i])
                    lastindex=i

            if len(dailydealsstarttime) == len(dailydealsendtime) + 1:
                rtn = factordaily['tradeprice'].values[-1] / opentwap - 1 + fee
                dailydealsrtn.append(rtn)
                dailydealsendtime.append(factordaily.index[-1])
                dailydealsholdperiods.append(237-lastindex)

            DealsRtn[date] = dailydealsrtn
            DealsStartTime[date] = dailydealsstarttime
            DealsEndTime[date] = dailydealsendtime
            DealsHoldPeriods[date] = dailydealsholdperiods

        result_short = {}
        for date in DealsRtn.keys():
            tmp = pd.DataFrame([DealsRtn[date], DealsStartTime[date], DealsEndTime[date], DealsHoldPeriods[date]]).transpose()
            result_short[date] = tmp

        result_short = pd.concat(result_short)
        result_short.columns=['rtn', 'starttime', 'endtime', 'holdperiods']

        RESULT={}
        RESULT['long'] = result_long
        RESULT['short'] = result_short

        tmp = pd.concat(RESULT)['rtn'].unstack(0)
        DailyDealNum = (~tmp.isnull()).groupby(level=0).sum().mean()
        AvgHoldPeriods = pd.concat(RESULT).unstack(0)['holdperiods'].groupby(level=0).mean().mean()
        SegementDailyReturn = pd.concat(RESULT).unstack(0)['rtn'].fillna(0).groupby(level=0).sum()*100
        Longshort = (SegementDailyReturn['long']-SegementDailyReturn['short'])

        ProfitPerDeal = pd.concat(RESULT)['rtn'].unstack(0).mean()*100

        SegementDailyReturn.cumsum().plot(title='Daily Profit Segment Curve')
        plt.xticks(rotation=45)
        plt.show()

        ProfitPerDeal.plot(kind='bar', title='Profit Per Deal Segment Curve')
        plt.show()

        summary = pd.concat([ProfitPerDeal ,DailyDealNum,AvgHoldPeriods,SegementDailyReturn.mean()],axis=1)
        summary.columns=['ProfitPerDeal (%)', 'DailyDealNum', 'AvgHoldPeriods', 'DailyReturn (%)']
        print(summary.transpose())
        Longshort.cumsum().plot(title='Long Short Curve')
        plt.xticks(rotation=45)
        plt.show()

        AutoCorr_1min = mergeinfo['tsrank'].corr(mergeinfo['tsrank'].shift(1))
        AutoCorr_5min = mergeinfo['tsrank'].corr(mergeinfo['tsrank'].shift(5))

        mergeinfo['future_rtn15min'] = mergeinfo.unstack(0).sort_index()['tradeprice'].pct_change(15).shift(-15).unstack()
        mergeinfo['future_rtn30min'] = mergeinfo.unstack(0).sort_index()['tradeprice'].pct_change(30).shift(-30).unstack()

        corr_30min_daily = mergeinfo.dropna()['tsrank'].rolling(237*tslookback).corr(mergeinfo.dropna()['future_rtn30min']).groupby(level=0).mean()
        corr_30min_daily.cumsum().plot(title='Tsrank 30-Minute Correlation (Cumulative)')
        plt.xticks(rotation=45)
        plt.show()
        
        summarydict = {}
        summarydict['LongShortAnualReturn (%)'] =  Longshort.mean()*250
        summarydict['LongShortSR'] = Longshort.mean()/Longshort.std()
        summarydict['LongShortMDD'] = (Longshort.cumsum()-Longshort.cumsum().expanding().max()).min()
        summarydict['LongShortWinningRate %'] = len(Longshort[Longshort>=0])/len(Longshort) *100
        summarydict['AutoCorr_1Min(ts)'] = AutoCorr_1min
        summarydict['AutoCorr_5Min(ts)'] = AutoCorr_5min
        summarydict['IC_30Min']  = mergeinfo['prediction'].corr(mergeinfo['future_rtn30min'])
        summarydict['IC_30Min(ts)']  = mergeinfo['tsrank'].corr(mergeinfo['future_rtn30min'])
        summarydict['BacktestPeroids']  = len(mergeinfo.unstack().index[tslookback+1:])
        summarydict = pd.DataFrame(summarydict, index=['prediction']).transpose()
        print(summarydict)
        return RESULT

    
    def calc_sharpe_perdeal_for_tsfactor_list(self, factor_list, variety, start_date, end_date, groupnum=10):
        res_df = pd.DataFrame(np.nan, index=factor_list, columns=['sharpe', 'perdeal_diff'])
        for f in factor_list:
            factor_df = pd.read_hdf('{}/factor_tsrank/{}/{}.h5'.format(self.__store_data_path, variety, f))
            _, sharpe, perdeal_diff = self.calc_statistic_by_factor_tsrank_df(factor_df, variety, start_date, end_date, groupnum)
            res_df.loc[f] = [sharpe, perdeal_diff]
        return res_df