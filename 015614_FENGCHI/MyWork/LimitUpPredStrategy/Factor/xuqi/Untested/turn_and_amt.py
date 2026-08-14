# author: kiki_777
# date: 2021/4/27

from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare('/arch1/group/800442/800319/LimitTickData20210615_20210715/')

start_date = 20210601
end_date = 20210715

date_list = get_date_range(start_date, end_date)

high = get_daily_1factor('high', date_list)
close = get_daily_1factor('close', date_list)
low = get_daily_1factor('low', date_list)
preclose = get_daily_1factor('pre_close', date_list)
pct = get_daily_1factor('pct_chg', date_list)
pe_ttm = get_daily_1factor('pe_ttm', date_list)
free_turn = get_daily_1factor('free_turn', date_list)
adjclose = get_daily_1factor('close_badj', date_list)
vwap = get_daily_1factor('vwap', date_list)
dt = get_daily_1factor('limit_down', date_list)
idx_close = get_daily_1factor('close', date_list, type='bench')
idx_pct = idx_close.pct_change(1)

w_h2c_mean = (high/close-1).rolling(30, min_periods=1).apply(lambda x: np.nanmean(x))
w_swing_mean = ((high-low)/preclose).rolling(30, min_periods=1).apply(lambda x: np.nanmean(x))
w_swing_wmean = ((high-low)/preclose).ewm(span=30, ignore_na=True).mean()


w_swing_pct = w_swing_wmean/w_swing_mean
w_pct_rank = pct.rolling(30).apply(lambda x: (x.size+1 - bn.rankdata(x)[-1])/x.size)
w_pe_ttm = pe_ttm.copy()

w_vwap2C = ((vwap * free_turn).rolling(30, min_periods=1).apply(lambda x: np.nansum(x))/(free_turn.rolling(30, min_periods=1).apply(lambda x: np.nansum(x))))/preclose

w_vt_corr = vwap.rolling(30).corr(free_turn)
w_dl_num = dt.rolling(30).sum()


def rolling_beta(x, y, period):

    cx = x.rolling(period).mean()
    cy = y.rolling(period).mean()
    cx2 = (x ** 2).rolling(period).sum()
    cxy = (x * y).rolling(period).sum()

    return (cxy - period * cx * cy)/(cx2 - period * (cx**2))


idx_pct_df = pd.DataFrame(np.repeat(np.array(idx_pct['SZZZ']).reshape(-1, 1), pct.shape[1], axis=1),
                          index=pct.index, columns=pct.columns)
w_exss_beta = rolling_beta(idx_pct_df, pct/100, 30)

w_exss_mean = (pct/100).sub(idx_pct['SZZZ'], axis = 0).rolling(30, min_periods=1).apply(lambda x: np.nanmean(x))

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


def trans_daily_to_tick(turn_vol_std, factor_name, address='/data/group/800442/800319/ZTfactors/20210615-20210715/'):
    turn_vol_std = turn_vol_std.shift(1).stack().reset_index()
    turn_vol_std.columns = ['date', 'code', 'factor']
    turn_vol_std = turn_vol_std.set_index(['date', 'code']).loc[sup_df.index]
    turn_vol_std_inday = sup_df.mul((turn_vol_std).loc[sup_df.index, 'factor'], axis=0)
    result = turn_vol_std_inday[LimitPool].stack().reindex(stock_pool_stack.index)
    result.to_pickle('%s/%s.pkl'%(address, factor_name))
    return result

trans_daily_to_tick(w_swing_mean, 'w_swing_mean')
trans_daily_to_tick(w_swing_wmean, 'w_swing_wmean')
trans_daily_to_tick(w_swing_pct, 'w_swing_pct')
trans_daily_to_tick(w_pct_rank, 'w_pct_rank')
trans_daily_to_tick(w_pe_ttm, 'w_pe_ttm')
trans_daily_to_tick(w_vwap2C, 'w_vwap2C')

trans_daily_to_tick(w_pct_rank, 'w_pct_rank')
trans_daily_to_tick(w_vt_corr, 'w_vt_corr')
trans_daily_to_tick(w_dl_num, 'w_dl_num')

trans_daily_to_tick(w_exss_beta, 'w_exss_beta')
trans_daily_to_tick(w_exss_mean, 'w_exss_mean')

vol = get_daily_1factor('volume', date_list)
vwap_5d = (vol*vwap).rolling(5).sum()/vol.rolling(5).sum()
w_gf_loss = ((close/vwap_5d-1)*free_turn).rolling(5).sum()/free_turn.rolling(5).sum()

trans_daily_to_tick(w_gf_loss, 'w_gf_loss')
