# author: kiki_777
# date: 2021/7/28
import sys

sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index

dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')


class BuySellSpread(object):

    def __init__(self, start_date=20210615, end_date=20210715):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def calculate(self, factor_name, save_path=None):

        LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                             start_date=self.start_date,
                                             end_date=self.end_date,
                                             date_list=None,
                                             start_tick=91500,
                                             end_tick=150000,
                                             tick_list=None,
                                             return_idx=True
                                             )
        Bid1Qty = dp.get_data_by_date_list(item='Buy1OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Bid2Qty = dp.get_data_by_date_list(item='Buy2OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Bid3Qty = dp.get_data_by_date_list(item='Buy3OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Bid4Qty = dp.get_data_by_date_list(item='Buy4OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Bid5Qty = dp.get_data_by_date_list(item='Buy5OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Ask1Qty = dp.get_data_by_date_list(item='Sell1OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Ask2Qty = dp.get_data_by_date_list(item='Sell2OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Ask3Qty = dp.get_data_by_date_list(item='Sell3OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Ask4Qty = dp.get_data_by_date_list(item='Sell4OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )
        Ask5Qty = dp.get_data_by_date_list(item='Sell5OrderQty',  # Tick字段名, 支持的字段见tick_items列表，
                                           # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                           start_date=20140101,
                                           end_date=20210228,
                                           date_list=None,  # 若传列表则忽略start_date和end_date参数
                                           start_tick=91500,  # 默认为91500
                                           end_tick=150000,  # 默认为150000
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )

        BidAskSpread = np.log(Bid1Qty+ Bid2Qty+ Bid3Qty + Bid4Qty + Bid5Qty) - np.log(Ask1Qty+Ask2Qty+Ask3Qty+Ask4Qty+Ask5Qty)
        factor = (BidAskSpread)[LimitPool].stack()

        if save_path:
            factor.to_pickle(save_path + factor_name + '.pkl')

        return factor


fc = BuySellSpread(start_date=20140102, end_date=20210715)
test = fc.calculate('BuySellSpread', '/arch1/group/800442/800319/ZTfactors/Approved_2021/')
