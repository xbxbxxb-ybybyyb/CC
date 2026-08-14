# @Time : 2021/4/1 16:23
# @Author : Zhichen Lu
# @File : Copy2XtraderTest.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
from xquant.xqutils import utils
from online_conf import local_config_path,init_conf_path,model_config_path
utils.copy2XTrader('/data/group/800319/strategy_local_path3_for_sim20210721/',md5_check=False)

print('/data/group/800319/strategy_local_path3_for_sim20210721/')



