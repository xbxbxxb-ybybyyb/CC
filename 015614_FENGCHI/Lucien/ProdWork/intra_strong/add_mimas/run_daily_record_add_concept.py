import os
os.chdir('/data/user/015614/Lucien/')
import time
import subprocess
import datetime as dt
from shutil import copyfile

if __name__ == "__main__":

    from xquant.factordata import FactorData

    s = FactorData()
    trade_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
    # trade_date = '20240301'   # 如果想要重新跑某一天的成交记录，直接改这里即可

    copyfile('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/ceres成交记录-20230214.xlsx',
             '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/ceres成交记录-%s.xlsx' % trade_date)

    os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/3.buy_record_generate.py {trade_date}')  # 总买入记录，这个添加了概念

    program5_list = [f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-1.sat_record_generate.py {trade_date}',
                     f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-2.jup_record_generate.py {trade_date}',
                     f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-3.eur_record_generate.py {trade_date}',
                     f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-4.metis_record_generate.py {trade_date}',
                     ]

    processes = [subprocess.Popen(program, shell=True) for program in program5_list]
    for process in processes:
        process.wait()

