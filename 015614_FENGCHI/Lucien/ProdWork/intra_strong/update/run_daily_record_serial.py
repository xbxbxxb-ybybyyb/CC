import os
os.chdir('/data/user/015614/Lucien/')
import time
import datetime as dt
from shutil import copyfile

if __name__ == "__main__":

    from xquant.factordata import FactorData

    s = FactorData()
    trade_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
    # trade_date = '20231023'   # 如果想要重新跑某一天的成交记录，直接改这里即可

    target_time = 170000
    while True:
        now_time = dt.datetime.now()
        now_time_int = int(now_time.strftime('%H%M%S'))
        now_time_str = now_time.strftime('%H:%M:%S')
        print(now_time_str)
        if now_time_int >= target_time:
            now_time = dt.datetime.now().strftime('%H:%M:%S')
            print('now time:%s' % now_time, ': start running v4:')
            break
        else:
            time.sleep(1)

    copyfile('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/ceres成交记录-20230214.xlsx',
             '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/ceres成交记录-%s.xlsx' % trade_date)

    cmd = f"python3 /data/user/015614/Lucien/ProdWork/intra_strong/4-1.plot_jup.py {trade_date}"  # 成交画图
    os.system(cmd)

    cmd = f"python3 /data/user/015614/Lucien/ProdWork/intra_strong/4-2.plot_eur.py {trade_date}"   # 成交画图New europa的
    os.system(cmd)

    cmd = f"python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-1.sat_record_generate.py {trade_date}"  # saturn成交记录
    os.system(cmd)

    cmd = f"python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-2.jup_record_generate.py {trade_date}"  # jupiter成交记录
    os.system(cmd)

    cmd = f"python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-3.eur_record_generate.py {trade_date}"   # Europa成交记录
    os.system(cmd)

