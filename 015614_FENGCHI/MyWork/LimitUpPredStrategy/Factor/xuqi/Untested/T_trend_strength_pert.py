# author: kiki_777
# date: 2021/5/20

from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *

class TickData:
    def __init__(self, start_date=20140101, end_date=20201231, start_tick=91500, end_tick=150000, return_idx=True):
        dp = TickDataPrepare('/arch1/group/800442/800319/LimitTickData20210615_20210715/')

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


td = TickData(start_date=20210615, end_date=20210715, start_tick=91500, end_tick=150000, return_idx=True)

dependencies_factors = ['LimitPool','LastPx']
# 导入因子
for item in dependencies_factors:
    exec('%s = td.get_tick_factor(\'%s\')' % (item, item))
stock_pool_stack = LimitPool[LimitPool].stack()

save_path='/data/group/800442/800319/ZTfactors/20210615-20210715/'
factor_name = 't_trend_strength_pert' ###日内价格位移/日内价格速度

AbsPxChg = abs(LastPx.pct_change(1, axis=1)).expanding(axis=1).mean()
open = get_daily_1factor('open', date_list=get_date_range(20210601, 20210715))
sup_df = pd.DataFrame(np.ones([LimitPool.shape[0], LimitPool.shape[1]]), index=LimitPool.index, columns=LimitPool.columns)

def trans_daily_to_tick(turn_vol_std):
    turn_vol_std.columns = ['date', 'code', 'factor']
    turn_vol_std = turn_vol_std.set_index(['date', 'code']).loc[sup_df.index]
    result = sup_df.mul((turn_vol_std).loc[sup_df.index, 'factor'], axis=0)

    return result

open_tick = trans_daily_to_tick(open.stack().reset_index())

t_tender_strength_pert = ((LastPx- open_tick)/AbsPxChg)[LimitPool].stack().loc[stock_pool_stack.index]

t_tender_strength_pert.to_pickle(save_path + factor_name + '.pkl')
