# coding: utf-8
# Author：fengchi863
# Date ：2022/1/10 14:36

import bottleneck as bn
import numpy as np
import pandas as pd
from xquant.factordata import FactorData

from FaaMonitor.Util.MyUtil import MyUtil
from PEWork.Base.StockFilterBase import StockFilterBase
from ShortTermTrading.Util.tools import save_xlsx
from ShortTermTrading.conf.path_conf import junk_path, param_path
from ShortTermTrading.dataApi import stockList


class GaiDieBuDie(StockFilterBase):
    def __init__(self, start_date, end_date):
        super().__init__(start_date, end_date)
        self.rps_threshold = 0.7

        # 申万二级行业指数
        raw_sw2_df = pd.read_excel(param_path + '申万二级指数2021.xlsx', index_col=0)
        sw2_code_list = raw_sw2_df.index.tolist()

        fd = FactorData()
        sw_ind_df = fd.get_factor_value('WIND_SWIndexMembers',
                                        factors=['S_CON_WINDCODE', 'S_INFO_WINDCODE', 'CUR_SIGN'],
                                        S_INFO_WINDCODE=sw2_code_list).set_index('S_CON_WINDCODE')
        sw_ind_df = sw_ind_df.query('CUR_SIGN == 1').sort_index()
        sw_ind_df.index = sw_ind_df.index.map(lambda x: stockList.trans_windcode2int(x))

        sw_code_ind_dict = sw_ind_df['S_INFO_WINDCODE'].to_dict()

        sw2_info = fd.get_factor_value('WIND_ASWSIndexEOD',
                                       factor_names=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_CLOSE', 'S_DQ_AMOUNT'],
                                       S_INFO_WINDCODE=sw2_code_list,
                                       TRADE_DT=[f'>={self.cal_start_date}'])
        sw2_close = sw2_info.pivot(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_CLOSE')
        sw2_close.index = sw2_close.index.map(int)
        sw2_close = sw2_close.loc[self.cal_start_date:self.end_date]
        sw2_close_pctchg = sw2_close.pct_change(1)

        wind_close_df = fd.get_factor_value('WIND_AIndexWindIndustriesEOD',
                                            factors=['TRADE_DT', 'S_DQ_CLOSE'],
                                            TRADE_DT=[f'>={self.cal_start_date}'],
                                            S_INFO_WINDCODE=['8841388.WI']).sort_values('TRADE_DT')
        wind_close_df = wind_close_df.set_index('TRADE_DT', drop=True)
        wind_close_df.index = wind_close_df.index.map(int)
        wind_close_df = wind_close_df.loc[self.cal_start_date:self.end_date]
        wind_pctchg = wind_close_df.pct_change(1)

        self.stats_df = None
        self.sw2_code_list = sw2_code_list
        self.sw2_close_pctchg = sw2_close_pctchg
        self.sw_code_ind_dict = sw_code_ind_dict
        self.wind_pctchg = wind_pctchg

    def rps(self, close, timeperiod):
        pctchg = close.pct_change(timeperiod)
        pctchg_quantile = pd.DataFrame(bn.nanrankdata(pctchg, axis=1) / np.nansum(np.isfinite(pctchg).values, axis=1)[:, None]
                                       > self.rps_threshold, index=pctchg.index, columns=pctchg.columns)
        return pctchg_quantile

    def rps_cond(self):
        rps_60d = self.rps(self.daily_close_badj, 60)
        rps_60d = pd.DataFrame(rps_60d.values, index=rps_60d.index, columns=rps_60d.columns)
        rps_60d = rps_60d.rolling(10).sum() > 0
        return rps_60d

    def get_strong_pool(self):
        rps_cond = self.rps_cond()
        strong_pool = rps_cond

        # stats
        daily_rps_cond_num = rps_cond.sum(axis=1)
        daily_strong_pool_sum = strong_pool.sum(axis=1)

        stats_df = pd.concat([daily_rps_cond_num, daily_strong_pool_sum], axis=1)
        stats_df.columns = ['rps_num', 'strong_num']
        # save_xlsx(stats_df, junk_path, 'strong_num.xlsx')
        self.stats_df = stats_df

        return strong_pool

    def get_sw2_close_pctchg(self, stk_id):
        if stk_id not in self.sw_code_ind_dict.keys():
            return [np.nan] * len(self.cal_date_list)
        else:
            return self.sw2_close_pctchg[self.sw_code_ind_dict[stk_id]].tolist()

    def sw2_down_stk_up(self):
        daily_sw2_pctchg = pd.DataFrame().reindex_like(self.daily_pctchg)
        for stk_id in daily_sw2_pctchg.columns:
            daily_sw2_pctchg[stk_id] = self.get_sw2_close_pctchg(stk_id)
        cond1 = daily_sw2_pctchg < -0.02
        cond2 = (self.daily_pctchg - daily_sw2_pctchg) > 0.02
        cond = cond1 & cond2
        return cond

    def index_down_stk_up(self):
        daily_wind_pctchg = pd.DataFrame(np.repeat(self.wind_pctchg.values, len(self.stk_list), axis=1),
                                         index=self.cal_date_list, columns=self.stk_list)
        cond1 = pd.DataFrame(daily_wind_pctchg.values < -0.01, index=self.cal_date_list, columns=self.stk_list)
        cond2 = (self.daily_pctchg - daily_wind_pctchg) > 0.02
        cond = cond1 & cond2
        return cond

    def long_up_shadow(self):
        cond1 = (self.daily_high_badj - np.maximum(self.daily_close_badj, self.daily_open_badj)) / (self.daily_high_badj - self.daily_low_badj) > 0.4
        cond2 = (self.daily_high_badj - self.daily_low_badj) / self.daily_low_badj > 0.02
        return cond1 & cond2

    def tomorrow_pctchg(self, threshold=0):
        cond = self.daily_pctchg > threshold
        return cond

    def yesterday_big_down(self, threshold=-0.03):
        cond = self.daily_pctchg < threshold
        return cond

    def gdbd_cond1(self):
        cond1 = self.long_up_shadow().shift(1)
        cond2 = self.tomorrow_pctchg(threshold=0)

        cond = cond1 & cond2
        return cond

    def gdbd_cond2(self):
        cond = self.sw2_down_stk_up()
        return cond

    def gdbd_cond3(self):
        cond = self.index_down_stk_up()
        return cond

    def gdbd_cond4(self):
        cond1 = self.yesterday_big_down(threshold=-0.03).shift(1)
        cond2 = self.tomorrow_pctchg(threshold=0)
        cond = cond1 & cond2
        return cond

    def get_gdbd_pool(self):
        strong_pool = self.get_strong_pool()
        gdbd_cond1 = self.gdbd_cond1()
        gdbd_cond2 = self.gdbd_cond2()
        gdbd_cond3 = self.gdbd_cond3()
        gdbd_cond4 = self.gdbd_cond4()
        gdbd = gdbd_cond1 | gdbd_cond2 | gdbd_cond3 | gdbd_cond4
        gdbd_times = gdbd.rolling(10).sum()
        gdbd_pool = gdbd_times > 3

        all_cond = strong_pool & gdbd_pool

        # stats
        gdbd_cond1_sum = gdbd_cond1.sum(axis=1)
        gdbd_cond2_sum = gdbd_cond2.sum(axis=1)
        gdbd_cond3_sum = gdbd_cond3.sum(axis=1)
        gdbd_cond4_sum = gdbd_cond4.sum(axis=1)
        daily_gdbd_pool = gdbd_pool.sum(axis=1)
        daily_all_cond = all_cond.sum(axis=1)

        stats_df1 = self.stats_df
        stats_df2 = pd.concat([gdbd_cond1_sum, gdbd_cond2_sum, gdbd_cond3_sum, gdbd_cond4_sum,
                               daily_gdbd_pool, daily_all_cond], axis=1)
        stats_df2.columns = ['长上影次日不跌', '相对SW2不跌', '相对大盘不跌', '大跌次日不跌',
                             '该跌不跌总数量', '叠加强势股后数量']
        stats_df = pd.concat([stats_df1, stats_df2], axis=1)
        stats_df = stats_df.loc[self.start_date:self.end_date]
        save_xlsx(stats_df, junk_path, 'strong_num.xlsx')
        return all_cond.loc[self.start_date:self.end_date]

    def check_all_cond_stock(self):
        ret = self.get_gdbd_pool()
        daily_stock = ret.stack()[ret.stack()]
        daily_stock = pd.DataFrame(daily_stock).reset_index().drop([0], axis=1)
        daily_stock.columns = ['日期', '股票代码']
        daily_stock = daily_stock.set_index('日期', drop=True)
        daily_stock['股票名称'] = daily_stock['股票代码'].apply(lambda x: MyUtil.get_1stock_name(x))
        daily_stock = daily_stock.loc[self.start_date:self.end_date]
        save_xlsx(daily_stock, junk_path, '该跌不跌每日股票池.xlsx')

        latest_gdbd_stk = daily_stock.loc[self.end_date]
        save_xlsx(latest_gdbd_stk, junk_path, f'该跌不跌股票池{self.end_date}.xlsx')
        return daily_stock


if __name__ == '__main__':
    gdbd = GaiDieBuDie(20211201, 20220124)
    ret = gdbd.check_all_cond_stock()


