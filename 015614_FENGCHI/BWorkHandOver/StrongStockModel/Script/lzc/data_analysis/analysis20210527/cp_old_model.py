# @Time : 2021/5/27 19:28
# @Author : Zhichen Lu
# @File : cp_old_model.py
from online_conf import local_config_path,model_config_path
import os,shutil

os.listdir(model_config_path)
shutil.copy(f'{model_config_path}model_conf20210518.pkl',f'{model_config_path}model_conf20210527.pkl')
# shutil.copy('')
shutil.copy('/data/group/800319/strategy_local_path3/',)