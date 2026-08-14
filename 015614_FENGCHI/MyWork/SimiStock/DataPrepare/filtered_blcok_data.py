# coding: utf-8
# Author：fengchi863
# Date ：2022/5/26 11:16

from SimiStock.dataApi import getData, stockList, tradeDate
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import pandas as pd
from SimiStock.SimiBackTest.FunctionApi import rolling_corr, get_date_list
from CrossFT.basic.operators import dt_corr2, dt_pct
import numpy as np


class FileterMethod:
    def __init__(self, trade_date=None):
        lag = 260
        if trade_date is None:
            today = tradeDate.get_today(dividing_point=23)
        else:
            today = trade_date
        date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(today, lag), today)
        pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list)
        close = getData.get_daily_1factor('close_badj', date_list=date_list)
        rong_df = pd.read_pickle(data_path + '2rong.pkl')
        clean_stock = pd.read_pickle(data_path + 'clean_stock.pkl')
        concept_df = getData.get_daily_1factor('SW20211', date_list=date_list)
        concept_df = concept_df.bfill()

        self.date_list = date_list
        self.pctchg = pctchg
        self.close = close
        self.rong_df = rong_df
        self.clean_stock = clean_stock
        self.concept_df = concept_df
        self.today_date = today
        self.long_period = 240
        self.middle_period = 120
        self.short_period = 60

    def get_concept_list(self, stk_id, trade_date):
        row = self.concept_df.loc[trade_date]
        ind_code = row[stk_id]
        stk_list = row[row == ind_code].index.tolist()
        rong_row = self.rong_df.loc[trade_date]
        rong_list = rong_row[rong_row == 1].index.tolist()
        stk_list = list(set(stk_list).intersection(set(rong_list)))
        clean_row = self.clean_stock.loc[trade_date]
        clean_list = clean_row[clean_row == 1].index.tolist()
        stk_list = list(set(stk_list).intersection(set(clean_list)))
        if stk_id in stk_list:
            stk_list.remove(stk_id)
        return stk_list

    @staticmethod
    def get_trade_days(date, trade_days, delay, type):
        if type == 'history':
            if delay > 0:
                return get_date_list(20130101, date)[-trade_days - delay:-delay]
            else:
                return get_date_list(20130101, date)[-trade_days - delay:]
        if type == 'future':
            now_date = tradeDate.get_today(17)
            return get_date_list(date, now_date)[delay:trade_days + delay]

    def judge_filter(self, stk_id):
        # %% 剔除规则1：波动率较大的
        long_std = self.pctchg.apply(lambda x: x.dropna().rolling(self.long_period).std())
        short_std = self.pctchg.apply(lambda x: x.dropna().rolling(self.short_period).std())

        long_std_90pct = long_std.quantile(0.9, axis=1)
        short_std_90pct = short_std.quantile(0.9, axis=1)
        long_flag = long_std[stk_id].iloc[-10:].mean() > long_std_90pct.iloc[-10:].mean()
        short_flag = short_std[stk_id].iloc[-10:].mean() > short_std_90pct.iloc[-10:].mean()
        filter1_flag = long_flag | short_flag

        # %% 剔除规则2：剔除相似度下降较大的
        concept_list = self.get_concept_list(stk_id, self.today_date)
        # ind_code = self.concept_df.loc[self.today_date, stk_id]
        # long_days = self.get_trade_days(self.today_date, trade_days=240, delay=0, type='history')
        # middle_days = self.get_trade_days(self.today_date, trade_days=120, delay=0, type='history')
        # short_days = self.get_trade_days(self.today_date, trade_days=60, delay=0, type='history')

        result = pd.Series()
        copy_pctchg = pd.DataFrame()
        for i in range(len(concept_list)):
            copy_pctchg[i] = self.pctchg.loc[:self.today_date, stk_id]

        # mid_corr = rolling_corr(self.pctchg.loc[:self.today_date, concept_list], copy_pctchg, window=self.middle_period)
        # short_corr = rolling_corr(self.pctchg.loc[:self.today_date, concept_list], copy_pctchg, window=self.short_period)
        mid_corr = dt_corr2(self.pctchg.loc[:self.today_date, concept_list].values[:, None, :], copy_pctchg.values[:, None, :], self.middle_period)
        short_corr = dt_corr2(self.pctchg.loc[:self.today_date, concept_list].values[:, None, :], copy_pctchg.values[:, None, :], self.short_period)
        mid_corr = pd.DataFrame(mid_corr[:, 0, :], index=copy_pctchg.index, columns=concept_list)
        short_corr = pd.DataFrame(short_corr[:, 0, :], index=copy_pctchg.index, columns=concept_list)

        now_mid_corr = mid_corr.iloc[-10:].mean().sort_values(ascending=False)
        now_short_corr = short_corr.iloc[-10:].mean().sort_values(ascending=False)

        use_stk_list = now_mid_corr.index[:10].tolist()

        result.loc['中期相似度'] = now_mid_corr.loc[use_stk_list].mean()
        result.loc['中期相似度历史分位数'] = mid_corr[use_stk_list].iloc[-360:].rank(pct=True).iloc[-10:].mean().mean()

        result.loc['短期相似度'] = now_short_corr.loc[use_stk_list].mean()
        result.loc['短期相似度历史分位数'] = short_corr[use_stk_list].iloc[-360:].rank(pct=True).iloc[-10:].mean().mean()

        _flag1 = (result['中期相似度'] - result['短期相似度']) > 0.2
        _flag2 = ((result['中期相似度'] < 0.5) | (result['短期相似度'] < 0.5)) & (result['中期相似度'] > 0.9)

        # %% 剔除规则3：剔除涨跌幅异动较为明显的
        pct_long = self.close.loc[:self.today_date, stk_id].pct_change(self.long_period) > 0.3
        pct_short = self.close.loc[:self.today_date, stk_id].pct_change(self.short_period) > 0.3
        pct_flag = pct_long.loc[self.today_date] & pct_short.loc[self.today_date]
        return filter1_flag | _flag1 | _flag2 | pct_flag


if __name__ == '__main__':
    fm = FileterMethod(20220526)
    bl = fm.judge_filter(603712)
