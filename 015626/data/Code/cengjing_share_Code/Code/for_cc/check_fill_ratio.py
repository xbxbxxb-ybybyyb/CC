fill_ratio_t = 0.9
fill_ratio_bar_t = 5

check_stock_list = ['volume', 'BuyTradeMoney', 'SellTradeMoney']

def check_fill_ratio(date):
    dc_ic = DataCenter(variety = 'IC', data_type='IndexStock', instrument_type='recent', 
                    data_dict = {'Stock':check_stock_list}, start_date = str(date), end_date = str(date), days_past = 0)
    dc_if = DataCenter(variety = 'IF', data_type='IndexStock', instrument_type='recent', 
                    data_dict = {'Stock':check_stock_list}, start_date = str(date), end_date = str(date), days_past = 0)
 
    temp = dc_ic.get_stock_data()['volume'].join(dc_if.get_stock_data()['volume'])
    temp = temp > 0
    fill_ratio = temp.sum(axis = 1) / 800

    if len(fill_ratio[fill_ratio < fill_ratio_t]) > fill_ratio_bar_t:
        print('stock fill ratio wrong:  %s' %  'volume')

    temp = dc_ic.get_stock_data()['BuyTradeMoney'].join(dc_if.get_stock_data()['BuyTradeMoney'])
    temp = temp + dc_ic.get_stock_data()['SellTradeMoney'].join(dc_if.get_stock_data()['SellTradeMoney'])
    temp = temp > 0
    fill_ratio = temp.sum(axis = 1) / 800

    if len(fill_ratio[fill_ratio < fill_ratio_t]) > fill_ratio_bar_t:
        print('stock fill ratio wrong:  %s' %  'BuyTradeMoney SellTradeMoney')