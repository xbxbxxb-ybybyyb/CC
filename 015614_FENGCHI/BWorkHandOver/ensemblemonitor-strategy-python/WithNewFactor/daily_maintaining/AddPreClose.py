# @Time : 2021/8/14 19:32
# @Author : Zhichen Lu
# @File : AddPreClose.py

import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])


from dataApi.getData import get_recent_trade_date,get_date_range
from dataApi.stockList import trans_windcode2int
from xquant.factordata import FactorData
import pandas as pd
import numpy as np
import datetime
from dataApi.sendInfo import send_message
fd = FactorData()

# date = get_recent_trade_date(dividing_point=7)
for date in [int(datetime.date.today().strftime('%Y%m%d'))]:
    code_list = pd.read_pickle(f'/data/group/800442/800319/strategy_HFfactor/{date}/DateCode/code_list.pkl')
    df = fd.get_factor_value('Basic_factor', None, [str(date)], ['mdc_pre_close'])['mdc_pre_close'].dropna().rename(
        'pre_close').reset_index().set_index('stock').drop('mddate', axis=1).iloc[:, 0]
    df.index = df.index.map(trans_windcode2int)
    df = df.reindex(code_list).values[None, :]
    np.save(f'/data/group/800442/800319/strategy_HFfactor/{date}/TmrLowFreq/pre_close.npy', df)
send_message(['015664'],'pre_close done')