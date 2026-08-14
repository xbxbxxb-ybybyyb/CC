# @Time : 2021/3/1 19:44
# @Author : Zhichen Lu
# @File : stk_list_update.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
import pandas as pd
# from online_conf import code_list_path, holding_info_path, local_config_path, path_for_930
import shutil, os
from dataApi.getData import get_pre_trade_date
import datetime
from xquant.xqutils.helper import link
import ftplib
import traceback
import requests, json
from dataApi.sendInfo import send_message
from online_conf import non_fix_path,non_fix_930_path
from ExtraTools import get_nonfix_in_val



# def upload(file_name, out_file_name):
#     ftp = ftplib.FTP()
#     ftp.encoding = 'gbk'
#     ftp.connect('168.8.2.68')
#     ftp.login(user='xquant', passwd='Xquant-32')
#     ftp.cwd('XQuant')
#     ftp.cwd('011477')
#     try:
#         ftp.mkd(f'{date}')
#     except:
#         pass
#     ftp.cwd(f'{date}')
#     try:
#         ftp.mkd(f'EnsembleMonitor_{date}')
#     except:
#         pass
#     ftp.cwd(f'EnsembleMonitor_{date}')
#     print('登陆成功')
#     fp = open(file_name, 'rb')
#     buf_size = 4096
#     ftp.storbinary("STOR {}".format(out_file_name), fp, buf_size)
#     fp.close()
#     ftp.quit()
#     print('上传成功')


lm = link.LinkMessage()
date = int(datetime.date.today().strftime('%Y%m%d'))
pre_date = get_pre_trade_date(date)
account = 201001
if not os.path.exists(f'/data/user/011477/Trade_Docs/{date}/'):
    os.mkdir(f'/data/user/011477/Trade_Docs/{date}/')
if not os.path.exists(f'/data/user/011477/Trade_Docs/{date}/EnsembleMonitor_{date}/'):
    os.mkdir(f'/data/user/011477/Trade_Docs/{date}/EnsembleMonitor_{date}/')

# if os.path.exists(f'/data/user/666888/Makalu/parameters/EnsembleMonitor/EnsembleMonitor_{date}.zip'):
#     shutil.copy(f'/data/user/666888/Makalu/parameters/EnsembleMonitor/EnsembleMonitor_{date}.zip',
#                 f'/data/user/011477/Trade_Docs/{date}/EnsembleMonitor_{date}/EnsembleMonitor_{date}.zip')
#     try:
#         upload(f'/data/user/666888/Makalu/parameters/EnsembleMonitor/EnsembleMonitor_{date}.zip', f'EnsembleMonitor_{date}.zip')
#     except:
#         send_message(['015664'], f'{date}参数传送失败')
#     send_message(['015664'], f'{date}调仓策略拷贝成功')
# else:
#     send_message(['015664', '015390'], f'EnsembleMonitor{date}调仓参数未生成！！！！！！！')
os.system('cp -r /data/group/800319/strategy_local_path3/morning_model/*  /data/group/800319/strategy_local_path_nonfix/morning_model/')
try:
    source_path = '/data/group/800442/800319/strategy_local_path/code_list_no688/'
    import time

    while True:
        if os.path.exists(f'{source_path}{pre_date}.pkl') or os.path.exists(f'{non_fix_path}daily_input_path/{date}/code_list{pre_date}.pkl'):
            break
        else:
            send_message(['015664'], '股票池未更新')
            time.sleep(120)
            continue
    if os.path.exists(f'{source_path}{pre_date}.pkl') or os.path.exists(f'{non_fix_path}daily_input/{date}/code_list{pre_date}.pkl'):
        if not os.path.exists(f'{non_fix_path}daily_input/{date}/code_list{pre_date}.pkl'):
            shutil.copy(f'{source_path}{pre_date}.pkl', f'{non_fix_path}daily_input/{date}/code_list{pre_date}.pkl')
            print('copied')
        else:
            print('exist code list')
    else:
        raise Exception('No code list')

    code_list = get_nonfix_in_val('code_list',date,non_fix_path)
    holding_info = get_nonfix_in_val('holding_info',date,non_fix_path)
    if os.path.exists(f'{non_fix_930_path}{pre_date}/StrategyOut/holding{pre_date}.pkl'):
        holding_930 = pd.read_pickle(f'{non_fix_930_path}{pre_date}/StrategyOut/holding{pre_date}.pkl')
    else:
        holding_930 = {'cash': 0}
        send_message(['015664'],'生成组合文件时930没有前一日持仓')
    if os.path.exists(f'{non_fix_path}morning_model/val_sign/{date}.pkl'):
        signal_930 = pd.read_pickle(f'{non_fix_path}morning_model/val_sign/{date}.pkl')
        lm.sendMessage(f'组合文件930信号数:{len(signal_930)}')
    else:
        signal_930 = pd.Series()
        lm.sendMessage('生成组合文件时930信号未生成')
    _ = holding_930.pop('cash')
    _ = holding_info.pop('cash')
    code_list = sorted(list(set(code_list).union({x for x in holding_info.keys()}).union(set(holding_930.keys())).union(set(signal_930.index.tolist()))))

    portfolio_file = pd.DataFrame({
        '买入交易账户': account,
        '卖出交易账户': account,
        # '买入证券账户':5160503,
        # '卖出证券账户':5160503,
        '买入证券数量': 10000000,
        '卖出证券数量': pd.Series(holding_info).reindex(code_list).fillna(0) + pd.Series(holding_930).reindex(code_list).fillna(0)
    }, index=code_list).reset_index().rename(columns={'index': '证券代码'})
    portfolio_file['卖出证券数量'] = portfolio_file['卖出证券数量'].fillna(0)
    if not os.path.exists(f'/{non_fix_path}/portfolio_file/{date}/'):
        os.makedirs(f'/{non_fix_path}/portfolio_file/{date}/')
    portfolio_file.to_excel(f'/{non_fix_path}/portfolio_file/{date}/EMPortFile{date}_{account}.xlsx')

    # portfolio_file.to_excel(f'/data/user/011477/Trade_Docs/{date}/EnsembleMonitor_{date}/EnsembleMonitor_{date}_{account}.xlsx')
    # upload(f'/data/user/011477/Trade_Docs/{date}/EnsembleMonitor_{date}/EnsembleMonitor_{date}_{account}.xlsx', f'EnsembleMonitor_{date}_{account}.xlsx')
    lm.sendMessage(f'交易组合生成成功{account}----------------{len(code_list)}')
except:
    lm.sendMessage('交易组合生成失败！！！！！！！！！！！！')
    info = traceback.format_exc()
    print(info)
    lm.sendMessage(info)
