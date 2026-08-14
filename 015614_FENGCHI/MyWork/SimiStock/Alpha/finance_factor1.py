# coding: utf-8
# Author：fengchi863
# Date ：2022/6/10 17:25

from SimiStock.dataApi import getData, tradeDate, stockList

if __name__ == '__main__':
    start_date = 20170101
    end_date = 20210101
    date_list = tradeDate.get_date_range(start_date, end_date)
    clean_stock = stockList.clean_stock_list().columns.tolist()
    bp = getData.get_daily_1factor('BP', date_list=date_list)
