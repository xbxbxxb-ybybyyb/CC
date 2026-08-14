# coding: utf-8
# Author：fengchi863
# Date ：2021/12/2 17:02
from xquant.marketdata import MarketData
from ShortTermTrading.dataApi import tradeDate, stockList, getData


class TransactionOrder:
    def __init__(self):
        self.mdp = MarketData()

    def get_transcation_order(self, stk_id, date):
        if type(stk_id) is int:
            stk_id = stockList.trans_int2windcode(stk_id)
        date = str(date)
        order = self.mdp.get_data_by_date('Order', stk_id, date, sort_by_receive_time=True)
        MDTime = order['MDTime'].values.astype('uint32')
        ReceiveDateTime = order['ReceiveDateTime'].values.astype('uint64')
        OrderPrice = order['OrderPrice'].values.astype('float32')
        OrderQty = order['OrderQty'].values.astype('uint32')
        OrderBSFlag = order['OrderBSFlag'].values
        OrderIndex = order['OrderIndex'].values.astype('uint32')
        OrderType = order['OrderType'].values.astype('uint32')

        return order

    def multi_func(self):
        pass


if __name__ == '__main__':
    to = TransactionOrder()
    ret1 = to.get_transcation_order(601688, 20200203)
    ret2 = to.get_transcation_order(858, 20200203)
    print(1)
