# coding: utf-8
# Author：fengchi863
# Date ：2025/5/28 13:27
import datetime as dt
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from MixedWork.GreyStockGenerator.tools import trans_any2code
from ProdWork.intra_strong.new_framework.tools import getExtraBuyInfo
import sys
import os
import time
s = FactorData()

if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
    date = '20250825'

lastdate = s.tradingday(date, -2)[0]
print('当前日期 = %s' % date)

date2 = date[:4] + '-' + date[4:6] + '-' + date[6:]
record_o45_fpath = f'/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_{date}.xls'
log_order_fpath = f'/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_{date}_prod.xlsx'

hist_sell_jupiter_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录-{lastdate}.xlsx'
hist_sell_europa_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录New-{lastdate}.xlsx'
hist_sell_saturn_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目二总卖出记录-{lastdate}.xlsx'
hist_sell_ceres_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录Ceres-{lastdate}.xlsx'
hist_sell_p4_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录P4-{lastdate}.xlsx'
hist_sell_mimas_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录Mimas-{lastdate}.xlsx'
hist_sell_metis_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录Metis-{lastdate}.xlsx'
hist_sell_leda_fpath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录Leda-{lastdate}.xlsx'

while not os.path.exists(record_o45_fpath):
    print(f'等待 {record_o45_fpath} !!!!!!!!!!')
    time.sleep(60)

record_o45 = pd.read_excel(record_o45_fpath)
todaySellDf = record_o45.query('委托方向 == "卖出"')
todayBuyDf = record_o45.query('委托方向 == "买入"')
todayBuyDf['证券代码'] = todayBuyDf['证券代码'].apply(trans_any2code)

orderDf = pd.read_excel(log_order_fpath, sheet_name='每日订单')
orderDf[['lastQty', 'lastPx']] = orderDf[['lastQty', 'lastPx']].astype(float)
orderDf['lastAmt'] = orderDf['lastQty'] * orderDf['lastPx']

if len(orderDf) > 0:
    orderDf = orderDf[orderDf['transactionTime'].apply(lambda x: x[11:13]) != '00'] # 不敢删，不知道为啥这么判断
    sell_orderDf = orderDf[orderDf['orderSide'] == 'Sell']
    buy_orderDf = orderDf[orderDf['orderSide'] == 'Buy']
else:
    orderDf = pd.DataFrame()
    sell_orderDf = pd.DataFrame()
    buy_orderDf = pd.DataFrame()

#%% 对买入进行分配
#%% 对买入进行分配
#%% 对买入进行分配

orderDf_jupiter = orderDf.query('actionSource == "JupiterN"')
orderDf_europa = orderDf.query('actionSource == "JupiterNew"')
orderDf_metis = orderDf.query('actionSource == "Metis"')
orderDf_leda = orderDf.query('actionSource == "Leda"')
orderDf_saturn = orderDf.query('actionSource == "Saturn"')
orderDf_ceres = orderDf.query('actionSource == "Ceres"')
orderDf_p4 = orderDf.query('actionSource == "P4"')
orderDf_mimas = orderDf.query('actionSource == "Mimas"')

todayBuyDf_jupiter = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_jupiter['stockcode'])))]
todayBuyDf_europa = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_europa['stockcode'])))]
todayBuyDf_metis = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_metis['stockcode'])))]
todayBuyDf_leda = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_leda['stockcode'])))]
todayBuyDf_saturn = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_saturn['stockcode'])))]
todayBuyDf_ceres = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_ceres['stockcode'])))]
todayBuyDf_p4 = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_p4['stockcode'])))]
todayBuyDf_mimas = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_mimas['stockcode'])))]

todayBuyDf_jupiter = getExtraBuyInfo(todayBuyDf_jupiter)

if len(todayBuyDf) == 0:
    print('今天成交回报没有买入！！！！！！')
    buyDf_jupiter = pd.DataFrame()
    buyDf_europa = pd.DataFrame()
    buyDf_metis = pd.DataFrame()
    buyDf_saturn = pd.DataFrame()
    buyDf_ceres = pd.DataFrame()
    buyDf_p4 = pd.DataFrame()
    buyDf_mimas = pd.DataFrame()
    buyDf_leda = pd.DataFrame()
else:
    buy_orderDf_tot_info = todayBuyDf.rename(columns={'证券代码': 'stockcode', '成交数量': 'deal_vol', '成交金额': 'deal_amt'})[['deal_vol', 'deal_amt', 'stockcode']]
    buy_orderDf_tot_info['deal_vwap'] = buy_orderDf_tot_info['deal_amt'] / buy_orderDf_tot_info['deal_vol']
    buy_orderDf_jupiter_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_jupiter['stockcode']))].set_index('stockcode')
    buy_orderDf_europa_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_europa['stockcode']))].set_index('stockcode')
    buy_orderDf_metis_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_metis['stockcode']))].set_index('stockcode')
    buy_orderDf_leda_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_leda['stockcode']))].set_index('stockcode')
    buy_orderDf_saturn_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_saturn['stockcode']))].set_index('stockcode')
    buy_orderDf_saturn_info = buy_orderDf_saturn_info[buy_orderDf_saturn_info['deal_amt'] != 0]
    buy_orderDf_ceres_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_ceres['stockcode']))].set_index('stockcode')
    buy_orderDf_ceres_info = buy_orderDf_ceres_info[buy_orderDf_ceres_info['deal_amt'] != 0]
    buy_orderDf_p4_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_p4['stockcode']))].set_index('stockcode')
    buy_orderDf_p4_info = buy_orderDf_p4_info[buy_orderDf_p4_info['deal_amt'] != 0]
    buy_orderDf_mimas_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(orderDf_mimas['stockcode']))].set_index('stockcode')
    buy_orderDf_mimas_info = buy_orderDf_mimas_info[buy_orderDf_mimas_info['deal_amt'] != 0]

    # 在日志中有jupiter买入或者jupiter尝试买入才会进行输出
    buyDf_jupiter = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_jupiter_info.index))]
    buyDf_europa = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_europa_info.index))]
    buyDf_metis = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_metis_info.index))]
    buyDf_leda = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_leda_info.index))]
    buyDf_saturn = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_saturn_info.index))]
    buyDf_ceres = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_ceres_info.index))]
    buyDf_p4 = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_p4_info.index))]
    buyDf_mimas = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_mimas_info.index))]

    # commonInfoColumns是成交回报中直接有的信息、buyExtraColumns是通过计算重新获取的信息
    buyDf_jupiter = getExtraBuyInfo(buyDf_jupiter)
    buyDf_europa = getExtraBuyInfo(buyDf_europa)
    buyDf_metis = getExtraBuyInfo(buyDf_metis)
    buyDf_leda = getExtraBuyInfo(buyDf_leda)
    buyDf_saturn = getExtraBuyInfo(buyDf_saturn)
    buyDf_ceres = getExtraBuyInfo(buyDf_ceres)
    buyDf_p4 = getExtraBuyInfo(buyDf_p4)
    buyDf_mimas = getExtraBuyInfo(buyDf_mimas)

    for idx, row in buyDf_jupiter.iterrows():
        stock_code = row['证券代码']
        sel_order = orderDf_jupiter[((orderDf_jupiter['ordStatus'] == 'PARTIALLY_FILLED') |
                                         (orderDf_jupiter['ordStatus'] == 'FILLED')) &
                                        (orderDf_jupiter['stockcode'] == stock_code)]
        buyDf_jupiter.loc[idx, ['成交数量', '成交金额']] = sel_order[['lastQty', 'lastAmt']].sum().values
        buyDf_jupiter.loc[idx, '成交均价'] = buyDf_jupiter.loc[idx, '成交金额'] / buyDf_jupiter.loc[idx, '成交数量']
        buyDf_jupiter.loc[idx, '买入当日收益率(%)'] = buyDf_jupiter.loc[idx, '买入当天收盘价'] / buyDf_jupiter.loc[idx, '成交均价'] - 1

    for idx, row in buyDf_metis.iterrows():
        stock_code = row['证券代码']
        sel_order = orderDf_metis[((orderDf_metis['ordStatus'] == 'PARTIALLY_FILLED') |
                                       (orderDf_metis['ordStatus'] == 'FILLED')) &
                                      (orderDf_metis['stockcode'] == stock_code)]
        buyDf_metis.loc[idx, ['成交数量', '成交金额']] = sel_order[['lastQty', 'lastAmt']].sum().values
        buyDf_metis.loc[idx, '成交均价'] = buyDf_metis.loc[idx, '成交金额'] / buyDf_metis.loc[idx, '成交数量']
        buyDf_metis.loc[idx, '买入当日收益率(%)'] = buyDf_metis.loc[idx, '买入当天收盘价'] / buyDf_metis.loc[idx, '成交均价'] - 1

    for idx, row in buyDf_europa.iterrows():
        stock_code = row['证券代码']
        flag = 0
        buy_vol = float(buy_orderDf_europa_info.loc[stock_code]['deal_vol'])
        buy_amt = float(buy_orderDf_europa_info.loc[stock_code]['deal_amt'])
        if stock_code in buyDf_jupiter[buyDf_jupiter['发生日期'] == date2]['证券代码'].tolist():
            buy_vol = buy_vol - float(buyDf_europa[(buyDf_europa['发生日期'] == date2) & (buyDf_europa['证券代码'] == stock_code)]['成交数量'])
            buy_amt = buy_amt - float(buyDf_europa[(buyDf_europa['发生日期'] == date2) & (buyDf_europa['证券代码'] == stock_code)]['成交金额'])
            flag = 1
        if stock_code in buyDf_metis[buyDf_metis['发生日期'] == date2]['证券代码'].tolist():
            buy_vol = buy_vol - float(buyDf_metis[(buyDf_metis['发生日期'] == date2) & (buyDf_metis['证券代码'] == stock_code)]['成交数量'])
            buy_amt = buy_amt - float(buyDf_metis[(buyDf_metis['发生日期'] == date2) & (buyDf_metis['证券代码'] == stock_code)]['成交金额'])
            flag = 1
        if stock_code in buyDf_ceres[buyDf_ceres['发生日期'] == date2]['证券代码'].tolist():
            buy_vol = buy_vol - float(buyDf_ceres[(buyDf_ceres['发生日期'] == date2) & (buyDf_ceres['证券代码'] == stock_code)]['成交数量'])
            buy_amt = buy_amt - float(buyDf_ceres[(buyDf_ceres['发生日期'] == date2) & (buyDf_ceres['证券代码'] == stock_code)]['成交金额'])
            flag = 1
        if stock_code in buyDf_p4[buyDf_p4['发生日期'] == date2]['证券代码'].tolist():
            buy_vol = buy_vol - float(buyDf_p4[(buyDf_p4['发生日期'] == date2) & (buyDf_p4['证券代码'] == stock_code)]['成交数量'])
            buy_amt = buy_amt - float(buyDf_p4[(buyDf_p4['发生日期'] == date2) & (buyDf_p4['证券代码'] == stock_code)]['成交金额'])
            flag = 1
        if stock_code in buyDf_mimas[buyDf_mimas['发生日期'] == date2]['证券代码'].tolist():
            buy_vol = buy_vol - float(buyDf_mimas[(buyDf_mimas['发生日期'] == date2) & (buyDf_mimas['证券代码'] == stock_code)]['成交数量'])
            buy_amt = buy_amt - float(buyDf_mimas[(buyDf_mimas['发生日期'] == date2) & (buyDf_mimas['证券代码'] == stock_code)]['成交金额'])
            flag = 1
        buyDf_europa.loc[idx, '成交数量'] = buy_vol
        buyDf_europa.loc[idx, '成交金额'] = buy_amt if buy_amt >= 0 else 0
        if flag == 0:
            buyDf_europa.loc[idx, ['成交数量', '成交金额', '成交均价']] = buy_orderDf_europa_info.loc[stock_code][['deal_vol', 'deal_amt', 'deal_vwap']].values
        buyDf_europa.loc[idx, '买入成交均价'] = buyDf_europa.loc[idx, '成交金额'] / buyDf_europa.loc[idx, '成交数量']
        buyDf_europa.loc[idx, '买入当日收益率(%)'] = buyDf_europa.loc[idx, '买入当天收盘价'] / buyDf_europa.loc[idx, '成交均价'] - 1

    for idx, row in buyDf_saturn.iterrows():
        stock_code = row['证券代码']
        sel_order = orderDf_saturn[((orderDf_saturn['ordStatus'] == 'PARTIALLY_FILLED') |
                                        (orderDf_saturn['ordStatus'] == 'FILLED')) &
                                       (orderDf_saturn['stockcode'] == stock_code)]
        buyDf_saturn.loc[idx, ['成交数量', '成交金额']] = sel_order[['lastQty', 'lastAmt']].sum().values
        buyDf_saturn.loc[idx, '成交均价'] = buyDf_saturn.loc[idx, '成交金额'] / buyDf_saturn.loc[idx, '成交数量']
        buyDf_saturn.loc[idx, '买入当日收益率(%)'] = buyDf_saturn.loc[idx, '买入当天收盘价'] / buyDf_saturn.loc[idx, '成交均价'] - 1
        # index_in_timecost = signal_info_pj2_931[signal_info_pj2_931['Unnamed: 0'] == stock_code].index.tolist()[0]
        # buyDf_saturn.loc[idx, ['委托金额']] = float(signal_info_pj2_931.loc[index_in_timecost][['totalOrderAmt']])

    for idx, row in buyDf_leda.iterrows():
        stock_code = row['证券代码']
        flag = 0
        buy_vol = float(buy_orderDf_leda_info.loc[stock_code]['deal_vol'])
        buy_amt = float(buy_orderDf_leda_info.loc[stock_code]['deal_amt'])
        if stock_code in buyDf_saturn[buyDf_saturn['发生日期'] == date2]['证券代码'].tolist():
            buy_vol = buy_vol - float(buyDf_saturn[(buyDf_saturn['发生日期'] == date2) & (buyDf_saturn['证券代码'] == stock_code)]['成交数量'])
            buy_amt = buy_amt - float(buyDf_saturn[(buyDf_saturn['发生日期'] == date2) & (buyDf_saturn['证券代码'] == stock_code)]['成交金额'])
            flag = 1
        buyDf_leda.loc[idx, '成交数量'] = buy_vol
        buyDf_leda.loc[idx, '成交金额'] = buy_amt
        if flag == 0:
            buyDf_leda.loc[idx, ['成交数量', '成交金额', '成交均价']] = buy_orderDf_leda_info.loc[stock_code][['deal_vol', 'deal_amt', 'deal_vwap']].values
        buyDf_leda.loc[idx, '成交均价'] = buyDf_leda.loc[idx, '成交金额'] / buyDf_leda.loc[idx, '成交数量']
        buyDf_leda.loc[idx, '买入当日收益率(%)'] = buyDf_leda.loc[idx, '买入当天收盘价'] / buyDf_leda.loc[idx, '成交均价'] - 1

    for idx, row in buyDf_ceres.iterrows():
        stock_code = row['证券代码']
        sel_order = orderDf_ceres[((orderDf_ceres['ordStatus'] == 'PARTIALLY_FILLED') |
                                   (orderDf_ceres['ordStatus'] == 'FILLED')) &
                                   (orderDf_ceres['stockcode'] == stock_code)]
        buyDf_ceres.loc[idx, ['成交数量', '成交金额']] = sel_order[['lastQty', 'lastAmt']].sum().values
        buyDf_ceres.loc[idx, '成交均价'] = buyDf_ceres.loc[idx, '成交金额'] / buyDf_ceres.loc[idx, '成交数量']
        # index_in_timecost = signal_info_ceres[signal_info_ceres['Unnamed: 0'] == stock_code].index.tolist()[0]
        # buyDf_ceres.loc[idx, ['委托金额']] = float(signal_info_ceres.loc[index_in_timecost][['target_amt']])
        # resDf_ceres.loc[dummy_resDfceres_index, ['委托金额']] = 0
        buyDf_ceres.loc[idx, '买入当日收益率(%)'] = (buyDf_ceres.loc[idx, '买入当天收盘价'] / buyDf_ceres.loc[idx, '成交均价'] - 1) * 100

    for idx, row in buyDf_p4.iterrows():
        stock_code = row['证券代码']
        sel_order = orderDf_p4[((orderDf_p4['ordStatus'] == 'PARTIALLY_FILLED') |
                                    (orderDf_p4['ordStatus'] == 'FILLED')) &
                                   (orderDf_p4['stockcode'] == stock_code)]
        buyDf_p4.loc[idx, ['成交数量', '成交金额']] = sel_order[['lastQty', 'lastAmt']].sum().values
        buyDf_p4.loc[idx, '成交均价'] = buyDf_p4.loc[idx, '成交金额'] / buyDf_p4.loc[idx, '成交数量']
        # idx_in_timecost = signal_info_p4[signal_info_p4['Unnamed: 0'] == stock_code].idx.tolist()[0]
        # buyDf_p4.loc[idx, ['委托金额']] = float(signal_info_p4.loc[idx_in_timecost][['target_amt']])
        # buyDf_p4.loc[idx, ['委托金额']] = 0
        buyDf_p4.loc[idx, '买入当日收益率(%)'] = (buyDf_p4.loc[idx, '买入当天收盘价'] / buyDf_p4.loc[idx, '成交均价'] - 1) * 100

    for idx, row in buyDf_mimas.iterrows():
        stock_code = row['证券代码']
        sel_order = orderDf_mimas[((orderDf_mimas['ordStatus'] == 'PARTIALLY_FILLED') |
                                       (orderDf_mimas['ordStatus'] == 'FILLED')) &
                                      (orderDf_mimas['stockcode'] == stock_code)]
        buyDf_mimas.loc[idx, ['成交数量', '成交金额']] = sel_order[['lastQty', 'lastAmt']].sum().values
        buyDf_mimas.loc[idx, '成交均价'] = buyDf_mimas.loc[buyDf_mimas, '成交金额'] / buyDf_mimas.loc[buyDf_mimas, '成交数量']
        # index_in_timecost = signal_info_mimas[signal_info_mimas['Unnamed: 0'] == stock_code].index.tolist()[0]
        # buyDf_mimas.loc[buyDf_mimas, ['委托金额']] = float(signal_info_mimas.loc[index_in_timecost][['target_amt']])
        # buyDf_mimas.loc[buyDf_mimas, ['委托金额']] = 0
        buyDf_mimas.loc[idx, '买入当日收益率(%)'] = (buyDf_mimas.loc[buyDf_mimas, '买入当天收盘价'] / buyDf_mimas.loc[buyDf_mimas, '成交均价'] - 1) * 100
#%% 对卖出进行分配
#%% 对卖出进行分配
#%% 对卖出进行分配

def read_sell(hist_sell_fpath):
    if not os.path.exists(hist_sell_fpath):
        return pd.DataFrame()
    sell_df = pd.read_excel(hist_sell_fpath, sheet_name='总卖出记录')
    sell_columns = list(sell_df.columns)
    if 'Unnamed: 0' in sell_columns:
        sell_columns.remove('Unnamed: 0')
    sell_df = sell_df[sell_columns]
    # sell_df['是否全部卖出'] = sell_df.apply(lambda x: 0 if x['卖出比例'] != '100.00%' else 1, axis=1)
    return sell_df

hist_sell_jupiter = read_sell(hist_sell_jupiter_fpath)
hist_sell_europa = read_sell(hist_sell_europa_fpath)
hist_sell_saturn = read_sell(hist_sell_saturn_fpath)
hist_sell_ceres = read_sell(hist_sell_ceres_fpath)
hist_sell_p4 = read_sell(hist_sell_p4_fpath)
hist_sell_mimas = read_sell(hist_sell_mimas_fpath)
hist_sell_metis = read_sell(hist_sell_metis_fpath)
hist_sell_leda = read_sell(hist_sell_leda_fpath)

dead_circle = 0
for idx, row in todaySellDf.iterrows():
    stock_code = trans_any2code(row['证券代码'])
    sold_qty = todaySellDf.loc[idx, '成交数量']

    def sell_one_day_holding(sold_qty, sell_df):
        history_idx = sell_df[(sell_df['证券代码'] == stock_code) & (sell_df['是否全部卖出'] != 1)].index[0]
        totalSold_indicator = sell_df.loc[history_idx]['是否全部卖出']
        if sell_df.loc[history_idx, '总卖出数量'] == '' or np.isnan(sell_df.loc[history_idx, '总卖出数量']):
            sold_already = 0
        else:
            sold_already = sell_df.loc[history_idx, '总卖出数量']
        qty_allocate_here = min((int(sell_df.loc[history_idx, '买入数量']) - sold_already), sold_qty)
        if totalSold_indicator == '' or sell_df.loc[history_idx, '总卖出数量'] == '' or np.isnan(sell_df.loc[history_idx, '总卖出数量']):  # 没卖出过
            sell_df.loc[history_idx, '卖出日期'] = str(todaySellDf.loc[idx, '发生日期'])
            sell_df.loc[history_idx, '卖出数量'] = qty_allocate_here
            sell_df.loc[history_idx, '卖出金额'] = qty_allocate_here * todaySellDf.loc[idx, '成交均价']
            sell_df.loc[history_idx, '卖出成交均价'] = str(todaySellDf.loc[idx, '成交均价'])
            sell_df.loc[history_idx, '总卖出数量'] = qty_allocate_here
        elif totalSold_indicator == 0:  # 之前未全部卖出
            sell_df.loc[history_idx, '卖出日期'] += ',' + str(todaySellDf.loc[idx, '发生日期'])
            sell_df.loc[history_idx, '卖出数量'] = str(sell_df.loc[history_idx, '卖出数量']) + ',' + str(qty_allocate_here)
            sell_df.loc[history_idx, '卖出成交均价'] = str(sell_df.loc[history_idx, '卖出成交均价']) + ',' + str(todaySellDf.loc[idx, '成交均价'])
            sell_df.loc[history_idx, '卖出金额'] = str(sell_df.loc[history_idx, '卖出金额']) + ',' + str(qty_allocate_here * todaySellDf.loc[idx, '成交均价'])
            sell_df.loc[history_idx, '总卖出数量'] = sell_df.loc[history_idx, '总卖出数量'] + qty_allocate_here
        if sell_df.loc[history_idx, '总卖出数量'] >= sell_df.loc[history_idx, '买入数量'] - 200:
            sell_df.loc[history_idx, '是否全部卖出'] = 1
            sell_df.loc[history_idx, '卖出比例'] = "100.00%"
        volume_left_to_be_sell = sold_qty - qty_allocate_here
        return volume_left_to_be_sell

    def find_min_date(sell_df):
        if len(sell_df[(sell_df['证券代码'] == stock_code) & (sell_df['是否全部卖出'] != 1)]['买入日期']) > 0:
            min_date = sell_df[(sell_df['证券代码'] == stock_code) & (sell_df['是否全部卖出'] != 1)]['买入日期'].min()
        else:
            min_date = '2099-12-31'
        return min_date

    def check_len(sell_df):
        if len(sell_df[(sell_df['证券代码'] == stock_code) & (sell_df['是否全部卖出'] != 1) & (sell_df['买入日期'] != date)]['买入日期']) > 0:
            return True
        else:
            return False

    def sell_by_sort(sell_df_list):
        check_list = [check_len(x) for x in sell_df_list]
        if sum(check_list) == 1:
            check_min_idx = check_list.index(True)
        else:
            check_min_idx = -1
        return check_min_idx, check_list

    volume_left_to_be_sell = sold_qty
    while volume_left_to_be_sell > 1e-5:
        jupiter_min_date = find_min_date(hist_sell_jupiter)
        europa_min_date = find_min_date(hist_sell_europa)
        metis_min_date = find_min_date(hist_sell_metis)
        leda_min_date = find_min_date(hist_sell_leda)
        saturn_min_date = find_min_date(hist_sell_saturn)
        ceres_min_date = find_min_date(hist_sell_ceres)
        p4_min_date = find_min_date(hist_sell_p4)
        mimas_min_date = find_min_date(hist_sell_mimas)

        sell_df_list = [hist_sell_jupiter, hist_sell_europa, hist_sell_metis, hist_sell_leda, hist_sell_saturn, hist_sell_ceres, hist_sell_p4, hist_sell_mimas]
        check_min_idx, check_list = sell_by_sort(sell_df_list)
        if check_min_idx >= 0:
            tmp_sell_df = sell_df_list[check_min_idx]
            volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, tmp_sell_df)
        else:
            print('！！！！！！！！！！ should not enter this place！！！！！！！！！！')
            # 该标的至少2个策略存在持仓, 先卖早买入的部分
            min_date = pd.Series([jupiter_min_date, europa_min_date, metis_min_date, leda_min_date, ceres_min_date, p4_min_date, mimas_min_date, saturn_min_date]).sort_values().iloc[0]
            max_date = pd.Series([jupiter_min_date, europa_min_date, metis_min_date, leda_min_date, ceres_min_date, p4_min_date, mimas_min_date, saturn_min_date]).sort_values(ascending=False).iloc[0]
            if min_date == max_date:
                print('日期全部一样，先卖谁？')
                dead_circle += 1
                if dead_circle > 5:  # 死循环5次即跳出这个循环
                    break
            elif jupiter_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_jupiter)
            elif europa_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_europa)
            elif metis_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_metis)
            elif leda_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_leda)
            elif saturn_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_saturn)
            elif ceres_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_ceres)
            elif p4_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_p4)
            elif mimas_min_date == min_date:
                volume_left_to_be_sell = sell_one_day_holding(volume_left_to_be_sell, hist_sell_mimas)
            else:
                print('error!')
                print(f'jupiter mindate:{jupiter_min_date}\n, ' + \
                      f'europa mindate:{europa_min_date}\n, ' + \
                      f'leda mindate:{leda_min_date}\n, ' + \
                      f'metis mindate:{metis_min_date}\n, ' + \
                      f'saturn mindate:{saturn_min_date}\n, ' + \
                      f'ceres mindate:{ceres_min_date}\n, ' + \
                      f'p4 mindate:{p4_min_date}\n, ' + \
                      f'mimas mindate:{mimas_min_date}\n, ')
                break

buy_columns = ['证券代码', '发生日期', '组合编号', '证券名称', '委托方向', '持仓', '成交数量', '成交金额', '成交均价', '涨跌幅(%)']

sell_columns = ['证券代码', '买入日期', '买入数量', '买入金额', '买入成交均价', '卖出数量', '卖出成交均价', '卖出金额', '是否全部卖出', '卖出比例',
                '卖出部分盈利金额', '卖出部分收益率(%)', '总卖出数量']


total_buy_df = {'Jupiter': buyDf_jupiter[buy_columns],
                'Europa': buyDf_europa[buy_columns],
                'Metis': buyDf_metis[buy_columns],
                'Leda': buyDf_leda[buy_columns],
                'Saturn': buyDf_saturn[buy_columns],
                'Ceres': buyDf_ceres[buy_columns],
                'Mimas': buyDf_mimas[buy_columns],
                'P4': buyDf_p4[buy_columns]}
total_sell_df = {'Jupiter': hist_sell_jupiter[sell_columns],
                'Europa': hist_sell_europa[sell_columns],
                'Metis': hist_sell_metis[sell_columns],
                'Leda': hist_sell_leda[sell_columns],
                'Saturn': hist_sell_saturn[sell_columns],
                'Ceres': hist_sell_ceres[sell_columns],
                'Mimas': hist_sell_mimas[sell_columns],
                'P4': hist_sell_p4[sell_columns]}

from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(total_buy_df, '/data/group/800463/日内强势股/实盘分析记录/策略买卖/', f'买入{date}.xlsx')
FileUtil.save_dict2xls(total_sell_df, '/data/group/800463/日内强势股/实盘分析记录/策略买卖/', f'卖出{date}.xlsx')