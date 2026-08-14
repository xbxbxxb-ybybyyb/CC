# coding: utf-8
# Author：fengchi863
# Date ：2021/9/13 21:19

'''
这个文件暂时废弃，不用这个文件生成labels
'''

from ShortTermTrading.dataApi import getData, tradeDate, stockList


class LablesGen:
    def __init__(self, start_date=20140701, end_date=20210701):
        self.start_date = start_date
        self.end_date = end_date
        self.date_list = tradeDate.get_date_range(start_date, end_date)

    def calc_ret(self):
        amt = getData.get_minute_1factor('amt', )


if __name__ == '__main__':
    lg = LablesGen(start_date=20140701, end_date=20210701)
    lg.calc_ret()
