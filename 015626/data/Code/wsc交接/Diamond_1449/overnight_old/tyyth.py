import os
import time
import pandas as pd
import multifactor.utility.dt as udt
from overnight.naming_config import trading_plan_path, trade_stop_time
from xquant.investment.strategyfile import upload_strategy_file
from xquant.xqutils.helper import link
lm = link.LinkMessage()


def excel_transmission_tyyth(trade_date):
    next_trading_day = udt.get_trading_day_offset(trade_date, 1)[0].strftime('%Y%m%d')
    sourse_path1 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'Diamond_%s_afternoon.xlsx' % (trade_date))
    sourse_path2 = os.path.join(trading_plan_path, '%s_%s' % (next_trading_day, trade_stop_time.strftime('%H%M')), 'Diamond_%s_morning.xlsx' % (next_trading_day))
    
    if os.path.exists(sourse_path1) & os.path.exists(sourse_path2):
        upload_strategy_file('DiamondStrategy', trade_date, 1, sourse_path1, is_delete = False, is_ready=1)
        upload_strategy_file('DiamondStrategy', next_trading_day, 1, sourse_path2, is_delete = False, is_ready=1)
        
        
if __name__ == '__main__':
    def flag_check(trade_date):
        next_trade_date = udt.get_trading_day_offset(trade_date,1)[0].strftime('%Y%m%d')
        path1 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'Diamond_%s_afternoon.xlsx' % (trade_date))
        path2 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'Diamond_%s_afternoon_1.xlsx' % (trade_date))
        next_trading_plan_savepath = os.path.join(trading_plan_path, '%s_%s' % (next_trade_date, trade_stop_time.strftime('%H%M')))
        path3 = os.path.join(next_trading_plan_savepath, 'Diamond_%s_morning.xlsx' % (next_trade_date))
        path4 = os.path.join(next_trading_plan_savepath, 'Diamond_%s_morning_1.xlsx' % (next_trade_date))
        con_1 = os.path.exists(path1) | os.path.exists(path2)
        con_2 = os.path.exists(path3) | os.path.exists(path4)
        return con_1 & con_2
        
    end_date = pd.Timestamp.now().strftime('%Y%m%d')

    while True:
        if flag_check(end_date):
            break
        time.sleep(2)
    print('flag check finished!')
    
    excel_transmission_tyyth(end_date)
    lm.sendMessage('一体化参数已上传')