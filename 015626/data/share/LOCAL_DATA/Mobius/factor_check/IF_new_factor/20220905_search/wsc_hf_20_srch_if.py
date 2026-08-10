from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class wsc_hf_20_srch_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['PxVolCorr','buy_smallorder_count','weight','buy_smallorder_money','sell_smallorder_money_v2','BuyUniqueOrderNum','buy_midorder_money','sell_midorder_money_v2']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = None 

    def calculate(self, df):
        pvc_w = (df['PxVolCorr'][-191:] * df['weight'][-191:]).sum(axis = 1)
        bbn_4_to_bun = (df['buy_smallorder_count'][-1:].sum(axis = 1) / df['BuyUniqueOrderNum'][-1:].sum(axis = 1)).values[-1]
        bba_4_r = df['buy_smallorder_money'][-11:].sum(axis = 1) / (df['buy_smallorder_money'][-11:] + df['sell_smallorder_money_v2'][-11:]).sum(axis = 1)
        bba_3_r_w = (df['buy_midorder_money'][-26:] / (df['buy_midorder_money'][-26:] + df['sell_midorder_money_v2'][-26:]) * df['weight'][-26:]).sum(axis = 1)

        x1 = ts_midpoint(ts_max(pvc_w, 110)[-81:], 80).values[-1]        
        x2 = midprice(midpoint(bba_3_r_w, 15)[-11:], bba_4_r, 10).values[-1]
        factor = (x1 + x2 + bbn_4_to_bun) * -1
        return factor