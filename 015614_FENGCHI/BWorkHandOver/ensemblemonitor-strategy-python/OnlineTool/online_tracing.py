# @Time : 2021/3/5 10:03
# @Author : Zhichen Lu
# @File : online_tracing.py
import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading/StockSelection', '/data/user/015664/TriggeredTrading/AWorkHandOver', '/data/user/015664/TriggeredTrading/AWorkHandOver/alphaResearch/dataUpdate', '/data/user/015664/TriggeredTrading/AWorkHandOver/Other/code', '/data/user/015664/TriggeredTrading'])


from xquant.marketdata import MarketData
import pandas as pd
# from online_conf import holding_info_path, daily_out_path, init_conf_path
from ExtraTools import get_path_conf
import gc, os
import time, datetime
from dataApi.tradeDate import get_pre_trade_date
import configparser
from ExtraTools import get_nonfix_in_val
# path_conf = get_path_conf()
# holding_info_path, init_conf_path = [path_conf[x] for x in ['holding_info_path', 'init_conf_path']]

date = int(datetime.date.today().strftime('%Y%m%d'))
conf = get_nonfix_in_val('ini',date,'/data/group/800319/strategy_local_path3/')#configparser.ConfigParser()
# conf.read(init_conf_path + '%d.ini' % date)
pre_account_value = eval(dict(conf['account_info'])['account_value'])

pre_date = get_pre_trade_date(date)
holding = get_nonfix_in_val('holding_info',date,'/data/group/800319/strategy_local_path3/')#pd.read_pickle(holding_info_path + '%d.pkl' % pre_date)
holding.pop('cash')
holding_stk = [x for x in holding]
#

from xquant.marketdata import MarketData

md = MarketData()
# md.get_data_by_date('Stock', stk, date, ['3'])[-1:].set_index('HTSCSecurityID')

#
from dataApi.sendInfo import send_message

while True:
    online_data = []
    for stk in holding_stk:
        temp_data = md.get_data_by_date('Stock', stk, date, ['3'])[-1:].set_index('HTSCSecurityID')
        online_data.append(temp_data[['LastPx', 'PreClosePx']])
    online_data = pd.concat(online_data)
    online_data['vol'] = pd.Series(holding)
    online_data['PreValue'] = online_data['vol'] * online_data['PreClosePx']
    online_data['pct_change'] = online_data['LastPx'] / online_data['PreClosePx'] - 1
    profit = (online_data['pct_change'] * online_data['PreValue']).sum()
    now = datetime.datetime.now().strftime('%H%M%S')
    # if datetime.datetime.now().minute>30 or datetime.datetime.now().hour>=10:
    #     send_message(['015664'],f'{now}:相对前日收益:{(profit * 100 / pre_account_value):.2f}%, 收益额 {profit}')
    print(f'{now}:相对前日收益:{(profit * 100 / pre_account_value):.2f}%, 收益额 {profit}')
    del online_data
    time.sleep(60)

