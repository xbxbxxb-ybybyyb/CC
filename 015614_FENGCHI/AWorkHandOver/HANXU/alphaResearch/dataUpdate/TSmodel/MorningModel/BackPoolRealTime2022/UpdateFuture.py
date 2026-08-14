import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.MorningModel.MorningDailyUpdate.DailyUpdate import \
    update_idx, update_mv_ind, update_future, store_special_neutral, multiprocess, store_risk_factor
from dataApi.tradeDate import get_pre_trade_date, get_recent_trade_date
from dataApi.sendInfo import send_message
import re

# Time 4min
amend_date = None
recent_date = amend_date if amend_date else get_recent_trade_date(dividing_point=19)
data_address = '/data/group/800442/800319/HFfactor/MorningFactor/data/'
future_types = [
    'future930t30h1d', 'future930t30h2d', 'future930t30h3d', 'future930t30h5d', 'future930t30h9d',
    'future930t240h1d', 'future930t240h2d', 'future930t240h3d', 'future930t240h5d', 'future930t240h9d',
    'future1000t210h1d', 'future1000t210h2d', 'future1000t210h3d', 'future1000t210h5d', 'future1000t210h9d',
]
future_std_methods = ['uniform', 'uniform10t30', 'uniform10t50', 'uniform20t50',
                      'WC', 'WCN', 'WCN1mv', 'log1pWC', 'log1pWCN', 'log1pWCN1mv']

update_idx(recent_date, data_address=data_address)
update_mv_ind(recent_date, data_address=data_address)
store_special_neutral('N1mv', ['mkt_cap_ard'], factor_address=data_address)


def _func_future(sub_list, line=0):
    for future_name in sub_list:
        future_days = int(re.match('^future(\d+)t(\d+)h(\d+)(d?)', future_name)[3]) + 1
        update_future(get_pre_trade_date(recent_date, future_days), future_type=future_name,
                      future_std_methods=future_std_methods, data_address=data_address)


multiprocess(15, _func_future, future_types)
store_risk_factor(factor_address=data_address)
send_message(['015664'], '日间标签更新成功')
