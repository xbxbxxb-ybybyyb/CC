import sys

sys.path.insert(0, '/data/user/020529/mobius_product/code')

import os
import warnings
import traceback
import pandas as pd
from config.base import pack_value_root
from toolkit.multifactor.data.utils import get_current_date
from toolkit.multifactor.utility.dt import get_trading_date_range
from toolkit.xdb_reader.generate_history_signal_norm2 import read_signal_from_xdb
from xquant.xqutils.helper import link


def main():
    YMD = '%Y%m%d'
    curr_date = str(get_current_date(new_date_time=18))

    model_date = '20250627'
    start_date = (pd.Timestamp(model_date) + pd.Timedelta(days=1)).strftime(YMD)
    trade_date_list = get_trading_date_range(start_date=start_date, end_date=curr_date)
    trade_date_list = [x.strftime(YMD) for x in trade_date_list]
    trade_date_list = trade_date_list[-3:]
    value_root = pack_value_root

    # ****************************************************************************************************

    strategy = '20250627_if_if_v7_crn'
    path_id = '50'
    for update_date in trade_date_list:
        update_model_norm2(strategy, path_id, value_root, model_date, update_date)

    strategy = '20250627_if_if_v7_crn'
    path_id = '55'
    for update_date in trade_date_list:
        update_model_norm2(strategy, path_id, value_root, model_date, update_date)

    strategy = '20250627_ic_ic_v7unifac_crn'
    path_id = '50'
    for update_date in trade_date_list:
        update_model_norm2(strategy, path_id, value_root, model_date, update_date)

    strategy = '20250627_ic_ic_v7unifac_crn'
    path_id = '55'
    for update_date in trade_date_list:
        update_model_norm2(strategy, path_id, value_root, model_date, update_date)

    strategy = '20250627_im_im_v1unifac_crn'
    path_id = '50'
    for update_date in trade_date_list:
        update_model_norm2(strategy, path_id, value_root, model_date, update_date)

    strategy = '20250627_im_im_v1unifac_crn'
    path_id = '55'
    for update_date in trade_date_list:
        update_model_norm2(strategy, path_id, value_root, model_date, update_date)

    # ****************************************************************************************************
    return None


def update_model_norm2(strategy, path_id, value_root, model_date, update_date):
    latest_date = None
    date_root = os.path.join(value_root, f'{strategy}_{path_id}', 'model_value', 'model_norm2')
    date_list = os.listdir(date_root)
    date_list = sorted(date_list, reverse=False)
    for date in date_list:
        if int(date) < int(update_date):
            latest_date = str(date)
    assert latest_date is not None, 'miss historical value'

    if latest_date == model_date:
        signal_path = os.path.join(value_root, f'{strategy}_{path_id}', 'model_value', 'model_norm2', model_date)
        file_list = os.listdir(signal_path)
        file_list.sort()
        signal_list = []
        for file in file_list:
            signal = pd.read_pickle(f'{signal_path}/{file}')
            signal_list.append(signal)
        signal_old = pd.concat(signal_list, axis=1).mean(axis=1)
    else:
        signal_path = os.path.join(value_root, f'{strategy}_{path_id}', 'model_value', 'model_norm2', latest_date, 'pred_comb2.pkl')
        signal_old = pd.read_pickle(signal_path)

    signal_new = read_signal_from_xdb(cols=[strategy], date=update_date, offset=int(path_id), model_group=strategy)
    if len(signal_new) == 237:
        signal_new = signal_new[strategy]
        signal = pd.concat([signal_old, signal_new], axis=0)
        signal = signal.sort_index()

        output_path = os.path.join(value_root, f'{strategy}_{path_id}', 'model_value', 'model_norm2', update_date, 'pred_comb2.pkl')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(output_path, flush=True)
        pd.to_pickle(signal, output_path)
    else:
        print(f'{strategy}_{path_id}: date={update_date}, len(signal_from_xdb)={len(signal_new)}', flush=True)
    return None


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    try:
        main()
    except:
        traceback.print_exc()
        link.LinkMessage().sendMessage('Error: model_value_crn_path_20250627')
