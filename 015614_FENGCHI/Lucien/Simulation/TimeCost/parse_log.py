# coding: utf-8
# Author：fengchi863
# Date ：2023/3/16 11:04

import gzip
import os
import re
import time

import pandas as pd
from dateutil.parser import parse

# date = sys.argv[1]
# file_flag = sys.argv[2]
# date = datetime.datetime.today().strftime('%Y%m%d')
date = '20230306'
file_flag = 'uat_lite-20230324'

# log_commonPath = sys.argv[3]
log_commonPath = r'/data/group/800463/xiely/日内强势股/log/'


def get_lines(_date, _file_flag):
    if os.path.exists(log_commonPath + r'StrongStrategy-%s-%s-%s-%s.log.gz' % (_date[:4], _date[4:6], _date[6:8], _file_flag)):
        g_file = gzip.GzipFile(log_commonPath + r'StrongStrategy-%s-%s-%s-%s.log.gz' % (_date[:4], _date[4:6], _date[6:8], _file_flag))
    else:
        g_file = gzip.GzipFile(r'/data/group/800463/日内强势股/log/' + r'StrongStrategy-%s-%s-%s-%s.log.gz' % (_date[:4], _date[4:6], _date[6:8], _file_flag))
    return list(map(lambda x: bytes.decode(x), g_file.readlines()))


lines = get_lines(date, file_flag)
if len(lines) > 0:
    factorTimeCost_df = pd.DataFrame(columns=['date', 'stock', 'factor_timeCost', 'source', 'machine_code'])
    modelPrediction_logtime_df = pd.DataFrame(columns=['date', 'stock', 'model_timeCost', 'modelPrediction_logtime', 'modelPrediction_logtime_show', 'start', 'end', 'source', 'machine_code'])
    startCalculateBy_df = pd.DataFrame(columns=['date', 'stock', 'source', 'startCalculateBy', 'ZTTradeTime', 'systemTimeNow', 'systemTimeZT', 'trigger_timedelay', 'wait_time', 'machine_code'])
    newPlaceOrder = pd.DataFrame(columns=['date', 'stock', 'quantity', 'price', 'logtime', 'systime', 'buyorsell', 'comments', 'SeqID', 'turnNum', 'actionSource', 'machine_code'])
    reachedZTTime_df = pd.DataFrame(columns=['date', 'stock', 'reachedZTTime', 'source', 'factor_values', 'machine_code'])
    OrderInfo_eurjpt_df = pd.DataFrame(columns=['date', 'stock', 'source', 'targetAmt', 'totalOrderAmt', 'singleStockAmtLmt', 'placeType', 'price', 'quantity', 'splitOrderNum', 'machine_code'])
    marketInfo_df = pd.DataFrame(
        columns=['date', 'stock', 'source', 'filledTradeList', 'tradeBuyMap', 'tradeSellMap', 'jhjjTradeBuyMap', 'jhjjTradeSellMap', 'lxjjTradeBuyMap', 'lxjjTradeSellMap', 'lxjjBuyNoSet',
                 'lxjjSellNoSet', 'last1MinTradeList', 'last1MinTradeBuyMap', 'last1MinTradeSellMap', 'fillList', 'lxjjFillList', 'last5SecFillList', 'last30SecFillList', 'last1MinFillList',
                 'last2MinFillList', 'last5MinFillList', 'quoteList', 'machine_code'])
    for line in lines:
        machine_code = line[line.find('[StrongStrategy-algo'):line.find('-n0]')]
        machine_code = machine_code.split('-')[-1]
        if 'INFO  c.h.s.s.StrongTradeExecutor - Order info:' in line and 'orderType=SaturnBuy' not in line and 'placeType=amendMRiskSplitLastShot' not in line and 'placeType=amendSplitLastShot' not in line:
            symbol = line[line.find('symbol=') + len('symbol='):].strip()
            actionSource = line[line.find('actionSource=') + len('actionSource='):line.find(', symbol=')]
            targetAmt = float(line[line.find('targetAmt=') + len('targetAmt='):line.find(', totalOrderAmt=')])
            if 'availableSellQtyInToday' in line:
                totalOrderAmt = float(line[line.find('totalOrderAmt=') + len('totalOrderAmt='):line.find(', availableSellQtyInToday=')])
                singleStockAmtLmt = float(line[line.find('singleStockAmtLmt=') + len('singleStockAmtLmt='):line.find(', highLimitPrice=')])
            else:
                totalOrderAmt = float(line[line.find('totalOrderAmt=') + len('totalOrderAmt='):line.find(', initAmt=')])
                singleStockAmtLmt = float(line[line.find('singleStockAmtLmt=') + len('singleStockAmtLmt='):line.find(', price=')])
            price = float(line[line.find('price=') + len('price='):line.find(', quantity=')])
            quantity = float(line[line.find('quantity=') + len('quantity='):line.find(', splitOrderNum=')])
            splitOrderNum = float(line[line.find('splitOrderNum=') + len('splitOrderNum='):line.find(', actionSource=')])
            placeType = line[line.find('placeType=') + len('placeType='):line.find(', nowPrice=')]
            OrderInfo_eurjpt_df.loc[len(OrderInfo_eurjpt_df)] = [date, symbol, actionSource, targetAmt, totalOrderAmt, singleStockAmtLmt, placeType, price, quantity, splitOrderNum, machine_code]
        if 'Triggered: reachedZTTime=' in line:
            symbol = line[line.find('symbol=') + len('symbol='):]
            symbol = symbol.strip()
            reachedZTTime = line[line.find('reachedZTTime=') + len('reachedZTTime='):line.find(', factor_values=')]
            source = line[line.find('BaseModelManager - ') + len('BaseModelManager - '):line.find(' Triggered: reachedZTTime=')]
            line_short = line[line.find('factor_values={') + len('factor_values={'):line.find('}, symbol=')]
            reachedZTTime_df.loc[len(reachedZTTime_df)] = [date, symbol, reachedZTTime, source, line_short, machine_code]
        elif 'market data stat info:' in line:
            symbol = line[line.find('symbol=') + len('symbol='):].strip()
            line_short = line[line.find('market data stat info: ') + len('market data stat info: '):line.find(', symbol=')]
            contents = re.findall(r'[;|; ]?(.*?)=(\d{1,10})[;|; ]?', line_short)
            source = line[line.find('MarketDataManager - ') + len('MarketDataManager - '):line.find(' market data stat info')]
            marketInfo_df.loc[len(marketInfo_df)] = [date, symbol, source] + [x[1] for x in contents] + [machine_code]
        elif 'startCalculateBy' in line:
            symbol = line[line.find('symbol=') + len('symbol='):].strip()
            source = line[line.find('JupiterAnalyzer - ') + len('JupiterAnalyzer - '):line.find(' startCalculateBy')]
            startCalculateBy = line[line.find('startCalculateBy') + len('startCalculateBy'):line.find(': timecost=')]
            ZTTradeTime = int(line[line.find('ZTTradeTime=') + len('ZTTradeTime='):line.find(', systemTimeNow=')])
            systemTimeNow = int(line[line.find('systemTimeNow=') + len('systemTimeNow='):line.find(', systemTimeZT=')])
            systemTimeZT = int(line[line.find('systemTimeZT=') + len('systemTimeZT='):line.find(', symbol=')])
            trigger_timeDelay = systemTimeZT - ZTTradeTime
            wait_time = systemTimeNow - systemTimeZT
            startCalculateBy_df.loc[len(startCalculateBy_df)] = [date, symbol, source, startCalculateBy, ZTTradeTime, systemTimeNow, systemTimeZT, trigger_timeDelay, wait_time, machine_code]
        elif 'NewOrderPlaced: symbol=' in line:
            symbol = line[line.find('symbol=') + len('symbol='):line.find(', nowDate=')]
            logtime = line[11:line.find(' [StrongStrategy-')]
            systime = float(line[line.find('systemTime=') + len('systemTime='):line.find(', clOrdId=')])
            quantity = float(line[line.find('Quantity=') + len('Quantity='):line.find(', Side=')])
            price = float(line[line.find('Price=') + len('Price='):line.find(', Quantity=')])
            buyorsell = line[line.find('Side=') + len('Side='):line.find(', portfolioNo=')]
            comments = line[line.find('comments=') + len('comments='):line.find(', lastFillIndex=')]
            SeqID = float(line[line.find('SeqID=') + len('SeqID='):line.find(', turnNum=')])
            turnNum = float(line[line.find('turnNum=') + len('turnNum='):line.find(', actionSource=')])
            actionSource = line[line.find('actionSource=') + len('actionSource='):].strip()
            newPlaceOrder.loc[len(newPlaceOrder)] = [date, symbol, quantity, price, logtime, systime, buyorsell, comments, SeqID, turnNum, actionSource, machine_code]
        elif 'Calculate factors:' in line and 'timeCost' in line:
            symbol = line[line.find('symbol=') + len('symbol='):line.find(', timeCost=')]
            timeCost = line[line.find('timeCost=') + len('timeCost='):line.find(', start=')]
            source = line[line.find('JupiterAnalyzer - ') + len('JupiterAnalyzer - '):line.find(' Calculate factors:')]
            factorTimeCost_df.loc[len(factorTimeCost_df)] = [date, symbol, timeCost, source, machine_code]
        elif 'Model prediction:' in line and 'timeCost' in line and 'start=' in line:
            symbol = line[line.find('symbol=') + len('symbol='):line.find(', shouldBuySignal=')]
            timeCost = line[line.find('timeCost=') + len('timeCost='):line.find(', start=')]
            start = float(line[line.find('start=') + len('start='):line.find(', end=')])
            end = float(line[line.find('end=') + len('end='):].strip())
            logtime = line[:line.find(' [StrongStrategy-')]
            logtime_show = int(time.mktime(parse(logtime).timetuple()) * 1000.0 + parse(logtime).microsecond / 1000.0)
            source = line[line.find('JupiterAnalyzer - ') + len('JupiterAnalyzer - '):line.find(' Model prediction:')]
            modelPrediction_logtime_df.loc[len(modelPrediction_logtime_df)] = [date, symbol, timeCost, logtime, logtime_show, start, end, source, machine_code]

    combined_df0 = pd.merge(startCalculateBy_df, reachedZTTime_df, left_on=['date', 'stock', 'source', 'machine_code'], right_on=['date', 'stock', 'source', 'machine_code'], how='left')
    combined_df1 = pd.merge(combined_df0, factorTimeCost_df, left_on=['date', 'stock', 'source', 'machine_code'], right_on=['date', 'stock', 'source', 'machine_code'], how='left')
    combined_df2 = pd.merge(combined_df1, modelPrediction_logtime_df[['date', 'stock', 'source', 'machine_code', 'model_timeCost']], left_on=['date', 'stock', 'source', 'machine_code'],
                            right_on=['date', 'stock', 'source', 'machine_code'], how='left')
    newPlaceOrder_eurjpt = newPlaceOrder[newPlaceOrder['actionSource'].isin(['JupiterNew', 'JupiterN'])]
    newPlaceOrder_eurjpt = newPlaceOrder_eurjpt.groupby(['date', 'stock', 'actionSource', 'machine_code']).head(1)
    newPlaceOrder_eurjpt = newPlaceOrder_eurjpt.rename(columns={'actionSource': 'source', 'systime': 'systimeOrder'})
    combined_df3 = pd.merge(combined_df2, newPlaceOrder_eurjpt[['date', 'stock', 'source', 'machine_code', 'systimeOrder', 'comments', 'SeqID', 'turnNum']],
                            left_on=['date', 'stock', 'source', 'machine_code'], right_on=['date', 'stock', 'source', 'machine_code'], how='left')
    combined_df3[['systemTimeZT', 'factor_timeCost', 'model_timeCost']] = combined_df3[['systemTimeZT', 'factor_timeCost', 'model_timeCost']].astype(float)
    combined_df3['total_time_cost'] = combined_df3['systimeOrder'] - combined_df3['systemTimeZT']
    combined_df3['other_time_cost'] = combined_df3['total_time_cost'] - combined_df3['factor_timeCost'] - combined_df3['model_timeCost']

    combined_df3 = combined_df3.sort_values('ZTTradeTime')
    first_mc_index_eur = combined_df3[combined_df3['source'] == 'JupiterNew'].groupby(['date', 'machine_code']).head(1).index.tolist()
    first_mc_index_jpt = combined_df3[combined_df3['source'] == 'JupiterN'].groupby(['date', 'machine_code']).head(1).index.tolist()
    combined_df3.loc[first_mc_index_eur + first_mc_index_jpt, '是否触发第一笔'] = 1
    combined_df3['是否触发第一笔'].fillna(0, inplace=True)

    first_order_mc_index_eur = combined_df3[combined_df3['source'] == 'JupiterNew'].dropna(subset=['systimeOrder']).groupby(['date', 'machine_code']).head(1).index.tolist()
    first_order_mc_index_jpt = combined_df3[combined_df3['source'] == 'JupiterN'].dropna(subset=['systimeOrder']).groupby(['date', 'machine_code']).head(1).index.tolist()
    combined_df3.loc[first_order_mc_index_eur + first_order_mc_index_jpt, '是否下单第一笔'] = 1
    combined_df3['是否下单第一笔'].fillna(0, inplace=True)

    last_is_zt = pd.read_pickle(r'/data/group/800463/param/factor_param/N_all_factor_zt_merge_%s_v8.pkl' % date)
    last_is_zt = last_is_zt[['last_is_zt']]
    last_is_zt['stock'] = last_is_zt.reset_index()['Ticker'].values
    last_is_zt['date'] = last_is_zt.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
    combined_df4 = pd.merge(combined_df3, last_is_zt, left_on=['date', 'stock'], right_on=['date', 'stock'], how='left')
    combined_df5 = pd.merge(combined_df4, marketInfo_df[['date', 'stock', 'machine_code', 'filledTradeList', 'source']], left_on=['date', 'stock', 'machine_code', 'source'],
                            right_on=['date', 'stock', 'machine_code', 'source'], how='left')
    combined_df5['group'] = combined_df5['machine_code'].replace({'168.62.9.55': 'low_median_96',
                                                                  '168.62.1.38': 'low_median_96',
                                                                  '168.62.1.39': 'low_median_96',
                                                                  '100.69.9.53': 'low_median_48',
                                                                  '100.69.9.54': 'low_median_48',
                                                                  '100.69.9.52': 'down_high_48',
                                                                  '168.62.1.83': 'down_high_48',
                                                                  '168.62.1.80': 'up_high_48',
                                                                  '168.62.1.82': 'up_high_48'})
    print(len(startCalculateBy_df), len(combined_df0), len(combined_df1), len(combined_df2), len(combined_df3), len(newPlaceOrder_eurjpt), len(combined_df4), len(combined_df5))
    if not os.path.exists(r'/data/group/800463/xiely/order-delay/%s-%s/' % (date, file_flag)):
        os.mkdir(r'/data/group/800463/xiely/order-delay/%s-%s/' % (date, file_flag))
    common_path = r'/data/group/800463/xiely/order-delay/%s-%s/' % (date, file_flag)
    factorTimeCost_df.to_pickle(common_path + 'factorTimeCost_df.pkl')
    modelPrediction_logtime_df.to_pickle(common_path + 'modelPrediction_logtime_df.pkl')
    startCalculateBy_df.to_pickle(common_path + 'startCalculateBy_df.pkl')
    newPlaceOrder.to_pickle(common_path + 'newPlaceOrder.pkl')
    reachedZTTime_df.to_pickle(common_path + 'reachedZTTime_df.pkl')
    OrderInfo_eurjpt_df.to_pickle(common_path + 'OrderInfo_eurjpt_df.pkl')
    marketInfo_df.to_pickle(common_path + 'marketInfo_df.pkl')
    combined_df5.to_pickle(common_path + 'combined_df5.pkl')
