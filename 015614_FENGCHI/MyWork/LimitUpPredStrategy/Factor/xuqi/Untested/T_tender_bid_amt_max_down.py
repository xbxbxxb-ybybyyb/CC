# author: kiki_777
# date: 2021/5/14
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare('/arch1/group/800442/800319/LimitTickData20210615_20210715/')
from xquant.factordata import FactorData
s = FactorData()
from multiprocessing import Pool
from tqdm import tqdm
from xquant.marketdata import MarketData



def cal_tender_tick_factor(stk, date):
    mdp = MarketData()
    code = trans_int2windcode(stk)
    df = mdp.get_data_by_date("Stock", code, str(date), ['1'], sort_by_receive_time=True)
    df = df[df['MDTime'] > '091500000']
    df['Buy1Amt'] = df['Buy1OrderQty'] * df['Buy1Price']
    df['Sell1Amt'] = df['Sell1OrderQty'] * df['Sell1Price']
    t_tender_bid_amt_max_down = max(df['Buy1Amt'].expanding().max() - df['Buy1Amt'])
    t_tender_bid_max_down = max(df['Buy1OrderQty'].expanding().max() - df['Buy1OrderQty'])
    t_tender_bidmask_amt_mean = (df['Buy1Amt']).mean()
    t_tender_bidmask_amt_std = (df['Buy1Amt']).std()
    return t_tender_bid_amt_max_down, t_tender_bid_max_down, t_tender_bidmask_amt_mean, t_tender_bidmask_amt_std


netBidRatio = pd.read_pickle('/data/group/800442/800319/ZTfactors/20210615-20210715/indexChgLast.pkl')
pool_day = netBidRatio.reset_index()[['date', 'code']].drop_duplicates().reset_index().drop(columns=['index'])


def mult_run(j):
    k = len(pool_day) // 24 + 1
    code = []
    date_lst = []
    t_tender_bid_amt_max_down = []
    t_tender_bid_max_down = []
    t_tender_bidmask_amt_mean = []
    t_tender_bidmask_amt_std = []

    for i in tqdm(range(k * j, min(k * (j + 1), len(pool_day)))):
        try:
            stk = int(pool_day.loc[i, 'code'])
            date = int(pool_day.loc[i, 'date'])
            a, b, c, d = cal_tender_tick_factor(stk, date)
            t_tender_bid_amt_max_down.append(a)
            t_tender_bid_max_down.append(b)
            t_tender_bidmask_amt_mean.append(c)
            t_tender_bidmask_amt_std.append(d)
            code.append(stk)
            date_lst.append(date)
        except:
            pass
    df = pd.DataFrame({'date': date_lst, 'code': code, 't_tender_bid_amt_max_down': t_tender_bid_amt_max_down,
                       't_tender_bid_max_down': t_tender_bid_max_down,
                       't_tender_bidmask_amt_mean': t_tender_bidmask_amt_mean,
                       't_tender_bidmask_amt_std': t_tender_bidmask_amt_std})

    print('done')
    print(df)

    return df


if __name__ == '__main__':
    processor = 24
    p = Pool(processor)
    res = []
    for i in range(processor):
        res.append(p.apply_async(mult_run, args=(i,)))
        print(str(i) + ' processor started !')
    p.close()
    p.join()
    factors = pd.concat([i.get() for i in res])
    print(factors)
    factors.to_pickle('/data/user/015628/chase_limitup/t_tender_factors_20210615_20210715.pkl')


tender_factor = pd.read_pickle('/data/user/015628/chase_limitup/t_tender_factors_20210615_20210715.pkl')
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



ff_share = get_daily_1factor('free_float_shares', date_list=get_date_range(20210610, 20210715))
ff_share_tick = trans_daily_to_tick(ff_share.shift(1).stack().reset_index())

t_tender_bid_amt_max_down = trans_daily_to_tick(tender_factor[['date', 'code', 't_tender_bid_amt_max_down']])
t_tender_bid_max_down = trans_daily_to_tick(tender_factor[['date', 'code', 't_tender_bid_max_down']])
t_tender_bidmask_amt_mean = trans_daily_to_tick(tender_factor[['date', 'code', 't_tender_bidmask_amt_mean']])
t_tender_bidmask_amt_std = trans_daily_to_tick(tender_factor[['date', 'code', 't_tender_bidmask_amt_std']])

t_tender_bid_ff_max_down = t_tender_bid_max_down/ff_share_tick

t_tender_bid_amt_max_down.to_pickle('/data/group/800442/800319/ZTfactors/20210615-20210715/t_tender_bid_amt_max_down.pkl')
t_tender_bid_ff_max_down.to_pickle('/data/group/800442/800319/ZTfactors/20210615-20210715/t_tender_bid_ff_max_down.pkl')
t_tender_bidmask_amt_mean.to_pickle('/data/group/800442/800319/ZTfactors/20210615-20210715/t_tender_bidmask_amt_mean.pkl')
t_tender_bidmask_amt_std.to_pickle('/data/group/800442/800319/ZTfactors/20210615-20210715/t_tender_bidmask_amt_std.pkl')

