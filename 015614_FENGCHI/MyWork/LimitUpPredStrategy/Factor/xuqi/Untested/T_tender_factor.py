# author: kiki_777
# date: 2021/5/6

from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData20210615_20210715/')
from xquant.factordata import FactorData
s = FactorData()

tender_factor = pd.read_pickle('/data/user/015628/chase_limitup/tender_factors.pkl')
LimitPool = dp.get_data_by_date_list(item='LimitPool',  # Tick字段名, 支持的字段见tick_items列表，
                                       # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                       start_date=20210615,
                                       end_date=20210715,
                                       date_list=None,  # 若传列表则忽略start_date和end_date参数
                                       start_tick=91500,  # 默认为91500
                                       end_tick=150000,  # 默认为150000
                                       tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                       return_idx=True  # True返回DataFrame, False返回2darray
                                       )

stock_pool_stack = LimitPool[LimitPool].stack()
sup_df = pd.DataFrame(np.ones([LimitPool.shape[0], LimitPool.shape[1]]), index=LimitPool.index, columns=LimitPool.columns)

def trans_daily_to_tick(turn_vol_std):
    turn_vol_std.columns = ['date', 'code', 'factor']
    turn_vol_std = turn_vol_std.set_index(['date', 'code']).loc[sup_df.index]
    turn_vol_std_inday = sup_df.mul((turn_vol_std).loc[sup_df.index, 'factor'], axis=0)
    result = turn_vol_std_inday[LimitPool].stack().reindex(stock_pool_stack.index)
    return result



ff_share = get_daily_1factor('free_float_shares', date_list=get_date_range(20130101, 20210228))
ff_share_tick = trans_daily_to_tick(ff_share.shift(1).stack().reset_index(), 'ff_share')

t_tender_bid = trans_daily_to_tick(tender_factor[['date', 'code', 't_tender_bid']])
t_tender_ask = trans_daily_to_tick(tender_factor[['date', 'code', 't_tender_ask']])
t_tender_bidmask = trans_daily_to_tick(tender_factor[['date', 'code', 't_tender_bidmask']])


t_tender_bid_ff_rate = t_tender_bid/ff_share_tick
t_tender_ask_ff_rate = t_tender_ask/ff_share_tick
t_tender_bidmask_ff_rate = t_tender_bidmask/ff_share_tick

t_tender_bid_ff_rate.to_pickle('/data/group/800442/800319/ZTfactors/Untested/t_tender_bid_ff_rate.pkl')
t_tender_ask_ff_rate.to_pickle('/data/group/800442/800319/ZTfactors/Untested/t_tender_ask_ff_rate.pkl')
t_tender_bidmask_ff_rate.to_pickle('/data/group/800442/800319/ZTfactors/Untested/t_tender_bidmask_ff_rate.pkl')