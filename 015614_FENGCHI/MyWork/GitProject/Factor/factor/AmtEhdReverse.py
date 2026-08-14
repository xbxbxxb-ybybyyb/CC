# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time

class AmtEhdReverse(BaseFactor):
    
    '''
    * 因子名：AmtEhdReverse
    * 逻辑：该因子是一个反转因子，根据每日的单笔平均成交量做了精细划分
    * 因子参数：日频数据价量与成交笔数
    * 作者：陈卓
    * 日期：2019.4.3
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.amt", "FactorData.Basic_factor.dealnum", 
    "FactorData.Basic_factor.adjfactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 41
    reform_window = 20
    min_reform_window = 10

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        dealnum = database.depend_data['FactorData.Basic_factor.dealnum']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']

        n = 20
        nd = n
        rho = 0.8
        # close_valid = close[is_valid_raw==1] * adjfactor
        close_valid = close * adjfactor
        # amt_valid = amt[is_valid_raw==1]
        amt_valid = amt
        # dn_valid = dealnum[is_valid_raw==1]
        dn_valid = dealnum
        # amt_deal = amt_valid / dn_valid
        amt_deal = amt_valid / dn_valid
        day_netv = close_valid/close_valid.shift(1)
        date = close_valid.index
        # alpha = pd.DataFrame(index=date, columns=close_valid.columns)
        # for i in range(nd, date.size):
        #     day = date[i]
        #     netv = day_netv.loc[day-pd.Timedelta(str(nd)+'d'):day]
        #     apd = amt_deal.loc[day-pd.Timedelta(str(nd)+'d'):day]
        #     alpha.loc[day] = netv[apd > apd.quantile(rho)].product(skipna=True) - netv[apd < apd.quantile(1-rho)].product(skipna=True)
        # alpha = -1. * alpha.rolling(window=nd, min_periods=int(nd/2)).mean()
        end_date = pd.to_datetime(date[-1])
        begin_date = end_date - pd.Timedelta('%sd'%nd)
        netv = day_netv.loc[begin_date.strftime('%Y%m%d'):end_date.strftime('%Y%m%d')]
        apd = amt_deal.loc[begin_date.strftime('%Y%m%d'):end_date.strftime('%Y%m%d')]
        # alpha = netv[apd > apd.quantile(rho)].product(skipna=True) - netv[apd < apd.quantile(1-rho)].product(skipna=True)
        
        a_index = pd.DataFrame(apd.values > apd.quantile(rho).values, index=apd.index, columns=apd.columns)
        alpha_a = netv[a_index].product(skipna=True)
        b_index = pd.DataFrame(apd.values < apd.quantile(1-rho).values, index=apd.index, columns=apd.columns)
        alpha_b = netv[b_index].product(skipna=True)
        
        alpha = alpha_a - alpha_b
        return -alpha

    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=self.min_reform_window).mean()
        return A