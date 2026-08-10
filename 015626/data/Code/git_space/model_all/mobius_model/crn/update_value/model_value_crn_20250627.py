import sys

sys.path.insert(0, '/data/user/020529/mobius_product/code')

import os
import time
import datetime
import warnings
import traceback
import pandas as pd
from config.base import pack_model_root, pack_value_root
from toolkit.multifactor.data.utils import get_current_date
from toolkit.multifactor.utility.dt import get_trading_date_range
from update_helper import update_model
from xquant.xqutils.helper import link


# **************************************************
# os.system('pip install onnx')
# os.system('pip install onnxruntime')
# **************************************************


def main():
    YMD = '%Y%m%d'
    YMD_HMS = '%Y-%m-%d %H:%M:%S'
    curr_date = str(get_current_date(new_date_time=18))

    now = datetime.datetime.now().strftime(YMD_HMS)
    print(f'[{now}] Check flags', flush=True)
    counter = 0
    while True:
        if check_flags(curr_date):
            break
        elif counter < 60 * 24:
            time.sleep(60)
            counter += 1
        else:
            raise RuntimeError('Timeout')
    now = datetime.datetime.now().strftime(YMD_HMS)
    print(f'[{now}] Flags ready', flush=True)

    # ****************************************************************************************************

    model_date = '20250627'
    start_date = (pd.Timestamp(model_date) + pd.Timedelta(days=1)).strftime(YMD)
    trade_date_list = get_trading_date_range(start_date=start_date, end_date=curr_date)
    trade_date_list = [x.strftime(YMD) for x in trade_date_list]
    trade_date_list = trade_date_list[-3:]
    model_root = pack_model_root
    value_root = pack_value_root

    # ****************************************************************************************************

    strategy = '20250627_if_if_v7_crn'
    model_times = {
        'crn_cla': [1, 5, 10],
        'crn_reg': [1, 5, 10],
        'crn_spot_cla': [10, 20, 30],
        'crn_spot_reg': [10, 20, 30],
        'crn_mlp_cla': [1, 5, 10, 20, 30],
        'crn_mlp_reg': [1, 5, 10, 20, 30],
    }
    num_models = 2 * 5  # num_seeds x num_folds(5)
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm'
    assert strategy.split('_')[0] == model_date
    update_model(strategy, model_times, num_models, factor_root, model_root, value_root, trade_date_list)

    strategy = '20250627_ic_ic_v7unifac_crn'
    model_times = {
        'crn_cla': [1, 5, 10],
        'crn_reg': [1, 5, 10],
        'crn_spot_cla': [10, 20, 30],
        'crn_spot_reg': [10, 20, 30],
        'crn_mlp_cla': [1, 5, 10, 20, 30],
        'crn_mlp_reg': [1, 5, 10, 20, 30],
    }
    num_models = 2 * 5  # num_seeds x num_folds(5)
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm'
    assert strategy.split('_')[0] == model_date
    update_model(strategy, model_times, num_models, factor_root, model_root, value_root, trade_date_list)

    strategy = '20250627_im_im_v1unifac_crn'
    model_times = {
        'crn_cla': [1, 5, 10],
        'crn_reg': [1, 5, 10],
        'crn_spot_cla': [10, 20, 30],
        'crn_spot_reg': [10, 20, 30],
        'crn_mlp_cla': [1, 5, 10, 20, 30],
        'crn_mlp_reg': [1, 5, 10, 20, 30],
    }
    num_models = 2 * 5  # num_seeds x num_folds(5)
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm'
    assert strategy.split('_')[0] == model_date
    update_model(strategy, model_times, num_models, factor_root, model_root, value_root, trade_date_list)

    # ****************************************************************************************************

    generate_flags(curr_date)
    return None


def check_flags(date):
    flag1 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/if_factors.success')
    flag2 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/ic_factors.success')
    flag3 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/im_factors.success')
    flag4 = os.path.exists(f'/data/user/020529/share/flag/{date}/rank_index.success')
    ready = flag1 and flag2 and flag3 and flag4
    return ready


def generate_flags(date):
    flag_path = f'/data/user/020529/share/flag/{date}/model_value_crn_20250627.success'
    flag_root = os.path.dirname(flag_path)
    os.makedirs(flag_root, exist_ok=True)
    file = open(flag_path, mode='w')
    file.close()
    return None


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    try:
        main()
    except:
        traceback.print_exc()
        link.LinkMessage().sendMessage('Error: model_value_crn_20250627')
