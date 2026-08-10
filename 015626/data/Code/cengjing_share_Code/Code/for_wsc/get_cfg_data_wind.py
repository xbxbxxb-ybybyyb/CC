import sched
import time
import os
import re
import datetime as dt
from functools import partial
import pandas as pd

from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
from WindPy import w
w.start()


def scheduler(func, target_trigger_time, delay=0):
    # init func at given time with delay as in milliseconds
    assert isinstance(target_trigger_time, pd.Timedelta)
    assert callable(func)
    target_trigger_time = (pd.Timestamp(pd.Timestamp.now().date()) + target_trigger_time).to_pydatetime().timestamp() + delay / 1000
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(target_trigger_time, 0, func)
    s.run(blocking=True)
    



def get_wsi_data(start_date, end_date, codes, store_path, fields='open,high,low,close,volume,amt,oi', timedelta=None):
    if not os.path.exists(store_path):
        os.makedirs(store_path)
    store_path1 = store_path + '/' + 'cfg_afternoon.h5'
    if timedelta is None:
        timedelta = pd.Timedelta('0D')
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    if (start_date - pd.Timestamp(start_date.date())).total_seconds() == 0:
        if tdt.get_trading_day_offset(start_date, 0)[0] == start_date:
            _start_date = tdt.get_trading_day_offset(start_date, -1)[0] + pd.Timedelta('1D') + timedelta
        else:
            _start_date = tdt.get_trading_day_offset(start_date, 0)[0] + pd.Timedelta('1D') + timedelta
        _end_date = end_date + pd.Timedelta('1D') + timedelta
    else:
        _start_date, _end_date = start_date, end_date
    assert isinstance(codes, list)
    codes_str = ','.join(codes)
    wdata = w.wsi(codes_str, fields, _start_date.strftime('%Y-%m-%d %H:%M:%S'), _end_date.strftime('%Y-%m-%d %H:%M:%S'))
    if wdata.ErrorCode != 0:
        assert len(codes) > 1, 'Quota may be exceeded'
        try:
            print('Num of codes exceeds limit %d. Msg: %s' % (len(codes), wdata.Data[0][0]))
        except:
            import pdb;pdb.set_trace()
        sep = int(len(codes) / 2)
        nested_list = [get_wsi_data(start_date, end_date, codes[:sep], fields, timedelta),
                       get_wsi_data(start_date, end_date, codes[sep:], fields, timedelta)]
        data_need = pd.concat(nested_list, axis=0).sort_index()
        data_need.to_hdf(store_path1, key='data_need')
        return None
    else:
        if len(codes) > 1:
            w_pd = pd.DataFrame(np.array(wdata.Data).T.tolist(), columns=wdata.Fields)
            w_pd['time'] = wdata.Times 
            data_need = w_pd.rename(columns={'time': 'dt', 'windcode': 'Ticker'}).set_index(['dt', 'Ticker']).dropna(how='all').sort_index()
            data_need.to_hdf(store_path1, key='data_need')
            return None
        else:
            w_pd = pd.DataFrame(np.array(wdata.Data).T.tolist(), columns=wdata.Fields, index=wdata.Times)
            w_pd['Ticker'] = codes[0]
            w_pd.index.name = 'dt'
            data_need = w_pd.reset_index().set_index(['dt', 'Ticker']).dropna(how='all').sort_index()
            data_need.to_hdf(store_path1, key='data_need')
            return None


if __name__ == '__main__':
    today_int = int(dt.datetime.now().strftime('%Y%m%d'))
    starttime = int(today_int * 1e6 + 93000)
    endtime = int(today_int * 1e6 + 112900)

    fdate_list_dt = IO.read_data([19980101, 21000101], ftype=FType.CALENDAR, h5root='B:/group/800080/warehouse/prod').index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    last_trade_date = fdate_list[fdate_list.index(today_int)-1]

    idx = IO.read_data(last_trade_date, alt = 'B:/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    _ = idx[['index_weight_hs300', 'index_weight_zz500']].sum(axis=1)
    tickers = _.loc[_ != 0].loc[pd.to_datetime(str(last_trade_date))].index.tolist()

    flag_root = 'A:/data/share/LOCAL_DATA/FLAG/' + str(today_int)
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + '/' + str(today_int) + '_cfg_afternoon.start'
    with open(flag_path_start,'w') as file:
        pass
    print(starttime, endtime, len(tickers))
    print(tickers)
    exit()
    get_wsi_data(start_date=starttime, end_date=endtime, codes=tickers,\
                                     store_path='A:/data/share/MD/CHINA_STOCK/noon_minute_for_overnight/'+ str(today_int),\
                                     fields='open,high,low,close,volume,amt')

    # get_wsi_data_afternoon = partial(get_wsi_data, start_date=starttime, end_date=endtime, codes=tickers,\
    #                                  store_path='A:/data/share/MD/CHINA_STOCK/noon_minute_for_overnight/'+ str(today_int),\
    #                                  fields='open,high,low,close,volume,amt')
    # today_data_afternoon = scheduler(get_wsi_data_afternoon, target_trigger_time=pd.Timedelta(hours=11, minutes=50), delay=100)

    flag_path_success = flag_root + '/' +  str(today_int) + '_cfg_afternoon.success'
    with open(flag_path_success, 'w') as file:
        pass
