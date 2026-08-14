# author: kiki_777
# date: 2021/4/27

from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData20210615_20210715/')
from xquant.factordata import FactorData
s = FactorData()

start_date = 20210601
end_date = 20210715

date_list = get_date_range(start_date, end_date)

high = get_daily_1factor('high', date_list)
low = get_daily_1factor('low', date_list)
zt = get_daily_1factor('limit_up', date_list)

yzb = (high == low) & zt
zcb = (high != low) & zt

AllEBNum = yzb.sum(axis=1)
ZTstockNum = zcb.sum(axis=1)
ZTstockNumRatio = ZTstockNum/zt.sum(axis=1)

ipo_date = s.get_factor_value('WIND_AShareIPO', factors=['s_info_windcode', 's_ipo_listdate'])

IPONum = ipo_date.groupby('S_IPO_LISTDATE').size()
IPONum.index = IPONum.index.map(int)
IPONum = IPONum.reindex(date_list).fillna(0)

Mean4dZTstockNumRatio = ZTstockNumRatio.rolling(4).mean()
AllEBNum4d = AllEBNum.rolling(4).mean()
StkZTNum4d = ZTstockNum.rolling(4).mean()

idx_close = get_daily_1factor('close', date_list, type='bench')
idx_pct = idx_close.pct_change(1)
idx_pct5 = idx_close.pct_change(5)
idx_pct20 = idx_close.pct_change(20)

idx_open = get_daily_1factor('open', date_list, type='bench')
idx_o2c = idx_open/idx_close.shift(1)-1



stk_class = pd.DataFrame(index=high.index, columns=high.columns)
stk_class.columns = stk_class.columns.map(trans_int2windcode)

stk_class[stk_class.columns[stk_class.columns.str.endswith('SZ')]] = 1
stk_class[stk_class.columns[stk_class.columns.str.endswith('SH')]] = 2
stk_class.columns = stk_class.columns.map(trans_windcode2int)

indexChgLast = ((stk_class == 1)*(high>0)).mul(idx_pct['SZCZ'], axis=0) + ((stk_class == 2)*(high>0)).mul(idx_pct['SZZZ'], axis=0)
indexChg20 = ((stk_class == 1)*(high>0)).mul(idx_pct20['SZCZ'], axis=0) + ((stk_class == 2)*(high>0)).mul(idx_pct20['SZZZ'], axis=0)
indexChg5 = ((stk_class == 1)*(high>0)).mul(idx_pct5['SZCZ'], axis=0) + ((stk_class == 2)*(high>0)).mul(idx_pct5['SZZZ'], axis=0)

indexO2Cchg = ((stk_class == 1)*(high>0)).mul(idx_o2c['SZCZ'], axis=0) + ((stk_class == 2)*(high>0)).mul(idx_o2c['SZZZ'], axis=0)

ZT_openningRatio = (zt.rolling(2).sum() == 2).sum(axis=1)/(zt.sum(axis =1).shift(1))

NumInterSects = (zt.rolling(2).sum() == 2).sum(axis=1)

open = get_daily_1factor('open', date_list)
close = get_daily_1factor('close', date_list)
preclose = get_daily_1factor('pre_close', date_list)
prem = open/preclose -1

MeanOpenPctChg = (zt.astype(int).shift(1).replace(0, np.nan)* prem).apply(lambda x: np.nanmean(x), axis=1)

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

trans_daily_to_tick(indexChgLast, 'indexChgLast')
trans_daily_to_tick(indexChg20, 'indexChg20')
trans_daily_to_tick(indexChg5, 'indexChg5')
trans_daily_to_tick(indexO2Cchg, 'indexO2Cchg')

def trans_series_to_df(s):

    df = pd.DataFrame(np.repeat(np.array(s).reshape(-1, 1), high.shape[1], axis = 1), index=high.index, columns=high.columns)

    return df



trans_daily_to_tick(trans_series_to_df(AllEBNum), 'AllEBNum')
trans_daily_to_tick(trans_series_to_df(ZTstockNum), 'ZTstockNum')
trans_daily_to_tick(trans_series_to_df(ZTstockNumRatio), 'ZTstockNumRatio')
trans_daily_to_tick(trans_series_to_df(IPONum), 'IPONum')
trans_daily_to_tick(trans_series_to_df(Mean4dZTstockNumRatio), 'Mean4dZTstockNumRatio')
trans_daily_to_tick(trans_series_to_df(AllEBNum4d), 'AllEBNum4d')
trans_daily_to_tick(trans_series_to_df(StkZTNum4d), 'StkZTNum4d')
trans_daily_to_tick(trans_series_to_df(ZT_openningRatio), 'ZT_openningRatio')
trans_daily_to_tick(trans_series_to_df(NumInterSects), 'NumInterSects')
trans_daily_to_tick(trans_series_to_df(MeanOpenPctChg), 'MeanOpenPctChg')



zt_prem = (zt.astype(int).shift(1).replace(0, np.nan)* prem)

NumGt5pct = (zt_prem > 0.05).sum(axis=1)/zt.shift(1).sum(axis=1)
Num2Bt5pct = ((zt_prem >= 0.02) & (zt_prem <= 0.05)).sum(axis=1)/zt.shift(1).sum(axis=1)
Num0Bt2pct = ((zt_prem >= 0) & (zt_prem <= 0.02)).sum(axis=1)/zt.shift(1).sum(axis=1)

trans_daily_to_tick(trans_series_to_df(NumGt5pct), 'NumGt5pct')
trans_daily_to_tick(trans_series_to_df(Num2Bt5pct), 'Num2Bt5pct')
trans_daily_to_tick(trans_series_to_df(Num0Bt2pct), 'Num0Bt2pct')

def cal_macd(data, short, long, m):

    diff = data.ewm(adjust=False, alpha=2/(short+1), ignore_na=True).mean()-\
           data.ewm(adjust=False, alpha=2/(long+1), ignore_na=True).mean()
    dea = diff.ewm(adjust=False, alpha=2/(m+1), ignore_na=True).mean()
    macd = 2*(diff-dea)

    return macd

idx_macd = cal_macd(idx_close, 12, 26, 9)
stk_macd = cal_macd(close, 12, 26, 9)

trans_daily_to_tick(stk_macd, 'stockhist')
trans_daily_to_tick(trans_series_to_df(idx_macd['SZZZ']), 'SHhist')
trans_daily_to_tick(trans_series_to_df(idx_macd['SZCZ']), 'SZhist')