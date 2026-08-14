import os
import sys
import datetime as dt

from xquant.factordata import FactorData
s = FactorData()
trade_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
# trade_date = '20231023'   # 如果想要重新跑某一天的成交记录，直接改这里即可

os.chdir('/data/user/015614/Lucien/')

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/0.concat_java_cpp.py {trade_date}') # 拼接java和cpp程序

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/1.sell_record_generate.py {trade_date}')   # 总卖出记录生成

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-1.label_summary_pj2.py {trade_date}') # 实盘触发项目二标签汇总

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-2.label_summary_pj2_931.py {trade_date}')   # 实盘触发项目二931标签汇总

#os.system('python3 /data/user/015614/Lucien/ProdWork/intra_strong/calESRate-v7_1.py')

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-3.label_summary_jup.py {trade_date}') # 生成实盘触发标签汇总

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-4.label_summary_eur.py {trade_date}')  # 实盘触发标签汇总New

# os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-5.label_summary_metis.py {trade_date}')  # 实盘触发标签汇总New

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/3.buy_record_generate.py {trade_date}') # 总买入记录

#os.system('python3 /data/user/015614/Lucien/ProdWork/intra_strong/run_daily_record.py')