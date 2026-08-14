# @Time : 2021/9/23 23:46
# @Author : Zhichen Lu
# @File : check_itntersection.py

from ExtraTools import get_path_conf
import pandas as pd

path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForMixSim/')
summary = pd.read_pickle(path_conf['daily_out_path']+'20210923.pkl')
all = set()
for bar in [1000,1030,1100,1300,1330,1400,1430]:

    all = all.union(summary['sell_order_record'][bar].index.tolist())
    all = all.union(summary['buy_order_record'][bar].index.tolist())


fc = ['600188.SH',
'601600.SH',
'300769.SZ',
'002202.SZ',
'603077.SH',
'000902.SZ',
'000739.SZ',
'600110.SH',
'300343.SZ',
'605305.SH',
'601678.SH',
'000591.SZ',
]