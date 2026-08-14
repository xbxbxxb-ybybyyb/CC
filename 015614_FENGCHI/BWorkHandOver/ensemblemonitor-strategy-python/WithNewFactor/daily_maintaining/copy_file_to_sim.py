# @Time : 2021/5/16 13:10
# @Author : Zhichen Lu
# @File : copy_file_to_sim.py
import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from online_conf import local_config_path,vol_info_path,hyper_param_path
import shutil
from dataApi.tradeDate import get_pre_trade_date

def get_path_conf(local_config_p):
    path_conf = dict(
    # 当日收盘持仓信息(持仓量、第一次买入信息、可交易量)
        local_config_path=local_config_p,
    holding_info_path =local_config_p + 'holding_info/',
    # 当日收盘持仓股的买入时间
    buy_time_info_path =local_config_p + 'buy_time_info/',
    # 超参数(均值、标准差)，日期为T-1日，参数用于T日
    hyper_param_path =local_config_p + 'factor_hyper_param/',
    # T-1日计算出用于T日的股票池，名字为T-1日
    code_list_path =local_config_p + 'code_list/',
    # 模型配置文件，文件名为模型更新的日期
    model_config_path =local_config_p + 'model_conf/',
    # 模型文件保存路径
    model_path =local_config_p + 'model/',
    # 每天策略初始化参数路径
    init_conf_path =local_config_p + 'daily_init_config/',
    # 每天输出路径
    daily_out_path =local_config_p + 'daily_output/',
    # 每天输出路径
    daily_out_path_offline =local_config_p + 'daily_output_offline/',
    # 算法交易比例路径,文件名为文件计算日期
    alog_trading_distr_path =local_config_p + 'algo_trading_distr/',
    #
    vol_info_path =local_config_p + 'vol_info/',
    restrict_list_path =local_config_p + 'restrict_list/',
        path_for_930=local_config_p + 'FolderFor930/',
        sub_output_path=local_config_p + 'daily_output/out_930/',
        ratio_path=f'{local_config_p}ratio/',
    )
    return path_conf

if __name__ == '__main__':
    import datetime
    from dataApi.sendInfo import send_message
    import os
    import traceback
    today = int(datetime.date.today().strftime('%Y%m%d'))
    date = get_pre_trade_date(today)
    try:
        path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForMixSim/')
        if os.path.exists(f'{vol_info_path}{date}_backup.pkl'):
            shutil.copy(f'{vol_info_path}{date}_backup.pkl',path_conf['vol_info_path']+f'{date}.pkl')
        else:
            shutil.copy(f'{vol_info_path}{date}.pkl', path_conf['vol_info_path'] + f'{date}.pkl')
        shutil.copy(f'{hyper_param_path}std{date}.pkl',path_conf['hyper_param_path']+f'std{date}.pkl')
        shutil.copy(f'{hyper_param_path}mean{date}.pkl',path_conf['hyper_param_path']+f'mean{date}.pkl')
        shutil.copy(f'{local_config_path}morning_model/val_sign/{get_pre_trade_date(date,-1)}.pkl',
                    path_conf['local_config_path']+f'morning_model/val_sign/{get_pre_trade_date(date,-1)}.pkl')
        send_message(['015664'],'仿真所需文件拷贝完成')
    except:
        send_message(['015664'],'拷贝仿真所需文件失败')
        print(traceback.format_exc())
        send_message(['015664'],traceback.format_exc())