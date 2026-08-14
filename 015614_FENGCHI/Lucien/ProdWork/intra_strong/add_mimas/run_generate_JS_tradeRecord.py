import os
import sys
import datetime as dt
import subprocess
import time

from xquant.factordata import FactorData
s = FactorData()
trade_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
# trade_date = '20250905'   # 如果想要重新跑某一天的成交记录，直接改这里即可

os.chdir('/data/user/015614/Lucien/')

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/0.concat_java_cpp.py {trade_date}') # 拼接java和cpp程序

# 获取返回信息，判断是否进入下一步
os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/0-1.calc_label_pattern.py {trade_date}')
while True:
    cmd = f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/0-1.calc_label_pattern.py {trade_date}'
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


os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/0-2.calc_md_data.py {trade_date}')

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/1.sell_record_generate.py {trade_date}') # 总卖出记录，大约不到3分钟

program2_list = [f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-2.label_summary_pj2_931.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-3.label_summary_jup.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-4.label_summary_eur.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-5.label_summary_metis.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-6.label_summary_leda.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-7.label_summary_ceres.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-8.label_summary_p4.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/2-9.label_summary_mimas.py {trade_date}',
                 ]

processes = [subprocess.Popen(program, shell=True) for program in program2_list]    # 都在1分钟之内
for process in processes:
    process.wait()

os.system(f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/3.buy_record_generate.py {trade_date}') # 总买入记录，大约3-5分钟

program5_list = [
    f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-1.sat_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-2.jup_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-3.eur_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-4.metis_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-5.leda_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-6.ceres_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-7.p4_record_generate.py {trade_date}',
                 f'python3 /data/user/015614/Lucien/ProdWork/intra_strong/add_mimas/5-8.mimas_record_generate.py {trade_date}',
                 ]

processes = [subprocess.Popen(program, shell=True) for program in program5_list]
for process in processes:
    process.wait()