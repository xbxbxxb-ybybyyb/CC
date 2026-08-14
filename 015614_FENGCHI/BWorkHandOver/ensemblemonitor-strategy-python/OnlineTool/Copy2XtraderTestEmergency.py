# @Time : 2021/4/1 16:23
# @Author : Zhichen Lu
# @File : Copy2XtraderTest.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
from xquant.xqutils import utils
from online_conf import local_config_path,init_conf_path,model_config_path,code_list_path,holding_info_path,path_for_930,condition_path
import pandas as pd
import shutil


# shutil.copy(f'{code_list_path}20211230.pkl',f'{code_list_path}20211231.pkl')
# shutil.copy(f'/data/group/800442/800319/strategy_local_path/code_list_no688/20211230.pkl',
#             '/data/group/800442/800319/strategy_local_path/code_list_no688/20211231.pkl')
# shutil.copy(f'{local_config_path}morning_model/val_sign/{20211231}.pkl',
#             f'{local_config_path}morning_model/val_sign/{20220104}.pkl')

# date = 20210827
# code_list = pd.read_pickle(f'{code_list_path}{date}.pkl')
# # # '600338.SH' in code_list
# code_list.remove('603396.SH')
# pd.to_pickle(code_list,f'{code_list_path}{date}.pkl')

# utils.copy2XTrader(code_list_path,md5_check=False)


# utils.copy2XTrader('/data/group/800319/strategy_local_path3/FolderFor930/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/model_conf/20220602/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/factor_hyper_param/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/morning_model/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/code_list/',md5_check=False)
# utils.copy2XTrader('/data/group/800319/strategy_local_path3/ratio/',md5_check=False)
# utils.copy2XTrader('/data/group/800319/strategy_local_path3/daily_init_config/',md5_check=False)
# utils.copy2XTrader('/data/group/800319/strategy_local_path3/holding_info/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/daily_init_config/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/FolderFor930/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/vol_info/',md5_check=False)


utils.copy2XTrader('/data/group/800319/strategy_local_path3/index_map.pkl',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/condition/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/vol_info/',md5_check=False)
utils.copy2XTrader('/data/group/800319/strategy_local_path3/FolderFor930/20211214/',md5_check=False)
# utils.copy2XTrader('/data/group/800319/strategy_local_path3/morning_model/val_sign/',md5_check=False)
# utils.copy2XTrader('/data/group/800319/strategy_local_path3//FolderFor930/20211013/',md5_check=False)
# utils.copy2XTrader(f'{local_config_path}morning_model/val_sign/', md5_check=False)
# utils.copy2XTrader(init_conf_path, md5_check=False)
# utils.copy2XTrader(model_config_path, md5_check=False)
# utils.copy2XTrader(local_config_path+'using_fix_list.pkl',md5_check=False)




