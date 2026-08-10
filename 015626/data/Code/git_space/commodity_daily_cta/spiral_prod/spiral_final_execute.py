import sched
import time, datetime
import pandas as pd
import os
import subprocess
from xquant.investment.strategyfile import *

def scheduler(func, target_trigger_time, delay=0):
    # init func at given time with delay as in milliseconds
    assert isinstance(target_trigger_time, pd.Timedelta)
    assert callable(func)
    target_trigger_time = (pd.Timestamp(pd.Timestamp.now().date()) + target_trigger_time).to_pydatetime().timestamp() + delay / 1000
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(target_trigger_time, 0, func)
    s.run(blocking=True)

def final_funcs():
    current_dir = os.path.dirname(__file__)
    print(os.listdir(current_dir))
    script_path = os.path.join(current_dir, 'spiral.py')
    subprocess.run(['python3', script_path])

def set_755_permission(path):
    for root, dirs, files in os.walk(path):
        # 设置目录权限为 755
        for d in dirs:
            dir_path = os.path.join(root, d)
            os.chmod(dir_path, 0o755)
            
is_prod = True
current_date = datetime.datetime.now().strftime('%Y%m%d')
    
udp_para_rootpath = '/data/user/015626/data/share/para/Spiral/Spiral_udp/'
set_755_permission(udp_para_rootpath)

if is_prod:
    # 后台
    upload_gccstrategy_file(strategy_id = "Spiral_udp", strategy_date = str(current_date),
                         upload_file_path=udp_para_rootpath,  is_stop=False, is_tradingsession=True)
    # 前台
    upload_strategy_file(strategy_id = "Spiral_udp", strategy_date = str(current_date), file_type = 1, 
                    upload_file_path = os.path.join(udp_para_rootpath, 'prod_front_spiral-udp-config#801101.json'), is_delete=False,  is_ready=1, disable_instance_validation=0, max_instance=1)            
else:
    # 后台
    sim_upload_gccstrategy_file(strategy_id = "Spiral_udp", strategy_date = str(current_date),
                         upload_file_path=udp_para_rootpath, is_tradingsession=True)
    # 前台
    sim_upload_strategy_file(strategy_id = "Spiral_udp", strategy_date = str(current_date), file_type = 1, 
                    upload_file_path = os.path.join(udp_para_rootpath, 'sim_front_spiral-udp-config#304301.json'), is_delete=False,  is_ready=1)        

print('spiral final execute 启动成功')
scheduler(final_funcs, pd.Timedelta(hours=14, minutes=55), delay=2000)