from DataFlowInfo import DataFlowInfo
from Position import Position
import numpy as np
class Broker:
    """
    交易所Waper,用于封装模拟交易所，初期开发暂时按照：
    每天虚定义一个broker
    当前一分钟下单，下一分钟开盘成交
    当前一个tick下单，下一tick价格成交

    后期进一步封装模拟交易所
    """
    def __init__(self,date : int,stk_list,data_freq = '1m'):
        self.date = date
        self.stk_list = stk_list
        self.dataflow = DataFlowInfo(date,stk_list,data_freq)
    # def __init__(self,date:int,stk_list,dataflow):
    #     self.date = date
    #     self.stk_list = stk_list
    #     self.dataflow = dataflow

    def Buy(self, stk_id, price, num, date_time):
        """
        :param stk_id: 股票代码
        :param num: 卖出手数
        :param date_time: 下单时间
        :return: 下单信息和下单后的Position状态
        """
        temp_mkt = self.dataflow.data.loc[stk_id,:,:].shift(-1)
        deal_ratio = (price - temp_mkt.loc[date_time,'low'])/\
                     (temp_mkt.loc[date_time,'high'] - temp_mkt.loc[date_time,'low'] +0.01)

        if deal_ratio<0:
            deal_ratio = 0
        if deal_ratio>1:
            deal_ratio = 1

        available_vol = deal_ratio*temp_mkt.loc[date_time,'vol']*0.5
        deal_vol = min(num,available_vol if not np.isnan(available_vol) else 0)
        deal_vol = int(deal_vol/100)*100
        return price,deal_vol

    def Sell(self, stk_id, price, num, date_time):
        """
        :param stk_id: 股票代码
        :param num: 卖出手数
        :param date_time: 下单时间
        :return: 下单信息和下单后的Position状态
        """
        temp_mkt = self.dataflow.data.loc[stk_id, :, :].shift(-1)
        deal_ratio = (temp_mkt.loc[date_time, 'high'] - price) / \
                     (temp_mkt.loc[date_time, 'high'] - temp_mkt.loc[date_time, 'low'] + 0.01)

        if deal_ratio < 0:
            deal_ratio = 0
        if deal_ratio > 1:
            deal_ratio = 1

        available_vol = deal_ratio * temp_mkt.loc[date_time, 'vol'] * 0.5
        deal_vol = min(num, available_vol if not np.isnan(available_vol) else 0)
        deal_vol = int(deal_vol / 100) * 100
        return price, deal_vol
    #(date_time,stk,target_vol,temp_close[stk],flag)
    def deal_with_order(self,order_list,position:Position):
        deal_info = []
        for order in order_list:
            date_time, stk, target_vol, price, flag = order
            if flag == 'B':
                deal_price, deal_vol = self.Buy(stk,price,target_vol,date_time)
                if deal_vol>0:
                    position.Buy(stk,target_vol,deal_price)
                elif deal_vol<0:
                    raise Exception('Wrong sig of deal vol %d'%deal_vol)
            elif flag=='S':
                deal_price, deal_vol = self.Sell(stk,price,target_vol,date_time)
                if deal_vol>0:
                    position.Sell(stk,target_vol,deal_price)
                elif deal_vol<0:
                    raise Exception('Wrong sig of deal vol %d'%deal_vol)
            else:
                raise Exception('Wrong trading flag %s'%str(flag))

            deal_info.append((date_time,stk,deal_vol,deal_price,flag))
        return deal_info
    # def load_mkt_info(self):
    #     """
    #     load行情数据用于撮合和返回
    #     :return: 所涉及的行情数据
    #     """
    #     return mkt_data
