# coding: utf-8
# Author：fengchi863
# Date ：2021/12/2 13:58

from xquant.marketdata import MarketData
from ShortTermTrading.dataApi import tradeDate, stockList, getData


class TransactionOrder:
    def __init__(self, start_date=20200101, end_date=20200201):
        self.mdp = MarketData()
        self.start_date = start_date
        self.end_date = end_date

    def get_transcation_order(self, stk_id, date):
        if type(stk_id) is int:
            stk_id = stockList.trans_int2windcode(stk_id)
        date = str(date)
        order = self.mdp.get_data_by_date('Order', stk_id, date, sort_by_receive_time=True)
        return order


if __name__ == '__main__':
    to = TransactionOrder()
    ret1 = to.get_transcation_order(601688, 20200203)
    ret2 = to.get_transcation_order(858, 20200203)
    list(set(ret1.columns.tolist()).intersection(ret2.columns.tolist()))
    print(1)
