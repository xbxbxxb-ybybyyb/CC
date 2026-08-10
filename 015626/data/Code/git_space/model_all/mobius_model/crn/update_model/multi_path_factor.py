import sys

sys.path.insert(0, '/data/user/020529/mobius_product/code')

import pandas as pd
from toolkit.multifactor.utility.dt import get_trading_date_range
from toolkit.xdb_reader.generate_history_signal_norm2 import read_factor_from_xdb
from config.base import root
from toolkit.path_helper import save_factor


def main():
    latest_date = '20250328'
    update_date = '20250627'
    for factor_base in ['IF_v7c', 'IC_v7c', 'IM_v1c']:
        for path_id in ['50', '55']:
            update_multi_path_data(factor_base=factor_base, latest_date=latest_date, update_date=update_date, path_id=path_id)
    return None


def update_multi_path_data(factor_base, latest_date, update_date, path_id):
    YMD = '%Y%m%d'
    factor_path = f'{root}/data/factor_{path_id}/{factor_base}.h5'
    print(factor_path, flush=True)
    factor_all = pd.read_hdf(factor_path)
    assert isinstance(factor_all, pd.DataFrame)
    print(factor_all.index[0], '~', factor_all.index[-1], flush=True)

    factor_date = factor_all.index[-1].strftime(YMD)
    if int(latest_date) > int(factor_date):
        latest_date = factor_date
    factor_all = factor_all.loc[:latest_date]

    trade_date_list = get_trading_date_range(start_date=latest_date, end_date=update_date)
    trade_date_list = [x.strftime(YMD) for x in trade_date_list]
    trade_date_list = trade_date_list[1:]

    factor_list = []
    for date in trade_date_list:
        temp = read_factor_from_xdb(date, path_id)
        temp = temp[factor_all.columns]
        factor_list.append(temp)
    factor_new = pd.concat(factor_list, axis=0)
    print(factor_new.index[0], '~', factor_new.index[-1], flush=True)

    factor_all = pd.concat([factor_all, factor_new], axis=0)
    factor_all = factor_all[~factor_all.index.duplicated(keep='first')]
    factor_all = factor_all.sort_index()
    print(factor_all.index[0], '~', factor_all.index[-1], flush=True)
    save_factor(factor_base=factor_base, factor_data=factor_all, path_id=path_id)
    return None


if __name__ == '__main__':
    main()
