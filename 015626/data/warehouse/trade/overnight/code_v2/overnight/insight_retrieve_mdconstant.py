from overnight.insight_base import *
from overnight.naming_config import *
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import multiprocessing
import pandas as pd
import numpy as np
import os
import sys


def calc_adjfactor_rt(preclose_ps):
    assert isinstance(preclose_ps, pd.Series)
    preclose_ps.name = 'preclose'
    now = pd.to_datetime(pd.Timestamp.now().date())
    prev_date = tdt.get_trading_day_offset(now, -1)[0]
    md = IO.read_data(prev_date, columns=['adjfactor', 'close']).loc[prev_date]
    md = md.join(preclose_ps)
    return md['adjfactor'] * md['close'] / md['preclose']


def retrieve_mdconstant_helper(release_resource=True):
    today = pd.Timestamp.now().strftime('%Y%m%d')
    data = job_wrapper(query_last_mdcontant, OnRecvMDConstant, postprocess_mdconstant,
                       release_resource=release_resource)
    # calculate adjfactor
    preclose_rt_ps = data['PreClosePx'] / 1E4
    preclose_rt_ps.name = 'preclose'
    limit_price_rt_ps = data['MaxPx'] / 1E4
    limit_price_rt_ps.name = 'limit'
    stopping_price_rt_ps = data['MinPx'] / 1E4
    stopping_price_rt_ps.name = 'stopping'
    adjfactor_rt_ps = calc_adjfactor_rt(preclose_rt_ps)
    adjfactor_rt_ps.name = 'adjfactor'
    # prepare mdconstant
    mdconstant = pd.concat([adjfactor_rt_ps, preclose_rt_ps, limit_price_rt_ps, stopping_price_rt_ps], axis=1, sort=False).sort_index().infer_objects()
    out_path = os.path.join(trade_root, 'hot', today, 'mdconstant.h5')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    mdconstant.to_hdf(out_path, 'mdconstant', mode='w')
    return mdconstant


if __name__ == '__main__':
    retrieve_mdconstant_helper()

