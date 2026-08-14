# coding: utf-8
# Author：fengchi863
# Date ：2021/3/5 15:37

from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare

class TickData:
    def __init__(self, start_date=20140101, end_date=20210228, start_tick=91500, end_tick=150000, return_idx=True):
        dp = TickDataPrepare()

        self.dp = dp
        self.start_date = start_date
        self.end_date = end_date
        self.start_tick = start_tick
        self.end_tick = end_tick
        self.return_idx = True

    def get_tick_factor(self, item=None):
        if item is None:
            raise KeyError('item must be given')
        ret = self.dp.get_data_by_date_list(item=item,
                                          start_date=self.start_date,
                                          end_date=self.end_date,
                                          date_list=None,
                                          start_tick=self.start_tick,
                                          end_tick=self.end_tick,
                                          tick_list=None,
                                          return_idx=self.return_idx
                                         )
        return ret

def trans_daily_to_tick(df, sup_df):
    df =df.shift(1).stack().reset_index()
    df.columns=['date','code','factor']
    df = df.set_index(['date','code']).loc[sup_df.index]
    df_inday = sup_df.mul(df.loc[sup_df.index,'factor'],axis=0)
    return df_inday

