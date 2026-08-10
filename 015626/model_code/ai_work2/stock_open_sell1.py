import sys
sys.path.insert(4,'/data/user/015626/JupyterNotebooks/utils/')
from KZZ_Factor_Test import *
import json,datetime,os,glob
from multiprocessing import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob
import bottleneck as bk
from operators_wyc import *
from tqdm import tqdm
from xquant.marketdata import MarketData as XMD
from xquant.thirdpartydata.marketdata import MarketData as XMDTP
def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')

def order_planner(auction_amount, stock_price, tick_deal_ratio=0.2, target_amount=3E6, order_freq=100, min_order_size=100):
    # action_amount: 09:25 total amount in RMB
    # stock_price: auction end stock price
    # tick_deal_ratio: deal ratio per tick
    # target_amount: order amount per stock in RMB
    # order_freq: gap between split orders in ms
    # min_order_size: stock exchange minimum vol size per stock
    # return: list of order volumns as in [500, 300, 100, 100, 100, ...]
    # the sum of return list <= (target_amount / stock_price)
    # each element in return list rounded by min_order_size
    TICK_AUCTION_RATIO = {1: 0.5617, 2: 0.2053, 3: 0.1326, 4: 0.1178, 5: 0.0986, 6: 0.0778, 7: 0.0725, 8: 0.0729, 9: 0.0762, 10: 0.0772, 
                          11: 0.078, 12: 0.0734, 13: 0.0719, 14: 0.0683, 15: 0.0634, 16: 0.0594, 17: 0.0598, 18: 0.0579, 19: 0.0575, 
                          20: 0.0614}
    target_vol = target_amount // (stock_price * min_order_size)
    if target_vol == 0:
        return []
    order_num_per_tick = int(np.floor(3 * 1000 / order_freq))
    residual_vol = 0
    delt_vol = 0
    order_list = []
    for key in sorted(TICK_AUCTION_RATIO.keys()):
        amt_tick = auction_amount * TICK_AUCTION_RATIO[key] * tick_deal_ratio
        vol_per_order = amt_tick / order_num_per_tick / (stock_price * min_order_size)
        vol_per_order_list = [vol_per_order // 1] * order_num_per_tick
        residual_vol += vol_per_order * order_num_per_tick - sum(vol_per_order_list)
        if residual_vol > 1:
            residual_num = residual_vol // 1
            residual_vol = residual_vol % 1
            vol_per_order_list = [item + 1 if idx < residual_num else item \
                                           for idx, item in enumerate(vol_per_order_list)]
        for v in vol_per_order_list:
            if v > 0:
                deal_v = min(v, target_vol - delt_vol)
                order_list.append(int(deal_v * min_order_size))
                delt_vol += deal_v
                if delt_vol == target_vol:
                    return order_list
    if np.sum(order_list) / min_order_size > target_vol:
        raise AssertionError('Abnormal Deal Volume')
        return []
    return order_list

m1 = pd.read_hdf('/data/user/015626/data/share/LOCAL_DATA/stock_open/M1_selected.h5')
m1 = m1.unstack().shift(1).stack().to_frame()
m1.columns = ['signal']
md = IO.read_data([20201120,20220909],columns=['open','close'])
m1 = m1.join(md, how = 'left')

m1= m1.loc[pd.to_datetime('20220101'):]

# price_index_list = [-2,-1,0,1,2]
def get_dealinfo_sell_submit(para):
    date = para[0]
    stock = para[1]
#     date = 20220105
#     stock = '000782.SZ'
    tran_deal_ratio = 1
    date = str(date)
    md = XMD()
    tick = md.get_data_by_time_frame("Stock", stock, "%s 092500000"%date, "%s 092959250"%date)
    transaction = md.get_data_by_time_frame("Transaction", stock, "%s 093000000"%date, "%s 093500250"%date)
    if len(tick) == 0 | len(transaction) == 0:
        return
    del(md)
    transaction = transaction[(transaction.TradePrice != 0) & (transaction.TradeType != 1)]
    auction_amount = tick.iloc[-1]['TotalValueTrade']
    openpx = tick.iloc[-1]['LastPx']

    timedelta_list = [x.strftime('%H%M%S%f')[:-3] for x in pd.date_range('09:30:00', '09:35:00', freq='100ms').to_list()]
    tran_list = []
    for i in range(1, len(timedelta_list)):
        temp = transaction[(transaction.MDTime >= timedelta_list[i-1]) & (transaction.MDTime < timedelta_list[i])]
        px_qty_list = [x for x in zip(temp.TradePrice.tolist(),temp.TradeQty.tolist())]
        px_qty_list = sorted(px_qty_list, key=lambda x:x[0], reverse = False)
        tran_list.append(px_qty_list)

    order_list = order_planner(auction_amount=auction_amount, stock_price=openpx)
    if len(order_list) == 0:
        return

    deal_vol = 0
    submit_deal_vol = 0
    deal_money = 0
    submit_deal_money = 0
    res_vol = 0
    order_idx = 0
    tran_idx = 0
    target_vol = np.sum(order_list)

    submit_list = [[openpx + i*0.01, order_list[0] * ordervol_ratio] for i in price_index_list]

    chedan_count = 0
    while deal_vol < np.sum(order_list) and order_idx < len(order_list) and deal_vol < target_vol:

        res_vol += order_list[order_idx]
        t_px_vol = tran_list[tran_idx]

        # 挂单撮合所用
        t_px_vol_for_submit_order = []

        # 主动单撮合
        for pv in t_px_vol:
            p = pv[0]
            v = pv[1]
            _deal_vol = min(res_vol, v * tran_deal_ratio, target_vol - deal_vol)
            deal_money += _deal_vol * p
            res_vol -= _deal_vol
            deal_vol += _deal_vol
            v -= _deal_vol
            if v > 0:
                t_px_vol_for_submit_order.append([p,v])

        # 挂单撮合
        t_px_vol_for_submit_order = [[p,v] for p,v in t_px_vol_for_submit_order]
        submit_list = sorted(submit_list, key = lambda x:x[0], reverse=True)
        submit_list = [[p,v] for p,v in submit_list]

        submit_0vol_index = []
        for j_submit in range(len(submit_list)-1, -1, -1):
            if deal_vol >= target_vol:
                break
            for i_deal in range(len(t_px_vol_for_submit_order)):
                if round(t_px_vol_for_submit_order[i_deal][0], 2) >= round(submit_list[j_submit][0], 2):
                    _deal_vol = min(t_px_vol_for_submit_order[i_deal][1], submit_list[j_submit][1], target_vol - deal_vol)
                    t_px_vol_for_submit_order[i_deal][1] = t_px_vol_for_submit_order[i_deal][1] - _deal_vol
                    submit_list[j_submit][1] = submit_list[j_submit][1] - _deal_vol

                    deal_money += _deal_vol * submit_list[j_submit][0]
                    submit_deal_money += _deal_vol * submit_list[j_submit][0]
                    deal_vol += _deal_vol
                    submit_deal_vol += _deal_vol

                    if submit_list[j_submit][1] == 0:
                        submit_0vol_index.append(j_submit)
                        break
                    if deal_vol >= target_vol:
                        break

        for jj in submit_0vol_index:
            del submit_list[jj]

        # 撮合完毕，继续挂单
        if len(t_px_vol) > 0:
            if not chedan:
                submit_list += [[t_px_vol[-1][0] + i*0.01, order_list[0] * ordervol_ratio] for i in price_index_list]
            else:
                if chedan_count == chedan_count_t:
                    submit_list = [[t_px_vol[-1][0] + i*0.01, order_list[0] * ordervol_ratio] for i in price_index_list]
                    chedan_count = 0

        chedan_count += 1

        order_idx += 1
        tran_idx += 1
    return pd.DataFrame([date, stock, deal_money, deal_vol, np.sum(order_list), submit_deal_money, submit_deal_vol], index = ['dt','Ticker','deal_money','deal_vol', 'target_vol', 'submit_deal_money', 'submit_deal_vol']).T

_m1 = m1.reset_index()
dtlist = [x.strftime('%Y%m%d') for x in _m1.dt.tolist()]
tickerlist = _m1.Ticker.tolist()
paralist = [x for x in zip(dtlist,tickerlist)]

pi_list = [[3,2,1,0,-1,-2],[4,3,2,1,0,-1],[5,4,3,2,1,0],[6,5,4,3,2,1],[7,6,5,4,3,2]]
ov_list = [0.8, 1, 1.2, 1.5, 2,3,4]
chedan_t_list = [5,10]
for price_index_list in pi_list:
    for ordervol_ratio in ov_list:
        for chedan in [True,False]:
            for chedan_count_t in chedan_t_list:
                rlist = []
                with Pool(24) as pool:
                    rlist = pool.map(get_dealinfo_sell_submit, paralist)
                tranr = pd.concat(rlist, axis = 0)
                tranr['dt'] = pd.to_datetime(tranr['dt'])
                tranr = tranr.set_index(['dt', 'Ticker']).sort_index()
                m1dealinfo = m1.join(tranr, how = 'left')

                m1dealinfo['deal_px'] = m1dealinfo['deal_money'] / m1dealinfo['deal_vol']
                m1dealinfo['slippage'] = m1dealinfo['deal_px'] / m1dealinfo['open'] - 1
                slippage = m1dealinfo['slippage'].mean()

                print(price_index_list, ordervol_ratio, chedan,chedan_count_t, slippage)
                with open('/data/user/015626/data/share/LOCAL_DATA/stock_open/stock_open_sell1.txt', 'a') as file:
                    file.write(str(datetime.datetime.now()) + '#'+ str(price_index_list) + '#' + str(ordervol_ratio)+ '#'+ str(chedan)+ '#'+ str(chedan_count_t) + '#'+ str(slippage) + '\r\n')                    