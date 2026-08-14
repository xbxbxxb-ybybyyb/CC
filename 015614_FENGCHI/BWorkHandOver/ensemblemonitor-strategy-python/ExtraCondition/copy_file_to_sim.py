# @Time : 2021/5/16 13:10
# @Author : Zhichen Lu
# @File : copy_file_to_sim.py
import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from online_conf import local_config_path,vol_info_path,hyper_param_path,matrix_conf
import shutil
from dataApi.tradeDate import get_pre_trade_date
from ExtraTools import get_path_conf

if __name__ == '__main__':
    import datetime
    from dataApi.sendInfo import send_message
    import os
    import traceback
    today = int(datetime.date.today().strftime('%Y%m%d'))
    date = get_pre_trade_date(today)
    try:
        path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForExtraSim/')
        if os.path.exists(f'{vol_info_path}{date}_backup.pkl'):
            shutil.copy(f'{vol_info_path}{date}_backup.pkl',path_conf['vol_info_path']+f'{date}.pkl')
        else:
            shutil.copy(f'{vol_info_path}{date}.pkl', path_conf['vol_info_path'] + f'{date}.pkl')

        shutil.copy(f'{hyper_param_path}std{date}.pkl',path_conf['hyper_param_path']+f'std{date}.pkl')
        shutil.copy(f'{hyper_param_path}mean{date}.pkl',path_conf['hyper_param_path']+f'mean{date}.pkl')
        shutil.copy(f'{local_config_path}morning_model/val_sign/{get_pre_trade_date(date,-1)}.pkl',
                    path_conf['local_config_path']+f'morning_model/val_sign/{get_pre_trade_date(date,-1)}.pkl')
        shutil.copy(f'{matrix_conf}{date}.pkl', path_conf['matrix_conf'] + f'{date}.pkl')
        send_message(['015664'],'仿真所需文件拷贝完成')
    except:
        send_message(['015664'],'拷贝仿真所需文件失败')
        print(traceback.format_exc())
        send_message(['015664'],traceback.format_exc())