import datetime as dt
import multifactor.utility.dt as udt
from xquant.xqutils.helper import link
from overnight.factor_generator import prepare_history
from overnight.utility import update_stock_multitime_data, get_current_futures_contract

lm = link.LinkMessage()


if __name__ == '__main__':
    print(str(dt.datetime.now()) + '*** prepare history ***')
    lm.sendMessage(str(dt.datetime.now()) + " start to prepare history data" )
    update_stock_multitime_data()
    prepare_history()
    
    today = dt.datetime.now().strftime('%Y%m%d')
    next_trading_day = udt.get_trading_day_offset(today, 1)[0].strftime('%Y%m%d')
    ticker_list = []
    ticker_list.append(get_current_futures_contract(prod_id='IC.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IC.CFE', trade_date=today, mode='season'))
    ticker_list.append(get_current_futures_contract(prod_id='IF.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IF.CFE', trade_date=today, mode='season'))
    ticker_list.append(get_current_futures_contract(prod_id='IH.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IH.CFE', trade_date=today, mode='season'))
    lm.sendMessage(str(ticker_list))
    lm.sendMessage(str(dt.datetime.now()) + " history data done!")

