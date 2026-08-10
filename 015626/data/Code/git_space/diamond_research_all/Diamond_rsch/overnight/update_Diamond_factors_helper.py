import os
import pandas as pd
from overnight.naming_config import trade_stop_time, hisfactor_path
from overnight.factor_generator import prepare_history, executor
from overnight.prepare_hot_dummy import prepare_hot_dummy
from overnight.utility import get_current_date


def get_factors(date):
    print(date, trade_stop_time.strftime('%H%M'))
    prepare_history(trade_date = date, has_hist=True, need_raw=True)
    prepare_hot_dummy(ref_date = date)
    factor_new = executor(trade_date = date, mode = 'history', tag='factors', need_norm=True, max_workers=24)
    savepath = os.path.join(hisfactor_path, str(date) + '_' + trade_stop_time.strftime('%H%M'))
    old_factor_path = os.path.join(savepath, str(date) + '_' + trade_stop_time.strftime('%H%M') + '.csv')
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    if os.path.exists(old_factor_path):
        factor_old = pd.read_csv(old_factor_path, index_col=0)
        factor_old = factor_old.loc[[i for i in factor_old.index if i not in factor_new.index]]  # 如果新旧因子有重合，则以新因子为准
        factor_new = pd.concat([factor_old, factor_new], axis=0)
    factor_new.to_csv(old_factor_path)
    
    
if __name__ == '__main__':
    date = get_current_date()
    get_factors(date)