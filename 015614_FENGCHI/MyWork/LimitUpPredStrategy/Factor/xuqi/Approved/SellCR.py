from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData20210615_20210715/')
from xquant.factordata import FactorData
s = FactorData()
from multiprocessing import Pool
from tqdm import tqdm

class SellCR(object):

    def __init__(self, start_date=20210615, end_date=20210715):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def get_transaction_data(self, code, date, address='/data/group/800442/800319/LimitTradeData'):

        date = str(trans_datetime2int(date))
        code = trans_int2windcode(code)
        trade_data = {}
        items = {
            'MDTime': 'TimeStamp',
            'TradePrice': 'Price',
            'TradeQty': 'Volume',
            'TradeMoney':'Amount',
            'TradeType': 'TradeType',
            'TradeBSFlag':'TradeBSFlag',
            'TradeBuyNo':'TradeBuyNo',
            'TradeSellNo':'TradeSellNo',
            'ReceiveDelay':'ReceiveDelay'
        }
        for item in items:
            trade_data[items[item]] = np.load(f'{address}/{item}/{code}{date}.npy')
        return trade_data

    def get_large_trade(self, stock_stack, i):

        test = self.get_transaction_data(int(stock_stack.index[i][1]),int(stock_stack.index[i][0]))
        df = pd.DataFrame(test)
        df['ReceiveTime'] = df['TimeStamp'] + df['ReceiveDelay']
        filtered = df[(df['ReceiveTime'] < stock_stack.index[i][2]*1000)]
        active_sell = filtered[(filtered['TradeBSFlag'] == 2) & (filtered['Price'] > 0)].groupby('TradeSellNo')['Volume', 'Amount'].sum()
        sell_cr = (active_sell['Amount'] * active_sell['Amount']).sum() / ((filtered['Amount'].sum()) ** 2) * 100

        return sell_cr

    def mult_run(self, stock_stack, j):
        k = len(stock_stack) // 24 + 1
        code = []
        date = []
        tick = []
        sell_cr = []
        for i in tqdm(range(k * j, k * (j + 1))):
            try:
                a = self.get_large_trade(stock_stack, i)
                sell_cr.append(a)
                code.append(stock_stack.index[i][1])
                date.append(stock_stack.index[i][0])
                tick.append(stock_stack.index[i][2])
            except:
                pass
        df = pd.DataFrame({'code': code, 'date': date, 'tick': tick, 'sell_cr': sell_cr})

        return df

    def calculate(self, factor_name, save_path=None):

        date_list = get_date_range(get_pre_trade_date(self.start_date, 10), self.end_date)
        LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                             start_date=self.start_date,
                                             end_date=self.end_date,
                                             date_list=None,
                                             start_tick=91500,
                                             end_tick=150000,
                                             tick_list=None,
                                             return_idx=True
                                             )
        stock_stack = LimitPool[LimitPool].stack()

        processor = 24
        p = Pool(processor)
        res = []

        for k in range(processor):
            res.append(p.apply_async(self.mult_run, args=(stock_stack, k)))
            print(str(k) + ' processor started !')
        p.close()
        p.join()
        factor = pd.concat([i.get() for i in res])
        factor = factor.set_index(['date', 'code', 'tick'])['sell_cr']
        factor = pd.Series(factor.loc[stock_stack.index].values, index=stock_stack.index)

        if save_path:
            factor.to_pickle(save_path + factor_name + '.pkl')

        return factor


fc = SellCR(start_date=20210615, end_date=20210715)
test = fc.calculate('SellCR')