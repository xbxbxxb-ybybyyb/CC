import pandas as pd
import numpy as np
import os
from config import *
root_path = '/data/group/800319/junkData/'
class DataFlowInfo:
    """
    用于存储某一交易日(月？待定)内所涉及的股票池的行情数据，供回测调用
    """
    def __init__(self,date,stk_list,data_freq = '1m'):
        self.date = date #日期 8位int
        self.stk_list = stk_list# 股票列表 list, 元素为 int格式
        # 加载pd.Pannel()格式的数据，items_axis:股票代码 main_axis:日期 minor_axis:高开底收
        self.data = self.load_data(data_freq)


    def load_data(self,data_freq,period = 'month'):
        """
        获取当前交易日内的行情数据
        :param data_freq: 频率 '1m' 'tick'
        :return: DataFrame
        """
        # 不过滤日期 2.3513946533203125
        # 每次读取单个stk过程中过滤日期  1.8648979663848877
        # 最后再过滤日期 2.2263224124908447
        if period=='month':
            month = int(self.date/100)
            date_list = s.tradingday(month*100+1,month*100+31)
        elif period == 'day':
            date_list = [self.date]
        if data_freq=='1m':
            data = {}
            for stk in self.stk_list:
                data[stk] = load_minutes_data(stk,date_list)
                # if not os.path.exists('%s/minuteByStock/%d.h5'%(root_path,stk)):
                #     print()
                #     raise Exception("Data of stock %s in %d are not available"%(stk,self.date))
                # temp_data = pd.HDFStore('%s/minuteByStock/%d.h5'%(root_path,stk))
                # try:
                #     data[stk] = temp_data['./%d'%stk].loc[self.date*10000:(self.date+1)*10000]
                # except:
                #     pass
                # temp_data.close()
        else:
            raise("Frequency Not Available")
        return pd.Panel(data)
    def update(self,date,stk_list,data_freq = '1m',period = 'month'):
        """
        更新所有数据
        :param date:
        :param stk_list:
        :param data_freq:
        :return:
        """
        self.__init__(date,stk_list,data_freq = '1m')
    def update_date(self,date,data_freq = '1m',period = 'month'):
        """
        更新日期以及self.data
        :param date:
        :param data_freq:
        :return:
        """

        if date == self.date:
            return 0
        present_month = int(self.date / 100)
        self.date = date
        if present_month!=int(self.date/100) and period=='month':
            print(date,'update')
            self.data = self.load_data(data_freq)
        elif period=='day':
            print(date,'update')
            self.data = self.load_data(data_freq,period)





