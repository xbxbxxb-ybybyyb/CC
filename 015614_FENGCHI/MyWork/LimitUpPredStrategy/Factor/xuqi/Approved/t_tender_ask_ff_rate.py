# author: kiki_777
# date: 2021/7/28
import sys
sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')
from tqdm import tqdm
from multiprocessing import Pool


class t_tender_ask_ff_rate(object):

    def __init__(self, start_date=20210615, end_date=20210715):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def cal_tender_tick_factor(self, stk, date):

        mdp = MarketData()
        code = trans_int2windcode(stk)
        df = mdp.get_data_by_date("Stock", code, str(date), ['1'], sort_by_receive_time=True)
        df = df[df['MDTime'] > '091500000']
        if df['TotalOfferQty'].iloc[-1] > 0:
            t_tender_ask = df['TotalOfferQty'].iloc[-1]
        else:
            t_tender_ask = 0
            for i in range(1, 11):
                t_tender_ask += df['Sell%sOrderQty' % i].iloc[-1]
        return t_tender_ask

    def mult_run(self, LimitPool,  j):
        k = len(LimitPool) // 24 + 1
        code = []
        date_lst = []
        t_tender_ask = []

        for i in tqdm(range(k * j, min(k * (j + 1), len(LimitPool)))):
            try:
                stk = int(LimitPool.loc[i, 'code'])
                date = int(LimitPool.loc[i, 'date'])
                a = self.cal_tender_tick_factor(stk, date)
                t_tender_ask.append(a)
                code.append(stk)
                date_lst.append(date)
            except:
                pass
        df = pd.DataFrame({'date': date_lst, 'code': code, 't_tender_ask': t_tender_ask})
        return df

    def calculate(self, factor_name, save_path=None):

        date_list = get_date_range(get_pre_trade_date(self.start_date, 10), self.end_date)
        free_share = get_daily_1factor('free_float_shares', date_list)
        LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                             start_date=self.start_date,
                                             end_date=self.end_date,
                                             date_list=None,
                                             start_tick=91500,
                                             end_tick=150000,
                                             tick_list=None,
                                             return_idx=True
                                             )

        processor = 24
        p = Pool(processor)
        res = []
        for i in range(processor):
            res.append(p.apply_async(self.mult_run, args=(LimitPool, i)))
            print(str(i) + ' processor started !')
        p.close()
        p.join()
        factor = pd.concat([i.get() for i in res])
        factor = factor.set_index(['date', 'code'])['t_tender_ask']
        free_share_tick= pd.DataFrame(np.repeat(free_share.shift(1).stack().loc[LimitPool.index].values, LimitPool.shape[1]).reshape(LimitPool.shape[0],LimitPool.shape[1]),
                                      index=LimitPool.index, columns=LimitPool.columns)
        factor = pd.DataFrame(np.repeat(factor.loc[LimitPool.index].values, LimitPool.shape[1]).reshape(LimitPool.shape[0],LimitPool.shape[1]),
                              index=LimitPool.index, columns=LimitPool.columns)
        factor = (factor/free_share_tick)[LimitPool].stack()

        if save_path:
            factor.to_pickle(save_path + factor_name + '.pkl')

        return factor


fc = t_tender_ask_ff_rate(start_date=20140102, end_date=20210715)
test = fc.calculate('t_tender_ask_ff_rate', '/arch1/group/800442/800319/ZTfactors/Approved_2021/')
