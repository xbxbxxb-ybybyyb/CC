# coding: utf-8
# Author：fengchi863
# Date ：2023/11/8 13:22
import sys
sys.path.append('/data/user/015614/Lucien')
import pandas as pd
from itertools import product
from xquant.factordata import FactorData
import datetime as dt
from dataApi.sendInfo import send_message
import os
import time
fd = FactorData()

"""
遇到节假日，需要进行修改代码，修改内容为weekday的范围
"""

# 分配当天的日期和时间
cur_time = int(dt.datetime.now().strftime('%H%M%S'))
cur_date = dt.date.today()
weekday = cur_date.weekday()
if 0 <= weekday <= 4:
    prod_day = True
else:
    prod_day = False

if 81000 < cur_time < 200000:
    prod_time = False
else:
    prod_time = True

if prod_day and prod_time:
    trade_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
else:
    trade_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -2)[0]

# trade_date = '20250909'   # 改成当天的日期即可

metis_path = '/data/group/800463/日内强势股/metis_log_parse/'
leda_path = '/data/group/800463/日内强势股/leda_log_parse/'
cpp_path = '/data/group/800463/日内强势股/cpp_log_parse/'
jupiter_path = '/data/group/800463/日内强势股/jupiter_log_parse/'
jupiterBj_path = '/data/group/800463/日内强势股/jupiterBj_log_parse/'
java_path = '/data/group/800463/日内强势股/log_parse/'
sell_path = '/data/group/800463/日内强势股/sell_log_parse/'
saturn_path = '/data/group/800463/日内强势股/saturn_log_parse/'
ceres_path = '/data/group/800463/日内强势股/ceres_log_parse/'
p4_path = '/data/group/800463/日内强势股/p4_log_parse/'
mimas_path = '/data/group/800463/日内强势股/mimas_log_parse/'

# 理应存在的因子模型及其环境
metis_envirs = ['prod']
leda_envirs = ['prod']
cpp_envirs = ['prod']
jupiter_envirs = ['prod']
jupiterBj_envirs = ['prod']
saturn_envirs = ['prod']
java_envirs = ['prod']
sell_envirs = ['prod']
ceres_envirs = ['prod']
p4_envirs = ['prod']
mimas_envirs = ['prod']

metis_strat = ['Metis']
leda_strat = ['Leda']
cpp_strat = ['New']
jupiter_strat = ['']
jupiterBj_strat = ['Bj']
saturn_strat = ['pj2']
java_strat = ['pj2']
sell_strat = ['JupiterZ']
ceres_strat = ['ceres']
p4_strat = ['p4']
mimas_strat = ['mimas']

metis_tuple = list(product(metis_envirs, metis_strat))
leda_tuple = list(product(leda_envirs, leda_strat))
cpp_tuple = list(product(cpp_envirs, cpp_strat))
jupiter_tuple = list(product(jupiter_envirs, jupiter_strat))
jupiterBj_tuple = list(product(jupiterBj_envirs, jupiterBj_strat))
java_tuple = list(product(java_envirs, java_strat))
saturn_tuple = list(product(saturn_envirs, saturn_strat))
sell_tuple = list(product(sell_envirs, sell_strat))
ceres_tuple = list(product(ceres_envirs, ceres_strat))
p4_tuple = list(product(p4_envirs, p4_strat))
mimas_tuple = list(product(mimas_envirs, mimas_strat))

def search():
    metis_message = 'Metis缺失: '
    leda_message = 'Leda缺失：'
    cpp_message = 'Europa缺失: '
    jupiter_message = 'Jupiter缺失: '
    jupiterBj_message = 'JupiterBj缺失: '
    java_message = 'Java缺失: '
    saturn_message = 'Saturn缺失: '
    sell_message = 'Sell缺失：'
    ceres_message = 'Ceres缺失：'
    p4_message = 'P4缺失：'
    mimas_message = 'Mimas缺失：'
    lost_file_num = 0

    for tup in metis_tuple:
        if not os.path.exists(metis_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_{trade_date}_{tup[0]}_3.xlsx'):
            metis_message += f'factor_{tup[0]}、'
            lost_file_num += 1
        if not os.path.exists(metis_path + f'模型差异/{trade_date}/模型差异{tup[1]}_{trade_date}_{tup[0]}.xlsx'):
            metis_message += f'model_{tup[0]}、'
            lost_file_num += 1

    for tup in leda_tuple:
        if not os.path.exists(leda_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_{trade_date}_{tup[0]}.xlsx'):
            leda_message += f'factor_{tup[0]}、'
            lost_file_num += 1
        if not os.path.exists(leda_path + f'模型差异/{trade_date}/模型差异{tup[1]}_{trade_date}_{tup[0]}.xlsx'):
            leda_message += f'model_{tup[0]}、'
            lost_file_num += 1

    for tup in cpp_tuple:
        if not os.path.exists(cpp_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_{trade_date}_{tup[0]}_3.xlsx'.replace('__', '_')):
            cpp_message += f'factor_{tup[0]}_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(cpp_path + f'模型差异/{trade_date}/模型差异{tup[1]}_{trade_date}_{tup[0]}.xlsx'):
            cpp_message += f'model_{tup[0]}_{tup[1]}、'
            lost_file_num += 1

    for tup in jupiter_tuple:
        if not os.path.exists(jupiter_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_{trade_date}_{tup[0]}_3.xlsx'.replace('__', '_')):
            jupiter_message += f'factor_{tup[0]}_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(jupiter_path + f'模型差异/{trade_date}/模型差异{tup[1]}_{trade_date}_{tup[0]}.xlsx'):
            jupiter_message += f'model_{tup[0]}_{tup[1]}、'
            lost_file_num += 1

    for tup in jupiterBj_tuple:
        if not os.path.exists(jupiterBj_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{trade_date}_{tup[0]}_3.xlsx'.replace('__', '_')):
            jupiterBj_message += f'factor_{tup[0]}_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(jupiterBj_path + f'模型差异/{trade_date}/模型差异_{trade_date}_{tup[0]}.xlsx'):
            jupiterBj_message += f'model_{tup[0]}_{tup[1]}、'
            lost_file_num += 1

    for tup in saturn_tuple:
        if not os.path.exists(saturn_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_931_{trade_date}_{tup[0]}.xlsx'.replace('__', '_')):
            saturn_message += f'factor_{tup[0]}_931_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(saturn_path + f'模型差异/{trade_date}/模型差异_{trade_date}_{tup[0]}_{tup[1]}_931.xlsx'):
            saturn_message += f'model_{tup[0]}_{tup[1]}_931、'
            lost_file_num += 1



    for tup in sell_tuple:
        if not os.path.exists(sell_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_{trade_date}_{tup[0]}.xlsx'.replace('__', '_')):
            sell_message += f'factor_{tup[0]}_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(sell_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_Sell13_931_{trade_date}_{tup[0]}.xlsx'.replace('__', '_')):
            sell_message += f'factor_{tup[0]}_Sell13_931、'
            lost_file_num += 1
        if not os.path.exists(sell_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_Sell13_930_{trade_date}_{tup[0]}.xlsx'.replace('__', '_')):
            sell_message += f'factor_{tup[0]}_Sell13_930、'
            lost_file_num += 1
        if not os.path.exists(sell_path + f'模型差异/{trade_date}/{tup[1]}模型差异_{trade_date}_{tup[0]}.xlsx'):
            sell_message += f'model_{tup[0]}_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(sell_path + f'模型差异/{trade_date}/卖出Sell1模型差异_{trade_date}_{tup[0]}.xlsx'):
            sell_message += f'model_{tup[0]}_Sell1、'
            lost_file_num += 1
    
    for tup in ceres_tuple:
        if not os.path.exists(ceres_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_931_{trade_date}_{tup[0]}.xlsx'.replace('__', '_')):
            ceres_message += f'factor_{tup[0]}_931_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(ceres_path + f'模型差异/{trade_date}/模型差异_{trade_date}_{tup[0]}_{tup[1]}_931.xlsx'):
            ceres_message += f'model_{tup[0]}_{tup[1]}_931、'
            lost_file_num += 1
            
    for tup in p4_tuple:
        if not os.path.exists(p4_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_931_{trade_date}_{tup[0]}.xlsx'.replace('__', '_')):
            p4_message += f'factor_{tup[0]}_931_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(p4_path + f'模型差异/{trade_date}/模型差异_{trade_date}_{tup[0]}_{tup[1]}_931.xlsx'):
            p4_message += f'model_{tup[0]}_{tup[1]}_931、'
            lost_file_num += 1
            
    for tup in mimas_tuple:
        if not os.path.exists(mimas_path + f'因子差异/{trade_date}_{tup[0]}/Factor_diff_{tup[1]}_931_{trade_date}_{tup[0]}.xlsx'.replace('__', '_')):
            mimas_message += f'factor_{tup[0]}_931_{tup[1]}、'
            lost_file_num += 1
        if not os.path.exists(mimas_path + f'模型差异/{trade_date}/模型差异_{trade_date}_{tup[0]}_{tup[1]}.xlsx'):
            mimas_message += f'model_{tup[0]}_{tup[1]}_931、'
            lost_file_num += 1

    message = metis_message + '\n' + leda_message + '\n' + cpp_message + '\n' + saturn_message + '\n' + sell_message + '\n' + jupiter_message + '\n' + jupiterBj_message + \
        ceres_message + '\n' + p4_message + '\n' + mimas_message
    return lost_file_num, message


while True:
    cur_time = int(dt.datetime.now().strftime('%H%M%S'))
    lost_file_num, message = search()
    if lost_file_num == 0:
        # 提醒双姐
        send_message(f'{trade_date}因子和模型对比文件均已生成——发送人：冯炽', ['015614', '003371'])  # 添加发送给双姐的
        # 提醒同事
        send_message(f'{trade_date}因子和模型对比文件均已生成', ['021012', '018107', '013550'])  # 添加发送给其他同事的
        # send_message(f'{trade_date}因子和模型对比文件均以生成——发送人：冯炽', ['015614'])
        print(f'{trade_date}因子和模型对比文件均已生成——发送人：冯炽')
        break
    else:
        time.sleep(60)  # 只有这种情况继续运行，不跳出while循环
        print('尚未生成完整，继续等待')
        if 221501 <= cur_time <= 221600:
            # 提醒同事
            send_message(message + '\n' + f'{trade_date}缺失{lost_file_num}个文件[时间:{cur_time}]', ['015614', '021012', '013550'])
        if 222901 <= cur_time <= 223000:
            # 提醒同事
            send_message(message + '\n' + f'{trade_date}缺失{lost_file_num}个文件[时间:{cur_time}]', ['015614', '021012', '013550'])
        if 72901 <= cur_time <= 73000:
            # 提醒同事
            send_message(message + '\n' + f'{trade_date}缺失{lost_file_num}个文件[时间:{cur_time}]', ['015614', '021012', '013550'])
        print('等待到早晨七点钟，运行结束，仍没有完全生成，发送缺失情况')
        print(message + '\n' + f'缺失{lost_file_num}个文件')