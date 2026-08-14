# @Time : 2020/8/10 14:50
# @Author : Zhichen Lu
# @File : factor_evaluation.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from dataApi.TrueSendFactorTest import _get_fix_factor_list, TrueSendFactorTest, _memory_used
from StrongStockModel.conf.path_config import root_path
import time
import gc
import os
import pandas as pd
import numpy as np
from xquant.compute.aimr import AIMR

"""
class TrueSendFactorSubTest(TrueSendFactorTest):
    def __init__(self,start_date=20140102, end_date=20190628, code_list=None, hold_days=5):
        super().__init__(start_date, end_date, code_list, hold_days)

    def load_factor(self, name, address):
        self.factor_type = 'minute'
        self.factor_name = name.split('.')[0]
        if name.endswith('.npy'):
            factor = np.load(address + '/' + name)
        elif name.endswith('.h5'):
            factor = pd.read_hdf(address+'/'+name,name.replace('.h5',''))
        elif name.endswith('.pkl'):
            factor = pd.read_pickle(address+'/'+name)
        else:
            raise Exception('Wrong file name tail')
        if isinstance(factor,type(np.array([]))):
            pass
        elif isinstance(factor,type(pd.DataFrame([]))):
            factor = factor.loc[self.date_list].reindex(self.code_list,axis=1)
            self.define_transaction_assumption(5)
            factor = factor.values.reshape((len(self.date_list),len(self.freq),factor.shape[0]))
        self.factor = factor
"""

N = 40

def main(part_idx):
    start_date = 20140102
    end_date = 20181231
    code_list = None
    hold_days = 5
    freq = 5  # 'Fix'

    stock_pool_name = 'strong'
    delay_min = 1
    order_keep_min = 10
    period = 'Y'
    roll_window = 245
    top_quantile = [0.05, 0.1, 0.15]
    amt_limit = 5e5
    output_address = '/data/group/800319/Strong_stock/5min_TsNorm%d_StrongTest/' % N
    if not os.path.exists(output_address):
        os.mkdir(output_address)

    t = time.time()
    factor_list = os.listdir(ts_norm_factor_path)  # _get_fix_factor_list()
    factor_list = list(filter(lambda x: not os.path.exists('%s/%s.xlsx' % (output_address, x.replace('.h5', ''))), factor_list))
    tsft = TrueSendFactorTest(start_date, end_date, code_list, hold_days)
    tsft.set_stock_pool(stock_pool_name)
    tsft.define_transaction_assumption(freq, delay_min, order_keep_min)
    print('memory_used=', _memory_used(), ' time_used=', time.time() - t)

    from tqdm import tqdm
    total_len = len(factor_list)
    start = total_len * (part_idx - 1) // partition
    end = total_len * part_idx // partition
    for factor_name in tqdm(factor_list[start:end]):
        factor_name = factor_name.replace('.h5', '')
        if os.path.exists('%s/%s.xlsx' % (output_address, factor_name)):
            print(factor_name, 'exist')
            continue
        # try:
        tsft.load_factor(factor_name, factor_type='minute', base_date=20140101, factor_address=ts_norm_factor_path)
        tsft.calc_ic(period)
        tsft.calc_top_ret(roll_window, top_quantile)
        tsft.calc_finish_ratio(amt_limit)
        tsft.output(output_address)
        print(factor_name, 'done')
        # except:
        #     print(factor_name, 'Wrong')
        #     pd.to_pickle(pd.DataFrame(), output_address + 'Wrong_%s.pkl' % factor_name)
        gc.collect()


partition = 5
ts_norm_factor_path = root_path + 'processed_factor_by_factor_5min/ts_norm_%d/' % N  # root_path + 'processed_factor_by_factor/ts_norm_%d/' % N

# preprocessed_ts_norm_by_factor_path = root_path + 'processed_factor_by_factor_5min/ts_norm_%d/'%N
if __name__ == '__main__':
    # para = int(AIMR.getParam())
    # main(para)
    # print(para, 'done')
    main(1)
