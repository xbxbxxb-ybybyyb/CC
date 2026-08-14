# @Time : 2021/9/16 14:39
# @Author : Zhichen Lu
# @File : basic_conf.py
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from dataApi.stockList import get_all_stock_ever_appear
_code_list = get_all_stock_ever_appear(20210531)
_date_list = get_date_range(20140701,20210531)
_cal_date_list = get_date_range(get_pre_trade_date(_date_list[0],40),_date_list[-1])
falcon_base = '/data/group/800442/800319/MillenniumFalcon/'
future_path = f'{falcon_base}future/'