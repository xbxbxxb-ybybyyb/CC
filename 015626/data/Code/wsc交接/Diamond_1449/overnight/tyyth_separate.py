import os
import time
import pandas as pd
import multifactor.utility.dt as udt
from overnight.naming_config import trading_plan_path, trade_stop_time
from xquant.investment.strategyfile import upload_strategy_file
from xquant.xqutils.helper import link
lm = link.LinkMessage()


def excel_transmission_tyyth_separate(trade_date):
    next_trading_day = udt.get_trading_day_offset(trade_date, 1)[0].strftime('%Y%m%d')
    sourse_path1 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')))
    sourse_path2 = os.path.join(trading_plan_path, '%s_%s' % (next_trading_day, trade_stop_time.strftime('%H%M')))
    
    for i in [i for i in os.listdir(sourse_path1) if i.startswith('afternoon')]:
        if not i.endswith('_1.xlsx'):
            upload_strategy_file('DiamondStrategy', trade_date, 1, os.path.join(sourse_path1, i), is_delete = False, is_ready=1)
    for i in [i for i in os.listdir(sourse_path2) if i.startswith('morning')]:
        if not i.endswith('_1.xlsx'):
            upload_strategy_file('DiamondStrategy', next_trading_day, 1, os.path.join(sourse_path2, i), is_delete = False, is_ready=1)
        
        
if __name__ == '__main__':
    def flag_check(trade_date):
        path1 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'task.success')
        con_1 = os.path.exists(path1)
        return con_1
        
    end_date = pd.Timestamp.now().strftime('%Y%m%d')

    while True:
        if flag_check(end_date):
            break
        time.sleep(2)
    print('flag check finished!')
    
    excel_transmission_tyyth_separate(end_date)
    lm.sendMessage('一体化参数已上传')