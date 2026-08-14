import sys
sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
import os
from tqdm import tqdm
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')

file_list = os.listdir('/data/user/015628/MakeMoney/LimitUpPredStrategy/Factor/015628/Approved/')

for file in ['Pct5d.py']:
    factor = file[:-3]
    print(factor)
    exec('from LimitUpPredStrategy.Factor.xuqi.Approved.%s import Factor'%factor)
    exec('fc = Factor(start_date=20140102, end_date=20210715)')
    exec('test = fc.calculate(%s, save_path=\'/arch1/group/800442/800319/ZTfactors/Approved_2021/\')'%factor)