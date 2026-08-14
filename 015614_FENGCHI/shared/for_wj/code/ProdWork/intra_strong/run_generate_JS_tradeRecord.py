import os
import sys
import datetime as dt

from xquant.factordata import FactorData
s = FactorData()
trade_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
# trade_date = '20230607'   # 如果想要重新跑某一天的成交记录，直接改这里即可

os.chdir('/data/user/015614/Lucien/')

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v2_1.py {trade_date}')   # 总卖出记录生成

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v5.py {trade_date}') # 实盘触发项目二标签汇总

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v5_2.py {trade_date}')   # 实盘触发项目二931标签汇总

#os.system('python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v7_1.py')


import time
import datetime as dt

target_time = 173000
while True:
     now_time = dt.datetime.now()
     now_time_int = int(now_time.strftime('%H%M%S'))
     now_time_str = now_time.strftime('%H:%M:%S')
     print(now_time_str)
     if now_time_int >= target_time:
            now_time = dt.datetime.now().strftime('%H:%M:%S')
            print('now time:%s'%(now_time), ': start running v1:')
                        
            break
     else:
            time.sleep(1)

print('now time:%s' % (dt.datetime.now().strftime('%H:%M:%S')))
os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v1.py {trade_date}') # 生成实盘触发标签汇总

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v1New.py {trade_date}')  # 实盘触发标签汇总New

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v3_2.py {trade_date}') # 总买入记录

#os.system('python3 /data/user/015614/Lucien/ProdWork/intra_strong/run_daily_record.py')