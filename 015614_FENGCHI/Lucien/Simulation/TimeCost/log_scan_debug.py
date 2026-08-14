# coding: utf-8
# Author：fengchi863
# Date ：2023/3/17 9:38

import sys
sys.path.append('/data/user/015614/Lucien')
import pandas as pd
import time
import re
import os
import zipfile
import gzip
import shutil
import pickle
from dateutil.parser import parse
import datetime
from dataApi.sendInfo import send_message
from Simulation.other_log_parse.simlite_dropdup import dropdup
from tqdm import tqdm

udp2machine = {'100.69.9.36': '168.62.9.55',
               '100.69.9.24': '168.62.1.38',
               '100.69.9.47': '168.62.1.80',
               '100.69.9.49': '168.62.1.82',
               '100.69.9.50': '168.62.1.83',
               '100.69.9.52': '168.62.1.84',
               '100.69.9.53': '168.62.1.85',
               '100.69.9.54': '168.62.1.86'
               }
# 168.62.1.39没有对应的UDP

ip_check_dict = {
    'low+medium+half_down_high': [55, 38, 39, 85, 86],
    '': []
}

"""20230329添加，映射关系，作为检查"""
eur_class_dict = pickle.load(open(r'/data/group/800463/xiely/save-file/forFc/log_config/eur_class_dict.pickle','rb'))
jpt_class_dict = pickle.load(open(r'/data/group/800463/xiely/save-file/forFc/log_config/jpt_class_dict.pickle','rb'))

# eur_class_factor_map = pd.read_pickle(r'/data/group/800463/xiely/save-file/forFc/log_config/eur_class_factor_map.pkl')
# jpt_class_factor_map = pd.read_pickle(r'/data/group/800463/xiely/save-file/forFc/log_config/jpt_class_factor_map.pkl')
# eur_class_factor_dict = eur_class_factor_map[['类名', 'factor_name']].set_index('类名').to_dict()['factor_name']
# jpt_class_factor_dict = jpt_class_factor_map[['类名', 'factor_name']].set_index('类名').to_dict()['factor_name']
#
# eur_sp_class = eur_class_dict['sp_class']
# eur_lows_class = eur_class_dict['extre_low_class']+' '+eur_class_dict['first_half_low_class']+' ' + eur_class_dict['second_half_low_class']
# eur_lows_median_class = eur_class_dict['extre_low_class']+' '+eur_class_dict['first_half_low_class']+' ' + eur_class_dict['second_half_low_class']+' ' + eur_class_dict['first_third_median_class']+' ' + eur_class_dict['second_third_median_class']+' ' + eur_class_dict['third_third_median_class']
#
# jpt_sp_class = jpt_class_dict['sp_class']
# jpt_lows_class = jpt_class_dict['extre_low_class']+' '+jpt_class_dict['first_half_low_class']+' ' + jpt_class_dict['second_half_low_class']
# jpt_lows_median_class = jpt_class_dict['extre_low_class']+' '+jpt_class_dict['first_half_low_class']+' ' + jpt_class_dict['second_half_low_class']+' ' + jpt_class_dict['first_third_median_class']+' ' + jpt_class_dict['second_third_median_class']+' ' + jpt_class_dict['third_third_median_class']
#
# eur_zone_dict = {'#300001':eur_sp_class,'#300002':eur_sp_class,'#300003':eur_sp_class,'#300007':eur_sp_class,'#300008':eur_sp_class,\
# '#300004':eur_lows_class,'#300009':eur_lows_class,'#300005':eur_lows_median_class,'#300006':eur_lows_median_class}
#
# jpt_zone_dict = {'#300001':jpt_sp_class,'#300002':jpt_sp_class,'#300003':jpt_sp_class,'#300007':jpt_sp_class,'#300008':jpt_sp_class,\
# '#300004':jpt_lows_class,'#300009':jpt_lows_class,'#300005':jpt_lows_median_class,'#300006':jpt_lows_median_class}

digit2factorSet = {'300001': '168.62.9.55', '300002': '168.62.1.38', '300003': '168.62.1.39', '300004': '168.62.1.82',
                   '300005': '168.62.1.83', '300006': '168.62.1.84', '300007': '168.62.1.85', '300008': '168.62.1.86',
                   '300009': '168.62.1.80'}

# eur_zone_dict = dict([(digit2factorSet[key[1:]], eur_zone_dict[key]) for key in eur_zone_dict.keys()])
# jpt_zone_dict = dict([(digit2factorSet[key[1:]], jpt_zone_dict[key]) for key in jpt_zone_dict.keys()])

date = datetime.datetime.today().strftime('%Y%m%d')
date = 20230330
log_path = f'/data/group/800463/sim-lite-log/{date}/'
output_log_path = '/data/group/800463/xiely/日内强势股/log/'

def unzip_file(fp):
    with zipfile.ZipFile(fp, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(fp))

def get_lines(_date, _file_flag):
    if os.path.exists(output_log_path + r'StrongStrategy-%s-%s-%s-%s.log.gz' % (_date[:4], _date[4:6], _date[6:8], _file_flag)):
        g_file = gzip.GzipFile(output_log_path + r'StrongStrategy-%s-%s-%s-%s.log.gz' % (_date[:4], _date[4:6], _date[6:8], _file_flag))
    else:
        g_file = gzip.GzipFile(r'/data/group/800463/日内强势股/log/' + r'StrongStrategy-%s-%s-%s-%s.log.gz' % (_date[:4], _date[4:6], _date[6:8], _file_flag))
    return list(map(lambda x: bytes.decode(x), g_file.readlines()))

def parse_1log(sim_date, flag):
    lines = get_lines(sim_date, flag)
    create_date = int(flag[-8:])

    # jpt_zone_dict = pd.read_pickle(f'/data/group/800463/xiely/save-file/forFc/daily/jpt_zone_dict_{sim_date}_{create_date}')
    # eur_zone_dict = pd.read_pickle(f'/data/group/800463/xiely/save-file/forFc/daily/eur_zone_dict_{sim_date}_{create_date}')
    # jpt_zone_dict = dict([(digit2factorSet[key[1:]], jpt_zone_dict[key]) for key in jpt_zone_dict.keys()])
    # eur_zone_dict = dict([(digit2factorSet[key[1:]], eur_zone_dict[key]) for key in eur_zone_dict.keys()])

    if len(lines) > 0:
        factorTimeCost_df = pd.DataFrame(columns=['date', 'stock', 'factor_timeCost', 'source', 'machine_code'])
        modelPrediction_logtime_df = pd.DataFrame(columns=['date', 'stock', 'model_timeCost', 'modelPrediction_logtime', 'modelPrediction_logtime_show', 'start', 'end', 'source', 'machine_code'])
        startCalculateBy_df = pd.DataFrame(
            columns=['date', 'stock', 'source', 'startCalculateBy', 'ZTTradeTime', 'systemTimeNow', 'systemTimeZT', 'trigger_timedelay', 'wait_time', 'machine_code'])
        newPlaceOrder = pd.DataFrame(columns=['date', 'stock', 'quantity', 'price', 'logtime', 'systime', 'buyorsell', 'comments', 'SeqID', 'turnNum', 'actionSource', 'machine_code'])
        reachedZTTime_df = pd.DataFrame(columns=['date', 'stock', 'reachedZTTime', 'source', 'factor_values', 'machine_code'])
        OrderInfo_eurjpt_df = pd.DataFrame(
            columns=['date', 'stock', 'source', 'targetAmt', 'totalOrderAmt', 'singleStockAmtLmt', 'placeType', 'price', 'quantity', 'splitOrderNum', 'machine_code'])
        marketInfo_df = pd.DataFrame(
            columns=['date', 'stock', 'source', 'filledTradeList', 'tradeBuyMap', 'tradeSellMap', 'jhjjTradeBuyMap', 'jhjjTradeSellMap', 'lxjjTradeBuyMap', 'lxjjTradeSellMap', 'lxjjBuyNoSet',
                     'lxjjSellNoSet', 'last1MinTradeList', 'last1MinTradeBuyMap', 'last1MinTradeSellMap', 'fillList', 'lxjjFillList', 'last5SecFillList', 'last30SecFillList', 'last1MinFillList',
                     'last2MinFillList', 'last5MinFillList', 'quoteList', 'machine_code'])
        machine_inst_num_dict = dict()
        for line in tqdm(lines):
            machine_code = line[line.find('[StrongStrategy-algo'):line.find('-n0]')]
            machine_code = machine_code.split('-')[-1]
            if 'INFO  c.h.s.s.StrongTradeExecutor - Order info:' in line and 'orderType=SaturnBuy' not in line and 'placeType=amendMRiskSplitLastShot' not in line and 'placeType=amendSplitLastShot' not in line:
                t1 = time.time()
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
                OrderInfo_eurjpt_df.loc[len(OrderInfo_eurjpt_df)] = [sim_date, symbol, actionSource, targetAmt, totalOrderAmt, singleStockAmtLmt, placeType, price, quantity, splitOrderNum,
                                                                     machine_code]
                print('kind1: ', time.time() - t1)
            if 'Triggered: reachedZTTime=' in line:
                t1 = time.time()
                symbol = line[line.find('symbol=') + len('symbol='):]
                symbol = symbol.strip()
                reachedZTTime = line[line.find('reachedZTTime=') + len('reachedZTTime='):line.find(', factor_values=')]
                source = line[line.find('BaseModelManager - ') + len('BaseModelManager - '):line.find(' Triggered: reachedZTTime=')]
                line_short = line[line.find('factor_values={') + len('factor_values={'):line.find('}, symbol=')]
                reachedZTTime_df.loc[len(reachedZTTime_df)] = [sim_date, symbol, reachedZTTime, source, line_short, machine_code]

                """"20230329新增，判断因子集合是否正确"""
                # factor_line = line[line.find('factor_values={') + len('factor_values={'):line.find('}, symbol=')]
                # factor_list = list(map(lambda x: x.split(', ')[1] if ',' in x else x, factor_line.split('=')))
                # factor_list = list(filter(lambda x: not x[0].isdigit(), factor_list))
                # if 'null' in factor_list:
                #     factor_list.remove('null')
                #
                # if len(factor_list) == 211:
                #     continue
                #
                # if machine_code.startswith('100'):
                #     ip_code = udp2machine[machine_code]
                # else:
                #     ip_code = machine_code

                # if 'JupiterN' in line and 'JupiterNew' not in line:
                #     should_factor_list = jpt_zone_dict[ip_code].split(' ')
                #     should_factor_list = ', '.join([jpt_class_factor_dict[clas] for clas in should_factor_list]).split(', ')
                #     if set(should_factor_list) == set(factor_list):
                #         continue
                #     else:
                #         print(f'Error：{flag[-8:]}创建的{sim_date}回放Jupiter因子集合错误')
                # if 'JupiterNew' in line:
                #     should_factor_list = eur_zone_dict[ip_code].split(' ')
                #     should_factor_list = ', '.join([eur_class_factor_dict[clas] for clas in should_factor_list]).split(', ')
                #     if set(should_factor_list) == set(factor_list):
                #         continue
                #     else:
                #         print(f'Error：{flag[-8:]}创建的{sim_date}回放Europa因子集合错误')
                print('kind2: ', time.time() - t1)
            elif 'market data stat info:' in line:
                t1 = time.time()
                symbol = line[line.find('symbol=') + len('symbol='):].strip()
                line_short = line[line.find('market data stat info: ') + len('market data stat info: '):line.find(', symbol=')]
                contents = re.findall(r'[;|; ]?(.*?)=(\d{1,10})[;|; ]?', line_short)
                source = line[line.find('MarketDataManager - ') + len('MarketDataManager - '):line.find(' market data stat info')]
                marketInfo_df.loc[len(marketInfo_df)] = [sim_date, symbol, source] + [x[1] for x in contents] + [machine_code]
                print('kind3: ', time.time() - t1)
            elif 'startCalculateBy' in line:
                t1 = time.time()
                symbol = line[line.find('symbol=') + len('symbol='):].strip()
                source = line[line.find('JupiterAnalyzer - ') + len('JupiterAnalyzer - '):line.find(' startCalculateBy')]
                startCalculateBy = line[line.find('startCalculateBy') + len('startCalculateBy'):line.find(': timecost=')]
                ZTTradeTime = int(line[line.find('ZTTradeTime=') + len('ZTTradeTime='):line.find(', systemTimeNow=')])
                systemTimeNow = int(line[line.find('systemTimeNow=') + len('systemTimeNow='):line.find(', systemTimeZT=')])
                systemTimeZT = int(line[line.find('systemTimeZT=') + len('systemTimeZT='):line.find(', symbol=')])
                trigger_timeDelay = systemTimeZT - ZTTradeTime
                wait_time = systemTimeNow - systemTimeZT
                startCalculateBy_df.loc[len(startCalculateBy_df)] = [sim_date, symbol, source, startCalculateBy, ZTTradeTime, systemTimeNow, systemTimeZT, trigger_timeDelay, wait_time, machine_code]
                print('kind4: ', time.time() - t1)
            elif 'NewOrderPlaced: symbol=' in line:
                t1 = time.time()
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
                newPlaceOrder.loc[len(newPlaceOrder)] = [sim_date, symbol, quantity, price, logtime, systime, buyorsell, comments, SeqID, turnNum, actionSource, machine_code]
                print('kind5: ', time.time() - t1)
            elif 'Calculate factors:' in line and 'timeCost' in line:
                t1 = time.time()
                symbol = line[line.find('symbol=') + len('symbol='):line.find(', timeCost=')]
                timeCost = line[line.find('timeCost=') + len('timeCost='):line.find(', start=')]
                source = line[line.find('JupiterAnalyzer - ') + len('JupiterAnalyzer - '):line.find(' Calculate factors:')]
                factorTimeCost_df.loc[len(factorTimeCost_df)] = [sim_date, symbol, timeCost, source, machine_code]
                print('kind6: ', time.time() - t1)
            elif 'Model prediction:' in line and 'timeCost' in line and 'start=' in line:
                t1 = time.time()
                symbol = line[line.find('symbol=') + len('symbol='):line.find(', shouldBuySignal=')]
                timeCost = line[line.find('timeCost=') + len('timeCost='):line.find(', start=')]
                start = float(line[line.find('start=') + len('start='):line.find(', end=')])
                end = float(line[line.find('end=') + len('end='):].strip())
                logtime = line[:line.find(' [StrongStrategy-')]
                logtime_show = int(time.mktime(parse(logtime).timetuple()) * 1000.0 + parse(logtime).microsecond / 1000.0)
                source = line[line.find('JupiterAnalyzer - ') + len('JupiterAnalyzer - '):line.find(' Model prediction:')]
                modelPrediction_logtime_df.loc[len(modelPrediction_logtime_df)] = [sim_date, symbol, timeCost, logtime, logtime_show, start, end, source, machine_code]
                print('kind7: ', time.time() - t1)
            elif 'Start Success' in line:
                t1 = time.time()
                tag_name = line[line.find('TagDate=') + len('TagDate=') + 9:line.find(' Start Success')]
                if machine_code in machine_inst_num_dict.keys():
                    machine_inst_num_dict[machine_code] += 1
                else:
                    machine_inst_num_dict[machine_code] = 1

                if int(machine_code[-2:]) in ip_check_dict[tag_name]:
                    pass
                elif machine_code in udp2machine.keys() and int(udp2machine[machine_code][-2:]) in ip_check_dict[tag_name]:
                    pass
                else:
                    # print(f'{machine_code}-{tag_name}')
                    pass
                print('kind8: ', time.time() - t1)
            elif 'rejected' in line:
                t1 = time.time()
                print('kind9: ', time.time() - t1)

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

        last_is_zt = pd.read_pickle(r'/data/group/800463/param/factor_param/N_all_factor_zt_merge_%s_v8.pkl' % sim_date)
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

        machine_inst_num_df = pd.DataFrame(pd.Series(machine_inst_num_dict), columns=['inst_num'])

        print(len(startCalculateBy_df), len(combined_df0), len(combined_df1), len(combined_df2), len(combined_df3), len(newPlaceOrder_eurjpt), len(combined_df4), len(combined_df5))
        if not os.path.exists(r'/data/group/800463/xiely/order-delay/%s-%s/' % (sim_date, flag)):
            os.mkdir(r'/data/group/800463/xiely/order-delay/%s-%s/' % (sim_date, flag))
        common_path = r'/data/group/800463/xiely/order-delay/%s-%s/' % (sim_date, flag)
        factorTimeCost_df.to_pickle(common_path + 'factorTimeCost_df.pkl')
        modelPrediction_logtime_df.to_pickle(common_path + 'modelPrediction_logtime_df.pkl')
        startCalculateBy_df.to_pickle(common_path + 'startCalculateBy_df.pkl')
        newPlaceOrder.to_pickle(common_path + 'newPlaceOrder.pkl')
        reachedZTTime_df.to_pickle(common_path + 'reachedZTTime_df.pkl')
        OrderInfo_eurjpt_df.to_pickle(common_path + 'OrderInfo_eurjpt_df.pkl')
        marketInfo_df.to_pickle(common_path + 'marketInfo_df.pkl')
        combined_df5.to_pickle(common_path + 'combined_df5.pkl')
        machine_inst_num_df.to_pickle(common_path + 'machine_inst_num_df.pkl')

log_file_cache = list()
# parse_1log('20230307', f'uat_lite-20230328')  # 测试用
while True:
    # time.sleep(60)

    cur_time = datetime.datetime.now().strftime('%H%M%S')
    cur_time = int(cur_time)
    # if cur_time >= 235800:
    #     break
    filename_list = list()

    if not os.path.exists(log_path):
        continue

    if os.listdir(log_path):
        filename_list = os.listdir(log_path)

    for filename in filename_list:
        # 不重复运行
        if filename not in log_file_cache:
            log_file_cache.append(filename)
        else:
            print(f'等待新的仿真日志中...{cur_time}')
            continue

        # 临时过滤一部分文件
        if filename.startswith('StrongStrategy-20230321') or filename.startswith('StrongStrategy-20230322'):
            continue

        # 步骤1：
        if filename.endswith('.zip'):
            print(filename)
            sim_date = filename.split('-')[1]
            create_date = filename.split('-')[2][:8]
            unzip_file(log_path + filename)
            for filename2 in os.listdir(log_path):
                if '.log.gz' in filename2:
                    shutil.copy(log_path + filename2, output_log_path + r'StrongStrategy-%s-%s-%s-%s-%s.log.gz' % (sim_date[:4], sim_date[4:6], sim_date[6:8], 'uat_lite', create_date))
                    os.remove(log_path + filename2)
                    os.remove(log_path + 'StrongStrategy-%s.zip' % sim_date)

            # 步骤2：
            parse_1log(sim_date, f'uat_lite-{create_date}')
            print(f'解析完成{sim_date}仿真日志')
            send_message(f'解析完成{sim_date}仿真日志')

            # dropdup(output_log_path + f'StrongStrategy-%s-%s-%s-uat_lite-%s.log.gz' % (sim_date[:4], sim_date[4:6], sim_date[6:8], create_date))

