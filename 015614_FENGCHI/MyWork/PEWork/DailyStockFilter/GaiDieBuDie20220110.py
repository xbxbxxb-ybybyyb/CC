# coding: utf-8
# Author：fengchi863
# Date ：2022/1/10 14:36

import bottleneck as bn
import numpy as np
import pandas as pd

from FaaMonitor.Util.MyUtil import MyUtil
from PEWork.Base.StockFilterBase import StockFilterBase
from ShortTermTrading.Util.tools import save_xlsx
from ShortTermTrading.conf.path_conf import junk_path


class GaiDieBuDie(StockFilterBase):
    def __init__(self, start_date, end_date):
        super().__init__(start_date, end_date)
        self.rps_threshold = 80

        self.stats_df = None

    def rps(self, close, timeperiod):
        pctchg = close.pct_change(timeperiod)
        pctchg_quantile = pd.DataFrame(bn.nanrankdata(pctchg, axis=1) / bn.nansum(np.isfinite(pctchg), axis=1)[:, None]
                                       > self.rps_threshold, index=pctchg.index, columns=pctchg.columns)
        return pctchg_quantile

    def rps_cond(self):
        rps_5d = self.rps(self.daily_close_badj, 5)
        rps_20d = self.rps(self.daily_close_badj, 20)
        rps_60d = self.rps(self.daily_close_badj, 60)
        rps_120d = self.rps(self.daily_close_badj, 120)
        rps_all = pd.DataFrame(rps_5d.values | rps_20d.values | rps_60d.values | rps_120d.values,
                               index=rps_5d.index, columns=rps_5d.columns)
        return rps_all

    def amt_cond(self):
        ret = self.daily_amt.rolling(5).mean() > self.daily_amt.rolling(20).mean()
        return ret

    def ma_cond(self):
        ma5 = self.daily_close_badj.rolling(5).mean()
        ma20 = self.daily_close_badj.rolling(20).mean()
        ret = ma5 > ma20
        return ret

    def get_strong_pool(self):
        rps_cond = self.rps_cond()
        amt_cond = self.amt_cond()
        ma_cond = self.ma_cond()

        strong_pool = rps_cond & amt_cond & ma_cond

        # stats
        daily_rps_cond_num = rps_cond.sum(axis=1)
        daily_amt_cond_num = amt_cond.sum(axis=1)
        daily_ma_cond_sum = ma_cond.sum(axis=1)
        daily_strong_pool_sum = strong_pool.sum(axis=1)

        stats_df = pd.concat([daily_rps_cond_num, daily_amt_cond_num, daily_ma_cond_sum, daily_strong_pool_sum], axis=1)
        stats_df.columns = ['rps_num', 'amt_num', 'ma_num', 'strong_num']
        # save_xlsx(stats_df, junk_path, 'strong_num.xlsx')
        self.stats_df = stats_df

        return strong_pool

    def long_up_shadow(self):
        cond1 = (self.daily_high_badj - self.daily_close_badj) / (self.daily_high_badj - self.daily_low_badj) > 0.4
        cond2 = (self.daily_high_badj - self.daily_close_badj) / self.daily_close_badj > 0.02
        return cond1 & cond2

    def yesterday_big_down(self):
        ret = self.daily_pctchg < -0.03
        return ret

    def horizon_after_big_down(self):
        cond1 = self.daily_close_badj / self.daily_high_badj.rolling(5).max() - 1 < -0.1
        cond2 = (self.daily_high_badj.rolling(2).max() - self.daily_low_badj.rolling(2).min()) / \
                self.daily_low_badj.rolling(2).min() - 1 < -0.03
        return cond1 & cond2

    def get_gdbd_pool(self):
        strong_pool = self.get_strong_pool()
        long_up_shadow = self.long_up_shadow()
        yesterday_big_down = self.yesterday_big_down()
        horizon_after_big_down = self.horizon_after_big_down()
        gdbd_pool = long_up_shadow | yesterday_big_down | horizon_after_big_down

        all_cond = strong_pool & gdbd_pool

        # stats
        daily_long_up_shadow_sum = long_up_shadow.sum(axis=1)
        daily_yesterday_big_down_num = yesterday_big_down.sum(axis=1)
        daily_horizon_after_big_down_num = horizon_after_big_down.sum(axis=1)
        daily_gdbd_pool = gdbd_pool.sum(axis=1)
        daily_all_cond = all_cond.sum(axis=1)

        stats_df1 = self.stats_df
        stats_df2 = pd.concat([daily_long_up_shadow_sum, daily_yesterday_big_down_num,
                              daily_horizon_after_big_down_num, daily_gdbd_pool, daily_all_cond], axis=1)
        stats_df2.columns = ['long_up_shadow_num', 'yesterday_big_down_num', 'horizon_after_big_down_num',
                             'gdbd_pool', 'all_cond']
        stats_df = pd.concat([stats_df1, stats_df2], axis=1)
        save_xlsx(stats_df, junk_path, 'strong_num.xlsx')
        return all_cond

    def check_all_cond_stock(self):
        ret = self.get_gdbd_pool()
        daily_stock = ret.stack()[ret.stack()]
        daily_stock = pd.DataFrame(daily_stock).reset_index().drop([0], axis=1)
        daily_stock.columns = ['日期', '股票代码']
        daily_stock = daily_stock.set_index('日期', drop=True)
        daily_stock['股票名称'] = daily_stock['股票代码'].apply(lambda x: MyUtil.get_1stock_name(x))
        daily_stock = daily_stock.loc[self.start_date:self.end_date]
        save_xlsx(daily_stock, junk_path, '该跌不跌每日股票池.xlsx')
        return daily_stock


if __name__ == '__main__':
    gdbd = GaiDieBuDie(20211001, 20220106)
    ret = gdbd.check_all_cond_stock()

