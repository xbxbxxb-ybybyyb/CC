import sys
sys.path.insert(4,'/data/user/015626/data/share/Code/for_lym/')

import importlib
importlib.import_module('generate_prod_para')
importlib.import_module('generate_sim_para')

import sys
sys.path.insert(1,'/data/user/015626/JupyterNotebooks/utils/')
from operators_all_wsc import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
from multifactor.IO import IO
import shutil

#send_link('arrow para generate done')

_,end_date,_ = check_update_date()
next_tday = udt.get_trading_day_offset(end_date, [1])[0].strftime('%Y%m%d')
para_root_path = '/data/group/800466/trade/Arrow/para/'
target_path1 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/test_samples/Arrow/v1_0_6/para/'
target_path2 = '/data/user/015626/data/share/LOCAL_DATA/Mobius/data_sample_for_dolphindb/Arrow_para/'
#shutil.copytree(os.path.join(para_root_path, f'Arrow_{next_tday}_sim'), os.path.join(target_path1, f'Arrow_{next_tday}_sim'))
#shutil.copytree(os.path.join(para_root_path, f'Arrow_{next_tday}_sim'), os.path.join(target_path2, f'Arrow_{next_tday}_sim'))

import zipfile
import os

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname=arc_name)

# 调用函数进行文件夹压缩
folder_to_compress = os.path.join(para_root_path, f'Arrow_{next_tday}', 'l2p_params', 'arrow_l2p-front')  # 要压缩的文件夹路径
zip_file_path = os.path.join(para_root_path, f'Arrow_{next_tday}', 'l2p_params', 'arrow_l2p-front.zip')  # 压缩后的zip文件路径
zip_folder(folder_to_compress, zip_file_path)

# upload para to production
from xquant.investment.strategyfile import *

file_info = upload_strategy_file(strategy_id="Arrow_udp", strategy_date= next_tday, file_type=1,
                                         upload_file_path=os.path.join(para_root_path, f'Arrow_{next_tday}', 'md_params', 'arrow_udp-front', 'Arrow_udp#305301.json'), is_delete=False)
assert file_info == True

file_info = upload_strategy_file(strategy_id="Arrow_l2p", strategy_date= next_tday, file_type=0,
                                         upload_file_path=os.path.join(para_root_path, f'Arrow_{next_tday}', 'l2p_params', 'arrow_portfolio.xlsx') , is_delete=False)
assert file_info == True

file_info = upload_strategy_file(strategy_id="Arrow_l2p", strategy_date= next_tday, file_type=1,
                                         upload_file_path=os.path.join(para_root_path, f'Arrow_{next_tday}', 'l2p_params', 'arrow_l2p-front.zip') , is_delete=False)
assert file_info == True

if os.path.exists(os.path.join(para_root_path, f'Arrow_{next_tday}', 'strategy_params', 'arrow_strategy', f'arrow_portfolio_sell_{next_tday}.xlsx')):
    file_info = upload_strategy_file(strategy_id="ArrowCppStrategy", strategy_date= next_tday, file_type=0,
                                             upload_file_path=os.path.join(para_root_path, f'Arrow_{next_tday}', 'strategy_params', 'arrow_strategy', f'arrow_portfolio_sell_{next_tday}.xlsx') , is_delete=False)
    assert file_info == True

    file_info = upload_strategy_file(strategy_id="ArrowCppStrategy", strategy_date= next_tday, file_type=1,
                                             upload_file_path=os.path.join(para_root_path, f'Arrow_{next_tday}', 'strategy_params', 'arrow_strategy-front', 'arrow_sell#305301.json') , is_delete=False)
    assert file_info == True
else:
    send_link('arrow no sell')

file_info = upload_strategy_file(strategy_id="ArrowCppStrategy", strategy_date= next_tday, file_type=0,
                                      upload_file_path=os.path.join(para_root_path, f'Arrow_{next_tday}', 'strategy_params', 'arrow_strategy', f'arrow_portfolio_buy_{next_tday}.xlsx') , is_delete=False)
assert file_info == True

file_info = upload_strategy_file(strategy_id="ArrowCppStrategy", strategy_date= next_tday, file_type=1,
                                      upload_file_path=os.path.join(para_root_path, f'Arrow_{next_tday}', 'strategy_params', 'arrow_strategy-front', 'arrow_buy#305301.json') , is_delete=False)
assert file_info == True

send_link('arrow para upload done')