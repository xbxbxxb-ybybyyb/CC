# @Time : 2021/4/1 16:23
# @Author : Zhichen Lu
# @File : Copy2XtraderTest.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
from xquant.xqutils import utils
import os
import datetime
from dataApi.tradeDate import get_pre_trade_date
from xquant.xqutils.helper import link
from ApplicationMixFactorAndMatrixIntegration import Application
from online_conf import local_config_path
import traceback
import time
import shutil
import pandas as pd

lm = link.LinkMessage()

date = int(datetime.date.today().strftime('%Y%m%d'))
pre_date = get_pre_trade_date(date)
if local_config_path != '/data/group/800319/strategy_local_path3/':
    lm.sendMessage('文件夹初始化错误')
    raise Exception('文件夹初始化错误')
#############
if not os.path.exists(f'{local_config_path}morning_model/val_sign/{date}.pkl'):
    lm.sendMessage('930文件在拷贝时未生成，请查验')
else:
    if not os.path.exists(f'{local_config_path}morning_model/val_sign_backup/{date}.pkl'):
        shutil.copy(f'{local_config_path}morning_model/val_sign/{date}.pkl',f'{local_config_path}morning_model/val_sign_backup/{date}.pkl')
# pd.to_pickle(pd.Series([]),f'{local_config_path}morning_model/val_sign/{date}.pkl')
################
print(1)
# app = Application(date=date)
# lm.sendMessage(f'930信号数量:{len(app.app930.signal)}, 930持仓数量: {len(app.app930.holding)}')
a=0
while True:
    try:
        app = Application(date=date)
        lm.sendMessage(f'930信号数量:{len(app.app930.signal)}, 930持仓数量: {len(app.app930.holding)}')
        app.get_first_target_plan()
        break
    except:

        if a ==0:
            info = traceback.format_exc()
            print(info)
            lm.sendMessage(info)
        else:
            lm.sendMessage('拷贝失败')
        # raise Exception(info)
        a += 1
        time.sleep(120)
print(local_config_path)
utils.copy2XTrader(local_config_path, md5_check=False)
lm.sendMessage('%s 文件夹已成功拷贝'%local_config_path)
app = Application(date)
lm.sendMessage(f'二次验证成功，930信号数：{len(app.app930.signal)}')
# utils.copy2sim('/data/group/800319/strategy_local_path3/','/data/group/800319/strategy_local_path3/')