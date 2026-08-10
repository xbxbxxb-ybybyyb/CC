import sys
sys.path.insert(1,'/data/user/015626/data/share/Code/git_space/futures-factor-framework/factor_framework/')

from xquant.marketdata import MarketData as XMD
# from xquant.thirdpartydata.marketdata import MarketData as XMDTP

import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import multifactor.utility.dt as udt
import numpy as np
import os, glob
from multiprocessing import Pool
import time
from multifactor.data.utils import *
import bottleneck as bk

bs_map = {1:'buy',2:'sell'}
orderlevel_map = {1:'small',2:'mid',3:'big',4:'super'}
col_list = ['lo_counts','lo_quantity','lo_amount','lo_hold_time','lo_first_hold_time','lo_finish_time']
col_list_cancel = ['lo_counts','lo_quantity','lo_amount','lo_hold_time']

standard_columns = ['open', 'high', 'low', 'close', 'twap', 'Buy1NumOrdersMean', 'Sell1NumOrdersMean', 'BidAskSpreadMean', 'Bid1AmtMean',
                    'Ask1AmtMean', 'volume', 'amount', 'AbsPxPath', 'PxStd', 'VolStd', 'AskVolMean', 'BidVolMean', 'BuyNumOrdersSumMean', 
                    'SellNumOrdersSumMean', 'BuyOrderQtySumMean', 'SellOrderQtySumMean', 'WeightBuyOrderQtySumMean',
                    'WeightSellOrderQtySumMean', 'OBI', 'TotalValueTrade', 'TotalVolumeTrade', 'TotalAskVol', 'TotalBidVol', 'BidP0', 
                    'BidV0', 'AskP0', 'AskV0', 'BidP1', 'BidV1', 'AskP1', 'AskV1', 'BidP2', 'BidV2', 'AskP2', 'AskV2', 'BidP3', 'BidV3', 
                    'AskP3', 'AskV3', 'BidP4', 'BidV4', 'AskP4', 'AskV4', 'PxVolCorr', 'SellTradeMoney', 'SellTradeQuantity',
                    'SellTradeNum', 'SellUniqueOrderNum', 'BuyTradeMoney', 'BuyTradeQuantity', 'BuyTradeNum', 'BuyUniqueOrderNum',
                    'sell_smallorder_count', 'sell_smallorder_money', 'sell_smallorder_volume', 'sell_midorder_count', 
                    'sell_midorder_money', 'sell_midorder_volume', 'sell_bigorder_count', 'sell_bigorder_money', 'sell_bigorder_volume',
                    'sell_superorder_count', 'sell_superorder_money', 'sell_superorder_volume', 'sell_smallorder_count_v2', 
                    'sell_smallorder_money_v2', 'sell_smallorder_volume_v2', 'sell_midorder_count_v2', 'sell_midorder_money_v2', 
                    'sell_midorder_volume_v2', 'sell_bigorder_count_v2', 'sell_bigorder_money_v2', 'sell_bigorder_volume_v2', 
                    'sell_superorder_count_v2', 'sell_superorder_money_v2', 'sell_superorder_volume_v2', 'buy_smallorder_count',
                    'buy_smallorder_money', 'buy_smallorder_volume', 'buy_midorder_count', 'buy_midorder_money', 'buy_midorder_volume',
                    'buy_bigorder_count', 'buy_bigorder_money', 'buy_bigorder_volume', 'buy_superorder_count', 'buy_superorder_money',
                    'buy_superorder_volume', 'market_map_limit_num', 'sell_market_map_limit_num', 'buy_market_map_limit_num', 
                    'abs_px_path_tran', 'trademoney_ret_sign_sum', 'trademoney_ret_weighted', 'buy_maxvol_price', 'buy_maxvol_price_vol',
                    'sell_maxvol_price', 'sell_maxvol_price_vol', 'maxvol_price', 'maxvol_price_vol', 'lo_counts', 'lo_quantity', 
                    'lo_amount', 'buy_lo_counts', 'buy_lo_quantity', 'buy_lo_amount', 'sell_lo_counts', 'sell_lo_quantity',
                    'sell_lo_amount', 'buy_small_lo_counts', 'buy_small_lo_quantity', 'buy_small_lo_amount', 'buy_mid_lo_counts',
                    'buy_mid_lo_quantity', 'buy_mid_lo_amount', 'buy_big_lo_counts', 'buy_big_lo_quantity', 'buy_big_lo_amount',
                    'buy_super_lo_counts', 'buy_super_lo_quantity', 'buy_super_lo_amount', 'sell_small_lo_counts', 'sell_small_lo_quantity',
                    'sell_small_lo_amount', 'sell_mid_lo_counts', 'sell_mid_lo_quantity', 'sell_mid_lo_amount', 'sell_big_lo_counts',
                    'sell_big_lo_quantity', 'sell_big_lo_amount', 'sell_super_lo_counts', 'sell_super_lo_quantity', 'sell_super_lo_amount',
                    'cancel_lo_counts', 'cancel_lo_quantity', 'cancel_lo_amount', 'buy_cancel_lo_counts', 'buy_cancel_lo_quantity',
                    'buy_cancel_lo_amount', 'sell_cancel_lo_counts', 'sell_cancel_lo_quantity', 'sell_cancel_lo_amount', 
                    'buy_small_cancel_lo_counts', 'buy_small_cancel_lo_quantity', 'buy_small_cancel_lo_amount', 'buy_mid_cancel_lo_counts',
                    'buy_mid_cancel_lo_quantity', 'buy_mid_cancel_lo_amount', 'buy_big_cancel_lo_counts', 'buy_big_cancel_lo_quantity',
                    'buy_big_cancel_lo_amount', 'buy_super_cancel_lo_counts', 'buy_super_cancel_lo_quantity', 'buy_super_cancel_lo_amount',
                    'sell_small_cancel_lo_counts', 'sell_small_cancel_lo_quantity', 'sell_small_cancel_lo_amount', 
                    'sell_mid_cancel_lo_counts', 'sell_mid_cancel_lo_quantity', 'sell_mid_cancel_lo_amount', 'sell_big_cancel_lo_counts',
                    'sell_big_cancel_lo_quantity', 'sell_big_cancel_lo_amount', 'sell_super_cancel_lo_counts',
                    'sell_super_cancel_lo_quantity', 'sell_super_cancel_lo_amount', 'weight', 'TotalBidQty', 'TotalOfferQty',
                    'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'WeightBuyNumOrdersSumMean', 'WeightSellNumOrdersSumMean',
                    'WeightBuyMoneySumMean', 'WeightSellMoneySumMean', 'Buy1Price_mean', 'Buy1OrderQty_mean', 'Buy1NumOrders_mean',
                    'Sell1Price_mean', 'Sell1OrderQty_mean', 'Sell1NumOrders_mean', 'allsell_smallorder_count',
                    'allsell_smallorder_money', 'allsell_smallorder_volume', 'allsell_midorder_count', 'allsell_midorder_money', 
                    'allsell_midorder_volume', 'allsell_bigorder_count', 'allsell_bigorder_money', 'allsell_bigorder_volume',
                    'allsell_superorder_count', 'allsell_superorder_money', 'allsell_superorder_volume', 'allbuy_smallorder_count',
                    'allbuy_smallorder_money', 'allbuy_smallorder_volume', 'allbuy_midorder_count', 'allbuy_midorder_money', 
                    'allbuy_midorder_volume', 'allbuy_bigorder_count', 'allbuy_bigorder_money', 'allbuy_bigorder_volume', 
                    'allbuy_superorder_count', 'allbuy_superorder_money', 'allbuy_superorder_volume', 'buy_order_money_thismin', 
                    'buy_order_money_othermin', 'sell_order_money_thismin', 'sell_order_money_othermin', 'buy_smallorder_count_thismin',
                    'buy_smallorder_money_thismin', 'buy_smallorder_volume_thismin', 'buy_midorder_count_thismin',
                    'buy_midorder_money_thismin', 'buy_midorder_volume_thismin', 'buy_bigorder_count_thismin', 'buy_bigorder_money_thismin',
                    'buy_bigorder_volume_thismin', 'buy_superorder_count_thismin', 'buy_superorder_money_thismin',
                    'buy_superorder_volume_thismin', 'buy_smallorder_count_othermin', 'buy_smallorder_money_othermin',
                    'buy_smallorder_volume_othermin', 'buy_midorder_count_othermin', 'buy_midorder_money_othermin',
                    'buy_midorder_volume_othermin', 'buy_bigorder_count_othermin', 'buy_bigorder_money_othermin',
                    'buy_bigorder_volume_othermin', 'buy_superorder_count_othermin', 'buy_superorder_money_othermin',
                    'buy_superorder_volume_othermin', 'sell_smallorder_count_thismin', 'sell_smallorder_money_thismin',
                    'sell_smallorder_volume_thismin', 'sell_midorder_count_thismin', 'sell_midorder_money_thismin', 
                    'sell_midorder_volume_thismin', 'sell_bigorder_count_thismin', 'sell_bigorder_money_thismin', 
                    'sell_bigorder_volume_thismin', 'sell_superorder_count_thismin', 'sell_superorder_money_thismin',
                    'sell_superorder_volume_thismin', 'sell_smallorder_count_othermin', 'sell_smallorder_money_othermin',
                    'sell_smallorder_volume_othermin', 'sell_midorder_count_othermin', 'sell_midorder_money_othermin',
                    'sell_midorder_volume_othermin', 'sell_bigorder_count_othermin', 'sell_bigorder_money_othermin', 
                    'sell_bigorder_volume_othermin', 'sell_superorder_count_othermin', 'sell_superorder_money_othermin',
                    'sell_superorder_volume_othermin', 'tran_count', 'tran_buy_unique_order_count', 'tran_sell_unique_order_count',
                    'adjfactor', 'stk_volatility', 'turnover_rate', 'float_shares', 'stk_index_corr_sh50', 'stk_index_corr_hs300', 
                    'stk_index_corr_zz500', 'stk_index_corr_zz1000']
standard_columns_oldframe = ['open', 'high', 'low', 'close', 'twap', 'Buy1NumOrdersMean', 'Sell1NumOrdersMean', 'BidAskSpreadMean', 'Bid1AmtMean',
                    'Ask1AmtMean', 'volume', 'amount', 'AbsPxPath', 'PxStd', 'VolStd', 'AskVolMean', 'BidVolMean', 'BuyNumOrdersSumMean', 
                    'SellNumOrdersSumMean', 'BuyOrderQtySumMean', 'SellOrderQtySumMean', 'WeightBuyOrderQtySumMean',
                    'WeightSellOrderQtySumMean', 'OBI', 'TotalValueTrade', 'TotalVolumeTrade', 'TotalAskVol', 'TotalBidVol', 'BidP0', 
                    'BidV0', 'AskP0', 'AskV0', 'BidP1', 'BidV1', 'AskP1', 'AskV1', 'BidP2', 'BidV2', 'AskP2', 'AskV2', 'BidP3', 'BidV3', 
                    'AskP3', 'AskV3', 'BidP4', 'BidV4', 'AskP4', 'AskV4', 'PxVolCorr', 'SellTradeMoney', 'SellTradeQuantity',
                    'SellTradeNum', 'SellUniqueOrderNum', 'BuyTradeMoney', 'BuyTradeQuantity', 'BuyTradeNum', 'BuyUniqueOrderNum',
                    'sell_smallorder_count', 'sell_smallorder_money', 'sell_smallorder_volume', 'sell_midorder_count', 
                    'sell_midorder_money', 'sell_midorder_volume', 'sell_bigorder_count', 'sell_bigorder_money', 'sell_bigorder_volume',
                    'sell_superorder_count', 'sell_superorder_money', 'sell_superorder_volume', 'sell_smallorder_count_v2', 
                    'sell_smallorder_money_v2', 'sell_smallorder_volume_v2', 'sell_midorder_count_v2', 'sell_midorder_money_v2', 
                    'sell_midorder_volume_v2', 'sell_bigorder_count_v2', 'sell_bigorder_money_v2', 'sell_bigorder_volume_v2', 
                    'sell_superorder_count_v2', 'sell_superorder_money_v2', 'sell_superorder_volume_v2', 'buy_smallorder_count',
                    'buy_smallorder_money', 'buy_smallorder_volume', 'buy_midorder_count', 'buy_midorder_money', 'buy_midorder_volume',
                    'buy_bigorder_count', 'buy_bigorder_money', 'buy_bigorder_volume', 'buy_superorder_count', 'buy_superorder_money',
                    'buy_superorder_volume', 'market_map_limit_num', 'sell_market_map_limit_num', 'buy_market_map_limit_num', 
                    'abs_px_path_tran', 'trademoney_ret_sign_sum', 'trademoney_ret_weighted', 'buy_maxvol_price', 'buy_maxvol_price_vol',
                    'sell_maxvol_price', 'sell_maxvol_price_vol', 'maxvol_price', 'maxvol_price_vol', 'lo_counts', 'lo_quantity', 
                    'lo_amount', 'buy_lo_counts', 'buy_lo_quantity', 'buy_lo_amount', 'sell_lo_counts', 'sell_lo_quantity',
                    'sell_lo_amount', 'buy_small_lo_counts', 'buy_small_lo_quantity', 'buy_small_lo_amount', 'buy_mid_lo_counts',
                    'buy_mid_lo_quantity', 'buy_mid_lo_amount', 'buy_big_lo_counts', 'buy_big_lo_quantity', 'buy_big_lo_amount',
                    'buy_super_lo_counts', 'buy_super_lo_quantity', 'buy_super_lo_amount', 'sell_small_lo_counts', 'sell_small_lo_quantity',
                    'sell_small_lo_amount', 'sell_mid_lo_counts', 'sell_mid_lo_quantity', 'sell_mid_lo_amount', 'sell_big_lo_counts',
                    'sell_big_lo_quantity', 'sell_big_lo_amount', 'sell_super_lo_counts', 'sell_super_lo_quantity', 'sell_super_lo_amount',
                    'cancel_lo_counts', 'cancel_lo_quantity', 'cancel_lo_amount', 'buy_cancel_lo_counts', 'buy_cancel_lo_quantity',
                    'buy_cancel_lo_amount', 'sell_cancel_lo_counts', 'sell_cancel_lo_quantity', 'sell_cancel_lo_amount', 
                    'buy_small_cancel_lo_counts', 'buy_small_cancel_lo_quantity', 'buy_small_cancel_lo_amount', 'buy_mid_cancel_lo_counts',
                    'buy_mid_cancel_lo_quantity', 'buy_mid_cancel_lo_amount', 'buy_big_cancel_lo_counts', 'buy_big_cancel_lo_quantity',
                    'buy_big_cancel_lo_amount', 'buy_super_cancel_lo_counts', 'buy_super_cancel_lo_quantity', 'buy_super_cancel_lo_amount',
                    'sell_small_cancel_lo_counts', 'sell_small_cancel_lo_quantity', 'sell_small_cancel_lo_amount', 
                    'sell_mid_cancel_lo_counts', 'sell_mid_cancel_lo_quantity', 'sell_mid_cancel_lo_amount', 'sell_big_cancel_lo_counts',
                    'sell_big_cancel_lo_quantity', 'sell_big_cancel_lo_amount', 'sell_super_cancel_lo_counts',
                    'sell_super_cancel_lo_quantity', 'sell_super_cancel_lo_amount', 'weight', 'TotalBidQty', 'TotalOfferQty',
                    'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'WeightBuyNumOrdersSumMean', 'WeightSellNumOrdersSumMean',
                    'WeightBuyMoneySumMean', 'WeightSellMoneySumMean', 'Buy1Price_mean', 'Buy1OrderQty_mean', 'Buy1NumOrders_mean',
                    'Sell1Price_mean', 'Sell1OrderQty_mean', 'Sell1NumOrders_mean', 'allsell_smallorder_count',
                    'allsell_smallorder_money', 'allsell_smallorder_volume', 'allsell_midorder_count', 'allsell_midorder_money', 
                    'allsell_midorder_volume', 'allsell_bigorder_count', 'allsell_bigorder_money', 'allsell_bigorder_volume',
                    'allsell_superorder_count', 'allsell_superorder_money', 'allsell_superorder_volume', 'allbuy_smallorder_count',
                    'allbuy_smallorder_money', 'allbuy_smallorder_volume', 'allbuy_midorder_count', 'allbuy_midorder_money', 
                    'allbuy_midorder_volume', 'allbuy_bigorder_count', 'allbuy_bigorder_money', 'allbuy_bigorder_volume', 
                    'allbuy_superorder_count', 'allbuy_superorder_money', 'allbuy_superorder_volume', 'buy_order_money_thismin', 
                    'buy_order_money_othermin', 'sell_order_money_thismin', 'sell_order_money_othermin', 'buy_smallorder_count_thismin',
                    'buy_smallorder_money_thismin', 'buy_smallorder_volume_thismin', 'buy_midorder_count_thismin',
                    'buy_midorder_money_thismin', 'buy_midorder_volume_thismin', 'buy_bigorder_count_thismin', 'buy_bigorder_money_thismin',
                    'buy_bigorder_volume_thismin', 'buy_superorder_count_thismin', 'buy_superorder_money_thismin',
                    'buy_superorder_volume_thismin', 'buy_smallorder_count_othermin', 'buy_smallorder_money_othermin',
                    'buy_smallorder_volume_othermin', 'buy_midorder_count_othermin', 'buy_midorder_money_othermin',
                    'buy_midorder_volume_othermin', 'buy_bigorder_count_othermin', 'buy_bigorder_money_othermin',
                    'buy_bigorder_volume_othermin', 'buy_superorder_count_othermin', 'buy_superorder_money_othermin',
                    'buy_superorder_volume_othermin', 'sell_smallorder_count_thismin', 'sell_smallorder_money_thismin',
                    'sell_smallorder_volume_thismin', 'sell_midorder_count_thismin', 'sell_midorder_money_thismin', 
                    'sell_midorder_volume_thismin', 'sell_bigorder_count_thismin', 'sell_bigorder_money_thismin', 
                    'sell_bigorder_volume_thismin', 'sell_superorder_count_thismin', 'sell_superorder_money_thismin',
                    'sell_superorder_volume_thismin', 'sell_smallorder_count_othermin', 'sell_smallorder_money_othermin',
                    'sell_smallorder_volume_othermin', 'sell_midorder_count_othermin', 'sell_midorder_money_othermin',
                    'sell_midorder_volume_othermin', 'sell_bigorder_count_othermin', 'sell_bigorder_money_othermin', 
                    'sell_bigorder_volume_othermin', 'sell_superorder_count_othermin', 'sell_superorder_money_othermin',
                    'sell_superorder_volume_othermin', 'tran_count', 'tran_buy_unique_order_count', 'tran_sell_unique_order_count']
time_list = ['sell_small_lo_hold_time', 'buy_super_lo_first_hold_time', 'sell_mid_cancel_lo_hold_time', 'sell_mid_lo_hold_time', 
             'sell_small_lo_first_hold_time', 'buy_lo_finish_time', 'sell_lo_finish_time', 'buy_small_lo_finish_time', 
             'buy_lo_hold_time', 'sell_super_lo_finish_time', 'buy_big_cancel_lo_hold_time', 'lo_hold_time', 'sell_big_lo_finish_time',
             'sell_mid_lo_finish_time', 'buy_cancel_lo_hold_time', 'buy_small_lo_hold_time', 'sell_big_cancel_lo_hold_time', 
             'buy_lo_first_hold_time', 'sell_super_cancel_lo_hold_time', 'buy_big_lo_hold_time', 'cancel_lo_hold_time', 
             'sell_small_lo_finish_time', 'sell_lo_first_hold_time', 'buy_small_lo_first_hold_time', 'sell_cancel_lo_hold_time',
             'lo_finish_time', 'buy_super_cancel_lo_hold_time', 'sell_super_lo_hold_time', 'buy_big_lo_first_hold_time', 
             'buy_mid_lo_finish_time', 'sell_mid_lo_first_hold_time', 'buy_super_lo_hold_time', 'buy_mid_lo_first_hold_time',
             'sell_super_lo_first_hold_time', 'buy_big_lo_finish_time', 'sell_small_cancel_lo_hold_time', 'sell_big_lo_hold_time',
             'buy_mid_lo_hold_time', 'lo_first_hold_time', 'buy_small_cancel_lo_hold_time', 'buy_mid_cancel_lo_hold_time',
             'buy_super_lo_finish_time', 'sell_big_lo_first_hold_time', 'sell_lo_hold_time']
ffill_list = ['open','high','low','close','twap','weight','WeightedAvgBidPx','WeightedAvgOfferPx','Buy1Price_mean','Sell1Price_mean','float_shares']
ffill_list_oldframe = ['open','high','low','close','twap','weight','WeightedAvgBidPx','WeightedAvgOfferPx','Buy1Price_mean','Sell1Price_mean']
nofill_list = ['AskP%d' % x for x in range(5)] + ['BidP%d' % x for x in range(5)] \
                + ['buy_big_cancel_lo_hold_time', 'buy_big_lo_finish_time', 'buy_big_lo_first_hold_time', 'buy_big_lo_hold_time', 
                   'buy_cancel_lo_hold_time', 'buy_lo_finish_time', 'buy_lo_first_hold_time', 'buy_lo_hold_time', 'buy_maxvol_price', 
                   'buy_mid_cancel_lo_hold_time', 'buy_mid_lo_finish_time', 'buy_mid_lo_first_hold_time', 'buy_mid_lo_hold_time',
                   'buy_small_cancel_lo_hold_time', 'buy_small_lo_finish_time', 'buy_small_lo_first_hold_time', 'buy_small_lo_hold_time',
                   'buy_super_cancel_lo_hold_time', 'buy_super_lo_finish_time', 'buy_super_lo_first_hold_time', 'buy_super_lo_hold_time',
                   'cancel_lo_hold_time', 'lo_finish_time', 'lo_first_hold_time', 'lo_hold_time', 'maxvol_price', 
                   'sell_big_cancel_lo_hold_time', 'sell_big_lo_finish_time', 'sell_big_lo_first_hold_time', 'sell_big_lo_hold_time',
                   'sell_cancel_lo_hold_time', 'sell_lo_finish_time', 'sell_lo_first_hold_time', 'sell_lo_hold_time', 
                   'sell_maxvol_price', 'sell_mid_cancel_lo_hold_time', 'sell_mid_lo_finish_time', 'sell_mid_lo_first_hold_time',
                   'sell_mid_lo_hold_time', 'sell_small_cancel_lo_hold_time', 'sell_small_lo_finish_time',
                   'sell_small_lo_first_hold_time', 'sell_small_lo_hold_time', 'sell_super_cancel_lo_hold_time', 
                   'sell_super_lo_finish_time', 'sell_super_lo_first_hold_time', 'sell_super_lo_hold_time']
fill0_list = list(set(standard_columns) - set(ffill_list) - set(nofill_list) - set(['adjfactor','stk_index_corr_sh50', 'stk_index_corr_hs300', 
                    'stk_index_corr_zz500', 'stk_index_corr_zz1000']))
fill0_list_oldframe = list(set(standard_columns_oldframe) - set(ffill_list) - set(nofill_list) - set(['adjfactor','stk_index_corr_sh50', 'stk_index_corr_hs300', 
                    'stk_index_corr_zz500', 'stk_index_corr_zz1000']))

def sh_order_checker(df_result, df_transaction, df_tick):
    """
    检查还原结果是否正确
    :param df_result: pd.DataFrame
        还原后的order数据
    :param df_transaction: pd.DataFrame
        上交所transaction数据
    :param df_tick: pd.DataFrame
        上交所tick数据
    :return: None
    """
    num = df_tick['TotalBidQty'].iloc[-1] + \
          df_tick['TotalOfferQty'].iloc[-1] + \
          df_result[df_result['OrderType'] == 10]['OrderQty'].sum() + \
          df_transaction['TradeQty'].sum() * 2 - \
          df_result[df_result['OrderType'] == 2]['OrderQty'].sum()
    assert np.isclose(num, 0)

def reform_sh_order(df_order, df_transaction, append_cancel_orders):
    if len(df_order) == 0 or len(df_transaction) == 0:
        return pd.DataFrame()
    # caution original index is ignored
    df_order_2 = df_order[df_order['OrderType'] == 2].copy()  # limit price order
    df_order_10 = df_order[df_order['OrderType'] == 10].copy()  # cancel order
    # transform pandas to dict to speed up record loc and modification
    df_order_2 = df_order_2.set_index(['OrderNO'])
    df_order_2 = df_order_2.T.to_dict(orient='series')
    for trans_rec in df_transaction.itertuples():
        if trans_rec.TradeBuyNo > trans_rec.TradeSellNo:
            order_no = trans_rec.TradeBuyNo
            order_bsflag = 1
        else:
            order_no = trans_rec.TradeSellNo
            order_bsflag = 2
        try:
            # if order exists in order dict, just modify price and quantity
            order_rec = df_order_2[order_no]
            if order_rec['OrderIndex'] == -1 or trans_rec.ApplSeqNum < order_rec['ApplSeqNum']:  # auction proof
                order_rec['OrderQty'] += trans_rec.TradeQty
                order_rec['OrderPrice'] = (max if order_bsflag == 1 else min)(order_rec['OrderPrice'],
                                                                              trans_rec.TradePrice)
        except KeyError:
            df_order_2[order_no] = pd.Series({'MDDate': trans_rec.MDDate,
                                              'MDTime': trans_rec.MDTime,
                                              'HTSCSecurityID': trans_rec.HTSCSecurityID,
                                              'OrderIndex': -1,  # not used in practice for SH
                                              'OrderType': 2,
                                              'OrderPrice': trans_rec.TradePrice,
                                              'OrderQty': trans_rec.TradeQty,
                                              'OrderBSFlag': order_bsflag,
                                              'ReceiveDateTime': trans_rec.ReceiveDateTime,
                                              'ApplSeqNum': trans_rec.ApplSeqNum})
    df_order_reformed = pd.DataFrame.from_dict(df_order_2, orient='index')
    df_order_reformed.index.name = 'OrderNO'
    df_order_reformed = df_order_reformed.reset_index()
    if append_cancel_orders:
        df_order_reformed = df_order_reformed.append(df_order_10, ignore_index=True, sort=False).sort_values(by='ApplSeqNum').reset_index(drop=True)
    else:
        df_order_reformed = df_order_reformed.sort_values(by='ApplSeqNum').reset_index(drop=True)
    return df_order_reformed

def get_order_holdtime(start_time,end_time):
    if start_time != start_time or end_time != end_time:
        return np.nan
    time_diff = (end_time - start_time).microseconds/1e6 + (end_time - start_time).seconds
    if (end_time.time() >= datetime.time(13,0)) and (start_time.time() <= datetime.time(11,30)):
        time_diff = time_diff - 90 * 60
    return time_diff

def get_OrderLevel(amt):
    if amt <= 40000:
        return 1
    elif (amt > 40000) and (amt <= 200000):
        return 2
    elif (amt > 200000) and (amt <= 1000000):
        return 3
    else:
        return 4    
    
def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
    
def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),0)

def aggregate_transaction(transaction):
    transactiondf = pd.DataFrame()
    if len(transaction) > 100:
        transaction.loc[transaction.TradeBSFlag == 1, 'ot_market_index'] = transaction['TradeBuyNo']
        transaction.loc[transaction.TradeBSFlag == 2, 'ot_market_index'] = transaction['TradeSellNo']

        transaction['dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        transaction['minute'] = transaction.dt.map(lambda x: x.replace(second=0,microsecond=0))
        transaction = transaction[transaction.TradePrice != 0]
        transaction = transaction[transaction.TradeType != 1] # 去除撤单，深交所用
        
        tran_count_info = transaction.groupby('minute').agg({'TradePrice':'count','TradeBuyNo':lambda x:len(x.unique()),'TradeSellNo':lambda x:len(x.unique())})
        tran_count_info.columns = ['tran_count','tran_buy_unique_order_count','tran_sell_unique_order_count']
        
        allsell_order_money = transaction.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
        allsell_small_order = allsell_order_money[allsell_order_money.TradeMoney <= 40000]
        allsell_mid_order = allsell_order_money[(allsell_order_money.TradeMoney > 40000) & (allsell_order_money.TradeMoney <= 200000)]
        allsell_big_order = allsell_order_money[(allsell_order_money.TradeMoney > 200000) & (allsell_order_money.TradeMoney <= 1000000)]
        allsell_super_order = allsell_order_money[(allsell_order_money.TradeMoney > 1000000)]
        allsell_small_order = allsell_small_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_smallorder_count','TradeMoney':'allsell_smallorder_money','TradeQty':'allsell_smallorder_volume'})
        allsell_mid_order = allsell_mid_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_midorder_count','TradeMoney':'allsell_midorder_money','TradeQty':'allsell_midorder_volume'})
        allsell_big_order = allsell_big_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_bigorder_count','TradeMoney':'allsell_bigorder_money','TradeQty':'allsell_bigorder_volume'})
        allsell_super_order = allsell_super_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_superorder_count','TradeMoney':'allsell_superorder_money','TradeQty':'allsell_superorder_volume'})

        allbuy_order_money = transaction.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        allbuy_small_order = allbuy_order_money[allbuy_order_money.TradeMoney <= 40000]
        allbuy_mid_order = allbuy_order_money[(allbuy_order_money.TradeMoney > 40000) & (allbuy_order_money.TradeMoney <= 200000)]
        allbuy_big_order = allbuy_order_money[(allbuy_order_money.TradeMoney > 200000) & (allbuy_order_money.TradeMoney <= 1000000)]
        allbuy_super_order = allbuy_order_money[(allbuy_order_money.TradeMoney > 1000000)]
        allbuy_small_order = allbuy_small_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_smallorder_count','TradeMoney':'allbuy_smallorder_money','TradeQty':'allbuy_smallorder_volume'})
        allbuy_mid_order = allbuy_mid_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_midorder_count','TradeMoney':'allbuy_midorder_money','TradeQty':'allbuy_midorder_volume'})
        allbuy_big_order = allbuy_big_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_bigorder_count','TradeMoney':'allbuy_bigorder_money','TradeQty':'allbuy_bigorder_volume'})
        allbuy_super_order = allbuy_super_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_superorder_count','TradeMoney':'allbuy_superorder_money','TradeQty':'allbuy_superorder_volume'})

        selldf = transaction[transaction.TradeBSFlag == 2]
        sellorder_money_v2 = selldf.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
        sell_small_order_v2 = sellorder_money_v2[sellorder_money_v2.TradeMoney <= 40000]
        sell_mid_order_v2 = sellorder_money_v2[(sellorder_money_v2.TradeMoney > 40000) & (sellorder_money_v2.TradeMoney <= 200000)]
        sell_big_order_v2 = sellorder_money_v2[(sellorder_money_v2.TradeMoney > 200000) & (sellorder_money_v2.TradeMoney <= 1000000)]
        sell_super_order_v2 = sellorder_money_v2[(sellorder_money_v2.TradeMoney > 1000000)]
        sell_small_order_v2 = sell_small_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_smallorder_count_v2','TradeMoney':'sell_smallorder_money_v2','TradeQty':'sell_smallorder_volume_v2'})
        sell_mid_order_v2 = sell_mid_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_midorder_count_v2','TradeMoney':'sell_midorder_money_v2','TradeQty':'sell_midorder_volume_v2'})
        sell_big_order_v2 = sell_big_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_bigorder_count_v2','TradeMoney':'sell_bigorder_money_v2','TradeQty':'sell_bigorder_volume_v2'})
        sell_super_order_v2 = sell_super_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_superorder_count_v2','TradeMoney':'sell_superorder_money_v2','TradeQty':'sell_superorder_volume_v2'})

        sellorder_money = selldf.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        sell_small_order = sellorder_money[sellorder_money.TradeMoney <= 40000]
        sell_mid_order = sellorder_money[(sellorder_money.TradeMoney > 40000) & (sellorder_money.TradeMoney <= 200000)]
        sell_big_order = sellorder_money[(sellorder_money.TradeMoney > 200000) & (sellorder_money.TradeMoney <= 1000000)]
        sell_super_order = sellorder_money[(sellorder_money.TradeMoney > 1000000)]
        sell_small_order = sell_small_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_smallorder_count','TradeMoney':'sell_smallorder_money','TradeQty':'sell_smallorder_volume'})
        sell_mid_order = sell_mid_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_midorder_count','TradeMoney':'sell_midorder_money','TradeQty':'sell_midorder_volume'})
        sell_big_order = sell_big_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_bigorder_count','TradeMoney':'sell_bigorder_money','TradeQty':'sell_bigorder_volume'})
        sell_super_order = sell_super_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_superorder_count','TradeMoney':'sell_superorder_money','TradeQty':'sell_superorder_volume'})

        selldfgroup = selldf.groupby('minute').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeSellNo':lambda x:len(x.unique())})
        selldfgroup = selldfgroup.rename(columns = {'TradeMoney':'SellTradeMoney','TradeQty':'SellTradeQuantity','TradePrice':'SellTradeNum','TradeSellNo':'SellUniqueOrderNum'})

        buydf = transaction[transaction.TradeBSFlag == 1]
        buyorder_money = buydf.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        buy_small_order = buyorder_money[buyorder_money.TradeMoney <= 40000]
        buy_mid_order = buyorder_money[(buyorder_money.TradeMoney > 40000) & (buyorder_money.TradeMoney <= 200000)]
        buy_big_order = buyorder_money[(buyorder_money.TradeMoney > 200000) & (buyorder_money.TradeMoney <= 1000000)]
        buy_super_order = buyorder_money[(buyorder_money.TradeMoney > 1000000)]
        buy_small_order = buy_small_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_smallorder_count','TradeMoney':'buy_smallorder_money','TradeQty':'buy_smallorder_volume'})
        buy_mid_order = buy_mid_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_midorder_count','TradeMoney':'buy_midorder_money','TradeQty':'buy_midorder_volume'})
        buy_big_order = buy_big_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_bigorder_count','TradeMoney':'buy_bigorder_money','TradeQty':'buy_bigorder_volume'})
        buy_super_order = buy_super_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_superorder_count','TradeMoney':'buy_superorder_money','TradeQty':'buy_superorder_volume'})


        buydfgroup = buydf.groupby('minute').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeBuyNo':lambda x:len(x.unique())})
        buydfgroup = buydfgroup.rename(columns = {'TradeMoney':'BuyTradeMoney','TradeQty':'BuyTradeQuantity','TradePrice':'BuyTradeNum','TradeBuyNo':'BuyUniqueOrderNum'})

        rlist = []
        for x in [transaction, selldf, buydf]:
            temp = x.groupby(['minute','ot_market_index'])['TradePrice'].count() # 主动成交单吃掉了多少单挂单
            temp = temp.groupby('minute').mean()
            rlist.append(temp)
        market_map_limit_num = pd.concat(rlist, axis = 1)
        market_map_limit_num.columns = ['market_map_limit_num','sell_market_map_limit_num','buy_market_map_limit_num']

        transaction['price_diff'] = transaction.TradePrice.diff()
        transaction['price_ret'] = transaction.TradePrice.pct_change()
        transaction['abs_price_diff'] = abs(transaction['price_diff'])
        transaction['TradeMoney_direction'] = np.sign(transaction['price_diff']) * transaction['TradeMoney']
        transaction['TradeMoney_ret_weighted'] = transaction['price_ret'] * transaction['TradeMoney']
        tran1 = transaction.groupby('minute')['abs_price_diff','TradeMoney_direction','TradeMoney_ret_weighted'].sum()
        tran1.columns = ['abs_px_path_tran','trademoney_ret_sign_sum','trademoney_ret_weighted']

        max_volume_price = transaction.groupby(['minute','TradePrice','TradeBSFlag'])['TradeQty'].sum()
        rlist = []
        level2_index_list = max_volume_price.index.get_level_values(2).unique().tolist()
        for i in [1,2]:
            if i in level2_index_list:
                select_level = max_volume_price.xs(i, level = 2)
                select_max_volume_price = select_level.loc[select_level.groupby('minute').idxmax()].reset_index(level = 1)#[['TradePrice']]
            else:
                select_max_volume_price = pd.DataFrame(columns = ['TradePrice', 'TradeQty'])
            rlist.append(select_max_volume_price)
        select_alllevel = max_volume_price.groupby(['minute','TradePrice']).sum()
        select_alllevel_max_volume_price = select_alllevel.loc[select_alllevel.groupby('minute').idxmax()].reset_index(level = 1)#[['TradePrice']]
        rlist.append(select_alllevel_max_volume_price)
        tran2 = pd.concat(rlist, axis = 1)
        tran2.columns = ['buy_maxvol_price','buy_maxvol_price_vol','sell_maxvol_price','sell_maxvol_price_vol','maxvol_price','maxvol_price_vol']

        transactiondf = pd.concat([selldfgroup, buydfgroup, sell_small_order, sell_mid_order, sell_big_order, 
                        sell_super_order,sell_small_order_v2, sell_mid_order_v2, sell_big_order_v2, sell_super_order_v2, 
                        buy_small_order, buy_mid_order, buy_big_order, buy_super_order, market_map_limit_num, tran1, tran2,
                        allsell_small_order,allsell_mid_order,allsell_big_order,allsell_super_order,allbuy_small_order,
                        allbuy_mid_order,allbuy_big_order,allbuy_super_order,tran_count_info], axis = 1)
    return transactiondf

def aggregate_tick(tick):
    fill_na_columns = ['Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price', 'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price', 'Sell5Price']
    tickdf = pd.DataFrame()
    if len(tick) > 100:
        tick[fill_na_columns] =  tick[fill_na_columns].replace(0,np.nan)
    
        tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        tick['minute'] = tick.dt.map(lambda x: x.replace(second=0))
        tick = tick.set_index('dt')
        tick['LastPx'] = tick['LastPx'].replace(0, np.nan)
        tick['OBI'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty'])
        tick['pricediff'] = abs(tick.LastPx.diff())
        tick['Bid1Amt'] = tick.Buy1Price * tick.Buy1OrderQty
        tick['Ask1Amt'] = tick.Sell1Price * tick.Sell1OrderQty
        tick['volume'] = tick.TotalVolumeTrade.diff()
        tick['VolStd'] = tick['volume']
        tick['amount'] = tick.TotalValueTrade.diff()
        tick['BidAskSpreadMean'] = tick['Sell1Price'] - tick['Buy1Price']

        tick['BuyNumOrdersSumMean'] = tick[['Buy'+str(i)+'NumOrders' for i in range(1,11)]].sum(axis = 1)
        tick['SellNumOrdersSumMean'] = tick[['Sell'+str(i)+'NumOrders' for i in range(1,11)]].sum(axis = 1)
        tick['BuyOrderQtySumMean'] = tick[['Buy'+str(i)+'OrderQty' for i in range(1,11)]].sum(axis = 1)
        tick['SellOrderQtySumMean'] = tick[['Sell'+str(i)+'OrderQty' for i in range(1,11)]].sum(axis = 1)
        tick['WeightBuyOrderQtySumMean'] = 0
        tick['WeightSellOrderQtySumMean'] = 0
        for i in range(1,11):
            tick['WeightBuyOrderQtySumMean'] += tick['Buy'+str(i)+'OrderQty'] * 0.8 ** (i-1)
            tick['WeightSellOrderQtySumMean'] += tick['Sell'+str(i)+'OrderQty'] * 0.8 ** (i-1)
            
        tick['BidVolMean'] = (tick[['Buy{}OrderQty'.format(i) for i in range(1, 11)]] * np.array(
            [0.8 ** i for i in range(10)])).sum(axis=1)
        tick['AskVolMean'] = (tick[['Sell{}OrderQty'.format(i) for i in range(1, 11)]] * np.array(
            [0.8 ** i for i in range(10)])).sum(axis=1)
        
        aggdict1 = {'AskVolMean':'mean','BidVolMean':'mean','BuyNumOrdersSumMean':'mean','SellNumOrdersSumMean':'mean','BuyOrderQtySumMean':'mean','SellOrderQtySumMean':'mean','WeightBuyOrderQtySumMean':'mean','WeightSellOrderQtySumMean':'mean','OBI':'mean'}

        tick['open'] = tick['LastPx']
        tick['high'] = tick['LastPx']
        tick['low'] = tick['LastPx']
        tick['close'] = tick['LastPx']
        tick['twap'] = tick['LastPx']
        aggdict_ohlc = {'open':'first','high':'max','low':'min','close':'last','twap':'mean'}

        pvcorrdf = tick[['minute','LastPx','volume']].groupby('minute').corr().xs('LastPx', level = 1)[['volume']]
        pvcorrdf.columns = ['PxVolCorr']
        aggdict = {'Buy1NumOrders':'mean','Sell1NumOrders':'mean','BidAskSpreadMean':'mean','Bid1Amt':'mean','Ask1Amt':'mean','volume':'sum','amount':'sum','pricediff':'sum','LastPx':'std','VolStd':'std'}
        
        aggdict2 = {'TotalValueTrade':'last','TotalVolumeTrade':'last','TotalOfferQty':'last','TotalBidQty':'last','Buy1Price':'last','Buy1OrderQty':'last', 'Sell1Price':'last','Sell1OrderQty':'last','Buy2Price':'last','Buy2OrderQty':'last', 'Sell2Price':'last','Sell2OrderQty':'last',
                   'Buy3Price':'last','Buy3OrderQty':'last', 'Sell3Price':'last','Sell3OrderQty':'last','Buy4Price':'last','Buy4OrderQty':'last', 'Sell4Price':'last','Sell4OrderQty':'last',
                   'Buy5Price':'last','Buy5OrderQty':'last', 'Sell5Price':'last','Sell5OrderQty':'last'}
        
        df1amt = tick.resample('1min').agg({**aggdict_ohlc, **aggdict, **aggdict1, **aggdict2})
        
        renamedict1 = {'Buy1NumOrders':'Buy1NumOrdersMean','Sell1NumOrders':'Sell1NumOrdersMean','Bid1Amt':'Bid1AmtMean','Ask1Amt':'Ask1AmtMean','pricediff':'AbsPxPath','LastPx':'PxStd'}
        
        renamedict2 = {'TotalOfferQty':'TotalAskVol','TotalBidQty':'TotalBidVol','Buy1Price':'BidP0','Buy1OrderQty':'BidV0', 'Sell1Price':'AskP0','Sell1OrderQty':'AskV0','Buy2Price':'BidP1','Buy2OrderQty':'BidV1', 'Sell2Price':'AskP1','Sell2OrderQty':'AskV1',
                   'Buy3Price':'BidP2','Buy3OrderQty':'BidV2', 'Sell3Price':'AskP2','Sell3OrderQty':'AskV2','Buy4Price':'BidP3','Buy4OrderQty':'BidV3', 'Sell4Price':'AskP3','Sell4OrderQty':'AskV3',
                   'Buy5Price':'BidP4','Buy5OrderQty':'BidV4', 'Sell5Price':'AskP4','Sell5OrderQty':'AskV4'}
        df1amt = df1amt.rename(columns = {**renamedict1, **renamedict2})
        
        tick['WeightBuyNumOrdersSumMean'] = 0
        tick['WeightSellNumOrdersSumMean'] = 0
        tick['WeightBuyMoneySumMean'] = 0
        tick['WeightSellMoneySumMean'] = 0
        for i in range(1,11):
            tick['WeightBuyNumOrdersSumMean'] += tick['Buy'+str(i)+'NumOrders'] * 0.8 ** (i-1)
            tick['WeightSellNumOrdersSumMean'] += tick['Sell'+str(i)+'NumOrders'] * 0.8 ** (i-1)
            tick['WeightBuyMoneySumMean'] += tick['Buy'+str(i)+'Price'] * tick['Buy'+str(i)+'OrderQty'] * 0.8 ** (i-1)
            tick['WeightSellMoneySumMean'] += tick['Sell'+str(i)+'Price'] * tick['Sell'+str(i)+'OrderQty'] * 0.8 ** (i-1)

        agg_dict_v3 = {'TotalBidQty':'last', 'TotalOfferQty':'last', 'WeightedAvgBidPx':'last', 'WeightedAvgOfferPx':'last',
                    'WeightBuyNumOrdersSumMean':'mean', 'WeightSellNumOrdersSumMean':'mean','WeightBuyMoneySumMean':'mean','WeightSellMoneySumMean':'mean',
                   'Buy1Price':'mean','Buy1OrderQty':'mean','Buy1NumOrders':'mean','Sell1Price':'mean','Sell1OrderQty':'mean','Sell1NumOrders':'mean'}

        tickv3 = tick.resample('1min').agg(agg_dict_v3).rename(columns = {x:f'{x}_mean' for x in ['Buy1Price','Buy1OrderQty','Buy1NumOrders','Sell1Price','Sell1OrderQty','Sell1NumOrders']})
        
        # check price
        if df1amt.close.sum() > 0:    
            tickdf = df1amt.join(pvcorrdf).join(tickv3)
    return tickdf

def aggregate_order_SZ(order, transaction):
    orderdf = pd.DataFrame()
    if (len(order) > 100) & (len(transaction) > 100):
        transaction['tran_dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        transaction_cancel = transaction[transaction.TradeType == 1] #挑选出来撤单
        transaction = transaction[(transaction.TradeType != 1) & (transaction.TradePrice != 0)] # 去除撤单，深交所用

        # 撤单
        transaction_cancel.loc[transaction_cancel.TradeBSFlag == 1, 'otindex'] = transaction_cancel['TradeBuyNo']
        transaction_cancel.loc[transaction_cancel.TradeBSFlag == 2, 'otindex'] = transaction_cancel['TradeSellNo']
        # 成交单
        transaction.loc[transaction.TradeBSFlag == 1, 'otindex'] = transaction['TradeSellNo']
        transaction.loc[transaction.TradeBSFlag == 2, 'otindex'] = transaction['TradeBuyNo']
        # 主动成交单,用来填补市价单的OrderAmt
        transaction.loc[transaction.TradeBSFlag == 1, 'market_otindex'] = transaction['TradeBuyNo']
        transaction.loc[transaction.TradeBSFlag == 2, 'market_otindex'] = transaction['TradeSellNo']

        # 订单与上交所处理不同
        order['dt'] = order.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        order['minute'] = order.dt.map(lambda x: x.replace(second=0,microsecond=0))
        # order['otindex'] = order['OrderNO'] # 用来标记order的序号
        order['otindex'] = order['OrderIndex']
        market_order = order[order.OrderType == 1]
        order = order[(order.OrderPrice > 0) & (order.OrderType != 1)]
        order['OrderAmt'] = order.OrderPrice * order.OrderQty
        # 填补市价单的OrderAmt
        orderamt = transaction.groupby('market_otindex').TradeMoney.sum().reset_index()
        orderamt.columns = ['otindex', 'OrderAmt']
        orderamt = orderamt.set_index('otindex')
        market_order = market_order.set_index('otindex').join(orderamt, how = 'left').reset_index()
        order = order.append(market_order).sort_values(by = 'dt')
        
        order_tran_minute_info = get_order_tran_minute_info(order.copy(), transaction.copy())

        order_normal = pd.merge(transaction[['tran_dt','TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney','otindex']], order, on=['otindex'], how = 'outer')
        order_normal = order_normal.sort_values(by = 'tran_dt')
        order_normal['dt'] = order_normal['dt'].fillna(order_normal['tran_dt'])
        order_normal['hold_time'] = order_normal.apply(lambda x:get_order_holdtime(x['dt'], x['tran_dt']), axis = 1)
        order_normal_first = order_normal.drop_duplicates(subset='otindex', keep = 'first')
        order_normal = order_normal.drop_duplicates(subset='otindex', keep = 'last')
        order_normal_first['first_hold_time'] = order_normal_first['hold_time']
        order_normal = pd.merge(order_normal, order_normal_first[['first_hold_time','otindex']], how = 'left')
        order_normal['finish_time'] = order_normal['hold_time'] - order_normal['first_hold_time'] # 一个订单从开始交易到交易结束花了多久
        order_normal.loc[order_normal.OrderType == 1,['hold_time','first_hold_time','finish_time']] = order_normal.loc[order_normal.OrderType == 1,['hold_time','first_hold_time','finish_time']].fillna(0)
        order_normal['tran_minute'] = order_normal.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))

        order_cancel = pd.merge(transaction_cancel[['tran_dt','TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney','otindex']], order, on=['otindex'], how = 'left')
        order_cancel = order_cancel.sort_values(by = 'tran_dt')
        order_cancel['dt'] = order_cancel['dt'].fillna(order_cancel['tran_dt'])
        order_cancel['hold_time'] = order_cancel.apply(lambda x:get_order_holdtime(x['dt'], x['tran_dt']), axis = 1)
        order_cancel['OrderAmt'] = order_cancel['OrderPrice'] * order_cancel['TradeQty']
        order_cancel['OrderQty'] = order_cancel['TradeQty']
        order_cancel['tran_minute'] = order_cancel.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))
        order_cancel['minute'] = order_cancel['tran_minute']
    
        orderdf = pd.concat([handle_normal_order(order_normal), handle_cancel_order(order_cancel), order_tran_minute_info], axis = 1)
    return orderdf

def aggregate_order_SH(order, transaction):
    orderdf = pd.DataFrame()
    if (len(order) > 100) & (len(transaction) > 100):
        order = reform_sh_order(order, transaction, append_cancel_orders=True)
        order['dt'] = order.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        order['minute'] = order.dt.map(lambda x: x.replace(second=0,microsecond=0))
        order['otindex'] = order['OrderNO'] # 用来标记order的序号
        order = order[order.OrderPrice > 0]
        order['OrderAmt'] = order.OrderPrice * order.OrderQty

        # 处理非撤单
        transaction['tran_dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        # transaction['tran_minute'] = transaction.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))
        transaction = transaction[transaction.TradePrice != 0]
        transaction.loc[transaction.TradeBSFlag == 1, 'otindex'] = transaction['TradeSellNo']
        transaction.loc[transaction.TradeBSFlag == 2, 'otindex'] = transaction['TradeBuyNo']
        
        order_tran_minute_info = get_order_tran_minute_info(order.copy(), transaction.copy())

        order_normal = order[order.OrderType != 10]
        order_normal = pd.merge(transaction[['tran_dt','TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney','otindex']], order_normal, on=['otindex'], how = 'outer')

        order_normal = order_normal.sort_values(by = 'tran_dt')
        order_normal['dt'] = order_normal['dt'].fillna(order_normal['tran_dt'])
        order_normal['hold_time'] = order_normal.apply(lambda x:get_order_holdtime(x['dt'], x['tran_dt']), axis = 1)
        order_normal_first = order_normal.drop_duplicates(subset='otindex', keep = 'first')
        order_normal = order_normal.drop_duplicates(subset='otindex', keep = 'last')
        order_normal_first['first_hold_time'] = order_normal_first['hold_time']
        order_normal = pd.merge(order_normal, order_normal_first[['first_hold_time','otindex']], how = 'left')
        order_normal['finish_time'] = order_normal['hold_time'] - order_normal['first_hold_time'] # 一个订单从开始交易到交易结束花了多久
        order_normal['tran_minute'] = order_normal.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))

        # 处理撤单
        order_cancel = order[order.OrderType == 10]
        order_cancel_list = order_cancel.otindex.tolist()
        order_cancel_temp = order[order.otindex.isin(order_cancel_list)]
        order_cancel_temp = order_cancel_temp.groupby('otindex').agg({'dt':lambda x:get_order_holdtime(x.iloc[0], x.iloc[-1])})
        order_cancel_temp = order_cancel_temp.reset_index()
        order_cancel_temp.columns = ['otindex','hold_time']
        order_cancel = pd.merge(order_cancel, order_cancel_temp, on=['otindex'],how = 'left')
        
        orderdf = pd.concat([handle_normal_order(order_normal), handle_cancel_order(order_cancel), order_tran_minute_info], axis = 1)
    return orderdf

def get_order_tran_minute_info(order, transaction):
    transaction['tran_minute'] = transaction.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))
    buy_order = order[order.OrderBSFlag == 1]
    sell_order = order[order.OrderBSFlag == 2]
    buy_order['TradeBuyNo'] = buy_order['OrderIndex']
    sell_order['TradeSellNo'] = sell_order['OrderIndex']

    buy_tranorder = pd.merge(transaction[['tran_dt','tran_minute','TradeBuyNo',  'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney']], buy_order, on=['TradeBuyNo'], how = 'left')
    sell_tranorder = pd.merge(transaction[['tran_dt','tran_minute','TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney']], sell_order, on=['TradeSellNo'], how = 'left')
    buy_tranorder = buy_tranorder.sort_values(by = 'tran_dt')
    buy_tranorder['minute'] = buy_tranorder['minute'].fillna(buy_tranorder['tran_minute'])
    sell_tranorder = sell_tranorder.sort_values(by = 'tran_dt')
    sell_tranorder['minute'] = sell_tranorder['minute'].fillna(sell_tranorder['tran_minute'])

    buy_tranorder_thismin = buy_tranorder[buy_tranorder.tran_minute == buy_tranorder.minute]
    buy_tranorder_othermin = buy_tranorder[buy_tranorder.tran_minute != buy_tranorder.minute]

    sell_tranorder_thismin = sell_tranorder[sell_tranorder.tran_minute == sell_tranorder.minute]
    sell_tranorder_othermin = sell_tranorder[sell_tranorder.tran_minute != sell_tranorder.minute]

    buy_order_money_thismin = buy_tranorder_thismin.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
    buy_small_order_thismin = buy_order_money_thismin[buy_order_money_thismin.TradeMoney <= 40000]
    buy_mid_order_thismin = buy_order_money_thismin[(buy_order_money_thismin.TradeMoney > 40000) & (buy_order_money_thismin.TradeMoney <= 200000)]
    buy_big_order_thismin = buy_order_money_thismin[(buy_order_money_thismin.TradeMoney > 200000) & (buy_order_money_thismin.TradeMoney <= 1000000)]
    buy_super_order_thismin = buy_order_money_thismin[(buy_order_money_thismin.TradeMoney > 1000000)]
    buy_small_order_thismin = buy_small_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_smallorder_count_thismin','TradeMoney':'buy_smallorder_money_thismin','TradeQty':'buy_smallorder_volume_thismin'})
    buy_mid_order_thismin = buy_mid_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_midorder_count_thismin','TradeMoney':'buy_midorder_money_thismin','TradeQty':'buy_midorder_volume_thismin'})
    buy_big_order_thismin = buy_big_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_bigorder_count_thismin','TradeMoney':'buy_bigorder_money_thismin','TradeQty':'buy_bigorder_volume_thismin'})
    buy_super_order_thismin = buy_super_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_superorder_count_thismin','TradeMoney':'buy_superorder_money_thismin','TradeQty':'buy_superorder_volume_thismin'})

    buy_tranorder_othermin['minute'] = buy_tranorder_othermin['tran_minute']
    buy_order_money_othermin = buy_tranorder_othermin.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
    buy_small_order_othermin = buy_order_money_othermin[buy_order_money_othermin.TradeMoney <= 40000]
    buy_mid_order_othermin = buy_order_money_othermin[(buy_order_money_othermin.TradeMoney > 40000) & (buy_order_money_othermin.TradeMoney <= 200000)]
    buy_big_order_othermin = buy_order_money_othermin[(buy_order_money_othermin.TradeMoney > 200000) & (buy_order_money_othermin.TradeMoney <= 1000000)]
    buy_super_order_othermin = buy_order_money_othermin[(buy_order_money_othermin.TradeMoney > 1000000)]
    buy_small_order_othermin = buy_small_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_smallorder_count_othermin','TradeMoney':'buy_smallorder_money_othermin','TradeQty':'buy_smallorder_volume_othermin'})
    buy_mid_order_othermin = buy_mid_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_midorder_count_othermin','TradeMoney':'buy_midorder_money_othermin','TradeQty':'buy_midorder_volume_othermin'})
    buy_big_order_othermin = buy_big_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_bigorder_count_othermin','TradeMoney':'buy_bigorder_money_othermin','TradeQty':'buy_bigorder_volume_othermin'})
    buy_super_order_othermin = buy_super_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_superorder_count_othermin','TradeMoney':'buy_superorder_money_othermin','TradeQty':'buy_superorder_volume_othermin'})

    sell_order_money_thismin = sell_tranorder_thismin.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
    sell_small_order_thismin = sell_order_money_thismin[sell_order_money_thismin.TradeMoney <= 40000]
    sell_mid_order_thismin = sell_order_money_thismin[(sell_order_money_thismin.TradeMoney > 40000) & (sell_order_money_thismin.TradeMoney <= 200000)]
    sell_big_order_thismin = sell_order_money_thismin[(sell_order_money_thismin.TradeMoney > 200000) & (sell_order_money_thismin.TradeMoney <= 1000000)]
    sell_super_order_thismin = sell_order_money_thismin[(sell_order_money_thismin.TradeMoney > 1000000)]
    sell_small_order_thismin = sell_small_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_smallorder_count_thismin','TradeMoney':'sell_smallorder_money_thismin','TradeQty':'sell_smallorder_volume_thismin'})
    sell_mid_order_thismin = sell_mid_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_midorder_count_thismin','TradeMoney':'sell_midorder_money_thismin','TradeQty':'sell_midorder_volume_thismin'})
    sell_big_order_thismin = sell_big_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_bigorder_count_thismin','TradeMoney':'sell_bigorder_money_thismin','TradeQty':'sell_bigorder_volume_thismin'})
    sell_super_order_thismin = sell_super_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_superorder_count_thismin','TradeMoney':'sell_superorder_money_thismin','TradeQty':'sell_superorder_volume_thismin'})

    sell_tranorder_othermin['minute'] = sell_tranorder_othermin['tran_minute']
    sell_order_money_othermin = sell_tranorder_othermin.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
    sell_small_order_othermin = sell_order_money_othermin[sell_order_money_othermin.TradeMoney <= 40000]
    sell_mid_order_othermin = sell_order_money_othermin[(sell_order_money_othermin.TradeMoney > 40000) & (sell_order_money_othermin.TradeMoney <= 200000)]
    sell_big_order_othermin = sell_order_money_othermin[(sell_order_money_othermin.TradeMoney > 200000) & (sell_order_money_othermin.TradeMoney <= 1000000)]
    sell_super_order_othermin = sell_order_money_othermin[(sell_order_money_othermin.TradeMoney > 1000000)]
    sell_small_order_othermin = sell_small_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_smallorder_count_othermin','TradeMoney':'sell_smallorder_money_othermin','TradeQty':'sell_smallorder_volume_othermin'})
    sell_mid_order_othermin = sell_mid_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_midorder_count_othermin','TradeMoney':'sell_midorder_money_othermin','TradeQty':'sell_midorder_volume_othermin'})
    sell_big_order_othermin = sell_big_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_bigorder_count_othermin','TradeMoney':'sell_bigorder_money_othermin','TradeQty':'sell_bigorder_volume_othermin'})
    sell_super_order_othermin = sell_super_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_superorder_count_othermin','TradeMoney':'sell_superorder_money_othermin','TradeQty':'sell_superorder_volume_othermin'})

    bsorder_thisothermin = pd.concat([buy_tranorder_thismin.groupby('minute')['TradeMoney'].sum(),buy_tranorder_othermin.groupby('minute')['TradeMoney'].sum(),sell_tranorder_thismin.groupby('minute')['TradeMoney'].sum(),sell_tranorder_othermin.groupby('minute')['TradeMoney'].sum()], axis = 1)

    bsorder_thisothermin.columns = ['buy_order_money_thismin','buy_order_money_othermin','sell_order_money_thismin','sell_order_money_othermin']

    order_tran = pd.concat([bsorder_thisothermin,buy_small_order_thismin,buy_mid_order_thismin,buy_big_order_thismin,buy_super_order_thismin,
                           buy_small_order_othermin,buy_mid_order_othermin,buy_big_order_othermin,buy_super_order_othermin,
                           sell_small_order_thismin,sell_mid_order_thismin,sell_big_order_thismin,sell_super_order_thismin,
                           sell_small_order_othermin,sell_mid_order_othermin,sell_big_order_othermin,sell_super_order_othermin], axis = 1)
    return order_tran
    
def handle_normal_order(order_normal):
    temp1 = order_normal.groupby('minute').agg({'OrderPrice':'count','OrderQty':'sum','OrderAmt':'sum'})
    temp1.columns = ['lo_counts','lo_quantity','lo_amount']
    
    col_list1 = ['lo_counts','lo_quantity','lo_amount']
    
    order_normal_BS = order_normal.groupby(['minute','OrderBSFlag']).agg({'OrderPrice':'count','OrderQty':'sum','OrderAmt':'sum'})
    
    result_list = []
    level1_index_list = order_normal_BS.index.get_level_values(1).unique().tolist()
    for bs_flag,bs_name in bs_map.items():
        if bs_flag in level1_index_list:
            temp = order_normal_BS.xs(bs_flag, level = 1)
            temp.columns = ['%s_%s' % (bs_name, x) for x in col_list1]
        else:
            temp = pd.DataFrame()
        result_list.append(temp)
    order_normal_minute = pd.concat(result_list, axis = 1, join = 'outer')

    order_normal['OrderLevel'] = order_normal.apply(lambda x:get_OrderLevel(x['OrderAmt']), axis = 1)
    order_normal_BS_level = order_normal.groupby(['minute','OrderBSFlag','OrderLevel']).agg({'OrderPrice':'count','OrderQty':'sum','OrderAmt':'sum'})
    result_list = []
    level1_normal_index_list = order_normal_BS_level.index.get_level_values(1).unique().tolist()
    for bs_flag,bs_name in bs_map.items():
        if bs_flag in level1_normal_index_list:
            temp_bs = order_normal_BS_level.xs(bs_flag, level = 1)
            odlevel_list = temp_bs.index.get_level_values(1).unique().tolist()
            for order_level,orderlevel_name in orderlevel_map.items():
                if order_level not in odlevel_list:
                    continue
                temp_bs_level = temp_bs.xs(order_level, level = 1)
                temp_bs_level.columns = ['%s_%s_%s' % (bs_name, orderlevel_name, x) for x in col_list1]
                result_list.append(temp_bs_level)
    if len(result_list) > 0:
        order_normal_level_minute = pd.concat(result_list, axis = 1, join = 'outer')
    else:
        order_normal_level_minute = pd.DataFrame()
        
    r1 = pd.concat([temp1,order_normal_minute,order_normal_level_minute], axis = 1)
    
    temp1 = order_normal.groupby('tran_minute').agg({'hold_time':'mean','first_hold_time':'mean','finish_time':'mean'})
    temp1.columns = ['lo_hold_time','lo_first_hold_time','lo_finish_time']

    order_normal_BS = order_normal.groupby(['tran_minute','OrderBSFlag']).agg({'hold_time':'mean','first_hold_time':'mean','finish_time':'mean'})

    col_list2 = ['lo_hold_time','lo_first_hold_time','lo_finish_time']
    result_list = []
    level1_index_list = order_normal_BS.index.get_level_values(1).unique().tolist()
    for bs_flag,bs_name in bs_map.items():
        if bs_flag in level1_index_list:
            temp = order_normal_BS.xs(bs_flag, level = 1)
            temp.columns = ['%s_%s' % (bs_name, x) for x in col_list2]
        else:
            temp = pd.DataFrame()
        result_list.append(temp)
    order_normal_minute = pd.concat(result_list, axis = 1, join = 'outer')

    order_normal['OrderLevel'] = order_normal.apply(lambda x:get_OrderLevel(x['OrderAmt']), axis = 1)
    order_normal_BS_level = order_normal.groupby(['tran_minute','OrderBSFlag','OrderLevel']).agg({'hold_time':'mean','first_hold_time':'mean','finish_time':'mean'})
    result_list = []
    level1_normal_index_list = order_normal_BS_level.index.get_level_values(1).unique().tolist()
    for bs_flag,bs_name in bs_map.items():
        if bs_flag in level1_normal_index_list:
            temp_bs = order_normal_BS_level.xs(bs_flag, level = 1)
            odlevel_list = temp_bs.index.get_level_values(1).unique().tolist()
            for order_level,orderlevel_name in orderlevel_map.items():
                if order_level not in odlevel_list:
                    continue
                temp_bs_level = temp_bs.xs(order_level, level = 1)
                temp_bs_level.columns = ['%s_%s_%s' % (bs_name, orderlevel_name, x) for x in col_list2]
                result_list.append(temp_bs_level)
    if len(result_list) > 0:
        order_normal_level_minute = pd.concat(result_list, axis = 1, join = 'outer')
    else:
        order_normal_level_minute = pd.DataFrame()
    
    r2 = pd.concat([temp1,order_normal_minute,order_normal_level_minute], axis = 1)
    
    return pd.concat([r1,r2], axis = 1)


def handle_cancel_order(order_cancel):
    temp2 = order_cancel.groupby('minute').agg({'OrderPrice':'count','OrderQty':'sum','OrderAmt':'sum','hold_time':'mean'})
    temp2.columns = ['cancel_lo_counts','cancel_lo_quantity','cancel_lo_amount','cancel_lo_hold_time']

    order_cancel_BS = order_cancel.groupby(['minute','OrderBSFlag']).agg({'OrderPrice':'count','OrderQty':'sum','OrderAmt':'sum','hold_time':'mean'})
    result_list = []
    level1_index_list = order_cancel_BS.index.get_level_values(1).unique().tolist()
    for bs_flag,bs_name in bs_map.items():
        if bs_flag in level1_index_list:
            temp = order_cancel_BS.xs(bs_flag, level = 1)
            temp.columns = ['%s_cancel_%s' % (bs_name, x) for x in col_list_cancel]
        else:
            temp = pd.DataFrame()
        result_list.append(temp)
    order_cancel_minute = pd.concat(result_list, axis = 1, join = 'outer')

    order_cancel['OrderLevel'] = order_cancel.apply(lambda x:get_OrderLevel(x['OrderAmt']), axis = 1)

    order_cancel_BS_level = order_cancel.groupby(['minute','OrderBSFlag','OrderLevel']).agg({'OrderPrice':'count','OrderQty':'sum','OrderAmt':'sum','hold_time':'mean'})

    result_list = []
    level1_cencel_index_list = order_cancel_BS_level.index.get_level_values(1).unique().tolist()
    for bs_flag,bs_name in bs_map.items():
        if bs_flag in level1_cencel_index_list:
            temp_bs = order_cancel_BS_level.xs(bs_flag, level = 1)
            odlevel_list = temp_bs.index.get_level_values(1).unique().tolist()
            for order_level,orderlevel_name in orderlevel_map.items():
                if order_level not in odlevel_list:
                    continue
                temp_bs_level = temp_bs.xs(order_level, level = 1)
                temp_bs_level.columns = ['%s_%s_cancel_%s' % (bs_name, orderlevel_name, x) for x in col_list_cancel]
                result_list.append(temp_bs_level)
    if len(result_list) > 0:
        order_cancel_level_minute = pd.concat(result_list, axis = 1, join = 'outer')
    else:
        order_cancel_level_minute = pd.DataFrame()
    
    return pd.concat([temp2,order_cancel_minute,order_cancel_level_minute], axis = 1)
    
        
def get_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50','IM.CFE':'index_weight_zz1000'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()

def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '14:56:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()
    
def get_csvdf_v2(para):
#     print(para)
    csvpath = os.path.join(rootpath, str(para[0]), para[1] + '.csv')
    if not os.path.exists(csvpath):
         return
    try:
        csvdf = pd.read_csv(csvpath, index_col=0, parse_dates=True)
    except:
        return
    target_index = get_index_fromdate(para[0])
    csvdf = target_index.join(csvdf, how = 'outer').sort_index()
    csvdf[ffill_list_oldframe] = csvdf[ffill_list_oldframe].replace(0,np.nan).fillna(method = 'ffill')
    csvdf[fill0_list_oldframe] = csvdf[fill0_list_oldframe].fillna(0)

    csvdf['Ticker'] = para[1]
    csvdf = csvdf.reindex(target_index.index).reset_index().set_index(['dt','Ticker'])[standard_columns_oldframe] 
    return csvdf

def get_csvdf_v3(csvpath):
#     print(para)
    if not os.path.exists(csvpath):
         return
    try:
        csvdf = pd.read_csv(csvpath, index_col=0, parse_dates=True)#.drop(time_list, axis = 1)
    except Exception as e:
        print(e, csvpath)
        return
    target_index = get_index_fromdate(int(csvpath.split('/')[-2]))
    csvdf = target_index.join(csvdf, how = 'outer').sort_index()
    csvdf[ffill_list] = csvdf[ffill_list].replace(0,np.nan).fillna(method = 'ffill')
    csvdf[fill0_list] = csvdf[fill0_list].fillna(0)

#     csvdf['Ticker'] = csvpath.split('/')[-1][:-3]
    csvdf = csvdf.reindex(target_index.index)[standard_columns] 
    return csvdf

def link_send_message(message):
    from xquant.xqutils.helper import link
    lm = link.LinkMessage()
    lm.sendMessage(message)
    del(lm)
    


def add_turnover_rate_and_adj(df, stock):
    df = df.reset_index()
    df['CHANGE_DT'] = df.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    ashare = ashare_total.loc[stock].reset_index(drop = True).sort_values(by = 'CHANGE_DT')
    temp = df[['CHANGE_DT']]
    temp2 = pd.merge(temp, ashare, on=['CHANGE_DT'], how = 'outer')
    temp2 = temp2.sort_values(['CHANGE_DT'])
    temp2['FLOAT_A_SHR'] = temp2['FLOAT_A_SHR'].fillna(method = 'ffill')
    temp2 = temp2[temp2.CHANGE_DT >= 20100101]
    temp2 = temp2.drop_duplicates(keep = 'last')

    _adj_df = adj_df.xs(stock, level = 1).reset_index().rename(columns = {'dt':'CHANGE_DT'})
    _adj_df['CHANGE_DT'] = _adj_df.CHANGE_DT.apply(lambda x:int(str(x.date()).replace('-','')))
    totaldf = pd.merge(df, temp2, on=['CHANGE_DT'], how = 'left')
    totaldf = pd.merge(totaldf, _adj_df, on=['CHANGE_DT'], how = 'left')
    

    totaldf = totaldf.drop(['CHANGE_DT'], axis = 1)
    totaldf.rename(columns = {'FLOAT_A_SHR':'float_shares'}, inplace = True)

    if ('volume' not in totaldf.columns) or ('float_shares' not in totaldf.columns):
        totaldf['turnover_rate'] = np.nan
    else:
        totaldf['turnover_rate'] = totaldf.volume / totaldf.float_shares / 100
    totaldf = totaldf.set_index(['dt'])
    totaldf = totaldf.sort_index()

    return totaldf

def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

# 聚合成新框架h5时所用
def get_h5_by_stock(stock):
    pathlist = glob.glob(csv_rootpath + '*/%s.csv' % stock)

    csvdf_list = []
    for path in pathlist:
        csvdf_list.append(get_csvdf_v3(path))
    if len(csvdf_list) == 0:
        print(stock, 'no csv!!!')
        return
    finaldf = pd.concat(csvdf_list, axis = 0).sort_index()

    stk_ret = finaldf['close'].pct_change(1, fill_method=None)
    finaldf['stk_volatility'] = ts_std(stk_ret, 15)

    ret_300 = index_ret_300.reindex(stk_ret.index)
    ret_500 = index_ret_500.reindex(stk_ret.index)
    ret_50 = index_ret_50.reindex(stk_ret.index)
    ret_1000 = index_ret_1000.reindex(stk_ret.index)
    finaldf['stk_index_corr_hs300'] = stk_ret.rolling(1200, min_periods=600).corr(ret_300).replace([-np.inf, np.inf], np.nan)
    finaldf['stk_index_corr_zz500'] = stk_ret.rolling(1200, min_periods=600).corr(ret_500).replace([-np.inf, np.inf], np.nan)
    finaldf['stk_index_corr_sh50'] = stk_ret.rolling(1200, min_periods=600).corr(ret_50).replace([-np.inf, np.inf], np.nan)
    finaldf['stk_index_corr_zz1000'] = stk_ret.rolling(1200, min_periods=600).corr(ret_1000).replace([-np.inf, np.inf], np.nan)

    finaldf = add_turnover_rate_and_adj(finaldf, stock)
    
    finaldf['Ticker'] = stock
    finaldf = finaldf.reset_index().set_index(['dt','Ticker'])
    
    IO.pd_hdf5_writer(finaldf, os.path.join(h5_path, '%s.h5' % stock), dataset=stock)
    
    
# 将每日的时间戳固定为9:30-14:56
def standard_index(data):
    t_days_list = udt.get_trading_date_range(str(data.index[0].date()).replace('-',''),str(data.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:56:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    data = index_df.join(data, how = 'left')
    return data
    


def get_adjfactor(stock, date):
    df = WIND_AShareEODPrices.copy()
    return df[df.S_INFO_WINDCODE == stock]['S_DQ_ADJFACTOR'].tolist()[0]



def add_turnover_rate(df, stock):
    df = df.reset_index()
    df['CHANGE_DT'] = df.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    ashare = ashare_total.loc[stock].reset_index(drop = True).sort_values(by = 'CHANGE_DT')
    temp = df[['CHANGE_DT']]
    temp2 = pd.merge(temp, ashare, on=['CHANGE_DT'], how = 'outer')
    temp2 = temp2.sort_values(['CHANGE_DT'])
    temp2['FLOAT_A_SHR'] = temp2['FLOAT_A_SHR'].fillna(method = 'ffill')
    temp2 = temp2[temp2.CHANGE_DT >= 20010101]
    temp2 = temp2.drop_duplicates(keep = 'last')

    totaldf = pd.merge(df, temp2, on=['CHANGE_DT'], how = 'left')
    

    totaldf = totaldf.drop(['CHANGE_DT'], axis = 1)
    totaldf.rename(columns = {'FLOAT_A_SHR':'float_shares'}, inplace = True)

    if ('volume' not in totaldf.columns) or ('float_shares' not in totaldf.columns):
        totaldf['turnover_rate'] = np.nan
    else:
        totaldf['turnover_rate'] = totaldf.volume / totaldf.float_shares / 100
    totaldf = totaldf.set_index(['dt'])
    totaldf = totaldf.sort_index()

    return totaldf
# 获取下一交易日的成分股及权重，好用来补充历时一个月的数据
def get_nexttday_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50','IM.CFE':'index_weight_zz1000'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
#     indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()

def update_cfgdata(para):
    try:
        print(para)
        date = para[0]
        stock = para[1]
        weight = round(para[2],5)

        csvpath = os.path.join(rootpath, str(date))
        filepath = os.path.join(csvpath, stock+'.csv')

        md = XMD()
        # mdtp = XMDTP()

        tick = md.get_data_by_date("Stock", stock, str(date))
        tickdf = aggregate_tick(tick)

        # transaction = md.getMDTransactionDataFrame(stock, str(date) + '000000', str(date) + '235959')
        transaction = md.get_data_by_date("Transaction", stock, str(date))
        transactiondf = aggregate_transaction(transaction.copy())

        # order = md.getMDOrderDataFrame(stock, str(date) + '000000', str(date) + '235959')
        order = md.get_data_by_date("Order", stock, str(date))
        if stock.endswith('SH'):
            orderdf = aggregate_order_SH(order, transaction)
        else:
            orderdf = aggregate_order_SZ(order, transaction)

        del(md)        
        result = pd.concat([tickdf, transactiondf, orderdf], axis = 1)
        result = result.drop(list(set(time_list) & set(result.columns.tolist())), axis = 1)
        # if len(result) == 0:
        #     return
        result['weight'] = weight

        result.index.name = 'dt'
        result.to_csv(filepath)

        result['adjfactor'] = get_adjfactor(stock, date)
        result = add_turnover_rate(result, stock)
        result = standard_index(result)

        result['Ticker'] = stock
        result = result.reset_index().set_index(['dt','Ticker'])

        h5_path = os.path.join(h5_rootpath, stock + '.h5')
        if os.path.exists(h5_path):
            historydf = IO.read_data([pre6date, date],alt = h5_path)
            result = historydf.append(result)

        result = result.reset_index(level = 1)
        stk_ret = (result['close'] * result['adjfactor'] / result.iloc[-1]['adjfactor']).pct_change(1, fill_method = None)
        result['stk_volatility'] = ts_std(stk_ret, 15)

        if len(result) < 1200:
            result['stk_index_corr_hs300'] = np.nan
            result['stk_index_corr_zz500'] = np.nan
            result['stk_index_corr_sh50'] = np.nan
            result['stk_index_corr_zz1000'] = np.nan
        else:
            ret_300 = index_ret_300.reindex(stk_ret.index)
            ret_500 = index_ret_500.reindex(stk_ret.index)
            ret_50 = index_ret_50.reindex(stk_ret.index)
            ret_1000 = index_ret_1000.reindex(stk_ret.index)
            result['stk_index_corr_hs300'] = stk_ret.rolling(1200, min_periods=600).corr(ret_300).replace([-np.inf, np.inf], np.nan)
            result['stk_index_corr_zz500'] = stk_ret.rolling(1200, min_periods=600).corr(ret_500).replace([-np.inf, np.inf], np.nan)
            result['stk_index_corr_sh50'] = stk_ret.rolling(1200, min_periods=600).corr(ret_50).replace([-np.inf, np.inf], np.nan)
            result['stk_index_corr_zz1000'] = stk_ret.rolling(1200, min_periods=600).corr(ret_1000).replace([-np.inf, np.inf], np.nan)

        result = result.loc[str(date)].reset_index().set_index(['dt','Ticker'])

        # save_stock_df_to_csv(result,stock,date)

        clist = result.columns.tolist()
        res_columns = list(set(standard_columns) - set(clist))
        if len(res_columns) > 0:
            for x in res_columns:
                result[x] = np.nan
        result[ffill_list] = result[ffill_list].replace([0],np.nan).fillna(method = 'ffill')
        result[fill0_list] = result[fill0_list].fillna(value = 0)

        result = result[standard_columns]
        if os.path.exists(h5_path):
            IO.pd_hdf5_writer(result, h5_path, dataset = stock, append = True)
        else:
            IO.pd_hdf5_writer(result, h5_path, dataset = stock)
    except Exception as e:
        link_send_message(str(para) + str(e))
        print(para, e)
        
# 补充历史一个月的数据
def update_30daysdata(plist, ncore):
    print(plist)
    
    for para in plist:
        with Pool(ncore) as pool:
            pool.map(update_cfgdata, para)        

def update_by_date(date, ncore = 24):
    if not os.path.exists(os.path.join(rootpath, str(date))):
        os.makedirs(os.path.join(rootpath, str(date)))
        
    last_tday = udt.get_trading_day_offset(date,-1)[0] #上一个交易日

    today_uplist = get_target_list('IC.CFE',last_tday,date) + get_target_list('IF.CFE',last_tday,date) 
    nexttday_uplist = get_nexttday_target_list('IC.CFE',date,date) + get_nexttday_target_list('IF.CFE',date,date)

    today_stklist = [x[1] for x in today_uplist]
    nexttday_stklist = [x[1] for x in nexttday_uplist]

    new_addstk_list = list(set(nexttday_stklist) - set(today_stklist))
    
    with Pool(ncore) as pool:
        pool.map(update_cfgdata, today_uplist)
    
    print('all stock finished!')
    print(new_addstk_list)
    # 如果有新调入的股票，进行处理
    if len(new_addstk_list) > 0:
        print('!')
        tdays30days = [int(str(x.date()).replace('-','')) for x in udt.get_trading_date_range(udt.get_trading_day_offset(date,-30)[0],date)]
        new_addstk_uplist = []
        
        for d in tdays30days:
            slist = []
            for stk in new_addstk_list:
                slist.append([d,stk,np.nan])
            new_addstk_uplist.append(slist)            

        print('start add history 30days date for new stock!')
        update_30daysdata(new_addstk_uplist, ncore = ncore)
    print('done')

    return

rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_STOCK/tick_transaction_order_tominute_v3/'
insample_rootpath = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/' 
suffix_dict = {'IC.CFE':'500','IF.CFE':'300','IH.CFE':'50','IM.CFE':'1000'}
for ticker in ['IF.CFE']:
    insample_path = os.path.join(insample_rootpath, 'cfg_hf_data_%s' % suffix_dict[ticker])
    if not os.path.exists(insample_path):
        os.makedirs(insample_path)

    for date_para in [(20201001,20220819)]:
        startdate,enddate = date_para[0], date_para[1]
        
        if startdate == enddate:
            print(ticker, ' startdate == enddate, data already exists!')

        paralist = get_target_list(ticker,startdate,enddate)

        print('start')
        dflist = []
        with Pool(24) as pool:
            dflist = pool.map(get_csvdf_v2, paralist)
        print('csv done') 

        for i in range(0,len(standard_columns_oldframe), 10):
            clist = standard_columns_oldframe[i:i+10]
            print(clist)
            newlist = [d[clist] for d in dflist if (d is not None)]
            df = pd.concat(newlist, axis = 0).sort_index().add_suffix('_%s' % suffix_dict[ticker])
            df = df.unstack()
            for x in df.columns.get_level_values(0).unique().tolist():
                print(x)
                df[x].to_pickle(os.path.join(insample_path,x+'.pkl'))
