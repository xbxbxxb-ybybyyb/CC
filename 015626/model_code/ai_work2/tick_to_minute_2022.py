import sys
sys.path.insert(4,'/data/user/015626/JupyterNotebooks/utils/')

from xquant.marketdata import MarketData
import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os,re
from multiprocessing import Pool
import time
from multifactor.data.utils import *

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
    
def get_cfg_hfdata(para):
    try:
        mdp = MarketData()

        date = para[0]
        stock = para[1]
        weight = round(para[2],5)


        csvpath = os.path.join(rootpath, str(date))
        filepath = os.path.join(csvpath, stock+'.csv')
        if os.path.exists(filepath):
            return

        tick = mdp.get_data_by_date("Stock", stock, str(date), ['3','5'])
        del(mdp)
        tickdf = pd.DataFrame()
        if len(tick) > 100:
            fill_na_columns = ['LastPx','Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price', 'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price', 'Sell5Price']
            tickdf = pd.DataFrame()
            tick[fill_na_columns] =  tick[fill_na_columns].replace(0,np.nan)

            tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
            tick['minute'] = tick.dt.map(lambda x: x.replace(second=0))
            tick = tick.set_index('dt')
            tick['OBI'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty']).replace(0, np.nan)
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

            # pvcorrdf = tick[['minute','LastPx','volume']].groupby('minute').corr().xs('LastPx', level = 1)[['volume']]
            # pvcorrdf.columns = ['PxVolCorr']
            aggdict = {'Buy1NumOrders':'mean','Sell1NumOrders':'mean','BidAskSpreadMean':'mean','Bid1Amt':'mean','Ask1Amt':'mean','volume':'sum','amount':'sum','pricediff':'sum','LastPx':'std','VolStd':'std'}

            aggdict2 = {'TotalValueTrade':'last','TotalVolumeTrade':'last','TotalOfferQty':'last','TotalBidQty':'last','Buy1Price':'last','Buy1OrderQty':'last', 'Sell1Price':'last','Sell1OrderQty':'last','Buy2Price':'last','Buy2OrderQty':'last', 'Sell2Price':'last','Sell2OrderQty':'last',
                       'Buy3Price':'last','Buy3OrderQty':'last', 'Sell3Price':'last','Sell3OrderQty':'last','Buy4Price':'last','Buy4OrderQty':'last', 'Sell4Price':'last','Sell4OrderQty':'last',
                       'Buy5Price':'last','Buy5OrderQty':'last', 'Sell5Price':'last','Sell5OrderQty':'last'}

            # df1amt = tick.resample('1min').agg({**aggdict_ohlc, **aggdict, **aggdict1, **aggdict2})

            renamedict1 = {'Buy1NumOrders':'Buy1NumOrdersMean','Sell1NumOrders':'Sell1NumOrdersMean','Bid1Amt':'Bid1AmtMean','Ask1Amt':'Ask1AmtMean','pricediff':'AbsPxPath','LastPx':'PxStd'}

            renamedict2 = {'TotalOfferQty':'TotalAskVol','TotalBidQty':'TotalBidVol','Buy1Price':'BidP0','Buy1OrderQty':'BidV0', 'Sell1Price':'AskP0','Sell1OrderQty':'AskV0','Buy2Price':'BidP1','Buy2OrderQty':'BidV1', 'Sell2Price':'AskP1','Sell2OrderQty':'AskV1',
                       'Buy3Price':'BidP2','Buy3OrderQty':'BidV2', 'Sell3Price':'AskP2','Sell3OrderQty':'AskV2','Buy4Price':'BidP3','Buy4OrderQty':'BidV3', 'Sell4Price':'AskP3','Sell4OrderQty':'AskV3',
                       'Buy5Price':'BidP4','Buy5OrderQty':'BidV4', 'Sell5Price':'AskP4','Sell5OrderQty':'AskV4'}
            # df1amt = df1amt.rename(columns = {**renamedict1, **renamedict2})

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

            # tickv3 = tick.resample('1min').agg(agg_dict_v3).rename(columns = {x:f'{x}_mean' for x in ['Buy1Price','Buy1OrderQty','Buy1NumOrders','Sell1Price','Sell1OrderQty','Sell1NumOrders']})

            # amtOBI
            for x in ['BuyOrderAmt_5','BuyOrderAmt_5_linear','BuyOrderAmt_5_exp','BuyOrderQty_5_exp','BuyOrderAmt_10','BuyOrderAmt_10_linear','BuyOrderAmt_10_exp','BuyOrderQty_10_exp',
                     'SellOrderAmt_5','SellOrderAmt_5_linear','SellOrderAmt_5_exp','SellOrderQty_5_exp','SellOrderAmt_10','SellOrderAmt_10_linear','SellOrderAmt_10_exp','SellOrderQty_10_exp',
                     'BuyOrderQty_5','BuyOrderQty_10','SellOrderQty_5','SellOrderQty_10']:
                tick[x] = 0

            for i in range(1,11):
                for kind in ['Buy', 'Sell']:
                    tick[f'{kind}{i}OrderAmt'] = (tick[f'{kind}{i}Price'] * tick[f'{kind}{i}OrderQty']).fillna(0)
                    tick[f'{kind}OrderAmt_10'] += tick[f'{kind}{i}OrderAmt']
                    tick[f'{kind}OrderQty_10'] += tick[f'{kind}{i}OrderQty']
                    tick[f'{kind}OrderAmt_10_linear'] += tick[f'{kind}{i}OrderAmt'] * (11-i) / 10
                    tick[f'{kind}OrderAmt_10_exp'] += tick[f'{kind}{i}OrderAmt'] * 0.8 ** (i-1)
                    tick[f'{kind}OrderQty_10_exp'] += tick[f'{kind}{i}OrderQty'] * 0.8 ** (i-1)
                    if i < 6:
                        tick[f'{kind}OrderAmt_5'] += tick[f'{kind}{i}OrderAmt']
                        tick[f'{kind}OrderQty_5'] += tick[f'{kind}{i}OrderQty']
                        tick[f'{kind}OrderAmt_5_linear'] += tick[f'{kind}{i}OrderAmt'] * (11-i) / 10
                        tick[f'{kind}OrderAmt_5_exp'] += tick[f'{kind}{i}OrderAmt'] * 0.8 ** (i-1)
                        tick[f'{kind}OrderQty_5_exp'] += tick[f'{kind}{i}OrderQty'] * 0.8 ** (i-1)

            tick['BuyOrderAmt_total'] = (tick['TotalBidQty'] * tick['WeightedAvgBidPx']).fillna(0)
            tick['SellOrderAmt_total'] = (tick['TotalOfferQty'] * tick['WeightedAvgOfferPx']).fillna(0)
            tick['amtOBI_total'] = (tick['BuyOrderAmt_total'] - tick['SellOrderAmt_total']) / (tick['BuyOrderAmt_total'] + tick['SellOrderAmt_total']).replace(0, np.nan)

            tick['amtOBI_1'] = (tick['Buy1OrderAmt'] - tick['Sell1OrderAmt']) / (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']).replace(0, np.nan)
            for i in [5,10]:
                tick[f'amtOBI_{i}'] = (tick[f'BuyOrderAmt_{i}'] - tick[f'SellOrderAmt_{i}']) / (tick[f'BuyOrderAmt_{i}'] + tick[f'SellOrderAmt_{i}']).replace(0, np.nan)
                for kind in ['linear','exp']:
                    tick[f'amtOBI_{i}_{kind}'] = (tick[f'BuyOrderAmt_{i}_{kind}'] - tick[f'SellOrderAmt_{i}_{kind}']) / (tick[f'BuyOrderAmt_{i}_{kind}'] + tick[f'SellOrderAmt_{i}_{kind}']).replace(0, np.nan)

            amtOBI_list = ['BuyOrderAmt_total', 'SellOrderAmt_total', 'amtOBI_total', 'BuyOrderAmt_5', 'BuyOrderAmt_5_linear', 'BuyOrderAmt_5_exp', 'BuyOrderAmt_10', 'BuyOrderAmt_10_linear', 'BuyOrderAmt_10_exp','SellOrderAmt_5', 'SellOrderAmt_5_linear', 'SellOrderAmt_5_exp',  'SellOrderAmt_10', 'SellOrderAmt_10_linear', 'SellOrderAmt_10_exp',  'amtOBI_1', 'amtOBI_5', 'amtOBI_5_linear', 'amtOBI_5_exp', 'amtOBI_10', 'amtOBI_10_linear', 'amtOBI_10_exp']
            amtOBI_dict = {x:'mean' for x in amtOBI_list}

            # amount 相关
            tick.loc[tick['LastPx'].pct_change() > 0, 'tickup_amount'] = tick['amount']
            tick['orderamt1_amount_ratio'] = (tick['Buy1OrderAmt'] - tick['Sell1OrderAmt']) / tick['amount'].replace(0, np.nan)
            for i in [5, 10]:
                tick[f'orderamt{i}_amount_ratio'] = (tick[f'BuyOrderAmt_{i}'] - tick[f'SellOrderAmt_{i}']) / tick['amount'].replace(0, np.nan)
                tick[f'BSOrderAmt_{i}_to_amount'] = (tick[f'BuyOrderAmt_{i}'] + tick[f'SellOrderAmt_{i}']) / tick['amount'].replace(0, np.nan)
            tick['BSOrderAmt_1_to_amount'] = (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']) / tick['amount'].replace(0, np.nan)

            amount_dict = {'BSOrderAmt_1_to_amount':'mean','BSOrderAmt_5_to_amount':'mean','BSOrderAmt_10_to_amount':'mean','tickup_amount':'sum', 'orderamt1_amount_ratio':'mean', 'orderamt5_amount_ratio':'mean', 'orderamt10_amount_ratio':'mean'}

            # bid ask spread
            tick['mid_price'] = tick[['Buy1Price', 'Sell1Price']].mean(axis = 1)
            # tick['mid_price'] = tick['mid_price'].fillna(value = tick[['Buy1Price','Sell1Price']].fillna(0).max(axis = 1))

            tick['bas'] = tick['Sell1Price'] - tick['Buy1Price']
            tick['bas_ratio'] = tick['bas'] / tick['mid_price']

            for i in range(1, 11):
                tick[f's1bndiff_{i}'] = tick['Sell1Price'] - tick[f'Buy{i}Price'] 
                tick[f'snb1diff_{i}'] = tick[f'Sell{i}Price'] - tick['Buy1Price']
                tick[f'snmiddiff_{i}'] = tick[f'Sell{i}Price'] - tick['mid_price']
                tick[f'bnmiddiff_{i}'] = tick['mid_price'] - tick[f'Buy{i}Price']
                tick[f'Amtmul_snmiddiff_{i}'] = tick[f'snmiddiff_{i}'] * tick[f'Sell{i}OrderAmt']
                tick[f'Amtmul_bnmiddiff_{i}'] = tick[f'bnmiddiff_{i}'] * tick[f'Buy{i}OrderAmt']

            for i in [5, 10]:
                for kind in ['Buy', 'Sell']:
                    tick[f'{kind}OrderWeightedPx_{i}'] = tick[f'{kind}OrderAmt_{i}'] / tick[f'{kind}OrderQty_{i}'].replace(0, np.nan)
                tick[f'bas_bas{i}'] = tick['bas'] / (tick[f'Sell{i}Price'] - tick[f'Buy{i}Price']).replace(0, np.nan)
                tick[f'bas_WeightedPxbas{i}'] = tick['bas'] / (tick[f'SellOrderWeightedPx_{i}'] - tick[f'BuyOrderWeightedPx_{i}']).replace(0, np.nan)
                tick[f'cumbas_{i}'] = tick[[f's1bndiff_{j + 1}' for j in range(i)]].sum(axis = 1) / tick[[f'snb1diff_{j + 1}' for j in range(i)]].sum(axis = 1).replace(0, np.nan)
                tick[f'bas_midpx_WeightedPxbas{i}'] = (tick[f'SellOrderWeightedPx_{i}'] - tick['mid_price']) / (tick[f'SellOrderWeightedPx_{i}'] - tick[f'BuyOrderWeightedPx_{i}']).replace(0, np.nan)
                tick[f'SBWeightedPx_{i}_to_midprice'] = (tick[f'SellOrderWeightedPx_{i}'] - tick[f'BuyOrderWeightedPx_{i}']) / tick['mid_price']
                tick[f'SWeightedPx_{i}_minusS1_to_midprice'] = (tick[f'SellOrderWeightedPx_{i}'] - tick['Sell1Price']) / tick['mid_price']
                tick[f'B1minus_BWeightedPx_{i}_to_midprice'] = (tick['Buy1Price'] - tick[f'BuyOrderWeightedPx_{i}']) / tick['mid_price']


            bas_list = ['B1minus_BWeightedPx_5_to_midprice','B1minus_BWeightedPx_10_to_midprice','SWeightedPx_5_minusS1_to_midprice','SWeightedPx_10_minusS1_to_midprice','SBWeightedPx_5_to_midprice','SBWeightedPx_10_to_midprice','mid_price', 'bas_ratio', 'BuyOrderWeightedPx_5', 'SellOrderWeightedPx_5', 'bas_bas5', 'bas_WeightedPxbas5', 'cumbas_5', 'bas_midpx_WeightedPxbas5', 'BuyOrderWeightedPx_10', 'SellOrderWeightedPx_10', 'bas_bas10', 'bas_WeightedPxbas10', 'cumbas_10', 'bas_midpx_WeightedPxbas10']
            bas_dict = {x:'mean' for x in bas_list}

            # vwap
            tick['tick_vwap'] = tick['amount'] / tick['volume'].replace(0, np.nan)
            tick['vwap_midprice'] = tick['tick_vwap'] / tick['mid_price']
            tick['vwapmid_lastpx'] = (tick['tick_vwap'] - tick['mid_price']) / tick['LastPx']
            tick['vwap_std'] = tick['tick_vwap']
            tick['vwap_ret_std'] = tick['tick_vwap'].pct_change()
            vwap_dict = {'tick_vwap':'mean', 'vwap_midprice':'mean', 'vwapmid_lastpx':'mean', 'vwap_std':'std', 'vwap_ret_std':'std'}

            # 15s的一些东西
            tickdata15s = tick.resample('15S').agg({'amount':'sum','volume':'sum','LastPx':'first'})
            tickdata15s = tickdata15s.loc[tickdata15s.index.second == 45].reset_index()
            tickdata15s['dt'] = tickdata15s.dt.map(lambda x:x.replace(second = 0))

            tickdata15s = tickdata15s.set_index('dt').add_suffix('_last15s')
            tickdata15s['vwap_last15s'] = tickdata15s['amount_last15s'] / tickdata15s['volume_last15s'].replace(0, np.nan)

            # cc系列
            tick['bas_std'] = tick['bas']
            tick['bid_ask_dis_ratio'] = (tick[[f'Sell{j}Price' for j in range(1,11)]].max(axis = 1) - tick['Sell1Price']) / (tick['Buy1Price'] - tick[[f'Buy{j}Price' for j in range(1,11)]].min(axis = 1)).replace(0, np.nan)
            tick['buy_amt_middiff_weighted'] = tick[[f'Amtmul_bnmiddiff_{i}' for j in range(1,11)]].sum(axis = 1) / tick[[f'bnmiddiff_{i}' for j in range(1,11)]].sum(axis = 1).replace(0, np.nan)
            tick['sell_amt_middiff_weighted'] = tick[[f'Amtmul_snmiddiff_{i}' for j in range(1,11)]].sum(axis = 1) / tick[[f'snmiddiff_{i}' for j in range(1,11)]].sum(axis = 1).replace(0, np.nan)
            tick['bs1_amt_mean'] = (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']) / 2
            tick['bs1_amt_min'] = tick[['Buy1OrderAmt', 'Sell1OrderAmt']].min(axis = 1)
            tick['amt_b1_ball'] = tick['Buy1OrderAmt'] / tick['BuyOrderAmt_10'].replace(0, np.nan)
            tick['amt_s1_sall'] = tick['Sell1OrderAmt'] / tick['SellOrderAmt_10'].replace(0, np.nan)
            tick['amt_b1_bexpall'] = tick['Buy1OrderAmt'] / tick['BuyOrderAmt_10_exp'].replace(0, np.nan)
            tick['amt_s1_sexpall'] = tick['Sell1OrderAmt'] / tick['SellOrderAmt_10_exp'].replace(0, np.nan)

            tick['amt_b1_s1'] = tick['Buy1OrderAmt'] / tick['Sell1OrderAmt'].replace(0, np.nan)
            tick['amt_bexpall_sexpall'] = tick['BuyOrderAmt_10_exp'] / tick['SellOrderAmt_10_exp'].replace(0, np.nan)
            tick['weighted_mid1'] = (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty']).replace(0, np.nan)
            for i in [5, 10]:
                tick[f'weighted_mid{i}'] = (tick[f'BuyOrderAmt_{i}'] + tick[f'SellOrderAmt_{i}']) / (tick[f'BuyOrderQty_{i}'] + tick[f'SellOrderQty_{i}']).replace(0, np.nan)
                tick[f'mid_weighted_mid{i}'] = tick['mid_price'] / tick[f'weighted_mid{i}']
                tick[f'expweighted_mid{i}'] = (tick[f'BuyOrderAmt_{i}_exp'] + tick[f'SellOrderAmt_{i}_exp']) / (tick[f'BuyOrderQty_{i}_exp'] + tick[f'SellOrderQty_{i}_exp']).replace(0, np.nan)
                tick[f'mid_expweighted_mid{i}'] = tick['mid_price'] / tick[f'expweighted_mid{i}']

            for kind in ['Buy', 'Sell']:
                # 先找出盘口买量或者卖量最高的价格
                amt_sell = tick[[f'{kind}{j}OrderAmt' for j in range(1,11)]]
                price_sell = tick[[f'{kind}{j}Price' for j in range(1,11)]]
                scols_name = [f'{kind}{j}Order' for j in range(1,11)]
                amtcols_name = [f'{kind}{j}OrderAmt' for j in range(1,11)]

                mask_sell = amt_sell.idxmax(axis = 1)
                # 哪档盘口挂单金额最大
                tick[f'idxmax_{str.lower(kind)}amt'] = mask_sell.apply(lambda x: re.sub("\D", "", x)).astype('int')
                mask_sell = mask_sell.reset_index()
                mask_sell.columns = ['dt','maxcol_name']
                mask_sell['mask'] = True
                mask_sell = mask_sell.set_index(['dt','maxcol_name']).unstack()['mask']
                res_cols = list(set(amtcols_name) - set(mask_sell.columns))
                if len(res_cols) > 0:
                    for res_col in res_cols:
                        mask_sell[res_col] = np.nan
                mask_sell = mask_sell[amtcols_name].fillna(False)
                mask_sell.columns = scols_name
                price_sell.columns = scols_name
                amt_sell.columns = scols_name

                tick[f'max_{str.lower(kind)}amt_price'] = price_sell[mask_sell].mean(axis = 1)
                tick[f'max_{str.lower(kind)}amt_price_mid'] = tick[f'max_{str.lower(kind)}amt_price'] / tick['mid_price']
                # 第一档盘口卖量最高价格之间的所有挂单量之和
                mask_sell = mask_sell.replace(False, np.nan).fillna(axis = 1, method = 'bfill').fillna(0).astype('bool')
                tick[f'{str.lower(kind)}_amtsum_1tomax'] = amt_sell[mask_sell].sum(axis = 1)

            cc_list = ['bid_ask_dis_ratio', 'buy_amt_middiff_weighted', 'sell_amt_middiff_weighted', 'bs1_amt_mean', 'bs1_amt_min', 'amt_b1_ball', 'amt_s1_sall', 'amt_b1_bexpall', 'amt_s1_sexpall', 'amt_b1_s1', 'amt_bexpall_sexpall', 'weighted_mid1', 'weighted_mid5', 'mid_weighted_mid5', 'expweighted_mid5', 'mid_expweighted_mid5', 'weighted_mid10', 'mid_weighted_mid10', 'expweighted_mid10', 'mid_expweighted_mid10', 'idxmax_buyamt', 'max_buyamt_price', 'max_buyamt_price_mid', 'buy_amtsum_1tomax', 'idxmax_sellamt', 'max_sellamt_price', 'max_sellamt_price_mid', 'sell_amtsum_1tomax']
            cc_dict = {'bas_std':'std'}
            cc_dict.update({x:'mean' for x in cc_list})

            agg_dict_v4 = {**amtOBI_dict,**amount_dict,**bas_dict,**vwap_dict,**cc_dict}
            tickv4 = tick.resample('1min').agg(agg_dict_v4).join(tickdata15s)

            # check price
            if tickv4.LastPx_last15s.sum() > 0:    
                tickdf = tickv4#pd.concat([df1amt, pvcorrdf, tickv3, tickv4], axis = 1)

                
        result = tickdf.replace([np.inf, -np.inf], np.nan)
        if len(result) == 0:
            return
#         result['weight'] = weight
        result.loc[:str(date) + ' 112900'].append(result.loc[str(date) + ' 130000':]).to_csv(filepath)
    except Exception as e:
        print(para, e)
    
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
    

                             
for ticker in ['IM.CFE']:
    print(ticker)
    rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/CSV/MINUTE/CHINA_STOCK/tick_to_minute_v5/'
    startdate,enddate,_ = check_update_date(20200701, 20221020)

    paralist = get_target_list(ticker,startdate,enddate)

    for x in list(set([y[0] for y in paralist])):
        csvpath = os.path.join(rootpath, str(x))
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)
            
    # download data       
    with Pool(processes = 24) as pool:
        pool.map(get_cfg_hfdata, paralist)

def link_send_message(message):
    from xquant.xqutils.helper import link
    lm = link.LinkMessage()
    lm.sendMessage(message)
    del(lm)       
link_send_message(str(enddate) + '_success')