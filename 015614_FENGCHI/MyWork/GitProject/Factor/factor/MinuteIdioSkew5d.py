# -*- coding: utf-8 -*-

"""

*因子名 : MinuteIdioSkew5d
*因子功能描述 :  FamaFrench三因子残差，5分钟级别，残差的偏度

*因子参数 : MinuteClose, mkt_cap_ard, bps, close
*作者 : 刘正
*因子创建日期 : 2018.12.25

"""
import mkl
mkl.set_num_threads(10)    
from sklearn.linear_model import LinearRegression

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class MinuteIdioSkew5d(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.mkt_cap_ard",
                   "FactorData.Basic_factor.close", "FactorData.WIND_AShareFinancialIndicator","FactorData.Basic_factor.is_valid"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 0
    minute_lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    reform_window = 5
    financial_lag = 200

    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):
        data_minute = {"FactorData.Basic_factor.close_minute":database.depend_data["FactorData.Basic_factor.close_minute"]}
        minute_data_transform(data_minute,operation=['drop','merge'])

        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        data = database.depend_data['FactorData.WIND_AShareFinancialIndicator']
        # data = data[data['STATEMENT_TYPE']==408001000]

        bps = data['S_FA_BPS'].unstack().fillna(method='ffill').reindex(columns=is_valid.columns).iloc[-1]
        
        close_minute = data_minute['FactorData.Basic_factor.close_minute']

        is_valid_one = pd.DataFrame(is_valid.values==1,index=is_valid.index,columns=is_valid.columns)
        status = ~is_valid_one

        mkt_cap_rank = database.depend_data['FactorData.Basic_factor.mkt_cap_ard'][is_valid_one]
        bps = bps[is_valid_one.columns]
        close = database.depend_data['FactorData.Basic_factor.close'][is_valid_one]
        
        book_to_price = bps/close

        date_list = np.unique(close_minute.index.strftime('%Y%m%d'))
        
        IdioSkew  = []

        for date in date_list:
            MinuteCloseDay5min = close_minute.loc[date]
            MinuteCloseDay5min  = MinuteCloseDay5min.asfreq(freq='5Min').dropna(how ='all')
    
            re = MinuteCloseDay5min/MinuteCloseDay5min.shift(1) - 1
            invalid_stock = status.loc[:,status.loc[date]].columns
            re.loc[:,invalid_stock] = np.nan
            re = re.replace(np.inf, 0)
            re = re.replace(-np.inf, 0)
    
            mkt_cap_rank_today  = mkt_cap_rank.loc[date].sort_values().dropna()
            book_to_price_today = book_to_price.loc[date].sort_values().dropna()
    
            small_stocks   = mkt_cap_rank_today[:int(len(mkt_cap_rank_today)/3)].index
            large_stocks   = mkt_cap_rank_today[-int(len(mkt_cap_rank_today)/3):].index
            low_bp_stocks  = book_to_price_today[:int(len(book_to_price_today)/3)].index
            high_bp_stocks = book_to_price_today[-int(len(book_to_price_today)/3):].index
    
            small_stocks_weight   = mkt_cap_rank_today[small_stocks] / mkt_cap_rank_today[small_stocks].sum()
            large_stocks_weight   = mkt_cap_rank_today[large_stocks] / mkt_cap_rank_today[large_stocks].sum()
            low_bp_stocks_weight  = mkt_cap_rank_today[low_bp_stocks] / mkt_cap_rank_today[low_bp_stocks].sum()
            high_bp_stocks_weight = mkt_cap_rank_today[high_bp_stocks] / mkt_cap_rank_today[high_bp_stocks].sum()
    
            small_ret   = (small_stocks_weight * re.loc[:,small_stocks]).sum(axis=1)
            large_ret   = (large_stocks_weight * re.loc[:, large_stocks]).sum(axis=1)
            low_bp_ret  = (low_bp_stocks_weight * re.loc[:, low_bp_stocks]).sum(axis=1)
            high_bp_ret = (high_bp_stocks_weight * re.loc[:, high_bp_stocks]).sum(axis=1)
    
            mkt_weight = mkt_cap_rank_today / mkt_cap_rank_today.sum()
            mkt = (mkt_weight * re.loc[:, mkt_cap_rank_today.index]).sum(axis=1)
            smb = small_ret - large_ret
            hml = high_bp_ret - low_bp_ret
    
            X = pd.concat([mkt, smb, hml], axis = 1).iloc[1:]
            idio_degree = {}
            resid_skew_stock = {}
            for stock in re.columns:
                if stock in invalid_stock:
                    idio_degree[stock] = np.nan
                    resid_skew_stock[stock] = np.nan
                    continue
                y = re[stock].iloc[1:]
                y = y.fillna(0)
                X = X.fillna(0)
                model = LinearRegression(n_jobs=1)
                model.fit(X, y)
                yhat = model.predict(X)
    
                SS_Residual = sum((y - yhat) ** 2)
                SS_Total = sum((y - np.mean(y)) ** 2)
                resid_skew_stock[stock] = (y - yhat).skew()
            resid_skew_stock = pd.Series(resid_skew_stock)
            resid_skew_stock.name = date
            IdioSkew.append(resid_skew_stock)
        IdioSkew = pd.DataFrame(IdioSkew)
        IdioSkew.index = pd.to_datetime(IdioSkew.index)
        return IdioSkew.iloc[-1]
    #
    #

    def reform(self, temp_result):
        return -temp_result.rolling(window=self.reform_window,min_periods=1).mean()

    # def definition(self, MinuteClose, is_valid_raw, Minute_Status, mkt_cap_ard, bps, close):
    #
    #     factor = self.minute_help(self.minute, 'MinuteIdioSkew5dHelp', MinuteClose, Minute_Status, mkt_cap_ard, bps,close, is_valid_raw)
    #     factor[(is_valid_raw == 0)|(Minute_Status == 1)|(Minute_Status == 2)|(Minute_Status == 3)|(Minute_Status == 5)] = np.nan
    #     factor = -factor.rolling(window=5,min_periods=1).mean()
    #     return factor
    #
    # def minute(self, MinuteClose, Minute_Status, mkt_cap_ard, bps, close, is_valid_raw):
    #
    #     status = (is_valid_raw == 0)|(Minute_Status == 1)|(Minute_Status == 2)|(Minute_Status == 3)|(Minute_Status == 5)
    #     mkt_cap_rank = mkt_cap_ard[is_valid_raw == 1]
    #     book_to_price = (bps/close)[is_valid_raw == 1]
    #
    #     date_list = np.unique(MinuteClose.index.strftime('%Y%m%d'))
    #     IdioSkew  = []
    #     for date in date_list:
    #         MinuteCloseDay5min = MinuteClose.loc[date]
    #         MinuteCloseDay5min  = MinuteCloseDay5min.asfreq(freq='5Min').dropna(how ='all')
    #
    #         re = MinuteCloseDay5min/MinuteCloseDay5min.shift(1) - 1
    #         invalid_stock = status.loc[:,status.loc[date]].columns
    #         re.loc[:,invalid_stock] = np.nan
    #         re = re.replace(np.inf, 0)
    #         re = re.replace(-np.inf, 0)
    #
    #         mkt_cap_rank_today  = mkt_cap_rank.loc[date].sort_values().dropna()
    #         book_to_price_today = book_to_price.loc[date].sort_values().dropna()
    #
    #         small_stocks   = mkt_cap_rank_today[:int(len(mkt_cap_rank_today)/3)].index
    #         large_stocks   = mkt_cap_rank_today[-int(len(mkt_cap_rank_today)/3):].index
    #         low_bp_stocks  = book_to_price_today[:int(len(book_to_price_today)/3)].index
    #         high_bp_stocks = book_to_price_today[-int(len(book_to_price_today)/3):].index
    #
    #         small_stocks_weight   = mkt_cap_rank_today[small_stocks] / mkt_cap_rank_today[small_stocks].sum()
    #         large_stocks_weight   = mkt_cap_rank_today[large_stocks] / mkt_cap_rank_today[large_stocks].sum()
    #         low_bp_stocks_weight  = mkt_cap_rank_today[low_bp_stocks] / mkt_cap_rank_today[low_bp_stocks].sum()
    #         high_bp_stocks_weight = mkt_cap_rank_today[high_bp_stocks] / mkt_cap_rank_today[high_bp_stocks].sum()
    #
    #         small_ret   = (small_stocks_weight * re.loc[:,small_stocks]).sum(axis=1)
    #         large_ret   = (large_stocks_weight * re.loc[:, large_stocks]).sum(axis=1)
    #         low_bp_ret  = (low_bp_stocks_weight * re.loc[:, low_bp_stocks]).sum(axis=1)
    #         high_bp_ret = (high_bp_stocks_weight * re.loc[:, high_bp_stocks]).sum(axis=1)
    #
    #         mkt_weight = mkt_cap_rank_today / mkt_cap_rank_today.sum()
    #         mkt = (mkt_weight * re.loc[:, mkt_cap_rank_today.index]).sum(axis=1)
    #         smb = small_ret - large_ret
    #         hml = high_bp_ret - low_bp_ret
    #
    #         X = pd.concat([mkt, smb, hml], axis = 1).iloc[1:]
    #         idio_degree = {}
    #         resid_skew_stock = {}
    #         for stock in re.columns:
    #             if stock in invalid_stock:
    #                 idio_degree[stock] = np.nan
    #                 resid_skew_stock[stock] = np.nan
    #                 continue
    #             y = re[stock].iloc[1:]
    #             y = y.fillna(0)
    #             X = X.fillna(0)
    #             model = LinearRegression(n_jobs=1)
    #             model.fit(X, y)
    #             yhat = model.predict(X)
    #
    #             SS_Residual = sum((y - yhat) ** 2)
    #             SS_Total = sum((y - np.mean(y)) ** 2)
    #             resid_skew_stock[stock] = (y - yhat).skew()
    #         resid_skew_stock = pd.Series(resid_skew_stock)
    #         resid_skew_stock.name = date
    #         IdioSkew.append(resid_skew_stock)
    #     IdioSkew = pd.DataFrame(IdioSkew)
    #     IdioSkew.index = pd.to_datetime(IdioSkew.index)
    #     return IdioSkew
    #
    #