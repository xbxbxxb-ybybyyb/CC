import sys
sys.path.insert(4,'/data/user/015626/data/share/Code/factor_test/')
sys.path.insert(4,'/data/user/015626/data/share/Code/strategy_back_test/')
sys.path.insert(4,'/data/user/015626/data/share/Code/utils/')

import subprocess
package_name = "/data/user/015626/PuLP-2.6.0-py3-none-any.whl"  # 要安装的包名
subprocess.check_call(["pip", "install", package_name])

import pandas as pd
import numpy as np
import datetime
import re
import os, glob
from xquant.marketdata import MarketData as XMD
from xquant.thirdpartydata.marketdata import MarketData as XMDTP
import multifactor.utility.common as ut
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from multifactor.IO import IO
from tqdm import tqdm
from multiprocessing import Pool
import dill
pd.set_option('max_columns',100)
import shutil
import bottleneck as bk
# from back_test_tick_multisignal_v3 import *
import random
from xquant.factordata import FactorData
from pandas.testing import assert_frame_equal
import matplotlib.pyplot as plt
from CHECK_PARA import *
# from SIF_Factor_Test23 import * 
import warnings
warnings.filterwarnings('ignore')
from pandas.testing import assert_frame_equal
from pulp import *

col_list = ['dt','Buy1Price','Sell1Price','HighPx_change', 'LowPx_change', 'LastPx','volume', 'amount', 'vwap']
for x in col_list:
    exec("%s_idx = col_list.index('%s')" % (x, x))

kind = 'IC'
# contract = 'IC2207'
# date = 20220707
def get_deal_px_vol(para):
    
    date = para[0]
    contract = para[1]
    if os.path.exists(f'/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/RECENT_MONTH_with_deal_estimate/{kind}_CFE/{date}.csv'):
        return
    print(para)
    signal_date = pd.read_csv('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/%s/%s.csv' % (contract, date), index_col=0, parse_dates=True)
    signal_date.loc[signal_date.HighPx != signal_date.HighPx.shift(1), 'HighPx_change'] = signal_date['HighPx']
    signal_date.loc[signal_date.LowPx != signal_date.LowPx.shift(1), 'LowPx_change'] = signal_date['LowPx']
    signal_date['volume'] = signal_date.TotalVolumeTrade.diff()
    signal_date['amount'] = signal_date.TotalValueTrade.diff()
    signal_date['vwap'] = signal_date['amount'] / signal_date['volume'] / 200
    signal_date = signal_date.replace([np.inf, -np.inf], np.nan)
    tickdf = signal_date.copy()
    signal_date = signal_date[['Buy1Price','Sell1Price','HighPx_change', 'LowPx_change', 'LastPx','volume', 'amount', 'vwap']].reset_index()
    signal_date[['Buy1Price','Sell1Price']] = signal_date[['Buy1Price','Sell1Price']].replace(0, np.nan)
    signal_date = signal_date.values

    px_vol_list = []
    for _k in range(len(signal_date)):
    #     print(_k)
        this_tick = signal_date[_k]
        volume = this_tick[volume_idx]
        amount = this_tick[amount_idx]
        vwap = this_tick[vwap_idx]
        time = this_tick[dt_idx]
        px_vol_dict = {}
        if volume > 0:
            Buy1Price = this_tick[Buy1Price_idx]
            Sell1Price = this_tick[Sell1Price_idx]
            highpx = this_tick[HighPx_change_idx]
            lowpx = this_tick[LowPx_change_idx]
            lastpx = this_tick[LastPx_idx]

            x0_px = round((vwap*10 - vwap*10 % 2)/10, 1)
            y0_px = x0_px + 0.2

            minpx = np.nanmin([Buy1Price, lowpx, lastpx])
            maxpx = np.nanmax([Sell1Price, highpx, lastpx])
            xnum = round(max((x0_px - minpx) / 0.2 + 1, 10), 0)
            ynum = round(max((maxpx - y0_px) / 0.2 + 1, 10), 0)
            xlist = [round(x0_px - 0.2*i, 1) for i in range(int(xnum))]
            ylist = [round(y0_px + 0.2*i, 1) for i in range(int(ynum))]

            highpx_idx, lowpx_idx, lastpx_idx = np.nan, np.nan, np.nan
            if highpx == highpx:
                if lastpx > highpx:
                    highpx = lastpx
                ylist = [x for x in ylist if x <= highpx]
                if highpx in ylist:
                    highpx_idx = 'y' + str(ylist.index(highpx))
            if lowpx == lowpx:
                if lastpx < lowpx:
                    lowpx = lastpx
                xlist = [x for x in xlist if x >= lowpx]
                lowpx_idx = 'x' + str(xlist.index(lowpx))
                if highpx in xlist:
                    highpx_idx = 'x' + str(xlist.index(highpx))

            if lastpx in ylist:
                lastpx_idx = 'y' + str(ylist.index(lastpx))
            elif lastpx in xlist:
                lastpx_idx = 'x' + str(xlist.index(lastpx))

            prob = LpProblem("myProblem", LpMinimize)
            # 建立变量
            material = ['x%s'%i for i in range(len(xlist))] + ['y%s'%i for i in range(len(ylist))]
            mass = LpVariable.dicts('', material, lowBound=0, upBound=volume, cat = 'Integer')
            # 设置目标函数
            if 'y0' in material:
                prob += -(mass['x0'] + mass['y0'])
            else:
                prob += -mass['x0']
            # 添加约束
            amount_restrain = {'x%s'%i:xlist[i] for i in range(len(xlist))}
            amount_restrain.update({'y%s'%i:ylist[i] for i in range(len(ylist))})
            prob += lpSum([amount_restrain[item] * mass[item] for item in material]) == amount / 200
            prob += lpSum([mass[item] for item in material]) == volume

            if highpx_idx == highpx_idx:
                prob += mass[highpx_idx] >= 1
            if lowpx_idx == lowpx_idx:
                prob += mass[lowpx_idx] >= 1
            prob += mass[lastpx_idx] >= 1
            _ = prob.solve()

            if _ == 1:
                for v in prob.variables():
                    if v.varValue is not None and v.varValue > 0:
                        name = v.name[1]
                        num = int(v.name[2:])
                        if name == 'x':
                            px = xlist[num]
                        elif name == 'y':
                            px = ylist[num]    
                        px_vol_dict[px] = v.varValue
            del(prob)
        px_vol_list.append(px_vol_dict)
    tickdf['deal_px_vol'] = px_vol_list
    tickdf.to_csv(f'/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/RECENT_MONTH_with_deal_estimate/{kind}_CFE/{date}.csv')

univ = IO.read_data([20241010,20241120], columns = ['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
univ = univ.xs(f'{kind}.CFE', level = 1).reset_index()

datelist = univ['dt'].tolist()
contractlist = univ.contract_00.tolist()
paralist = [[int(datelist[i].strftime('%Y%m%d')), contractlist[i][:6]] for i in range(len(datelist))]

with Pool(24) as pool:
    pool.map(get_deal_px_vol, paralist)
#for para in paralist:
#    get_deal_px_vol(para)