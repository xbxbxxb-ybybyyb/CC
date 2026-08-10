from overnight.factor_generator import *
from overnight.insight_retrieve_mdconstant import *
from overnight.insight_retrieve_alla import *
from overnight.insight_retrieve_misc_minute import *
from overnight.utility import *
from overnight.naming_config import *
import multifactor.utility.dt as udt
from multiprocessing import Process
import datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()





if __name__ == '__main__':
    print(str(datetime.datetime.now()) + '*** prepare history ***')
    lm.sendMessage(str(datetime.datetime.now()) + " start to prepare history data" )
    update_stock_multitime_data()
    prepare_history()
    
    today = datetime.datetime.now().strftime('%Y%m%d')
    next_trading_day = udt.get_trading_day_offset(today, 1)[0].strftime('%Y%m%d')
    ticker_list = []
    ticker_list.append(get_current_futures_contract(prod_id='IC.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IC.CFE', trade_date=today, mode='season'))
    ticker_list.append(get_current_futures_contract(prod_id='IF.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IF.CFE', trade_date=today, mode='season'))
    ticker_list.append(get_current_futures_contract(prod_id='IH.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IH.CFE', trade_date=today, mode='season'))
    lm.sendMessage(str(ticker_list))
    
    ftp = ftplib.FTP('168.8.2.68')
    ftp.login('xquant', 'Xquant-32')
    ftp_path1 = '/XQuant/011477/%s' % today
    ftp_path2 = '/XQuant/011477/%s/Diamond_%s' % (today, today)
    ftp_path3 = '/XQuant/011477/%s' % next_trading_day
    ftp_path4 = '/XQuant/011477/%s/Diamond_%s' % (next_trading_day, next_trading_day)
    try:
        ftp.mkd(ftp_path1)
    except Exception as e:
        if 'Already exists, failed to create' in str(e):
            print(ftp_path1)
            print(e)
        else:
            print(ftp_path1)
            raise RuntimeError
    
    try:
        ftp.mkd(ftp_path2)
    except Exception as e:
        if 'Already exists, failed to create' in str(e):
            print(ftp_path2)
            print(e)
        else:
            print(ftp_path2)
            raise RuntimeError
            
    try:
        ftp.mkd(ftp_path3)
    except Exception as e:
        if 'Already exists, failed to create' in str(e):
            print(ftp_path3)
            print(e)
        else:
            print(ftp_path3)
            raise RuntimeError

    try:
        ftp.mkd(ftp_path4)
    except Exception as e:
        if 'Already exists, failed to create' in str(e):
            print(ftp_path4)
            print(e)
        else:
            print(ftp_path4)
            raise RuntimeError
    lm.sendMessage(str(datetime.datetime.now()) + " history data done!")

