import os
import sys
import datetime as dt
import subprocess
import time

from xquant.factordata import FactorData
s = FactorData()
trade_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
# trade_date = '20250528'   # 如果想要重新跑某一天的成交记录，直接改这里即可

os.chdir('/data/user/015614/Lucien/')

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/0.concat_java_cpp.py {trade_date}') # 拼接java和cpp程序

# 获取返回信息，判断是否进入下一步
os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/0-1.calc_label_pattern.py {trade_date}')
while True:
    cmd = f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/0-1.calc_label_pattern.py {trade_date}'
    subp = subprocess.Popen(cmd, encoding='utf-8', shell=True, stdout=subprocess.PIPE)
    out, err = subp.communicate()   # 获得了程序中的所有输出

    success_flag = 0
    for line in out.splitlines():
        if '所有形态数据均以计算完成并保存' in line:
            success_flag = 1
    if success_flag:
        break
    else:
        time.sleep(300)


os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/update/0-1.calc_md_data.py {trade_date}')

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/1.sell_record_generate.py {trade_date}') # 总卖出记录，大约不到3分钟

program2_list = [f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-2.label_summary_pj2_931.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-3.label_summary_jup.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-4.label_summary_eur.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-5.label_summary_metis.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/2-6.label_summary_leda.py {trade_date}',
                 ]

processes = [subprocess.Popen(program, shell=True) for program in program2_list]    # 都在1分钟之内
for process in processes:
    process.wait()

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/3.buy_record_generate.py {trade_date}') # 总买入记录，大约3-5分钟

#os.system('python3 /data/user/015614/Lucien/ProdWork/intra_strong/run_daily_record.py')

#%% 原来在第二个文件，看看能否在一个里面运行
from shutil import copyfile
copyfile('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/ceres成交记录-20230214.xlsx',
             '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/ceres成交记录-%s.xlsx' % trade_date)

program5_list = [
    f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-1.sat_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-2.jup_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-3.eur_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-4.metis_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/5-5.leda_record_generate.py {trade_date}',
                 ]

processes = [subprocess.Popen(program, shell=True) for program in program5_list]
for process in processes:
    process.wait()